"""Unit tests for interface Pydantic models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.models.interfaces.access import AccessInterfaceCreate
from app.models.interfaces.trunk import TrunkInterfaceCreate
from app.models.interfaces.loopback import LoopbackInterfaceCreate


class TestAccessInterface:
    def test_valid(self):
        intf = AccessInterfaceCreate(
            name="Ethernet1/1",
            mode="access",
            access_vlan=100,
        )
        assert intf.access_vlan == 100

    def test_vlan_range(self):
        with pytest.raises(ValidationError):
            AccessInterfaceCreate(
                name="Ethernet1/1", mode="access", access_vlan=0
            )
        with pytest.raises(ValidationError):
            AccessInterfaceCreate(
                name="Ethernet1/1", mode="access", access_vlan=4095
            )


class TestTrunkInterface:
    def test_valid(self):
        intf = TrunkInterfaceCreate(
            name="Ethernet1/2",
            mode="trunk",
        )
        assert intf.mode == "trunk"


class TestLoopbackInterface:
    def test_valid(self):
        intf = LoopbackInterfaceCreate(
            name="Loopback0",
            mode="loopback",
            vrf="default",
            ipv4_address="10.0.0.1/32",
        )
        assert intf.ipv4_address == "10.0.0.1/32"