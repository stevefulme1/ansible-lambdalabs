"""Unit tests for the cluster module."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.stevefulme1.lambdalabs.plugins.modules import cluster


class TestClusterDocumentation:
    """Validate module documentation strings."""

    def test_documentation_exists(self):
        assert cluster.DOCUMENTATION is not None
        assert len(cluster.DOCUMENTATION) > 0


class TestClusterExamples:
    """Validate module examples."""

    def test_examples_contain_fqcn(self):
        assert "stevefulme1.lambdalabs" in cluster.EXAMPLES
