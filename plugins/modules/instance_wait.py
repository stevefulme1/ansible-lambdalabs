#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Wait for a Lambda Labs instance to reach a target state."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_wait
short_description: Wait for a Lambda Labs instance to reach a target state
description:
  - Poll an instance until it reaches the requested state or a timeout occurs.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_id:
    description: Instance ID to monitor.
    type: str
    required: true
  target_state:
    description: State to wait for.
    type: str
    choices: [active, terminated, booting, unhealthy]
    default: active
  poll_interval:
    description: Seconds between status checks.
    type: int
    default: 15
  max_wait:
    description: Maximum seconds to wait before failing.
    type: int
    default: 600
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: Wait for instance to become active
  stevefulme1.lambdalabs.instance_wait:
    api_key: "{{ lambda_api_key }}"
    instance_id: abc123
    target_state: active
    max_wait: 300
"""

RETURN = r"""
instance:
  description: Instance details once target state is reached.
  type: dict
  returned: success
elapsed:
  description: Seconds waited.
  type: int
  returned: always
"""

import time

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
        target_state=dict(
            type="str",
            choices=["active", "terminated", "booting", "unhealthy"],
            default="active",
        ),
        poll_interval=dict(type="int", default=15),
        max_wait=dict(type="int", default=600),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=False, instance={}, elapsed=0)

    client = LambdaClient(module.params["api_key"], module.params["timeout"])
    target = module.params["target_state"]
    start = time.time()

    try:
        while True:
            elapsed = int(time.time() - start)
            if elapsed >= module.params["max_wait"]:
                module.fail_json(
                    msg="Timed out waiting for state '{0}' after {1}s".format(target, elapsed),
                    elapsed=elapsed,
                )

            result = client.get("instances/{0}".format(module.params["instance_id"]))
            data = result.get("data", {})
            if data.get("status") == target:
                module.exit_json(changed=False, instance=data, elapsed=elapsed)

            time.sleep(module.params["poll_interval"])
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
