"""Unit tests for Switch Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.inventory import SwitchCreate


class TestSwitchCreate:
    def test_valid(self):
        sw = SwitchCreate(
            name="dc1-leaf-01",
            serial_number="FDO12345678",
            role="leaf",
        )
        assert sw.name == "dc1-leaf-01"
        assert sw.role == "leaf"

    def test_required_fields(self):
        with pytest.raises(ValidationError) as exc_info:
            SwitchCreate(
                serial_number="FDO12345678",
                role="leaf",
            )
        assert "field required" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            SwitchCreate(
                name="dc1-leaf-01",
                role="leaf",
            )
        assert "field required" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            SwitchCreate(
                name="dc1-leaf-01",
                serial_number="FDO12345678",
            )
        assert "field required" in str(exc_info.value)

    def test_invalid_serial_number(self):
        with pytest.raises(ValidationError) as exc_info:
            SwitchCreate(
                name="dc1-leaf-01",
                serial_number="INVALID_SERIAL",
                role="leaf",
            )
        assert "value is not a valid serial number" in str(exc_info.value)

    def test_invalid_role(self):
        with pytest.raises(ValidationError) as exc_info:
            SwitchCreate(
                name="dc1-leaf-01",
                serial_number="FDO12345678",
                role="invalid_role",
            )
        assert "unexpected value; permitted: 'leaf', 'spine'" in str(
            exc_info.value
        )