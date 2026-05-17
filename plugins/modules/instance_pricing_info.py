#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Get current pricing per Lambda Labs instance type."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_pricing_info
short_description: Get current pricing per instance type
description:
  - Retrieve per-hour pricing for each Lambda Labs GPU instance type.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
author:
  - Steve Fulmer (@stevefulme1)
options:
  api_key:
    description:
      - Lambda Labs API key for authentication.
    type: str
    required: true
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
  timeout:
    description:
      - API request timeout in seconds.
    type: int
    default: 30
"""

EXAMPLES = r"""
- name: Get pricing
  stevefulme1.lambdalabs.instance_pricing_info:
    api_key: "{{ lambda_api_key }}"
  register: pricing
"""

RETURN = r"""
pricing:
  description: Pricing data keyed by instance type.
  type: dict
  returned: always
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def main():
    argument_spec = lambda_argument_spec()
    argument_spec.update(
        limit=dict(type='int', default=100),
        offset=dict(type='int', default=0),
    )
    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=True
    )
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instance-types")
        pricing = {}
        for name, info in result.get("data", {}).items():
            spec = info.get("instance_type", {})
            pricing[name] = {
                "price_cents_per_hour": spec.get("price_cents_per_hour"),
                "description": spec.get("description"),
            }
        module.exit_json(changed=False, pricing=pricing)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
