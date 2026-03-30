"""Policy, Policy Group, and Policy Group Assignment Pydantic models (E.22/E.23)."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.common import TimestampMixin


# ── Policy (E.22) ───────────────────────────────────────────────

class PolicyCreate(BaseModel):
    """Create a freeform policy attached to a switch."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    switch_name: str = Field(
        ...,
        max_length=128,
        description="Switch hostname where policy is applied.",
        examples=["LEAF-1"]
    )
    template_name: str = Field(
        ...,
        max_length=128,
        description="NDFC template name (e.g., switch_freeform).",
        examples=["switch_freeform"]
    )
    priority: Optional[int] = Field(
        default=500,
        ge=1,
        le=1000,
        description="Policy priority (lower numbers executed first).",
        examples=[500]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=256,
        description="User-defined policy description.",
        examples=["NTP configuration for LEAF-1"]
    )
    config: Optional[str] = Field(
        default=None,
        description="Freeform NX-OS CLI configuration block.",
        examples=["ntp server 10.1.1.1\nntp server 10.1.1.2"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "switch_name": "LEAF-1",
                    "template_name": "switch_freeform",
                    "priority": 500,
                    "config": "ntp server 10.1.1.1\nntp server 10.1.1.2",
                }
            ]
        }
    }


class PolicyUpdate(BaseModel):
    """Update a policy. switch_name cannot change."""

    template_name: Optional[str] = Field(
        default=None,
        max_length=128,
        description="Updated NDFC template name.",
        examples=["switch_freeform_v2"]
    )
    priority: Optional[int] = Field(
        default=None,
        ge=1,
        le=1000,
        description="Updated policy priority.",
        examples=[400]
    )
    description: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Updated policy description.",
        examples=["Updated NTP configuration"]
    )
    config: Optional[str] = Field(
        default=None,
        description="Updated freeform NX-OS CLI configuration.",
        examples=["ntp server 10.1.1.3"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "priority": 400,
                    "config": "ntp server 10.1.1.3"
                }
            ]
        }
    }


class PolicyRead(TimestampMixin):
    """Response body for a policy."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    switch_name: str = Field(
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    template_name: str = Field(
        description="NDFC template name.",
        examples=["switch_freeform"]
    )
    priority: Optional[int] = Field(
        default=None,
        description="Policy priority.",
        examples=[500]
    )
    description: Optional[str] = Field(
        default=None,
        description="Policy description.",
        examples=["NTP configuration"]
    )
    config: Optional[str] = Field(
        default=None,
        description="Freeform NX-OS CLI config.",
        examples=["ntp server 10.1.1.1"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


# ── Policy Group (E.23) ─────────────────────────────────────────

class PolicyGroupPolicyEntry(BaseModel):
    """A policy reference within a group."""

    template_name: str = Field(
        ...,
        max_length=128,
        description="NDFC template name.",
        examples=["switch_freeform"]
    )
    priority: Optional[int] = Field(
        default=500,
        ge=1,
        le=1000,
        description="Priority within this group.",
        examples=[500]
    )
    config: Optional[str] = Field(
        default=None,
        description="Freeform NX-OS CLI configuration.",
        examples=["feature interface-vlan"]
    )

    model_config = {"extra": "forbid"}


class PolicyGroupCreate(BaseModel):
    """Create a policy group."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    name: str = Field(
        ...,
        max_length=64,
        description="Unique policy group name.",
        examples=["GRP_LEAF_COMMON"]
    )
    policies: list[PolicyGroupPolicyEntry] = Field(
        ...,
        min_length=1,
        description="List of policies included in this group.",
    )
    switches: list[str] = Field(
        ...,
        min_length=1,
        description="List of switch hostnames where this group is applied.",
        examples=[["LEAF-1", "LEAF-2"]]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "name": "GRP_LEAF_COMMON",
                    "policies": [
                        {
                            "template_name": "switch_freeform",
                            "priority": 500,
                            "config": "ntp server 10.1.1.1",
                        }
                    ],
                    "switches": ["LEAF-1", "LEAF-2"],
                }
            ]
        }
    }


class PolicyGroupUpdate(BaseModel):
    """Update a policy group."""

    policies: Optional[list[PolicyGroupPolicyEntry]] = Field(
        default=None,
        min_length=1,
        description="Updated list of policies in the group."
    )
    switches: Optional[list[str]] = Field(
        default=None,
        min_length=1,
        description="Updated list of switch hostnames.",
        examples=[["LEAF-3", "LEAF-4"]]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "switches": ["LEAF-1", "LEAF-2", "LEAF-3"]
                }
            ]
        }
    }


class PolicyGroupRead(TimestampMixin):
    """Response body for a policy group."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    name: str = Field(
        description="Policy group name.",
        examples=["GRP_LEAF_COMMON"]
    )
    policies: list[PolicyGroupPolicyEntry] = Field(
        default=[],
        description="List of policies.",
    )
    switches: list[str] = Field(
        default=[],
        description="List of switch hostnames.",
        examples=[["LEAF-1", "LEAF-2"]]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }


# ── Policy Group Assignment (E.23) ──────────────────────────────

class PolicyGroupAssignmentCreate(BaseModel):
    """Assign a policy group to a switch (switch_name is string, NOT UUID FK)."""

    fabric_id: UUID = Field(
        ...,
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    switch_name: str = Field(
        ...,
        max_length=128,
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    group_name: str = Field(
        ...,
        max_length=64,
        description="Policy group name to assign.",
        examples=["GRP_LEAF_COMMON"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "00000000-0000-0000-0000-000000000001",
                    "switch_name": "LEAF-1",
                    "group_name": "GRP_LEAF_COMMON",
                }
            ]
        }
    }


class PolicyGroupAssignmentUpdate(BaseModel):
    """Update a policy group assignment."""

    group_name: Optional[str] = Field(
        default=None,
        max_length=64,
        description="New policy group name.",
        examples=["GRP_LEAF_NEW"]
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "group_name": "GRP_LEAF_NEW"
                }
            ]
        }
    }


class PolicyGroupAssignmentRead(TimestampMixin):
    """Response body for a policy group assignment."""

    fabric_id: UUID = Field(
        description="Parent fabric UUID.",
        examples=["00000000-0000-0000-0000-000000000001"]
    )
    switch_name: str = Field(
        description="Switch hostname.",
        examples=["LEAF-1"]
    )
    group_name: str = Field(
        description="Policy group name.",
        examples=["GRP_LEAF_COMMON"]
    )

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }
