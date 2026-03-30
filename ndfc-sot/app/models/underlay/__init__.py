"""Underlay Pydantic models."""

from app.models.underlay.general import UnderlayGeneralCreate, UnderlayGeneralRead, UnderlayGeneralUpdate
from app.models.underlay.ipv4 import UnderlayIpv4Create, UnderlayIpv4Read, UnderlayIpv4Update
from app.models.underlay.ipv6 import UnderlayIpv6Create, UnderlayIpv6Read, UnderlayIpv6Update
from app.models.underlay.isis import UnderlayIsisCreate, UnderlayIsisRead, UnderlayIsisUpdate
from app.models.underlay.ospf import UnderlayOspfCreate, UnderlayOspfRead, UnderlayOspfUpdate
from app.models.underlay.bgp import UnderlayBgpCreate, UnderlayBgpRead, UnderlayBgpUpdate
from app.models.underlay.bfd import UnderlayBfdCreate, UnderlayBfdRead, UnderlayBfdUpdate
from app.models.underlay.multicast import UnderlayMulticastCreate, UnderlayMulticastRead, UnderlayMulticastUpdate

__all__ = [
    "UnderlayGeneralCreate", "UnderlayGeneralRead", "UnderlayGeneralUpdate",
    "UnderlayIpv4Create", "UnderlayIpv4Read", "UnderlayIpv4Update",
    "UnderlayIpv6Create", "UnderlayIpv6Read", "UnderlayIpv6Update",
    "UnderlayIsisCreate", "UnderlayIsisRead", "UnderlayIsisUpdate",
    "UnderlayOspfCreate", "UnderlayOspfRead", "UnderlayOspfUpdate",
    "UnderlayBgpCreate", "UnderlayBgpRead", "UnderlayBgpUpdate",
    "UnderlayBfdCreate", "UnderlayBfdRead", "UnderlayBfdUpdate",
    "UnderlayMulticastCreate", "UnderlayMulticastRead", "UnderlayMulticastUpdate",
]
