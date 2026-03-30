"""VRF CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.overlay.vrf import VrfCreate, VrfRead, VrfUpdate
from app.services.vrf_service import VrfService

router = APIRouter(
    prefix="/vrfs",
    tags=["Overlay: VRFs"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/fabric/{fabric_id}",
    response_model=list[VrfRead],
    summary="List VRFs in a fabric",
)
async def list_vrfs(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VrfService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{vrf_id}",
    response_model=VrfRead,
    summary="Get a VRF by ID",
)
async def get_vrf(vrf_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VrfService(db)
    return await svc.get_by_id(vrf_id)


@router.post(
    "",
    response_model=VrfRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a VRF",
)
async def create_vrf(payload: VrfCreate, db: AsyncSession = Depends(get_db)):
    svc = VrfService(db)
    row = await svc.create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[VrfRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple VRFs",
)
async def create_vrfs_bulk(
    payloads: list[VrfCreate], db: AsyncSession = Depends(get_db)
):
    svc = VrfService(db)
    rows = await svc.create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/{vrf_id}",
    response_model=VrfRead,
    summary="Update a VRF",
)
async def update_vrf(
    vrf_id: UUID, payload: VrfUpdate, db: AsyncSession = Depends(get_db)
):
    svc = VrfService(db)
    row = await svc.update(vrf_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/{vrf_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a VRF",
)
async def delete_vrf(vrf_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = VrfService(db)
    await svc.delete(vrf_id)
    await db.commit()
