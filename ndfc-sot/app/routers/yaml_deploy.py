"""YAML generation and Ansible deployment endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

import yaml

from app.auth import verify_api_key
from app.database import get_db
from app.services.yaml_builder import YamlBuilder
from app.validators.referential import validate_fabric_exists

router = APIRouter(
    prefix="/yaml",
    tags=["YAML & Deploy"],
    dependencies=[Depends(verify_api_key)],
)


@router.get(
    "/{fabric_id}",
    summary="Preview NAC-DC YAML for a fabric (JSON)",
)
async def preview_yaml(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await validate_fabric_exists(db, fabric_id)
    builder = YamlBuilder(db)
    return await builder.build_fabric_yaml(fabric_id)


@router.get(
    "/download/{fabric_id}",
    summary="Download NAC-DC YAML for a fabric",
    response_class=Response,
)
async def download_yaml(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await validate_fabric_exists(db, fabric_id)
    builder = YamlBuilder(db)
    data = await builder.build_fabric_yaml(fabric_id)
    content = yaml.dump(data, default_flow_style=False, sort_keys=False)
    return Response(
        content=content,
        media_type="application/x-yaml",
        headers={"Content-Disposition": f"attachment; filename=fabric_{fabric_id}.yml"},
    )


@router.post(
    "/generate/{fabric_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Generate and store NAC-DC YAML for a fabric",
)
async def generate_yaml(fabric_id: UUID, db: AsyncSession = Depends(get_db)):
    await validate_fabric_exists(db, fabric_id)
    builder = YamlBuilder(db)
    data = await builder.build_fabric_yaml(fabric_id)
    return {"fabric_id": str(fabric_id), "yaml": data}
