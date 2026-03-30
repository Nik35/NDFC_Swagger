"""VRF Lite Extension + Multisite CRUD service layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.overlay_extensions import VrfLiteExtensionDB
from app.db_models.multisite import MultisiteDB
from app.exceptions import ConflictError, NotFoundError


class VrfLiteExtensionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[VrfLiteExtensionDB]:
        result = await self.db.execute(
            select(VrfLiteExtensionDB).where(
                VrfLiteExtensionDB.fabric_id == fabric_id
            )
        )
        return list(result.scalars().all())

    async def get_by_id(self, ext_id: UUID) -> VrfLiteExtensionDB:
        row = await self.db.get(VrfLiteExtensionDB, ext_id)
        if not row:
            raise NotFoundError(f"VRF Lite Extension {ext_id} not found")
        return row

    async def create(self, data: dict) -> VrfLiteExtensionDB:
        row = VrfLiteExtensionDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[VrfLiteExtensionDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> VrfLiteExtensionDB:
        result = await self.db.execute(
            select(VrfLiteExtensionDB).where(
                VrfLiteExtensionDB.fabric_id == data["fabric_id"],
                VrfLiteExtensionDB.vrf_name == data["vrf_name"],
                VrfLiteExtensionDB.switch_name == data["switch_name"],
                VrfLiteExtensionDB.interface == data["interface"],
            )
        )
        existing = result.scalars().first()
        if existing:
            for k, v in data.items():
                if k != "fabric_id":
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(data)

    async def delete(self, ext_id: UUID) -> None:
        row = await self.get_by_id(ext_id)
        await self.db.delete(row)
        await self.db.flush()


class MultisiteService:
    """1:1 per fabric upsert pattern."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_fabric(self, fabric_id: UUID) -> MultisiteDB:
        result = await self.db.execute(
            select(MultisiteDB).where(MultisiteDB.fabric_id == fabric_id)
        )
        row = result.scalars().first()
        if not row:
            raise NotFoundError(f"Multisite config for fabric {fabric_id} not found")
        return row

    async def upsert(self, fabric_id: UUID, data: dict) -> MultisiteDB:
        result = await self.db.execute(
            select(MultisiteDB).where(MultisiteDB.fabric_id == fabric_id)
        )
        existing = result.scalars().first()
        if existing:
            for k, v in data.items():
                if k != "fabric_id":
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        row = MultisiteDB(fabric_id=fabric_id, **data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def delete(self, fabric_id: UUID) -> None:
        row = await self.get_by_fabric(fabric_id)
        await self.db.delete(row)
        await self.db.flush()
