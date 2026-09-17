from datetime import date
from decimal import Decimal

from models.risk_market_data import (
    HistoricalAssetSeries,
)
from tools.risk_metrics import (
    calculate_simple_returns,
)


# =========================
# Historical Price Alignment
# Keeps only dates shared by every asset series.
# =========================

def align_historical_prices(
    series_list: list[HistoricalAssetSeries],
) -> tuple[
    list[date],
    dict[str, list[Decimal]],
]:

    if not series_list:
        raise ValueError(
            "At least one historical asset series is required."
        )

    frequencies = {
        series.frequency
        for series in series_list
    }

    if len(frequencies) != 1:
        raise ValueError(
            "Historical series must use the same frequency."
        )

    currencies = {
        series.currency
        for series in series_list
    }

    if (
        None in currencies
        or len(currencies) != 1
    ):
        raise ValueError(
            "Historical series must use one explicit common currency."
        )

    asset_classes = [
        series.asset_class
        for series in series_list
    ]

    if len(asset_classes) != len(
        set(asset_classes)
    ):
        raise ValueError(
            "Historical series cannot contain duplicate asset classes."
        )

    common_dates = {
        observation.observation_date
        for observation
        in series_list[0].observations
    }

    for series in series_list[1:]:
        common_dates &= {
            observation.observation_date
            for observation
            in series.observations
        }

    aligned_dates = sorted(
        common_dates
    )

    if len(aligned_dates) < 3:
        raise ValueError(
            "At least three common dates are required "
            "for sample risk calculations."
        )

    aligned_prices = {}

    for series in series_list:

        prices_by_date = {
            observation.observation_date:
            observation.price
            for observation
            in series.observations
        }

        aligned_prices[
            series.asset_class.value
        ] = [
            prices_by_date[
                observation_date
            ]
            for observation_date
            in aligned_dates
        ]

    return (
        aligned_dates,
        aligned_prices,
    )


# =========================
# Aligned Return Series
# Converts synchronized prices into synchronized returns.
# =========================

def build_aligned_return_series(
    series_list: list[HistoricalAssetSeries],
) -> dict[str, list[Decimal]]:

    _, aligned_prices = (
        align_historical_prices(
            series_list
        )
    )

    return {
        asset_class:
        calculate_simple_returns(
            prices
        )
        for asset_class, prices
        in aligned_prices.items()
    }