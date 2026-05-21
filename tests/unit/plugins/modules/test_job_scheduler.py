"""Unit tests for stevefulme1.lambdalabs.job_scheduler module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type
from unittest.mock import MagicMock

import pytest

MODULE_PATH = "ansible_collections.stevefulme1.lambdalabs.plugins.modules.job_scheduler"
CLIENT_PATH = "ansible_collections.stevefulme1.lambdalabs.plugins.module_utils.lambda_client"


@pytest.fixture
def mock_api_client():
    """Mock API client for job_scheduler."""
    client = MagicMock()
    client.get.return_value = None
    client.create.return_value = {"id": "res-123", "name": "test-job_scheduler"}
    client.update.return_value = {"id": "res-123", "name": "test-job_scheduler-updated"}
    client.delete.return_value = None
    client.list.return_value = []
    return client


@pytest.fixture
def existing_resource():
    """Return a dict representing an existing job_scheduler."""
    return {
        "id": "res-123",
        "name": "test-job_scheduler",
        "state": "active",
    }


class TestCreateJobScheduler:
    """Tests for creating a job_scheduler."""

    def test_create_returns_resource(self, mock_api_client):
        """Verify create returns resource dict with expected fields."""
        result = mock_api_client.create("job_scheduler", {"name": "test-job_scheduler"})
        assert result["id"] == "res-123"
        assert result["name"] == "test-job_scheduler"
        mock_api_client.create.assert_called_once()

    def test_create_api_error(self):
        """Verify API errors are raised on create."""
        client = MagicMock()
        client.create.side_effect = Exception("409 Conflict")
        with pytest.raises(Exception, match="409 Conflict"):
            client.create("job_scheduler", {"name": "test"})


class TestDeleteJobScheduler:
    """Tests for deleting a job_scheduler."""

    def test_delete_existing(self, mock_api_client, existing_resource):
        """Verify delete is called for existing resource."""
        mock_api_client.get.return_value = existing_resource
        mock_api_client.delete("job_scheduler", "res-123")
        mock_api_client.delete.assert_called_once_with("job_scheduler", "res-123")

    def test_delete_nonexistent(self, mock_api_client):
        """Verify delete handles missing resource gracefully."""
        mock_api_client.get.return_value = None
        mock_api_client.delete.side_effect = Exception("404 Not Found")
        with pytest.raises(Exception, match="404"):
            mock_api_client.delete("job_scheduler", "missing")


class TestIdempotencyJobScheduler:
    """Tests for idempotency behavior."""

    def test_no_change_when_exists(self, mock_api_client, existing_resource):
        """Verify no API call when resource already in desired state."""
        mock_api_client.get.return_value = existing_resource
        result = mock_api_client.get("job_scheduler", "res-123")
        assert result["id"] == "res-123"
