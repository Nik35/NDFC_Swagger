"""Interface CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.interfaces import InterfaceCreate, InterfaceRead, InterfaceUpdate
from app.services.interface_service import InterfaceService

router = APIRouter(
    prefix="/interfaces",
    tags=["Topology: Interfaces"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/switch/{switch_id}",
    response_model=list[InterfaceRead],
    summary="List interfaces on a switch",
)
async def list_interfaces(switch_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = InterfaceService(db)
    return await svc.list_by_switch(switch_id)


@router.get(
    "/fabric/{fabric_id}",
    response_model=list[InterfaceRead],
    summary="List all interfaces in a fabric",
)
async def list_interfaces_by_fabric(
    fabric_id: UUID, db: AsyncSession = Depends(get_db)
):
    svc = InterfaceService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{interface_id}",
    response_model=InterfaceRead,
    summary="Get an interface by ID",
)
async def get_interface(interface_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = InterfaceService(db)
    return await svc.get_by_id(interface_id)


@router.post(
    "",
    response_model=InterfaceRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create an interface",
)
async def create_interface(payload: InterfaceCreate, switch_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = InterfaceService(db)
    data = payload.model_dump()
    data["switch_id"] = switch_id
    row = await svc.create(data)
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[InterfaceRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple interfaces",
)
async def create_interfaces_bulk(
    payloads: list[InterfaceCreate], switch_id: UUID, db: AsyncSession = Depends(get_db)
):
    svc = InterfaceService(db)
    items = []
    for p in payloads:
        d = p.model_dump()
        d["switch_id"] = switch_id
        items.append(d)
    rows = await svc.create_bulk(items)
    await db.commit()
    return rows


@router.patch(
    "/{interface_id}",
    response_model=InterfaceRead,
    summary="Update an interface",
)
async def update_interface(
    interface_id: UUID, payload: InterfaceUpdate, db: AsyncSession = Depends(get_db)
):
    svc = InterfaceService(db)
    row = await svc.update(interface_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/{interface_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an interface",
)
async def delete_interface(interface_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = InterfaceService(db)
    await svc.delete(interface_id)
    await db.commit()
