from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from models.market import AssetClass


# =========================
# Strict Base Model
# Rejects unexpected fields in historical risk data.
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


# =========================
# Historical Frequency
# Makes observation frequency explicit before series are compared.
# =========================

class HistoricalFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# =========================
# Historical Price Point
# Represents ONE dated price observation for a market proxy.
# =========================

class HistoricalPricePoint(StrictBaseModel):
    observation_date: date # Date associated with this observation.

    price: Decimal = Field(
        gt=Decimal("0")
    ) # Positive historical proxy price.


# =========================
# Historical Asset Series
# Represents ONE asset-class proxy across time.
# =========================

class HistoricalAssetSeries(StrictBaseModel):
    asset_class: AssetClass # Economic exposure represented by the proxy.

    symbol: str # Provider/instrument symbol.

    proxy_name: str # Human-readable explanation of the chosen proxy.

    currency: str | None = None # Currency of the underlying price series.

    frequency: HistoricalFrequency # Daily, weekly or monthly observations.

    source: str # Provider supplying the data.

    observations: list[HistoricalPricePoint] = Field(
        min_length=2
    ) # Historical observations ordered from oldest to newest.

    @model_validator(mode="after")
    def validate_observations(
        self,
    ) -> "HistoricalAssetSeries":

        dates = [
            observation.observation_date
            for observation in self.observations
        ]

        if len(
            dates
        ) != len(
            set(dates)
        ):
            raise ValueError(
                "Historical series cannot contain duplicate dates."
            )

        if dates != sorted(
            dates
        ):
            raise ValueError(
                "Historical observations must be ordered "
                "from oldest to newest."
            )

        return self