#!/usr/bin/python
# -*- coding: utf-8 -*-

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
  - Steve Fulmer
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
    module = AnsibleModule(argument_spec=lambda_argument_spec(), supports_check_mode=True)
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
