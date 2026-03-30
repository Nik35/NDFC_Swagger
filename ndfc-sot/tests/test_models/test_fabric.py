"""Unit tests for Fabric Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.fabric import FabricCreate


class TestFabricCreate:
    """Tests for FabricCreate validation."""

    def test_valid_minimal(self):
        f = FabricCreate(name="dc1", bgp_as=65001)
        assert f.name == "dc1"
        assert f.bgp_as == 65001

    def test_name_too_long(self):
        with pytest.raises(ValidationError):
            FabricCreate(name="x" * 65, bgp_as=65001)

    def test_bgp_as_range(self):
        with pytest.raises(ValidationError):
            FabricCreate(name="dc1", bgp_as=0)
        with pytest.raises(ValidationError):
            FabricCreate(name="dc1", bgp_as=4294967296)

    def test_name_regex(self):
        """Fabric name should be alphanumeric + hyphens/underscores."""
        f = FabricCreate(name="dc1-prod_01", bgp_as=65001)
        assert f.name == "dc1-prod_01"