#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Update instance tags/metadata on Lambda Labs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: instance_tag
short_description: Update instance tags and metadata
description:
  - Set or update tags on a Lambda Labs instance.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  instance_id:
    description: Instance ID to tag.
    type: str
    required: true
  tags:
    description: Dictionary of tags to set.
    type: dict
    required: true
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
- name: Tag an instance
  stevefulme1.lambdalabs.instance_tag:
    api_key: "{{ lambda_api_key }}"
    instance_id: abc123
    tags:
      project: llm-training
      team: ml-platform
"""

RETURN = r"""
instance:
  description: Updated instance details.
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
        tags=dict(type="dict", required=True),
    )
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    if module.check_mode:
        module.exit_json(changed=True, instance={})

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        result = client.post(
            "instances/{0}/tags".format(module.params["instance_id"]),
            data=module.params["tags"],
        )
        module.exit_json(changed=True, instance=result.get("data", {}))
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
