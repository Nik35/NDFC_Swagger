"""Global config service — 1:1 per fabric, upsert pattern."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.global_config import FabricGlobalDB
from app.exceptions import NotFoundError


class GlobalService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_fabric(self, fabric_id: UUID) -> FabricGlobalDB:
        result = await self.db.execute(
            select(FabricGlobalDB).where(FabricGlobalDB.fabric_id == fabric_id)
        )
        row = result.scalars().first()
        if not row:
            raise NotFoundError(f"Global config for fabric {fabric_id} not found")
        return row

    async def upsert(self, fabric_id: UUID, data: dict) -> FabricGlobalDB:
        result = await self.db.execute(
            select(FabricGlobalDB).where(FabricGlobalDB.fabric_id == fabric_id)
        )
        existing = result.scalars().first()
        if existing:
            for k, v in data.items():
                if k != "fabric_id":
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        row = FabricGlobalDB(fabric_id=fabric_id, **data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def delete(self, fabric_id: UUID) -> None:
        row = await self.get_by_fabric(fabric_id)
        await self.db.delete(row)
        await self.db.flush()
