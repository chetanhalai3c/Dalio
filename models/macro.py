from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict


# =========================
# Strict Base Model
# Shared validation rule: reject unexpected fields.
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"  # Reject fields we did not explicitly define.
    )


# =========================
# Trend Direction
# Standard vocabulary for how an indicator is moving.
# =========================

class TrendDirection(str, Enum):
    RISING = "rising"    # Indicator is increasing.
    FALLING = "falling"  # Indicator is decreasing.
    STABLE = "stable"    # Indicator is broadly unchanged.
    UNKNOWN = "unknown"  # Direction has not been determined.


# =========================
# Macro Observation
# One economic indicator plus its comparison and source.
# =========================

class MacroObservation(StrictBaseModel):
    indicator: str                              # Name of the economic indicator.

    latest_value: Decimal                       # Most recent observed value.
    previous_value: Decimal | None = None       # Previous value, if available.

    unit: str                                   # %, index, GBP, etc.

    latest_period: str                          # Period the latest value belongs to.
    previous_period: str | None = None          # Period for the previous value.

    direction: TrendDirection = (
        TrendDirection.UNKNOWN
    )                                           # Standardised trend direction.

    source: str                                 # Organisation/source providing the data.
    source_url: str | None = None               # Link to the original source, if available.

    retrieved_at: datetime | None = None         # Exact time this data was retrieved.


# =========================
# Macro Snapshot
# Groups key macro indicators for one geography and date.
# =========================

class MacroSnapshot(StrictBaseModel):
    geography: str                              # Country or region being analysed.
    geography_code: str | None = None           # Optional standardised geography code.

    as_of_date: date                            # Date this macro picture represents.

    growth: MacroObservation | None = None       # Economic-growth observation, if available.
    inflation: MacroObservation | None = None    # Inflation observation, if available.
    policy_rate: MacroObservation | None = None  # Central-bank interest-rate observation, if available.