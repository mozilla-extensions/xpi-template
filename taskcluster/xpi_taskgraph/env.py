# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""
Apply some defaults and minor modifications to the jobs defined in the build
kind.
"""

from __future__ import absolute_import, print_function, unicode_literals
import os

from taskgraph.transforms.base import TransformSequence


transforms = TransformSequence()


@transforms.add
def env_from_decision(config, jobs):
    env_vars = ("XPI_BASE_REPOSITORY", "XPI_HEAD_REF", "XPI_HEAD_REPOSITORY",
                "XPI_HEAD_REV", "XPI_PULL_REQUEST_NUMBER", "XPI_REPOSITORY_TYPE")
    xpi_env = {}
    for env_var in env_vars:
        if env_var in os.environ:
            xpi_env[env_var] = os.environ[env_var]
    for job in jobs:
        env = job.setdefault("worker", {}).setdefault("env", {})
        env.update(xpi_env)
        yield job
