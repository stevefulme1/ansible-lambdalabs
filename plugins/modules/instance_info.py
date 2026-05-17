#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""List or get details about Lambda Labs instances."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_info
short_description: List or get Lambda Labs instance details
description:
  - Retrieve information about running Lambda Labs instances.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_id:
    description: Specific instance ID to query. Omit to list all.
    type: str
  limit:
    description:
      - Maximum number of results to return.
    type: int
    default: 100
  offset:
    description:
      - Number of results to skip for pagination.
    type: int
    default: 0
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: List all instances
  stevefulme1.lambdalabs.instance_info:
    api_key: "{{ lambda_api_key }}"
  register: result

- name: Get a specific instance
  stevefulme1.lambdalabs.instance_info:
    api_key: "{{ lambda_api_key }}"
    instance_id: abc123
"""

RETURN = r"""
instances:
  description: List of instance details.
  type: list
  returned: always
  elements: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def main():
    spec = lambda_argument_spec()
    spec.update(instance_id=dict(type="str"))
    spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        iid = module.params.get("instance_id")
        if iid:
            result = client.get("instances/{0}".format(iid))
            instances = [result.get("data", {})]
        else:
            result = client.get("instances")
            instances = result.get("data", [])
        module.exit_json(changed=False, instances=instances)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
