"""Policy + Policy Group CRUD endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import verify_api_key
from app.database import get_db
from app.models.policy.policy import (
    PolicyCreate, PolicyRead, PolicyUpdate,
    PolicyGroupCreate, PolicyGroupRead, PolicyGroupUpdate
)
from app.services.policy_service import PolicyService, PolicyGroupService

router = APIRouter(
    prefix="/policies",
    tags=["Policy"],
    dependencies=[Depends(verify_api_key)],
)


# ── Policies ────────────────────────────────────────────────────

@router.get(
    "/fabric/{fabric_id}",
    response_model=list[PolicyRead],
    summary="List policies in a fabric",
)
async def list_policies(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/{policy_id}",
    response_model=PolicyRead,
    summary="Get a policy by ID",
)
async def get_policy(policy_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyService(db)
    return await svc.get_by_id(policy_id)


@router.post(
    "",
    response_model=PolicyRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a policy",
)
async def create_policy(payload: PolicyCreate, db: AsyncSession = Depends(get_db)):
    svc = PolicyService(db)
    row = await svc.create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/bulk",
    response_model=list[PolicyRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple policies",
)
async def create_policies_bulk(
    payloads: list[PolicyCreate], db: AsyncSession = Depends(get_db)
):
    svc = PolicyService(db)
    rows = await svc.create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/{policy_id}",
    response_model=PolicyRead,
    summary="Update a policy",
)
async def update_policy(
    policy_id: UUID, payload: PolicyUpdate, db: AsyncSession = Depends(get_db)
):
    svc = PolicyService(db)
    row = await svc.update(policy_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/{policy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a policy",
)
async def delete_policy(policy_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyService(db)
    await svc.delete(policy_id)
    await db.commit()


# ── Policy Groups ──────────────────────────────────────────────

@router.get(
    "/groups/fabric/{fabric_id}",
    response_model=list[PolicyGroupRead],
    summary="List policy groups in a fabric",
)
async def list_policy_groups(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyGroupService(db)
    return await svc.list_by_fabric(fabric_id)


@router.get(
    "/groups/{group_id}",
    response_model=PolicyGroupRead,
    summary="Get a policy group by ID",
)
async def get_policy_group(group_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyGroupService(db)
    return await svc.get_by_id(group_id)


@router.post(
    "/groups",
    response_model=PolicyGroupRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a policy group",
)
async def create_policy_group(payload: PolicyGroupCreate, db: AsyncSession = Depends(get_db)):
    svc = PolicyGroupService(db)
    row = await svc.create(payload.model_dump())
    await db.commit()
    return row


@router.post(
    "/groups/bulk",
    response_model=list[PolicyGroupRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create multiple policy groups",
)
async def create_policy_groups_bulk(
    payloads: list[PolicyGroupCreate], db: AsyncSession = Depends(get_db)
):
    svc = PolicyGroupService(db)
    rows = await svc.create_bulk([p.model_dump() for p in payloads])
    await db.commit()
    return rows


@router.patch(
    "/groups/{group_id}",
    response_model=PolicyGroupRead,
    summary="Update a policy group",
)
async def update_policy_group(
    group_id: UUID, payload: PolicyGroupUpdate, db: AsyncSession = Depends(get_db)
):
    svc = PolicyGroupService(db)
    row = await svc.update(group_id, payload.model_dump(exclude_unset=True))
    await db.commit()
    return row


@router.delete(
    "/groups/{group_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a policy group",
)
async def delete_policy_group(group_id: UUID, db: AsyncSession = Depends(get_db)):
    svc = PolicyGroupService(db)
    await svc.delete(group_id)
    await db.commit()
