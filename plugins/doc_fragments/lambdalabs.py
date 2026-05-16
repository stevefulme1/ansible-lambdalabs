"""Documentation fragment for Lambda Labs modules."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment:
    DOCUMENTATION = r"""
options:
  api_key:
    description:
      - Lambda Labs API key used for authentication.
      - Can also be set via the E(LAMBDA_API_KEY) environment variable.
    type: str
    required: true
  timeout:
    description:
      - HTTP request timeout in seconds.
    type: int
    default: 30
"""
