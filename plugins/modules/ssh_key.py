#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Add or delete SSH keys on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ssh_key
short_description: Add or delete Lambda Labs SSH keys
description:
  - Register or remove SSH public keys on Lambda Labs.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Name for the SSH key.
    type: str
    required: true
  public_key:
    description: SSH public key content (required when O(state=present)).
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Add an SSH key
  stevefulme1.lambdalabs.ssh_key:
    api_key: "{{ lambda_api_key }}"
    name: deploy-key
    public_key: "ssh-ed25519 AAAA..."
    state: present

- name: Remove an SSH key
  stevefulme1.lambdalabs.ssh_key:
    api_key: "{{ lambda_api_key }}"
    name: deploy-key
    state: absent
"""

RETURN = r"""
ssh_key:
  description: SSH key details.
  type: dict
  returned: when state is present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def find_key(client, name):
    result = client.get("ssh-keys")
    for key in result.get("data", []):
        if key.get("name") == name:
            return key
    return None


def main():
    spec = lambda_argument_spec()
    spec.update(
        name=dict(type="str", required=True),
        public_key=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(
        argument_spec=spec,
        required_if=[("state", "present", ["public_key"])],
        supports_check_mode=True,
    )

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        existing = find_key(client, module.params["name"])

        if module.params["state"] == "present":
            if existing:
                module.exit_json(changed=False, ssh_key=existing)
            if module.check_mode:
                module.exit_json(changed=True, ssh_key={})
            result = client.post(
                "ssh-keys",
                data={
                    "name": module.params["name"],
                    "public_key": module.params["public_key"],
                },
            )
            module.exit_json(changed=True, ssh_key=result.get("data", {}))
        else:
            if not existing:
                module.exit_json(changed=False)
            if module.check_mode:
                module.exit_json(changed=True)
            key_id = existing.get("id")
            client.delete("ssh-keys/{0}".format(key_id))
            module.exit_json(changed=True)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
