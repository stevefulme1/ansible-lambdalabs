#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Restart a Lambda Labs instance."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_restart
short_description: Restart a Lambda Labs instance
description:
  - Restart a running Lambda Labs GPU instance.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_ids:
    description: List of instance IDs to restart.
    type: list
    elements: str
    required: true
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Restart an instance
  stevefulme1.lambdalabs.instance_restart:
    api_key: "{{ lambda_api_key }}"
    instance_ids:
      - abc123
"""

RETURN = r"""
restarted_ids:
  description: IDs of restarted instances.
  type: list
  returned: always
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def main():
    spec = lambda_argument_spec()
    spec.update(instance_ids=dict(type="list", elements="str", required=True))
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=True, restarted_ids=module.params["instance_ids"])

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post(
            "instance-operations/restart",
            data={"instance_ids": module.params["instance_ids"]},
        )
        module.exit_json(
            changed=True,
            restarted_ids=result.get("data", {}).get("restarted_instances", []),
        )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
