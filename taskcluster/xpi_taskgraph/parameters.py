# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function, unicode_literals

import os

import six
from six import text_type
from taskgraph.parameters import extend_parameters_schema
from voluptuous import Required


extend_parameters_schema({
    Required("template_base_repository"): text_type,
    Required("template_head_repository"): text_type,
    Required("template_head_ref"): text_type,
    Required("template_head_rev"): text_type,
    Required("template_repository_type"): text_type,
})


def to_unicode(obj):
    if six.PY3 and isinstance(obj, six.binary_type):
        obj = obj.decode('utf-8')
    return obj


def get_decision_parameters(graph_config, parameters):
    parameters["template_base_repository"] = to_unicode(os.environ.get("TEMPLATE_BASE_REPOSITORY", ""))
    parameters["template_head_repository"] = to_unicode(os.environ.get("TEMPLATE_HEAD_REPOSITORY", ""))
    parameters["template_head_ref"] = to_unicode(os.environ.get("TEMPLATE_HEAD_REF", ""))
    parameters["template_head_rev"] = to_unicode(os.environ.get("TEMPLATE_HEAD_REV", ""))
    parameters["template_repository_type"] = to_unicode(os.environ.get("TEMPLATE_REPOSITORY_TYPE", ""))
