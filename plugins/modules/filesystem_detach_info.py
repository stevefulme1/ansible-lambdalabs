#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""List or get details about Lambda Labs filesystem detachments."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: filesystem_detach_info
short_description: List or get Lambda Labs filesystem detachments
description:
  - Retrieve information about filesystem detachments.
  - This module is read-only and does not modify any resources.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  filesystem_id:
    description: Specific filesystem id to query. Omit to list all.
    type: str
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
notes:
  - This module is read-only and supports check mode.
  - Use C(limit) and C(offset) for pagination of large result sets.
author:
  - Steve Fulmer (@stevefulme1)
seealso:
  - module: stevefulme1.lambdalabs.filesystem_detach
"""

EXAMPLES = r"""
- name: List all filesystem detachments
  stevefulme1.lambdalabs.filesystem_detach_info:
    api_key: "{{ lambda_api_key }}"
  register: result

- name: Get a specific record
  stevefulme1.lambdalabs.filesystem_detach_info:
    api_key: "{{{ lambda_api_key }}}"
    filesystem_id: abc123
"""

RETURN = r"""
filesystem_detachments:
  description: List of filesystem detachments.
  type: list
  returned: always
  elements: dict
  contains:
    id:
      description: Unique identifier.
      type: str
      returned: always
    name:
      description: Resource name.
      type: str
      returned: when available
    status:
      description: Current status.
      type: str
      returned: when available
    created_at:
      description: Creation timestamp.
      type: str
      returned: when available
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
    spec.update(
        limit=dict(type="int", default=100),
        offset=dict(type="int", default=0),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        filesystem_id = module.params.get("filesystem_id")
        if filesystem_id:
            result = client.get("file-systems/{0}".format(filesystem_id))
            items = [result.get("data", {})]
        else:
            result = client.get("file-systems")
            items = result.get("data", [])
        module.exit_json(changed=False, filesystem_detachments=items)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
