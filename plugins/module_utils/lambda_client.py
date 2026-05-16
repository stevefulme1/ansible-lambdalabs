"""Base API client for Lambda Labs Cloud API."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError, URLError


API_BASE = "https://cloud.lambda.ai/api/v1/"


class LambdaError(Exception):
    """Exception raised by the Lambda API client."""

    def __init__(self, message, status_code=None, response_body=None):
        super(LambdaError, self).__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class LambdaClient:
    """REST client for the Lambda Labs Cloud API.

    Args:
        api_key: Bearer token for authentication.
        timeout: HTTP request timeout in seconds.
    """

    def __init__(self, api_key, timeout=30):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = API_BASE

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _headers(self):
        return {
            "Authorization": "Bearer {0}".format(self.api_key),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method, path, data=None):
        url = "{0}{1}".format(self.base_url, path.lstrip("/"))
        body = json.dumps(data).encode("utf-8") if data else None

        try:
            response = open_url(
                url,
                method=method,
                headers=self._headers(),
                data=body,
                timeout=self.timeout,
            )
            raw = response.read()
            return json.loads(raw) if raw else {}
        except HTTPError as exc:
            raw = exc.read()
            try:
                detail = json.loads(raw)
            except Exception:
                detail = raw.decode("utf-8", errors="replace")
            raise LambdaError(
                "HTTP {0}: {1}".format(exc.code, detail),
                status_code=exc.code,
                response_body=detail,
            )
        except URLError as exc:
            raise LambdaError("URL error: {0}".format(exc.reason))

    # ------------------------------------------------------------------
    # Public convenience methods
    # ------------------------------------------------------------------

    def get(self, path):
        """Send a GET request."""
        return self._request("GET", path)

    def post(self, path, data=None):
        """Send a POST request."""
        return self._request("POST", path, data=data)

    def delete(self, path, data=None):
        """Send a DELETE request."""
        return self._request("DELETE", path, data=data)


def lambda_argument_spec():
    """Return the common argument spec shared by all Lambda modules."""
    return dict(
        api_key=dict(type="str", required=True, no_log=True),
        timeout=dict(type="int", default=30),
    )
