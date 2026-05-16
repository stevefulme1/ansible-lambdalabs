#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Create or delete Lambda Labs filesystem snapshots."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: filesystem_snapshot
short_description: Create or delete filesystem snapshots
description:
  - Manage point-in-time snapshots of persistent filesystems.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  filesystem_id:
    description: Filesystem ID to snapshot.
    type: str
    required: true
  name:
    description: Snapshot name.
    type: str
  snapshot_id:
    description: Snapshot ID (required for O(state=absent)).
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
- name: Create snapshot
  stevefulme1.lambdalabs.filesystem_snapshot:
    api_key: "{{ lambda_api_key }}"
    filesystem_id: fs-123
    name: pre-training-snapshot
    state: present
"""

RETURN = r"""
snapshot:
  description: Snapshot details.
  type: dict
  returned: when state is present
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
        filesystem_id=dict(type="str", required=True),
        name=dict(type="str"),
        snapshot_id=dict(type="str"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(
        argument_spec=spec,
        required_if=[
            ("state", "present", ["name"]),
            ("state", "absent", ["snapshot_id"]),
        ],
        supports_check_mode=True,
    )

    if module.check_mode:
        module.exit_json(changed=True, snapshot={})

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        if module.params["state"] == "present":
            result = client.post(
                "file-systems/{0}/snapshots".format(module.params["filesystem_id"]),
                data={"name": module.params["name"]},
            )
            module.exit_json(changed=True, snapshot=result.get("data", {}))
        else:
            client.delete(
                "file-systems/{0}/snapshots/{1}".format(
                    module.params["filesystem_id"],
                    module.params["snapshot_id"],
                )
            )
            module.exit_json(changed=True)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
