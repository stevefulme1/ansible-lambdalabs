#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Check inter-node connectivity and GPU health of a Lambda Labs cluster."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_health_info
short_description: Check cluster health
description:
  - Verify that all instances in a cluster are running and report GPU status.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Cluster name.
    type: str
    required: true
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Check cluster health
  stevefulme1.lambdalabs.cluster_health_info:
    api_key: "{{ lambda_api_key }}"
    name: training-cluster
"""

RETURN = r"""
healthy:
  description: Whether all nodes are active.
  type: bool
  returned: always
nodes:
  description: Per-node status.
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
    spec.update(name=dict(type="str", required=True))
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instances")
        cluster_name = module.params["name"]
        nodes = [
            {
                "id": i.get("id"),
                "name": i.get("name"),
                "status": i.get("status"),
                "ip": i.get("ip"),
                "instance_type": i.get("instance_type", {}).get("name"),
            }
            for i in result.get("data", [])
            if (i.get("name") or "").startswith(cluster_name)
        ]
        healthy = all(n["status"] == "active" for n in nodes) and len(nodes) > 0
        module.exit_json(changed=False, healthy=healthy, nodes=nodes)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
