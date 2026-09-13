from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


# =========================
# Strict Base Model
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


# =========================
# Trend Direction
# =========================

class TrendDirection(str, Enum):
    RISING = "rising"
    FALLING = "falling"
    STABLE = "stable"
    UNKNOWN = "unknown"


# =========================
# Macro Observation
# =========================

class MacroObservation(StrictBaseModel):
    indicator: str

    latest_value: Decimal
    previous_value: Decimal | None = None

    unit: str

    latest_period: str
    previous_period: str | None = None

    direction: TrendDirection = (
        TrendDirection.UNKNOWN
    )

    source: str
    source_url: str | None = None

    retrieved_at: datetime | None = None


# =========================
# Macro Snapshot
# =========================

class MacroSnapshot(StrictBaseModel):
    geography: str
    geography_code: str | None = None

    as_of_date: date

    growth: MacroObservation | None = None
    inflation: MacroObservation | None = None
    policy_rate: MacroObservation | None = None