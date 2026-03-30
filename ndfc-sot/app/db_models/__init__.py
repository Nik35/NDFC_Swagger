"""Import all DB models so Alembic can discover them."""

from app.db_models.base import Base, UUIDTimestampMixin  # noqa: F401

from app.db_models.fabric import FabricDB  # noqa: F401
from app.db_models.global_config import FabricGlobalDB  # noqa: F401
from app.db_models.multisite import MultisiteDB  # noqa: F401
from app.db_models.switch import SwitchDB  # noqa: F401
from app.db_models.interface import InterfaceDB  # noqa: F401
from app.db_models.topology import (  # noqa: F401
    FabricLinkDB,
    EdgeConnectionDB,
    TorPeerDB,
)
from app.db_models.vpc_peer import VpcPeerDB  # noqa: F401
from app.db_models.underlay import (  # noqa: F401
    UnderlayGeneralDB,
    UnderlayIpv4DB,
    UnderlayIpv6DB,
    UnderlayIsisDB,
    UnderlayOspfDB,
    UnderlayBgpDB,
    UnderlayBfdDB,
    UnderlayMulticastDB,
)
from app.db_models.vrf import VrfDB, VrfSwitchAttachmentDB  # noqa: F401
from app.db_models.network import NetworkDB, NetworkSwitchAttachmentDB  # noqa: F401
from app.db_models.overlay_extensions import VrfLiteExtensionDB  # noqa: F401
from app.db_models.route_control import (  # noqa: F401
    Ipv4PrefixListDB,
    Ipv6PrefixListDB,
    StandardCommunityListDB,
    ExtendedCommunityListDB,
    IpAsPathAccessListDB,
    RouteMapDB,
    IpAclDB,
    MacListDB,
    ObjectGroupDB,
    TimeRangeDB,
)
from app.db_models.policy import PolicyDB, PolicyGroupDB  # noqa: F401
