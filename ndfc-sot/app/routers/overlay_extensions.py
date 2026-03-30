"""Overlay extension endpoints — VRF Lite + Multisite."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.services.overlay_extension_service import (
    VrfLiteExtensionService,
    MultisiteService,
)

router = APIRouter(
    prefix="/overlay-extensions",
    tags=["Overlay Extensions"],
    dependencies=[Depends(verify_api_key)],
)


# ── VRF Lite Extensions ──────────────────────────────────────────

@router.get("/vrf-lite/fabric/{fabric_id}", summary="List VRF Lite extensions")
async def list_vrf_lite(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await VrfLiteExtensionService(db).list_by_fabric(fabric_id)


@router.get("/vrf-lite/{ext_id}", summary="Get a VRF Lite extension by ID")
async def get_vrf_lite(ext_id: UUID, db: AsyncSession = Depends(get_db)):
    return await VrfLiteExtensionService(db).get_by_id(ext_id)


@router.post(
    "/vrf-lite",
    status_code=status.HTTP_201_CREATED,
    summary="Create a VRF Lite extension",
)
async def create_vrf_lite(payload: dict, db: AsyncSession = Depends(get_db)):
    row = await VrfLiteExtensionService(db).create(payload)
    await db.commit()
    return row


@router.post(
    "/vrf-lite/bulk",
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple VRF Lite extensions",
)
async def create_vrf_lite_bulk(
    payloads: list[dict], db: AsyncSession = Depends(get_db)
):
    rows = await VrfLiteExtensionService(db).create_bulk(payloads)
    await db.commit()
    return rows


@router.delete(
    "/vrf-lite/{ext_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a VRF Lite extension",
)
async def delete_vrf_lite(ext_id: UUID, db: AsyncSession = Depends(get_db)):
    await VrfLiteExtensionService(db).delete(ext_id)
    await db.commit()


# ── Multisite ─────────────────────────────────────────────────────

@router.get("/multisite/fabric/{fabric_id}", summary="Get multisite config")
async def get_multisite(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    return await MultisiteService(db).get_by_fabric(fabric_id)


@router.put("/multisite/fabric/{fabric_id}", summary="Upsert multisite config")
async def upsert_multisite(
    fabric_id: UUID, payload: dict, db: AsyncSession = Depends(get_db)
):
    row = await MultisiteService(db).upsert(fabric_id, payload)
    await db.commit()
    return row


@router.delete(
    "/multisite/fabric/{fabric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete multisite config",
)
async def delete_multisite(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await MultisiteService(db).delete(fabric_id)
    await db.commit()
