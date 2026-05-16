#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Get filesystem usage statistics from Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: filesystem_usage_info
short_description: Get filesystem usage statistics
description:
  - Retrieve storage usage for Lambda Labs persistent filesystems.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  filesystem_id:
    description: Specific filesystem ID. Omit to list all.
    type: str
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Get filesystem usage
  stevefulme1.lambdalabs.filesystem_usage_info:
    api_key: "{{ lambda_api_key }}"
"""

RETURN = r"""
filesystems:
  description: List of filesystem usage data.
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
    spec.update(filesystem_id=dict(type="str"))
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("file-systems")
        data = result.get("data", [])
        fid = module.params.get("filesystem_id")
        if fid:
            data = [fs for fs in data if fs.get("id") == fid]
        module.exit_json(changed=False, filesystems=data)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
