"""vPC Peer CRUD service layer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.vpc_peer import VpcPeerDB
from app.exceptions import ConflictError, NotFoundError


class VpcPeerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[VpcPeerDB]:
        result = await self.db.execute(
            select(VpcPeerDB).where(VpcPeerDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, peer_id: UUID) -> VpcPeerDB:
        row = await self.db.get(VpcPeerDB, peer_id)
        if not row:
            raise NotFoundError(f"vPC peer {peer_id} not found")
        return row

    async def get_by_peers(
        self, fabric_id: UUID, peer1: str, peer2: str
    ) -> VpcPeerDB | None:
        result = await self.db.execute(
            select(VpcPeerDB).where(
                VpcPeerDB.fabric_id == fabric_id,
                VpcPeerDB.peer1 == peer1,
                VpcPeerDB.peer2 == peer2,
            )
        )
        return result.scalars().first()

    async def create(self, data: dict) -> VpcPeerDB:
        existing = await self.get_by_peers(
            data["fabric_id"], data["peer1"], data["peer2"]
        )
        if existing:
            raise ConflictError(
                f"vPC peer {data['peer1']}/{data['peer2']} already exists"
            )
        row = VpcPeerDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[VpcPeerDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> VpcPeerDB:
        existing = await self.get_by_peers(
            data["fabric_id"], data["peer1"], data["peer2"]
        )
        if existing:
            for k, v in data.items():
                if k != "fabric_id":
                    setattr(existing, k, v)
            await self.db.flush()
            await self.db.refresh(existing)
            return existing
        return await self.create(data)

    async def delete(self, peer_id: UUID) -> None:
        row = await self.get_by_id(peer_id)
        await self.db.delete(row)
        await self.db.flush()
