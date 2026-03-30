"""Shared interface base fields and MTU validator."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InterfaceBase(BaseModel):
    """Fields shared across all interface modes."""

    description: Optional[str] = Field(default=None, max_length=256, description="Interface description.")
    enabled: Optional[bool] = Field(default=True, description="Admin state (no shutdown).")
    freeform_config: Optional[str] = Field(default=None, description="Raw NX-OS CLI to append.")


SPEED_CHOICES = ["auto", "100mb", "1gb", "10gb", "25gb", "40gb", "100gb"]


def validate_mtu(v: str | None) -> str | None:
    """MTU must be 1500-9216, 'default', or 'jumbo'."""
    if v is None:
        return v
    if v.lower() in ("default", "jumbo"):
        return v.lower()
    try:
        n = int(v)
    except ValueError:
        raise ValueError("MTU must be an integer 1500-9216, 'default', or 'jumbo'")
    if not (1500 <= n <= 9216):
        raise ValueError("MTU must be between 1500 and 9216")
    return str(n)