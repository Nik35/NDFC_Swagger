"""Switch CRUD service layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.switch import SwitchDB
from app.exceptions import ConflictError, NotFoundError
from app.models.inventory import SwitchCreate, SwitchUpdate


class SwitchService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[SwitchDB]:
        result = await self.db.execute(
            select(SwitchDB).where(SwitchDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, switch_id: UUID) -> SwitchDB:
        row = await self.db.get(SwitchDB, switch_id)
        if not row:
            raise NotFoundError(f"Switch {switch_id} not found")
        return row

    async def get_by_name(self, fabric_id: UUID, name: str) -> SwitchDB | None:
        result = await self.db.execute(
            select(SwitchDB).where(
                SwitchDB.fabric_id == fabric_id, SwitchDB.name == name
            )
        )
        return result.scalars().first()

    async def create(self, payload: SwitchCreate) -> SwitchDB:
        existing = await self.get_by_name(payload.fabric_id, payload.name)
        if existing:
            raise ConflictError(
                f"Switch '{payload.name}' already exists in fabric {payload.fabric_id}"
            )
        row = SwitchDB(**payload.model_dump())
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, payloads: list[SwitchCreate]) -> list[SwitchDB]:
        results = []
        for p in payloads:
            results.append(await self.create(p))
        return results

    async def update(self, switch_id: UUID, payload: SwitchUpdate) -> SwitchDB:
        row = await self.get_by_id(switch_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(row, field, value)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def upsert(self, payload: SwitchCreate) -> SwitchDB:
        existing = await self.get_by_name(payload.fabric_id, payload.name)
        if existing:
            for field, value in payload.model_dump().items():
                if field != "fabric_id":
                    setattr(existing, field, value)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(payload)

    async def delete(self, switch_id: UUID) -> None:
        row = await self.get_by_id(switch_id)
        await self.db.delete(row)
        await self.db.flush()
