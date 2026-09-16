from datetime import date, datetime
# date = date represented by the whole market snapshot.
# datetime = exact time an individual observation was retrieved.

from decimal import Decimal
# Precise numeric representation for prices, yields, rates, etc.

from enum import Enum
# Restricts fields to predefined allowed values.

from pydantic import BaseModel, ConfigDict, Field
# BaseModel = validation foundation.
# ConfigDict = controls validation behaviour.
# Field = lets us configure model fields such as safe default lists.


# =========================
# Strict Base Model
# Shared validation rule: reject unexpected data.
# =========================

class StrictBaseModel(BaseModel):
    # Reject unexpected fields so bad provider data cannot
    # silently enter the Market Agent's trusted state.

    model_config = ConfigDict(
        extra="forbid"  # Only explicitly defined fields are accepted.
    )


# =========================
# Asset Classes
# Standard vocabulary for the major asset groups.
# =========================

class AssetClass(str, Enum):
    EQUITIES = "equities"                    # Stocks / equity markets.
    GOVERNMENT_BONDS = "government_bonds"  # Sovereign government debt.
    GOLD = "gold"                            # Gold exposure.
    COMMODITIES = "commodities"             # Broad or individual commodities.
    CASH = "cash"                            # Cash / cash-equivalent exposure.
    CRYPTO = "crypto"                        # Cryptocurrency exposure.


# =========================
# Measurement Types
# Defines what the observed numeric value represents.
# =========================

class MeasurementType(str, Enum):
    PRICE = "price"  # Market price.
    INDEX = "index"  # Index level.
    YIELD = "yield"  # Bond or similar yield.
    RATE = "rate"    # Interest/rate-style measurement.


# =========================
# Market Direction
# Standard vocabulary for movement between observations.
# =========================

class MarketDirection(str, Enum):
    RISING = "rising"    # Latest value is higher.
    FALLING = "falling"  # Latest value is lower.
    STABLE = "stable"    # Value is unchanged.
    UNKNOWN = "unknown"  # Direction cannot yet be determined.


# =========================
# Market Observation
# Defines ONE standardised market data point.
# =========================

class MarketObservation(StrictBaseModel):
    asset_name: str                         # Instrument or benchmark being observed.

    asset_class: AssetClass                 # Major asset category it belongs to.

    symbol: str | None = None               # Provider ticker/identifier, if available.

    geography: str | None = None            # Country or market context, if relevant.

    measurement_type: MeasurementType       # Tells us whether value is price/index/yield/rate.

    latest_value: Decimal                   # Most recent observed value.
    previous_value: Decimal | None = None   # Previous value for comparison, if available.

    unit: str                               # USD, percent, index_points, etc.

    currency: str | None = None             # Currency denomination, where relevant.

    latest_period: str                      # Period/date belonging to latest_value.
    previous_period: str | None = None      # Period/date belonging to previous_value.

    direction: MarketDirection = MarketDirection.UNKNOWN
    # Trend defaults to UNKNOWN until the data layer calculates it.

    source: str                             # Provider/source of the observation.
    source_url: str | None = None           # Original evidence URL, if available.
    retrieved_at: datetime | None = None     # Exact time the observation was retrieved.


# =========================
# Market Snapshot
# Groups many MarketObservations into one market evidence package.
# =========================

class MarketSnapshot(StrictBaseModel):
    as_of_date: date                        # Date represented by this market snapshot.

    investor_country: str | None = None     # Investor location/context, if known.
    base_currency: str | None = None        # Investor's main comparison currency.

    observations: list[MarketObservation] = Field(
        default_factory=list
    )
    # Flexible collection of market observations.
    # default_factory=list gives each MarketSnapshot its own empty list.