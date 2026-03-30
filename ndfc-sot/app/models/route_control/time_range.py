"""Time Range Pydantic models."""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from app.models.common import TimestampMixin

MONTHS = Literal[
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
DAYS = Literal[
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
    "Saturday", "Sunday", "daily", "weekdays", "weekend",
]


class PeriodicSchedule(BaseModel):
    day: list[DAYS] = Field(
        ..., min_length=1, description="Day(s) of the week for the periodic schedule.", 
        examples=[["Monday", "Wednesday", "Friday"], ["weekdays"]]
    )
    start_hours: int = Field(
        ..., ge=0, le=23, description="Start hour (0-23).", examples=[9]
    )
    start_minutes: int = Field(
        ..., ge=0, le=59, description="Start minute (0-59).", examples=[0]
    )
    end_hours: int = Field(
        ..., ge=0, le=23, description="End hour (0-23).", examples=[17]
    )
    end_minutes: int = Field(
        ..., ge=0, le=59, description="End minute (0-59).", examples=[0]
    )

    model_config = {"extra": "forbid"}


class AbsoluteSchedule(BaseModel):
    start_day: Optional[int] = Field(
        default=None, ge=1, le=31, description="Start day of the month.", examples=[1]
    )
    start_month: Optional[MONTHS] = Field(
        default=None, description="Start month.", examples=["January"]
    )
    start_year: Optional[int] = Field(
        default=None, ge=2000, le=2099, description="Start year.", examples=[2024]
    )
    start_hours: Optional[int] = Field(
        default=None, ge=0, le=23, description="Start hour.", examples=[0]
    )
    start_minutes: Optional[int] = Field(
        default=None, ge=0, le=59, description="Start minute.", examples=[0]
    )
    end_day: Optional[int] = Field(
        default=None, ge=1, le=31, description="End day of the month.", examples=[31]
    )
    end_month: Optional[MONTHS] = Field(
        default=None, description="End month.", examples=["December"]
    )
    end_year: Optional[int] = Field(
        default=None, ge=2000, le=2099, description="End year.", examples=[2024]
    )
    end_hours: Optional[int] = Field(
        default=None, ge=0, le=23, description="End hour.", examples=[23]
    )
    end_minutes: Optional[int] = Field(
        default=None, ge=0, le=59, description="End minute.", examples=[59]
    )

    model_config = {"extra": "forbid"}


class TimeRangeEntry(BaseModel):
    seq_number: int = Field(
        ..., ge=1, description="Sequence number for this entry.", examples=[10, 20]
    )
    remark: Optional[str] = Field(
        default=None, description="Optional remark for this entry.", examples=["Business hours only"]
    )
    periodic: Optional[PeriodicSchedule] = Field(
        default=None, description="Periodic schedule definition."
    )
    absolute: Optional[AbsoluteSchedule] = Field(
        default=None, description="Absolute schedule definition."
    )

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def _exactly_one(self) -> "TimeRangeEntry":
        present = sum(1 for x in [self.remark, self.periodic, self.absolute] if x is not None)
        if present != 1:
            raise ValueError("Exactly one of remark, periodic, or absolute must be provided")
        return self


class TimeRangeCreate(BaseModel):
    fabric_id: UUID = Field(
        ..., description="UUID of the parent fabric.", examples=["123e4567-e89b-12d3-a456-426614174000"]
    )
    name: str = Field(
        ..., max_length=63, pattern=r"^[A-Za-z][A-Za-z0-9_-]{0,62}$", 
        description="Unique name for the time range.", examples=["BUSINESS-HOURS"]
    )
    entries: list[TimeRangeEntry] = Field(
        ..., min_length=1, description="List of entries defining the time range rules."
    )

    model_config = {
        "extra": "forbid",
        "json_schema_extra": {
            "examples": [
                {
                    "fabric_id": "123e4567-e89b-12d3-a456-426614174000",
                    "name": "BUSINESS-HOURS",
                    "entries": [
                        {
                            "seq_number": 10,
                            "periodic": {
                                "day": ["weekdays"], 
                                "start_hours": 8, 
                                "start_minutes": 0, 
                                "end_hours": 18, 
                                "end_minutes": 0
                            },
                        }
                    ],
                }
            ]
        }
    }


class TimeRangeUpdate(BaseModel):
    entries: Optional[list[TimeRangeEntry]] = Field(
        default=None, min_length=1, description="Updated list of time range entries."
    )

    model_config = {"extra": "forbid"}


class TimeRangeRead(TimestampMixin):
    fabric_id: UUID = Field(description="UUID of the parent fabric.")
    name: str = Field(description="Name of the time range.")
    entries: list[TimeRangeEntry] = Field(default=[], description="List of time range entries.")

    model_config = {
        "from_attributes": True,
        "extra": "forbid"
    }