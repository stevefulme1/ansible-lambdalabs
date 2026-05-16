#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Create or delete Lambda Labs persistent filesystems."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: filesystem
short_description: Create or delete persistent filesystems
description:
  - Manage persistent shared filesystems on Lambda Labs.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  name:
    description: Filesystem name.
    type: str
    required: true
  region:
    description: Region for the filesystem (required when O(state=present)).
    type: str
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Create a persistent filesystem
  stevefulme1.lambdalabs.filesystem:
    api_key: "{{ lambda_api_key }}"
    name: training-data
    region: us-east-1
    state: present
"""

RETURN = r"""
filesystem:
  description: Filesystem details.
  type: dict
  returned: when state is present
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


def find_filesystem(client, name):
    result = client.get("file-systems")
    for fs in result.get("data", []):
        if fs.get("name") == name:
            return fs
    return None


def main():
    spec = lambda_argument_spec()
    spec.update(
        name=dict(type="str", required=True),
        region=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(
        argument_spec=spec,
        required_if=[("state", "present", ["region"])],
        supports_check_mode=True,
    )

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        existing = find_filesystem(client, module.params["name"])

        if module.params["state"] == "present":
            if existing:
                module.exit_json(changed=False, filesystem=existing)
            if module.check_mode:
                module.exit_json(changed=True, filesystem={})
            result = client.post(
                "file-systems",
                data={
                    "name": module.params["name"],
                    "region": module.params["region"],
                },
            )
            module.exit_json(changed=True, filesystem=result.get("data", {}))
        else:
            if not existing:
                module.exit_json(changed=False)
            if module.check_mode:
                module.exit_json(changed=True)
            client.delete("file-systems/{0}".format(existing["id"]))
            module.exit_json(changed=True)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
