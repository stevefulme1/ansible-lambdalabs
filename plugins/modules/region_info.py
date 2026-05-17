#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""List available Lambda Labs regions."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: region_info
short_description: List available regions
description:
  - Retrieve all regions where Lambda Labs instances can be launched.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
author:
  - Steve Fulmer (@stevefulme1)
options:
  api_key:
    description:
      - Lambda Labs API key for authentication.
    type: str
    required: true
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
  timeout:
    description:
      - API request timeout in seconds.
    type: int
    default: 30
"""

EXAMPLES = r"""
- name: List regions
  stevefulme1.lambdalabs.region_info:
    api_key: "{{ lambda_api_key }}"
"""

RETURN = r"""
regions:
  description: List of available regions.
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
        result = client.get("instance-types")
        regions = set()
        for info in result.get("data", {}).values():
            for r in info.get("regions_with_capacity_available", []):
                regions.add(r.get("name", ""))
        module.exit_json(
            changed=False,
            regions=[{"name": r} for r in sorted(regions) if r],
        )
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
