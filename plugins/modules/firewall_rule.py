#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Add or remove firewall rules on Lambda Labs instances."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: firewall_rule
short_description: Add or remove firewall rules
description:
  - Manage firewall rules on Lambda Labs instances.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_id:
    description: Instance ID to manage rules for.
    type: str
    required: true
  protocol:
    description: Network protocol.
    type: str
    choices: [tcp, udp, icmp]
    default: tcp
  port_range:
    description: Port range (e.g. C(8080) or C(8000-9000)).
    type: str
  source_cidr:
    description: Source CIDR block (e.g. C(0.0.0.0/0)).
    type: str
    default: "0.0.0.0/0"
  state:
    description: Desired state.
    type: str
    choices: [present, absent]
    default: present
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Allow SSH
  stevefulme1.lambdalabs.firewall_rule:
    api_key: "{{ lambda_api_key }}"
    instance_id: abc123
    protocol: tcp
    port_range: "22"
    source_cidr: "10.0.0.0/8"
    state: present
"""

RETURN = r"""
rules:
  description: Current firewall rules after change.
  type: list
  returned: success
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
    spec.update(
        instance_id=dict(type="str", required=True),
        protocol=dict(type="str", choices=["tcp", "udp", "icmp"], default="tcp"),
        port_range=dict(type="str"),
        source_cidr=dict(type="str", default="0.0.0.0/0"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=True, rules=[])

    client = LambdaClient(module.params["api_key"], module.params["timeout"])
    iid = module.params["instance_id"]

    rule_data = {
        "protocol": module.params["protocol"],
        "port_range": module.params.get("port_range"),
        "source_cidr": module.params["source_cidr"],
    }

    try:
        if module.params["state"] == "present":
            result = client.post(
                "instances/{0}/firewall-rules".format(iid),
                data=rule_data,
            )
        else:
            result = client.delete(
                "instances/{0}/firewall-rules".format(iid),
                data=rule_data,
            )
        module.exit_json(changed=True, rules=result.get("data", []))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
