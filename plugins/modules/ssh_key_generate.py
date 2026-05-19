#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Generate a new SSH key pair on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ssh_key_generate
short_description: Generate a new SSH key pair via Lambda Labs API
description:
  - Generate a new SSH key pair. The private key is returned once and
    must be saved immediately.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Name for the generated key.
    type: str
    required: true
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Generate SSH key
  stevefulme1.lambdalabs.ssh_key_generate:
    api_key: "{{ lambda_api_key }}"
    name: auto-key
  register: key
"""

RETURN = r"""
ssh_key:
  description: Generated key details including private key.
  type: dict
  returned: success
  contains:
    private_key:
      description: PEM-encoded private key (only returned once).
      type: str
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

    if module.check_mode:
        module.exit_json(changed=True, ssh_key={})

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post("ssh-keys", data={"name": module.params["name"]})
        key_data = result.get("data", {})
        private_key = key_data.get("private_key")
        if private_key:
            module.no_log_values.add(private_key)
        module.exit_json(changed=True, ssh_key=key_data)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
