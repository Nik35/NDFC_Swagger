"""Overlay Pydantic models."""

from app.models.overlay.vrf import (
    VrfCreate, VrfUpdate, VrfRead,
    VrfSwitchAttachCreate, VrfSwitchAttachRead,
)
from app.models.overlay.network import (
    NetworkCreate, NetworkUpdate, NetworkRead,
    NetworkSwitchAttachCreate, NetworkSwitchAttachRead,
)
from app.models.overlay.vrf_lite_extension import (
    VrfLiteExtensionCreate, VrfLiteExtensionUpdate, VrfLiteExtensionRead,
)

__all__ = [
    "VrfCreate", "VrfUpdate", "VrfRead",
    "VrfSwitchAttachCreate", "VrfSwitchAttachRead",
    "NetworkCreate", "NetworkUpdate", "NetworkRead",
    "NetworkSwitchAttachCreate", "NetworkSwitchAttachRead",
    "VrfLiteExtensionCreate", "VrfLiteExtensionUpdate", "VrfLiteExtensionRead",
]
