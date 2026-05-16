#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Attach a filesystem to a Lambda Labs instance."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: filesystem_attach
short_description: Attach filesystem to instance
description:
  - Attach a persistent filesystem to a running instance.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_id:
    description: Instance ID to attach to.
    type: str
    required: true
  filesystem_id:
    description: Filesystem ID to attach.
    type: str
    required: true
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Attach filesystem
  stevefulme1.lambdalabs.filesystem_attach:
    api_key: "{{ lambda_api_key }}"
    instance_id: abc123
    filesystem_id: fs-456
"""

RETURN = r"""
result:
  description: Attach operation result.
  type: dict
  returned: success
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
        instance_id=dict(type="str", required=True),
        filesystem_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=True, result={})

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post(
            "file-systems/{0}/attach".format(module.params["filesystem_id"]),
            data={"instance_id": module.params["instance_id"]},
        )
        module.exit_json(changed=True, result=result.get("data", {}))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
