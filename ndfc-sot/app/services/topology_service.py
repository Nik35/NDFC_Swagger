"""Topology services — FabricLink, EdgeConnection, TorPeer."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db_models.topology import FabricLinkDB, EdgeConnectionDB, TorPeerDB
from app.exceptions import ConflictError, NotFoundError


class FabricLinkService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[FabricLinkDB]:
        result = await self.db.execute(
            select(FabricLinkDB).where(FabricLinkDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, link_id: UUID) -> FabricLinkDB:
        row = await self.db.get(FabricLinkDB, link_id)
        if not row:
            raise NotFoundError(f"Fabric link {link_id} not found")
        return row

    async def create(self, data: dict) -> FabricLinkDB:
        row = FabricLinkDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[FabricLinkDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> FabricLinkDB:
        result = await self.db.execute(
            select(FabricLinkDB).where(
                FabricLinkDB.fabric_id == data["fabric_id"],
                FabricLinkDB.source_switch == data["source_switch"],
                FabricLinkDB.source_interface == data["source_interface"],
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

    async def delete(self, link_id: UUID) -> None:
        row = await self.get_by_id(link_id)
        await self.db.delete(row)
        await self.db.flush()


class EdgeConnectionService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[EdgeConnectionDB]:
        result = await self.db.execute(
            select(EdgeConnectionDB).where(EdgeConnectionDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, conn_id: UUID) -> EdgeConnectionDB:
        row = await self.db.get(EdgeConnectionDB, conn_id)
        if not row:
            raise NotFoundError(f"Edge connection {conn_id} not found")
        return row

    async def create(self, data: dict) -> EdgeConnectionDB:
        row = EdgeConnectionDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[EdgeConnectionDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> EdgeConnectionDB:
        result = await self.db.execute(
            select(EdgeConnectionDB).where(
                EdgeConnectionDB.fabric_id == data["fabric_id"],
                EdgeConnectionDB.switch_name == data["switch_name"],
                EdgeConnectionDB.interface == data["interface"],
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

    async def delete(self, conn_id: UUID) -> None:
        row = await self.get_by_id(conn_id)
        await self.db.delete(row)
        await self.db.flush()


class TorPeerService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_by_fabric(self, fabric_id: UUID) -> list[TorPeerDB]:
        result = await self.db.execute(
            select(TorPeerDB).where(TorPeerDB.fabric_id == fabric_id)
        )
        return list(result.scalars().all())

    async def get_by_id(self, peer_id: UUID) -> TorPeerDB:
        row = await self.db.get(TorPeerDB, peer_id)
        if not row:
            raise NotFoundError(f"ToR peer {peer_id} not found")
        return row

    async def create(self, data: dict) -> TorPeerDB:
        row = TorPeerDB(**data)
        self.db.add(row)
        await self.db.flush()
        await self.db.refresh(row)
        return row

    async def create_bulk(self, items: list[dict]) -> list[TorPeerDB]:
        return [await self.create(d) for d in items]

    async def upsert(self, data: dict) -> TorPeerDB:
        result = await self.db.execute(
            select(TorPeerDB).where(
                TorPeerDB.fabric_id == data["fabric_id"],
                TorPeerDB.switch_name == data["switch_name"],
                TorPeerDB.peer_switch == data["peer_switch"],
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

    async def delete(self, peer_id: UUID) -> None:
        row = await self.get_by_id(peer_id)
        await self.db.delete(row)
        await self.db.flush()
