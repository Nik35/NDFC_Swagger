"""Fabric CRUD service layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.fabric import FabricDB
from app.exceptions import ConflictError, NotFoundError
from app.models.fabric import FabricCreate, FabricUpdate


class FabricService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_all(self) -> list[FabricDB]:
        result = await self.db.execute(select(FabricDB))
        return list(result.scalars().all())

    async def get_by_id(self, fabric_id: UUID) -> FabricDB:
        fabric = await self.db.get(FabricDB, fabric_id)
        if not fabric:
            raise NotFoundError(f"Fabric {fabric_id} not found")
        return fabric

    async def get_by_name(self, name: str) -> FabricDB | None:
        result = await self.db.execute(
            select(FabricDB).where(FabricDB.name == name)
        )
        return result.scalars().first()

    async def create(self, payload: FabricCreate) -> FabricDB:
        existing = await self.get_by_name(payload.name)
        if existing:
            raise ConflictError(f"Fabric '{payload.name}' already exists")
        fabric = FabricDB(**payload.model_dump())
        self.db.add(fabric)
        await self.db.flush()
        await self.db.refresh(fabric)
        return fabric

    async def create_bulk(self, payloads: list[FabricCreate]) -> list[FabricDB]:
        results = []
        for p in payloads:
            results.append(await self.create(p))
        return results

    async def update(self, fabric_id: UUID, payload: FabricUpdate) -> FabricDB:
        fabric = await self.get_by_id(fabric_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(fabric, field, value)
        await self.db.flush()
        await self.db.refresh(fabric)
        return fabric

    async def upsert(self, payload: FabricCreate) -> FabricDB:
        existing = await self.get_by_name(payload.name)
        if existing:
            for field, value in payload.model_dump().items():
                setattr(existing, field, value)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(payload)

    async def delete(self, fabric_id: UUID) -> None:
        fabric = await self.get_by_id(fabric_id)
        await self.db.delete(fabric)
        await self.db.flush()
