#!/usr/bin/python
# -*- coding: utf-8 -*-

"""List SSH keys on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ssh_key_info
short_description: List Lambda Labs SSH keys
description:
  - Retrieve all registered SSH keys.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: List SSH keys
  stevefulme1.lambdalabs.ssh_key_info:
    api_key: "{{ lambda_api_key }}"
  register: keys
"""

RETURN = r"""
ssh_keys:
  description: List of SSH key objects.
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
    module = AnsibleModule(argument_spec=lambda_argument_spec(), supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("ssh-keys")
        module.exit_json(changed=False, ssh_keys=result.get("data", []))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
