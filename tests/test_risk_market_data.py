from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalAssetSeries,
    HistoricalFrequency,
    HistoricalPricePoint,
)


# =========================
# Historical Price Point
# Valid positive historical price should be accepted.
# =========================

def test_historical_price_point():

    point = HistoricalPricePoint(
        observation_date=date(
            2026,
            1,
            1,
        ),
        price=Decimal("100"),
    )

    assert point.price == Decimal("100")


# =========================
# Historical Asset Series
# Ordered proxy history should form a valid series.
# =========================

def test_historical_asset_series():

    series = HistoricalAssetSeries(
        asset_class=AssetClass.EQUITIES,
        symbol="SPY",
        proxy_name="SPDR S&P 500 ETF Trust",
        currency="USD",
        frequency=HistoricalFrequency.DAILY,
        source="Example Provider",
        observations=[
            HistoricalPricePoint(
                observation_date=date(
                    2026,
                    1,
                    1,
                ),
                price=Decimal("100"),
            ),
            HistoricalPricePoint(
                observation_date=date(
                    2026,
                    1,
                    2,
                ),
                price=Decimal("101"),
            ),
        ],
    )

    assert series.asset_class == AssetClass.EQUITIES
    assert series.symbol == "SPY"

    assert len(
        series.observations
    ) == 2


# =========================
# Invalid Price
# Historical prices must be positive.
# =========================

def test_zero_historical_price_rejected():

    with pytest.raises(
        ValidationError
    ):
        HistoricalPricePoint(
            observation_date=date(
                2026,
                1,
                1,
            ),
            price=Decimal("0"),
        )


# =========================
# Minimum History
# A usable series requires at least two observations.
# =========================

def test_historical_series_requires_two_observations():

    with pytest.raises(
        ValidationError
    ):
        HistoricalAssetSeries(
            asset_class=AssetClass.EQUITIES,
            symbol="SPY",
            proxy_name="SPDR S&P 500 ETF Trust",
            currency="USD",
            frequency=HistoricalFrequency.DAILY,
            source="Example Provider",
            observations=[
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        1,
                    ),
                    price=Decimal("100"),
                ),
            ],
        )


# =========================
# Duplicate Dates
# One series cannot contain multiple prices for the same date.
# =========================

def test_duplicate_historical_dates_rejected():

    with pytest.raises(
        ValidationError
    ):
        HistoricalAssetSeries(
            asset_class=AssetClass.GOLD,
            symbol="GLD",
            proxy_name="Gold Proxy",
            currency="USD",
            frequency=HistoricalFrequency.DAILY,
            source="Example Provider",
            observations=[
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        1,
                    ),
                    price=Decimal("100"),
                ),
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        1,
                    ),
                    price=Decimal("101"),
                ),
            ],
        )


# =========================
# Chronological Order
# Risk calculations require consistently ordered observations.
# =========================

def test_historical_dates_must_be_ordered():

    with pytest.raises(
        ValidationError
    ):
        HistoricalAssetSeries(
            asset_class=AssetClass.EQUITIES,
            symbol="SPY",
            proxy_name="SPDR S&P 500 ETF Trust",
            currency="USD",
            frequency=HistoricalFrequency.DAILY,
            source="Example Provider",
            observations=[
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        2,
                    ),
                    price=Decimal("101"),
                ),
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        1,
                    ),
                    price=Decimal("100"),
                ),
            ],
        )


# =========================
# Strict Contract
# Unexpected fields should not silently enter the risk pipeline.
# =========================

def test_unknown_historical_field_rejected():

    with pytest.raises(
        ValidationError
    ):
        HistoricalPricePoint(
            observation_date=date(
                2026,
                1,
                1,
            ),
            price=Decimal("100"),
            invented_return=Decimal("0.5"),
        )