"""Network CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.overlay.network import NetworkCreate, NetworkRead, NetworkUpdate
from app.services.network_service import NetworkService

router = APIRouter(
    prefix="/networks",
    tags=["Overlay: Networks"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/fabric/{fabric_id}",
    response_model=list[NetworkRead],
    summary="List networks in a fabric",
)
async def list_networks(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NetworkService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{network_id}",
    response_model=NetworkRead,
    summary="Get a network by ID",
)
async def get_network(network_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NetworkService(db)
    return await svc.get_by_id(network_id)


@router.post(
    "",
    response_model=NetworkRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a network",
)
async def create_network(payload: NetworkCreate, db: AsyncSession = Depends(get_db)):
    svc = NetworkService(db)
    row = await svc.create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[NetworkRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple networks",
)
async def create_networks_bulk(
    payloads: list[NetworkCreate], db: AsyncSession = Depends(get_db)
):
    svc = NetworkService(db)
    rows = await svc.create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/{network_id}",
    response_model=NetworkRead,
    summary="Update a network",
)
async def update_network(
    network_id: UUID, payload: NetworkUpdate, db: AsyncSession = Depends(get_db)
):
    svc = NetworkService(db)
    row = await svc.update(network_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/{network_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a network",
)
async def delete_network(network_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = NetworkService(db)
    await svc.delete(network_id)
    await db.commit()
