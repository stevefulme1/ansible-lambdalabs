#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Scale a Lambda Labs GPU cluster up or down."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_scale
short_description: Scale cluster up or down
description:
  - Adjust the number of nodes in a Lambda Labs GPU cluster.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Cluster name.
    type: str
    required: true
  desired_count:
    description: Desired number of nodes.
    type: int
    required: true
  instance_type:
    description: Instance type (needed when scaling up).
    type: str
  region:
    description: Region (needed when scaling up).
    type: str
  ssh_key_names:
    description: SSH key names (needed when scaling up).
    type: list
    elements: str
    default: []
  file_system_names:
    description: Filesystem names (needed when scaling up).
    type: list
    elements: str
    default: []
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Scale cluster to 8 nodes
  stevefulme1.lambdalabs.cluster_scale:
    api_key: "{{ lambda_api_key }}"
    name: training-cluster
    desired_count: 8
    instance_type: gpu_8x_h100
    region: us-east-1
    ssh_key_names: [my-key]
"""

RETURN = r"""
current_count:
  description: Current node count after scaling.
  type: int
  returned: always
added_ids:
  description: IDs of newly launched instances.
  type: list
  returned: when scaling up
  elements: str
removed_ids:
  description: IDs of terminated instances.
  type: list
  returned: when scaling down
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
    spec.update(
        name=dict(type="str", required=True),
        desired_count=dict(type="int", required=True),
        instance_type=dict(type="str"),
        region=dict(type="str"),
        ssh_key_names=dict(type="list", elements="str", default=[]),
        file_system_names=dict(type="list", elements="str", default=[]),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instances")
        cluster_name = module.params["name"]
        current = [
            i
            for i in result.get("data", [])
            if (i.get("name") or "").startswith(cluster_name)
            and i.get("status") != "terminated"
        ]
        current_count = len(current)
        desired = module.params["desired_count"]

        if current_count == desired:
            module.exit_json(changed=False, current_count=current_count)

        if module.check_mode:
            module.exit_json(changed=True, current_count=desired)

        if desired > current_count:
            add = desired - current_count
            launch = client.post(
                "instance-operations/launch",
                data={
                    "region_name": module.params["region"],
                    "instance_type_name": module.params["instance_type"],
                    "ssh_key_names": module.params["ssh_key_names"],
                    "file_system_names": module.params["file_system_names"],
                    "quantity": add,
                    "name": cluster_name,
                },
            )
            module.exit_json(
                changed=True,
                current_count=desired,
                added_ids=launch.get("data", {}).get("instance_ids", []),
            )
        else:
            remove_count = current_count - desired
            remove_ids = [i["id"] for i in current[:remove_count]]
            client.post(
                "instance-operations/terminate", data={"instance_ids": remove_ids}
            )
            module.exit_json(
                changed=True,
                current_count=desired,
                removed_ids=remove_ids,
            )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
