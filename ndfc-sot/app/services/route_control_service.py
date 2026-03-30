"""Route Control CRUD service layer — all entries stored as JSONB arrays.

Covers: ipv4/ipv6 prefix lists, standard/extended community lists,
AS-path access lists, route maps, IP ACLs, MAC lists, object groups,
time ranges.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.route_control import (
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
from app.exceptions import ConflictError, NotFoundError


class _NamedEntityService:
    """Base for fabric_id + name keyed route-control entities with JSONB entries."""

    model = None  # Set in subclasses
    entity_name = "Entity"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list:
        result = await self.db.execute(
            select(self.model).where(self.model.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, entity_id: UUID):
        row = await self.db.get(self.model, entity_id)
        if not row:
            raise NotFoundError(f"{self.entity_name} {entity_id} not found")
        return row

    async def get_by_name(self, fabric_id: UUID, name: str):
        result = await self.db.execute(
            select(self.model).where(
                self.model.fabric_id == fabric_id, self.model.name == name
            )
        )
        return result.scalars().first()

    async def create(self, data: dict):
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            raise ConflictError(
                f"{self.entity_name} '{data['name']}' already exists in fabric {data['fabric_id']}"
            )
        row = self.model(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list:
        return [await self.create(d) for d in items]

    async def update(self, entity_id: UUID, data: dict):
        row = await self.get_by_id(entity_id)
        for k, v in data.items():
            if k not in ("id", "fabric_id", "name", "created_at", "updated_at"):
                setattr(row, k, v)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def upsert(self, data: dict):
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            return await self.update(existing.id, data)
        return await self.create(data)

    async def delete(self, entity_id: UUID) -> None:
        row = await self.get_by_id(entity_id)
        await self.db.delete(row)
        await self.db.flush()


class Ipv4PrefixListService(_NamedEntityService):
    model = Ipv4PrefixListDB
    entity_name = "IPv4 Prefix List"


class Ipv6PrefixListService(_NamedEntityService):
    model = Ipv6PrefixListDB
    entity_name = "IPv6 Prefix List"


class StandardCommunityListService(_NamedEntityService):
    model = StandardCommunityListDB
    entity_name = "Standard Community List"


class ExtendedCommunityListService(_NamedEntityService):
    model = ExtendedCommunityListDB
    entity_name = "Extended Community List"


class IpAsPathAccessListService(_NamedEntityService):
    model = IpAsPathAccessListDB
    entity_name = "AS-Path Access List"


class RouteMapService(_NamedEntityService):
    model = RouteMapDB
    entity_name = "Route Map"


class IpAclService(_NamedEntityService):
    model = IpAclDB
    entity_name = "IP ACL"


class MacListService(_NamedEntityService):
    model = MacListDB
    entity_name = "MAC List"


class ObjectGroupService(_NamedEntityService):
    model = ObjectGroupDB
    entity_name = "Object Group"


class TimeRangeService(_NamedEntityService):
    model = TimeRangeDB
    entity_name = "Time Range"
