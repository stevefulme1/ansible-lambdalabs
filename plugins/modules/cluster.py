#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Launch a multi-node GPU cluster on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster
short_description: Launch multi-node GPU cluster
description:
  - Launch multiple instances with shared filesystem as a logical cluster.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Cluster name (used as instance name prefix).
    type: str
    required: true
  instance_type:
    description: GPU instance type for all nodes.
    type: str
    required: true
  count:
    description: Number of nodes to launch.
    type: int
    required: true
  ssh_key_names:
    description: SSH key names.
    type: list
    elements: str
    required: true
  file_system_names:
    description: Shared filesystem names.
    type: list
    elements: str
    default: []
  region:
    description: Region.
    type: str
    required: true
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Launch 4-node H100 cluster
  stevefulme1.lambdalabs.cluster:
    api_key: "{{ lambda_api_key }}"
    name: training-cluster
    instance_type: gpu_8x_h100
    count: 4
    ssh_key_names: [my-key]
    file_system_names: [shared-data]
    region: us-east-1
"""

RETURN = r"""
instance_ids:
  description: IDs of launched cluster instances.
  type: list
  returned: success
  elements: str
cluster_name:
  description: Cluster name prefix.
  type: str
  returned: success
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
        instance_type=dict(type="str", required=True),
        count=dict(type="int", required=True),
        ssh_key_names=dict(type="list", elements="str", required=True, no_log=False),
        file_system_names=dict(type="list", elements="str", default=[]),
        region=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=True, instance_ids=[], cluster_name=module.params["name"])

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post(
            "instance-operations/launch",
            data={
                "region_name": module.params["region"],
                "instance_type_name": module.params["instance_type"],
                "ssh_key_names": module.params["ssh_key_names"],
                "file_system_names": module.params["file_system_names"],
                "quantity": module.params["count"],
                "name": module.params["name"],
            },
        )
        module.exit_json(
            changed=True,
            instance_ids=result.get("data", {}).get("instance_ids", []),
            cluster_name=module.params["name"],
        )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
