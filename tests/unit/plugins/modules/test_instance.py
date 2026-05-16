"""Unit tests for the instance module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.lambdalabs.plugins.modules import instance


class TestInstanceDocumentation:
    """Validate module documentation strings."""

    def test_documentation_has_instance_type(self):
        assert "instance_type" in instance.DOCUMENTATION

    def test_documentation_has_state(self):
        assert "state" in instance.DOCUMENTATION

    def test_documentation_has_region(self):
        assert "region" in instance.DOCUMENTATION

    def test_documentation_has_ssh_key_names(self):
        assert "ssh_key_names" in instance.DOCUMENTATION

    def test_documentation_has_instance_ids(self):
        assert "instance_ids" in instance.DOCUMENTATION


class TestInstanceExamples:
    """Validate module examples."""

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.lambdalabs" in instance.EXAMPLES


class TestInstanceReturn:
    """Validate module return documentation."""

    def test_return_exists(self):
        assert instance.RETURN is not None
        assert len(instance.RETURN) > 0
