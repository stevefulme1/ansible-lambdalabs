#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Validate API key and get Lambda Labs account info."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: api_key_info
short_description: Validate API key and get account info
description:
  - Verify that the API key is valid and retrieve account details.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
author:
  - Steve Fulmer (@stevefulme1)
options:
"""

EXAMPLES = r"""
- name: Validate API key
  stevefulme1.lambdalabs.api_key_info:
    api_key: "{{ lambda_api_key }}"
"""

RETURN = r"""
account:
  description: Account details.
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
        client.get("instances")
        module.exit_json(changed=False, account={"valid": True})
    except LambdaError as exc:
        if exc.status_code == 401:
            module.exit_json(changed=False, account={"valid": False})
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
