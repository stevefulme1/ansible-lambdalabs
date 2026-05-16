#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Dynamic inventory plugin for Lambda Labs GPU Cloud."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
name: lambda_inventory
short_description: Lambda Labs dynamic inventory
description:
  - Query the Lambda Labs API for all instances and build inventory
    grouped by instance type, region, and status.
version_added: "1.0.0"
extends_documentation_fragment:
  - inventory_cache
  - constructed
options:
  api_key:
    description: Lambda Labs API key.
    type: str
    required: true
    env:
      - name: LAMBDA_API_KEY
  timeout:
    description: HTTP request timeout.
    type: int
    default: 30
author:
  - Steve Fulmer
"""

EXAMPLES = r"""
# lambda_inventory.yml
plugin: stevefulme1.lambdalabs.lambda_inventory
api_key: "{{ lookup('env', 'LAMBDA_API_KEY') }}"
"""

import json

from ansible.errors import AnsibleError
from ansible.plugins.inventory import BaseInventoryPlugin, Constructable, Cacheable
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError


class InventoryModule(BaseInventoryPlugin, Constructable, Cacheable):
    NAME = "lambda_inventory"

    def verify_file(self, path):
        if super(InventoryModule, self).verify_file(path):
            return path.endswith(("lambda_inventory.yml", "lambda_inventory.yaml"))
        return False

    def _fetch_instances(self, api_key, timeout):
        url = "https://cloud.lambda.ai/api/v1/instances"
        headers = {
            "Authorization": "Bearer {0}".format(api_key),
            "Accept": "application/json",
        }
        try:
            response = open_url(url, headers=headers, timeout=timeout)
            return json.loads(response.read()).get("data", [])
        except (HTTPError, URLError) as exc:
            raise AnsibleError("Lambda API error: {0}".format(exc))

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache=cache)
        self._read_config_data(path)

        api_key = self.get_option("api_key")
        timeout = self.get_option("timeout")

        cache_key = self.get_cache_key(path)
        instances = None

        if cache:
            try:
                instances = self._cache.get(cache_key)
            except KeyError:
                pass

        if instances is None:
            instances = self._fetch_instances(api_key, timeout)
            if cache:
                self._cache[cache_key] = instances

        for inst in instances:
            hostname = inst.get("ip") or inst.get("id")
            if not hostname:
                continue

            self.inventory.add_host(hostname)

            # Host vars
            self.inventory.set_variable(hostname, "instance_id", inst.get("id"))
            self.inventory.set_variable(hostname, "ip_address", inst.get("ip"))
            self.inventory.set_variable(hostname, "hostname", inst.get("hostname"))
            self.inventory.set_variable(
                hostname,
                "ansible_host",
                inst.get("ip"),
            )

            itype_info = inst.get("instance_type", {})
            itype = itype_info.get("name", "unknown")
            self.inventory.set_variable(hostname, "instance_type", itype)

            region = inst.get("region", {}).get("name", "unknown")
            self.inventory.set_variable(hostname, "region", region)

            status = inst.get("status", "unknown")
            self.inventory.set_variable(hostname, "status", status)

            filesystems = [fs.get("name") for fs in inst.get("file_systems", [])]
            self.inventory.set_variable(hostname, "filesystems", filesystems)

            # Groups
            type_group = "type_{0}".format(itype.replace(".", "_"))
            self.inventory.add_group(type_group)
            self.inventory.add_host(hostname, group=type_group)

            region_group = "region_{0}".format(region.replace("-", "_"))
            self.inventory.add_group(region_group)
            self.inventory.add_host(hostname, group=region_group)

            status_group = "status_{0}".format(status)
            self.inventory.add_group(status_group)
            self.inventory.add_host(hostname, group=status_group)

            # Constructed features
            strict = self.get_option("strict")
            self._set_composite_vars(
                self.get_option("compose"), inst, hostname, strict=strict
            )
            self._add_host_to_composed_groups(
                self.get_option("groups"), inst, hostname, strict=strict
            )
            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"), inst, hostname, strict=strict
            )
