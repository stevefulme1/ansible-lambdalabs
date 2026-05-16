"""Unit tests for the filesystem module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.lambdalabs.plugins.modules import filesystem


class TestFilesystemDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert filesystem.DOCUMENTATION is not None
        assert len(filesystem.DOCUMENTATION) > 0

    def test_documentation_has_name(self):
        assert "name" in filesystem.DOCUMENTATION

    def test_documentation_has_state(self):
        assert "state" in filesystem.DOCUMENTATION


class TestFilesystemExamples:
    """Validate module examples."""

    def test_examples_exist(self):
        assert filesystem.EXAMPLES is not None
        assert len(filesystem.EXAMPLES) > 0
