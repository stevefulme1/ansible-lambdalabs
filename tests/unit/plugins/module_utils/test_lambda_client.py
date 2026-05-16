"""Unit tests for lambda_client module_utils."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from unittest.mock import MagicMock

from ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client import (
    LambdaClient,
    LambdaError,
    lambda_argument_spec,
)


class TestLambdaArgumentSpec:
    """Tests for lambda_argument_spec."""

    def test_has_api_key(self):
        spec = lambda_argument_spec()
        assert "api_key" in spec

    def test_has_timeout(self):
        spec = lambda_argument_spec()
        assert "timeout" in spec

    def test_api_key_is_no_log(self):
        spec = lambda_argument_spec()
        assert spec["api_key"].get("no_log") is True


class TestLambdaClient:
    """Tests for LambdaClient."""

    def test_init(self):
        client = LambdaClient(api_key="test-key", timeout=60)
        assert client.api_key == "test-key"
        assert client.timeout == 60

    def test_init_default_timeout(self):
        client = LambdaClient(api_key="test-key")
        assert client.timeout == 30

    def test_init_with_mock_module(self):
        module = MagicMock()
        module.params = {"api_key": "mod-key", "timeout": 45}
        client = LambdaClient(
            api_key=module.params["api_key"],
            timeout=module.params["timeout"],
        )
        assert client.api_key == "mod-key"
        assert client.timeout == 45


class TestLambdaError:
    """Tests for LambdaError."""

    def test_message(self):
        err = LambdaError("something broke")
        assert str(err) == "something broke"

    def test_status_code(self):
        err = LambdaError("fail", status_code=404)
        assert err.status_code == 404

    def test_response_body(self):
        err = LambdaError("fail", response_body='{"error": "not found"}')
        assert err.response_body == '{"error": "not found"}'
