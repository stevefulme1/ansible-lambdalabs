#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""List instances belonging to a Lambda Labs cluster."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: cluster_info
short_description: List cluster instances
description:
  - Retrieve all instances matching a cluster name prefix.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Cluster name to filter by.
    type: str
    required: true
author:
  - Steve Fulmer (@stevefulme1)
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
"""

EXAMPLES = r"""
- name: List cluster nodes
  stevefulme1.lambdalabs.cluster_info:
    api_key: "{{ lambda_api_key }}"
    name: training-cluster
"""

RETURN = r"""
instances:
  description: Instances in the cluster.
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
    spec.update(
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instances")
        cluster_name = module.params["name"]
        instances = [
            i
            for i in result.get("data", [])
            if (i.get("name") or "").startswith(cluster_name)
        ]
        module.exit_json(changed=False, instances=instances)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
