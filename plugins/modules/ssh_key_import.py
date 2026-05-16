#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Import an SSH key from a local file path."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: ssh_key_import
short_description: Import SSH key from file path
description:
  - Read an SSH public key from a local file and register it on Lambda Labs.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Name for the SSH key.
    type: str
    required: true
  path:
    description: Local path to the SSH public key file.
    type: path
    required: true
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Import SSH key from file
  stevefulme1.lambdalabs.ssh_key_import:
    api_key: "{{ lambda_api_key }}"
    name: my-key
    path: ~/.ssh/id_ed25519.pub
"""

RETURN = r"""
ssh_key:
  description: Registered SSH key details.
  type: dict
  returned: success
"""

import os

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def main():
    spec = lambda_argument_spec()
    spec.update(
        name=dict(type="str", required=True),
        path=dict(type="path", required=True),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    key_path = os.path.expanduser(module.params["path"])
    if not os.path.isfile(key_path):
        module.fail_json(msg="SSH key file not found: {0}".format(key_path))

    try:
        with open(key_path, "r") as fh:
            public_key = fh.read().strip()
    except IOError as exc:
        module.fail_json(msg="Failed to read key file: {0}".format(exc))

    if module.check_mode:
        module.exit_json(changed=True, ssh_key={})

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post(
            "ssh-keys",
            data={"name": module.params["name"], "public_key": public_key},
        )
        module.exit_json(changed=True, ssh_key=result.get("data", {}))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
