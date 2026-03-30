"""Deploy and YAML preview Pydantic models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr


class DeployRequest(BaseModel):
    """Request body to trigger a deployment."""

    dry_run: bool = Field(
        default=True, description="If true, run Ansible in --check mode."
    )
    tags: Optional[list[str]] = Field(
        default=None, description="Ansible --tags filter."
    )
    limit: Optional[str] = Field(
        default=None, description="Ansible --limit filter."
    )
    auth_username: Optional[str] = Field(
        default=None, description="NDFC username."
    )
    auth_password: Optional[SecretStr] = Field(
        default=None, description="NDFC password."
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"dry_run": True, "tags": ["networks", "vrfs"]}
            ]
        }
    }


class DeployResponse(BaseModel):
    """Response after queuing a deployment."""

    job_id: str = Field(description="Celery task ID.")
    status: Literal[
        "queued", "running", "success", "failed", "dry_run"
    ] = Field(description="Current job status.")
    message: str = Field(description="Human-readable status message.")
    yaml_preview: Optional[str] = Field(
        default=None, description="Generated YAML content."
    )
    warnings: Optional[list[str]] = Field(
        default=None, description="YAML generation warnings."
    )
    errors: Optional[list[str]] = Field(
        default=None, description="YAML generation errors."
    )


class DeployStatusResponse(BaseModel):
    """Status of a queued deployment job."""

    job_id: str = Field(description="Celery task ID.")
    status: Literal[
        "queued", "running", "success", "failed"
    ] = Field(description="Job status.")
    message: str = Field(description="Status message.")
    started_at: Optional[datetime] = Field(
        default=None, description="Job start time."
    )
    completed_at: Optional[datetime] = Field(
        default=None, description="Job completion time."
    )
    ansible_output: Optional[str] = Field(
        default=None, description="Ansible stdout."
    )


class YamlPreviewResponse(BaseModel):
    """Response for YAML preview endpoint."""

    fabric_name: str = Field(description="Fabric name.")
    yaml_content: str = Field(description="Raw YAML string.")
    json_content: dict = Field(description="Same data as Python dict.")
    warnings: list[str] = Field(
        default_factory=list, description="Missing optional data warnings."
    )
    errors: list[str] = Field(
        default_factory=list, description="Missing required data errors."
    )
    is_valid: bool = Field(description="True if no errors.")