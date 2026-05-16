#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Check real-time GPU availability on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_availability_info
short_description: Check real-time GPU availability by type and region
description:
  - Query the Lambda Labs API for current GPU instance availability.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_type:
    description: Filter by instance type name.
    type: str
  region:
    description: Filter by region name.
    type: str
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Check H100 availability
  stevefulme1.lambdalabs.instance_availability_info:
    api_key: "{{ lambda_api_key }}"
    instance_type: gpu_8x_h100
"""

RETURN = r"""
availability:
  description: Availability data by instance type and region.
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
    spec = lambda_argument_spec()
    spec.update(
        instance_type=dict(type="str"),
        region=dict(type="str"),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)
    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.get("instance-types")
        data = result.get("data", {})

        itype = module.params.get("instance_type")
        region = module.params.get("region")

        if itype:
            data = {k: v for k, v in data.items() if k == itype}
        if region:
            filtered = {}
            for k, v in data.items():
                regions = [
                    r for r in v.get("regions_with_capacity_available", [])
                    if r.get("name") == region
                ]
                if regions:
                    entry = dict(v)
                    entry["regions_with_capacity_available"] = regions
                    filtered[k] = entry
            data = filtered

        module.exit_json(changed=False, availability=data)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
