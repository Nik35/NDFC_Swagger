"""Underlay service — 8 singleton sub-sections, each 1:1 per fabric.

All follow the same upsert-by-fabric_id pattern.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.underlay import (
    UnderlayGeneralDB,
    UnderlayIpv4DB,
    UnderlayIpv6DB,
    UnderlayIsisDB,
    UnderlayOspfDB,
    UnderlayBgpDB,
    UnderlayBfdDB,
    UnderlayMulticastDB,
)
from app.exceptions import NotFoundError


class _SingletonService:
    """Base for 1:1-per-fabric underlay services."""

    model = None  # Set in subclasses

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_fabric(self, fabric_id: UUID):
        result = await self.db.execute(
            select(self.model).where(self.model.fabric_id == fabric_id)
        )
        row = result.scalars().first()
        if not row:
            raise NotFoundError(
                f"{self.model.__tablename__} not found for fabric {fabric_id}"
            )
        return row

    async def upsert(self, fabric_id: UUID, data: dict):
        result = await self.db.execute(
            select(self.model).where(self.model.fabric_id == fabric_id)
        )
        existing = result.scalars().first()
        if existing:
            for k, v in data.items():
                if k != "fabric_id":
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        row = self.model(fabric_id=fabric_id, **data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def delete(self, fabric_id: UUID) -> None:
        row = await self.get_by_fabric(fabric_id)
        await self.db.delete(row)
        await self.db.flush()


class UnderlayGeneralService(_SingletonService):
    model = UnderlayGeneralDB


class UnderlayIpv4Service(_SingletonService):
    model = UnderlayIpv4DB


class UnderlayIpv6Service(_SingletonService):
    model = UnderlayIpv6DB


class UnderlayIsisService(_SingletonService):
    model = UnderlayIsisDB


class UnderlayOspfService(_SingletonService):
    model = UnderlayOspfDB


class UnderlayBgpService(_SingletonService):
    model = UnderlayBgpDB


class UnderlayBfdService(_SingletonService):
    model = UnderlayBfdDB


class UnderlayMulticastService(_SingletonService):
    model = UnderlayMulticastDB
