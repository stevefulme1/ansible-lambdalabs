#!/usr/bin/python
# -*- coding: utf-8 -*-

"""List available Lambda Labs GPU instance types."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_type_info
short_description: List available Lambda Labs GPU instance types
description:
  - Retrieve the catalogue of GPU instance types (A100, H100, etc.).
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: List GPU instance types
  stevefulme1.lambdalabs.instance_type_info:
    api_key: "{{ lambda_api_key }}"
  register: types
"""

RETURN = r"""
instance_types:
  description: Available instance types with specs and pricing.
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
    module = AnsibleModule(
        argument_spec=lambda_argument_spec(), supports_check_mode=True
    )
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instance-types")
        module.exit_json(changed=False, instance_types=result.get("data", {}))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
