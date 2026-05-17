#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, Steve Fulmer
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""List or get details about Lambda Labs scheduled jobs."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: job_scheduler_info
short_description: Get Lambda Labs scheduled job info
description:
  - Retrieve information about scheduled GPU jobs on Lambda Labs.
version_added: "1.0.0"
extends_documentation_fragment:
  - stevefulme1.lambdalabs.lambdalabs
options:
  job_id:
    description: Specific job ID to query. Omit to list all.
    type: str
author:
  - Steve Fulmer (@stevefulme1)
"""

EXAMPLES = r"""
- name: List all scheduled jobs
  stevefulme1.lambdalabs.job_scheduler_info:
    api_key: "{{ lambda_api_key }}"
  register: result

- name: Get a specific scheduled job
  stevefulme1.lambdalabs.job_scheduler_info:
    api_key: "{{ lambda_api_key }}"
    job_id: job-xyz789
"""

RETURN = r"""
scheduled_jobs:
  description: List of scheduled job details.
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
    spec.update(job_id=dict(type="str"))
    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    client = LambdaClient(module.params["api_key"], module.params["timeout"])

    try:
        jid = module.params.get("job_id")
        if jid:
            result = client.get("instances/{0}".format(jid))
            jobs = [result.get("data", {})]
        else:
            result = client.get("instances")
            jobs = result.get("data", [])
        module.exit_json(changed=False, scheduled_jobs=jobs)
    except LambdaError as exc:
        module.fail_json(msg=str(exc))


if __name__ == "__main__":
    main()
