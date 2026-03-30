"""Interface CRUD service layer.

Single interfaces table with ``type`` discriminator + JSONB ``type_config``.
"""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.interface import InterfaceDB
from app.exceptions import ConflictError, NotFoundError


class InterfaceService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_switch(self, switch_id: UUID) -> list[InterfaceDB]:
        result = await self.db.execute(
            select(InterfaceDB).where(InterfaceDB.switch_id == switch_id)
        )
        return list(result.scalars().all())

    async def list_by_fabric(self, fabric_id: UUID) -> list[InterfaceDB]:
        from app.db_models.switch import SwitchDB

        stmt = (
            select(InterfaceDB)
            .join(SwitchDB, InterfaceDB.switch_id == SwitchDB.id)
            .where(SwitchDB.fabric_id == fabric_id)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, iface_id: UUID) -> InterfaceDB:
        row = await self.db.get(InterfaceDB, iface_id)
        if not row:
            raise NotFoundError(f"Interface {iface_id} not found")
        return row

    async def get_by_name(self, switch_id: UUID, name: str) -> InterfaceDB | None:
        result = await self.db.execute(
            select(InterfaceDB).where(
                InterfaceDB.switch_id == switch_id, InterfaceDB.name == name
            )
        )
        return result.scalars().first()

    async def create(self, data: dict) -> InterfaceDB:
        existing = await self.get_by_name(data["switch_id"], data["name"])
        if existing:
            raise ConflictError(
                f"Interface '{data['name']}' already exists on switch {data['switch_id']}"
            )
        
        # Mapping flattened data to DB model (with type_config)
        base_fields = {
            "switch_id", "name", "type", "description",
            "admin_state", "mtu", "speed", "freeform_config",
        }
        # Alias mode to type if present
        if "mode" in data and "type" not in data:
            data["type"] = data.pop("mode")
        # Alias enabled to admin_state if present
        if "enabled" in data and "admin_state" not in data:
            data["admin_state"] = data.pop("enabled")
            
        db_ready = {}
        type_config = {}
        for k, v in data.items():
            if k in base_fields:
                if k == "mtu" and isinstance(v, str):
                    try:
                        db_ready[k] = int(v)
                    except ValueError:
                        db_ready[k] = None # Or handle default
                else:
                    db_ready[k] = v
            else:
                type_config[k] = v
        
        if type_config:
            db_ready["type_config"] = type_config

        row = InterfaceDB(**db_ready)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[InterfaceDB]:
        results = []
        for d in items:
            results.append(await self.create(d))
        return results

    async def update(self, iface_id: UUID, data: dict) -> InterfaceDB:
        row = await self.get_by_id(iface_id)
        
        base_fields = {
            "description", "admin_state", "mtu", "speed", "freeform_config",
        }
        # Alias enabled to admin_state if present
        if "enabled" in data:
            data["admin_state"] = data.pop("enabled")

        current_type_config = row.type_config or {}
        
        for k, v in data.items():
            if k in base_fields:
                if k == "mtu" and isinstance(v, str):
                    try:
                        setattr(row, k, int(v))
                    except ValueError:
                        pass
                else:
                    setattr(row, k, v)
            elif k not in ("id", "switch_id", "name", "type", "created_at", "updated_at"):
                current_type_config[k] = v
        
        row.type_config = current_type_config
        
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def upsert(self, data: dict) -> InterfaceDB:
        existing = await self.get_by_name(data["switch_id"], data["name"])
        if existing:
            for field, value in data.items():
                if field not in ("id", "switch_id", "created_at", "updated_at"):
                    setattr(existing, field, value)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(data)

    async def delete(self, iface_id: UUID) -> None:
        row = await self.get_by_id(iface_id)
        await self.db.delete(row)
        await self.db.flush()
