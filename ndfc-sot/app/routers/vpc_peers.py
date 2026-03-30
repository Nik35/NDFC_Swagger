"""vPC Peer CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.topology import VpcPeerCreate, VpcPeerRead, VpcPeerUpdate
from app.services.vpc_peer_service import VpcPeerService

router = APIRouter(
    prefix="/vpc-peers",
    tags=["Topology: vPC Peers"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/fabric/{fabric_id}",
    response_model=list[VpcPeerRead],
    summary="List vPC peers in a fabric",
)
async def list_vpc_peers(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VpcPeerService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{peer_id}",
    response_model=VpcPeerRead,
    summary="Get a vPC peer by ID",
)
async def get_vpc_peer(peer_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VpcPeerService(db)
    return await svc.get_by_id(peer_id)


@router.post(
    "",
    response_model=VpcPeerRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a vPC peer pair",
)
async def create_vpc_peer(payload: VpcPeerCreate, db: AsyncSession = Depends(get_db)):
    svc = VpcPeerService(db)
    row = await svc.create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[VpcPeerRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple vPC peer pairs",
)
async def create_vpc_peers_bulk(
    payloads: list[VpcPeerCreate], db: AsyncSession = Depends(get_db)
):
    svc = VpcPeerService(db)
    rows = await svc.create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/{peer_id}",
    response_model=VpcPeerRead,
    summary="Update a vPC peer pair",
)
async def update_vpc_peer(
    peer_id: UUID, payload: VpcPeerUpdate, db: AsyncSession = Depends(get_db)
):
    svc = VpcPeerService(db)
    row = await svc.update(peer_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/{peer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vPC peer pair",
)
async def delete_vpc_peer(peer_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VpcPeerService(db)
    await svc.delete(peer_id)
    await db.commit()
