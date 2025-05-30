# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""


import os

from taskgraph.transforms.base import TransformSequence
from taskgraph.util.schema import resolve_keyed_by
from taskgraph.util.keyed_by import evaluate_keyed_by


transforms = TransformSequence()

FORMATS = {
    "mozillaonline-privileged": "gcp_prod_privileged_webextension",
    # normandy-privileged is deprecated
    "normandy-privileged": "gcp_prod_privileged_webextension",
    "privileged": "gcp_prod_privileged_webextension",
    "system": "gcp_prod_system_addon",
}


@transforms.add
def define_signing_flags(config, tasks):
    for task in tasks:
        dep = task["primary-dependency"]
        # Current kind will be prepended later in the transform chain.
        task["name"] = _get_dependent_job_name_without_its_kind(dep)
        attributes = dep.attributes.copy()
        if task.get("attributes"):
            attributes.update(task["attributes"])
        task["attributes"] = attributes
        task["attributes"]["signed"] = True
        if "run_on_tasks_for" in task["attributes"]:
            task.setdefault("run-on-tasks-for", task["attributes"]["run_on_tasks_for"])

        for key in ("worker-type", "worker.signing-type"):
            resolve_keyed_by(
                task,
                key,
                item_name=task["name"],
                level=config.params["level"],
            )
        yield task


@transforms.add
def build_signing_task(config, tasks):
    xpi_type = os.environ.get("XPI_SIGNING_TYPE", "unknown")
    for task in tasks:
        if xpi_type not in FORMATS:
            continue
        dep = task["primary-dependency"]
        task["dependencies"] = {"build": dep.label}
        artifact_prefix = dep.task["payload"]["env"]["ARTIFACT_PREFIX"].rstrip("/")
        if not artifact_prefix.startswith("public"):
            scopes = task.setdefault("scopes", [])
            scopes.append(f"queue:get-artifact:{artifact_prefix}/*")
        xpi_name = dep.task["extra"]["xpi-name"]
        # XXX until we can figure out what to sign, assume
        #     `{artifact_prefix}/{xpi_name}.xpi`
        path = f"{artifact_prefix}/{xpi_name}.xpi"
        format = FORMATS[xpi_type]
        task["worker"]["upstream-artifacts"] = [
            {
                "taskId": {"task-reference": "<build>"},
                "taskType": "build",
                "paths": [path],
                "formats": [format],
            }
        ]
        task.setdefault("extra", {})["xpi-name"] = xpi_name
        del task["primary-dependency"]
        yield task


def _get_dependent_job_name_without_its_kind(dependent_job):
    return dependent_job.label[len(dependent_job.kind) + 1 :]
