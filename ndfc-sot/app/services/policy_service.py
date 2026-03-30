"""Policy + Policy Group CRUD service layer (E.22/E.23)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.policy import PolicyDB, PolicyGroupDB
from app.exceptions import ConflictError, NotFoundError


class PolicyService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[PolicyDB]:
        result = await self.db.execute(
            select(PolicyDB).where(PolicyDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, policy_id: UUID) -> PolicyDB:
        row = await self.db.get(PolicyDB, policy_id)
        if not row:
            raise NotFoundError(f"Policy {policy_id} not found")
        return row

    async def get_by_natural_key(
        self, fabric_id: UUID, switch_name: str, template_name: str
    ) -> PolicyDB | None:
        result = await self.db.execute(
            select(PolicyDB).where(
                PolicyDB.fabric_id == fabric_id,
                PolicyDB.switch_name == switch_name,
                PolicyDB.template_name == template_name,
            )
        )
        return result.scalars().first()

    async def create(self, data: dict) -> PolicyDB:
        existing = await self.get_by_natural_key(
            data["fabric_id"], data["switch_name"], data["template_name"]
        )
        if existing:
            raise ConflictError(
                f"Policy '{data['template_name']}' for switch '{data['switch_name']}' already exists"
            )
        row = PolicyDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[PolicyDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> PolicyDB:
        existing = await self.get_by_natural_key(
            data["fabric_id"], data["switch_name"], data["template_name"]
        )
        if existing:
            for k, v in data.items():
                if k not in ("id", "fabric_id", "created_at", "updated_at"):
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(data)

    async def delete(self, policy_id: UUID) -> None:
        row = await self.get_by_id(policy_id)
        await self.db.delete(row)
        await self.db.flush()


class PolicyGroupService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[PolicyGroupDB]:
        result = await self.db.execute(
            select(PolicyGroupDB).where(PolicyGroupDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, group_id: UUID) -> PolicyGroupDB:
        row = await self.db.get(PolicyGroupDB, group_id)
        if not row:
            raise NotFoundError(f"Policy group {group_id} not found")
        return row

    async def get_by_name(self, fabric_id: UUID, name: str) -> PolicyGroupDB | None:
        result = await self.db.execute(
            select(PolicyGroupDB).where(
                PolicyGroupDB.fabric_id == fabric_id,
                PolicyGroupDB.name == name,
            )
        )
        return result.scalars().first()

    async def create(self, data: dict) -> PolicyGroupDB:
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            raise ConflictError(
                f"Policy group '{data['name']}' already exists in fabric {data['fabric_id']}"
            )
        row = PolicyGroupDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[PolicyGroupDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> PolicyGroupDB:
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            for k, v in data.items():
                if k not in ("id", "fabric_id", "name", "created_at", "updated_at"):
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(data)

    async def delete(self, group_id: UUID) -> None:
        row = await self.get_by_id(group_id)
        await self.db.delete(row)
        await self.db.flush()
