#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Terminate all instances in a Lambda Labs cluster."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_terminate
short_description: Terminate all instances in a cluster
description:
  - Terminate every instance matching the cluster name prefix.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Cluster name to terminate.
    type: str
    required: true
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Terminate cluster
  stevefulme1.lambdalabs.cluster_terminate:
    api_key: "{{ lambda_api_key }}"
    name: training-cluster
"""

RETURN = r"""
terminated_ids:
  description: IDs of terminated instances.
  type: list
  returned: success
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
    spec.update(name=dict(type="str", required=True))
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instances")
        cluster_name = module.params["name"]
        ids = [
            i["id"] for i in result.get("data", [])
            if (i.get("name") or "").startswith(cluster_name) and i.get("status") != "terminated"
        ]

        if not ids:
            module.exit_json(changed=False, terminated_ids=[])

        if module.check_mode:
            module.exit_json(changed=True, terminated_ids=ids)

        client.post("instance-operations/terminate", data={"instance_ids": ids})
        module.exit_json(changed=True, terminated_ids=ids)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
