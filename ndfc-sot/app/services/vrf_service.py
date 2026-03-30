"""VRF + VRF Switch Attachment CRUD service layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.vrf import VrfDB, VrfSwitchAttachmentDB
from app.exceptions import ConflictError, NotFoundError


class VrfService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[VrfDB]:
        result = await self.db.execute(
            select(VrfDB).where(VrfDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, vrf_id: UUID) -> VrfDB:
        row = await self.db.get(VrfDB, vrf_id)
        if not row:
            raise NotFoundError(f"VRF {vrf_id} not found")
        return row

    async def get_by_name(self, fabric_id: UUID, name: str) -> VrfDB | None:
        result = await self.db.execute(
            select(VrfDB).where(
                VrfDB.fabric_id == fabric_id, VrfDB.name == name
            )
        )
        return result.scalars().first()

    async def create(self, data: dict) -> VrfDB:
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            raise ConflictError(
                f"VRF '{data['name']}' already exists in fabric {data['fabric_id']}"
            )
        switches = data.pop("switches", None)
        row = VrfDB(**data)
        self.db.add(row)
        await self.db.flush()
        if switches:
            await self._sync_attachments(row.id, row.fabric_id, switches)
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[VrfDB]:
        return [await self.create(d) for d in items]

    async def update(self, vrf_id: UUID, data: dict) -> VrfDB:
        row = await self.get_by_id(vrf_id)
        switches = data.pop("switches", None)
        for k, v in data.items():
            if k not in ("id", "fabric_id", "created_at", "updated_at"):
                setattr(row, k, v)
        if switches is not None:
            await self._sync_attachments(vrf_id, row.fabric_id, switches)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def upsert(self, data: dict) -> VrfDB:
        existing = await self.get_by_name(data["fabric_id"], data["name"])
        if existing:
            return await self.update(existing.id, data)
        return await self.create(data)

    async def delete(self, vrf_id: UUID) -> None:
        row = await self.get_by_id(vrf_id)
        await self.db.delete(row)
        await self.db.flush()

    # ── switch attachments ────────────────────────────────────

    async def list_attachments(self, vrf_id: UUID) -> list[VrfSwitchAttachmentDB]:
        result = await self.db.execute(
            select(VrfSwitchAttachmentDB).where(
                VrfSwitchAttachmentDB.vrf_id == vrf_id
            )
        )
        return list(result.scalars().all())

    async def _sync_attachments(
        self, vrf_id: UUID, fabric_id: UUID, switches: list[dict]
    ) -> None:
        """Replace all switch attachments for a VRF."""
        from app.validators.referential import validate_switches_exist
        
        # Validate that all provided switch hostnames exist in the fabric
        hostnames = [sw["hostname"] for sw in switches if "hostname" in sw]
        if hostnames:
            await validate_switches_exist(self.db, fabric_id, hostnames)

        # Delete existing
        existing = await self.list_attachments(vrf_id)
        for a in existing:
            await self.db.delete(a)
        await self.db.flush()
        # Create new
        for sw in switches:
            att = VrfSwitchAttachmentDB(vrf_id=vrf_id, **sw)
            self.db.add(att)
        await self.db.flush()
