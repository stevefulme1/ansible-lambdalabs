#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Launch or terminate Lambda Labs GPU instances."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance
short_description: Launch or terminate Lambda Labs GPU instances
description:
  - Launch new GPU instances or terminate existing ones on Lambda Labs Cloud.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Name for the instance.
    type: str
  instance_type:
    description: GPU instance type (e.g. C(gpu_1x_a100), C(gpu_8x_h100)).
    type: str
  region:
    description: Region to launch in (e.g. C(us-east-1)).
    type: str
  ssh_key_names:
    description: List of SSH key names to attach.
    type: list
    elements: str
    default: []
  file_system_names:
    description: List of persistent filesystem names to attach.
    type: list
    elements: str
    default: []
  quantity:
    description: Number of instances to launch.
    type: int
    default: 1
  instance_ids:
    description: Instance IDs to terminate (required when O(state=absent)).
    type: list
    elements: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Launch an A100 instance
  stevefulme1.lambdalabs.instance:
    api_key: "{{ lambda_api_key }}"
    name: training-box
    instance_type: gpu_1x_a100
    region: us-east-1
    ssh_key_names:
      - my-key
    state: present

- name: Terminate instances
  stevefulme1.lambdalabs.instance:
    api_key: "{{ lambda_api_key }}"
    instance_ids:
      - abc123
    state: absent
"""

RETURN = r"""
instances:
  description: List of launched instance details.
  type: list
  returned: when state is present
  elements: dict
terminated_ids:
  description: IDs of terminated instances.
  type: list
  returned: when state is absent
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def launch_instances(client, params):
    payload = {
        "region_name": params["region"],
        "instance_type_name": params["instance_type"],
        "ssh_key_names": params["ssh_key_names"],
        "file_system_names": params["file_system_names"],
        "quantity": params["quantity"],
    }
    if params.get("name"):
        payload["name"] = params["name"]
    return client.post("instance-operations/launch", data=payload)


def terminate_instances(client, instance_ids):
    return client.post(
        "instance-operations/terminate",
        data={"instance_ids": instance_ids},
    )


def main():
    spec = lambda_argument_spec()
    spec.update(
        name=dict(type="str"),
        instance_type=dict(type="str"),
        region=dict(type="str"),
        ssh_key_names=dict(type="list", elements="str", default=[]),
        file_system_names=dict(type="list", elements="str", default=[]),
        quantity=dict(type="int", default=1),
        instance_ids=dict(type="list", elements="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(
        argument_spec=spec,
        required_if=[
            ("state", "present", ["instance_type", "region", "ssh_key_names"]),
            ("state", "absent", ["instance_ids"]),
        ],
        supports_check_mode=True,
    )

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        if module.params["state"] == "present":
            if module.check_mode:
                module.exit_json(changed=True, instances=[])
            result = launch_instances(client, module.params)
            module.exit_json(
                changed=True,
                instances=result.get("data", {}).get("instance_ids", []),
            )
        else:
            if module.check_mode:
                module.exit_json(
                    changed=True, terminated_ids=module.params["instance_ids"]
                )
            result = terminate_instances(client, module.params["instance_ids"])
            module.exit_json(
                changed=True,
                terminated_ids=result.get("data", {}).get("terminated_instances", []),
            )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
