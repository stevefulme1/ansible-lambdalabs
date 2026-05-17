#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Schedule and manage GPU jobs on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: job_scheduler
short_description: Schedule and manage GPU jobs on Lambda Labs
description:
  - Schedule, manage, and cancel GPU compute jobs on Lambda Labs Cloud.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Name for the scheduled job.
    type: str
    required: true
  instance_type:
    description: GPU instance type (e.g. C(gpu_1x_a100)).
    type: str
  region:
    description: Region to launch in.
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
  job_id:
    description: Job ID to manage (required when O(state=absent)).
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Schedule a GPU job
  stevefulme1.lambdalabs.job_scheduler:
    api_key: "{{ lambda_api_key }}"
    name: batch-inference
    instance_type: gpu_1x_a100
    region: us-west-1
    ssh_key_names:
      - my-key
    state: present

- name: Cancel a scheduled job
  stevefulme1.lambdalabs.job_scheduler:
    api_key: "{{ lambda_api_key }}"
    name: batch-inference
    job_id: job-xyz789
    state: absent
"""

RETURN = r"""
job:
  description: Scheduled job details.
  type: dict
  returned: when state is present
terminated_ids:
  description: IDs of terminated job instances.
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


def schedule_job(client, params):
    payload = {
        "region_name": params["region"],
        "instance_type_name": params["instance_type"],
        "ssh_key_names": params["ssh_key_names"],
        "file_system_names": params["file_system_names"],
        "quantity": params["quantity"],
        "name": params["name"],
    }
    return client.post("instance-operations/launch", data=payload)


def main():
    spec = lambda_argument_spec()
    spec.update(
        name=dict(type="str", required=True),
        instance_type=dict(type="str"),
        region=dict(type="str"),
        ssh_key_names=dict(type="list", elements="str", default=[], no_log=False),
        file_system_names=dict(type="list", elements="str", default=[]),
        quantity=dict(type="int", default=1),
        job_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(
        argument_spec=spec,
        required_if=[
            ("state", "present", ["instance_type", "region", "ssh_key_names"]),
            ("state", "absent", ["job_id"]),
        ],
        supports_check_mode=True,
    )

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        if module.params["state"] == "present":
            if module.check_mode:
                module.exit_json(changed=True, job={})
            result = schedule_job(client, module.params)
            module.exit_json(
                changed=True,
                job=result.get("data", {}),
            )
        else:
            if module.check_mode:
                module.exit_json(changed=True, terminated_ids=[module.params["job_id"]])
            result = client.post(
                "instance-operations/terminate",
                data={"instance_ids": [module.params["job_id"]]},
            )
            module.exit_json(
                changed=True,
                terminated_ids=result.get("data", {}).get("terminated_instances", []),
            )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
