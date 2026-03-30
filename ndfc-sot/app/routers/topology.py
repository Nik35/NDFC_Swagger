"""Topology CRUD endpoints — Fabric Links, Edge Connections, ToR Peers."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.topology import (
    FabricLinkCreate, FabricLinkRead, FabricLinkUpdate,
    EdgeConnectionCreate, EdgeConnectionRead, EdgeConnectionUpdate,
    ToRPeerCreate, ToRPeerRead, ToRPeerUpdate
)
from app.services.topology_service import (
    FabricLinkService,
    EdgeConnectionService,
    TorPeerService,
)

router = APIRouter(
    prefix="/topology",
    tags=["Topology: Links"],
    dependencies=[Depends(verify_api_key)],
)


# ── Fabric Links ──────────────────────────────────────────────────

@router.get(
    "/fabric-links/fabric/{fabric_id}",
    response_model=list[FabricLinkRead],
    summary="List fabric links"
)
async def list_fabric_links(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await FabricLinkService(db).list_by_fabric(fabric_id)


@router.get(
    "/fabric-links/{link_id}",
    response_model=FabricLinkRead,
    summary="Get a fabric link by ID"
)
async def get_fabric_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    return await FabricLinkService(db).get_by_id(link_id)


@router.post(
    "/fabric-links",
    response_model=FabricLinkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a fabric link",
)
async def create_fabric_link(payload: FabricLinkCreate, db: AsyncSession = Depends(get_db)):
    row = await FabricLinkService(db).create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/fabric-links/bulk",
    response_model=list[FabricLinkRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple fabric links",
)
async def create_fabric_links_bulk(
    payloads: list[FabricLinkCreate], db: AsyncSession = Depends(get_db)
):
    rows = await FabricLinkService(db).create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/fabric-links/{link_id}",
    response_model=FabricLinkRead,
    summary="Update a fabric link",
)
async def update_fabric_link(
    link_id: UUID, payload: FabricLinkUpdate, db: AsyncSession = Depends(get_db)
):
    row = await FabricLinkService(db).update(link_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/fabric-links/{link_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a fabric link",
)
async def delete_fabric_link(link_id: UUID, db: AsyncSession = Depends(get_db)):
    await FabricLinkService(db).delete(link_id)
    await db.commit()


# ── Edge Connections ──────────────────────────────────────────────

@router.get(
    "/edge-connections/fabric/{fabric_id}",
    response_model=list[EdgeConnectionRead],
    summary="List edge connections"
)
async def list_edge_connections(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await EdgeConnectionService(db).list_by_fabric(fabric_id)


@router.get(
    "/edge-connections/{conn_id}",
    response_model=EdgeConnectionRead,
    summary="Get an edge connection by ID"
)
async def get_edge_connection(conn_id: UUID, db: AsyncSession = Depends(get_db)):
    return await EdgeConnectionService(db).get_by_id(conn_id)


@router.post(
    "/edge-connections",
    response_model=EdgeConnectionRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an edge connection",
)
async def create_edge_connection(payload: EdgeConnectionCreate, db: AsyncSession = Depends(get_db)):
    row = await EdgeConnectionService(db).create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/edge-connections/bulk",
    response_model=list[EdgeConnectionRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple edge connections",
)
async def create_edge_connections_bulk(
    payloads: list[EdgeConnectionCreate], db: AsyncSession = Depends(get_db)
):
    rows = await EdgeConnectionService(db).create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/edge-connections/{conn_id}",
    response_model=EdgeConnectionRead,
    summary="Update an edge connection",
)
async def update_edge_connection(
    conn_id: UUID, payload: EdgeConnectionUpdate, db: AsyncSession = Depends(get_db)
):
    row = await EdgeConnectionService(db).update(conn_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/edge-connections/{conn_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an edge connection",
)
async def delete_edge_connection(conn_id: UUID, db: AsyncSession = Depends(get_db)):
    await EdgeConnectionService(db).delete(conn_id)
    await db.commit()


# ── ToR Peers ─────────────────────────────────────────────────────

@router.get(
    "/tor-peers/fabric/{fabric_id}",
    response_model=list[ToRPeerRead],
    summary="List ToR peers"
)
async def list_tor_peers(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await TorPeerService(db).list_by_fabric(fabric_id)


@router.get(
    "/tor-peers/{peer_id}",
    response_model=ToRPeerRead,
    summary="Get a ToR peer by ID"
)
async def get_tor_peer(peer_id: UUID, db: AsyncSession = Depends(get_db)):
    return await TorPeerService(db).get_by_id(peer_id)


@router.post(
    "/tor-peers",
    response_model=ToRPeerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a ToR peer",
)
async def create_tor_peer(payload: ToRPeerCreate, db: AsyncSession = Depends(get_db)):
    row = await TorPeerService(db).create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/tor-peers/bulk",
    response_model=list[ToRPeerRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple ToR peers",
)
async def create_tor_peers_bulk(
    payloads: list[ToRPeerCreate], db: AsyncSession = Depends(get_db)
):
    rows = await TorPeerService(db).create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/tor-peers/{peer_id}",
    response_model=ToRPeerRead,
    summary="Update a ToR peer",
)
async def update_tor_peer(
    peer_id: UUID, payload: ToRPeerUpdate, db: AsyncSession = Depends(get_db)
):
    row = await TorPeerService(db).update(peer_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/tor-peers/{peer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a ToR peer",
)
async def delete_tor_peer(peer_id: UUID, db: AsyncSession = Depends(get_db)):
    await TorPeerService(db).delete(peer_id)
    await db.commit()
