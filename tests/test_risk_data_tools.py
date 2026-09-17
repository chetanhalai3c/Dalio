from datetime import date
from decimal import Decimal

import pytest

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalAssetSeries,
    HistoricalFrequency,
    HistoricalPricePoint,
)
from tools.risk_data_tools import (
    align_historical_prices,
    build_aligned_return_series,
)


# =========================
# Test Helper
# Builds small historical proxy series.
# =========================

def make_series(
    asset_class,
    symbol,
    currency,
    frequency,
    observations,
):

    return HistoricalAssetSeries(
        asset_class=asset_class,
        symbol=symbol,
        proxy_name=f"{symbol} Proxy",
        currency=currency,
        frequency=frequency,
        source="Example Provider",
        observations=[
            HistoricalPricePoint(
                observation_date=observation_date,
                price=price,
            )
            for observation_date, price
            in observations
        ],
    )


# =========================
# Common Date Alignment
# Only observations shared by every series should survive.
# =========================

def test_align_historical_prices():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (
                date(2026, 1, 1),
                Decimal("100"),
            ),
            (
                date(2026, 1, 2),
                Decimal("105"),
            ),
            (
                date(2026, 1, 3),
                Decimal("110"),
            ),
            (
                date(2026, 1, 4),
                Decimal("121"),
            ),
        ],
    )

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "BOND",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (
                date(2026, 1, 1),
                Decimal("100"),
            ),
            (
                date(2026, 1, 3),
                Decimal("95"),
            ),
            (
                date(2026, 1, 4),
                Decimal("95"),
            ),
        ],
    )

    dates, prices = align_historical_prices(
        [
            equities,
            bonds,
        ]
    )

    assert dates == [
        date(2026, 1, 1),
        date(2026, 1, 3),
        date(2026, 1, 4),
    ]

    assert prices["equities"] == [
        Decimal("100"),
        Decimal("110"),
        Decimal("121"),
    ]

    assert prices["government_bonds"] == [
        Decimal("100"),
        Decimal("95"),
        Decimal("95"),
    ]


# =========================
# Aligned Returns
# Risk maths should receive returns calculated from shared dates only.
# =========================

def test_build_aligned_return_series():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (
                date(2026, 1, 1),
                Decimal("100"),
            ),
            (
                date(2026, 1, 2),
                Decimal("999"),
            ),
            (
                date(2026, 1, 3),
                Decimal("110"),
            ),
            (
                date(2026, 1, 4),
                Decimal("121"),
            ),
        ],
    )

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "BOND",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (
                date(2026, 1, 1),
                Decimal("100"),
            ),
            (
                date(2026, 1, 3),
                Decimal("95"),
            ),
            (
                date(2026, 1, 4),
                Decimal("95"),
            ),
        ],
    )

    result = build_aligned_return_series(
        [
            equities,
            bonds,
        ]
    )

    assert result["equities"] == [
        Decimal("0.1"),
        Decimal("0.1"),
    ]

    assert result["government_bonds"] == [
        Decimal("-0.05"),
        Decimal("0"),
    ]


# =========================
# Frequency Validation
# Daily and monthly observations must not be mixed directly.
# =========================

def test_mixed_frequencies_rejected():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    gold = make_series(
        AssetClass.GOLD,
        "GLD",
        "USD",
        HistoricalFrequency.MONTHLY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    with pytest.raises(
        ValueError
    ):
        align_historical_prices(
            [
                equities,
                gold,
            ]
        )


# =========================
# Currency Validation
# Return series must share a common currency before comparison.
# =========================

def test_mixed_currencies_rejected():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "BOND",
        "GBP",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    with pytest.raises(
        ValueError
    ):
        align_historical_prices(
            [
                equities,
                bonds,
            ]
        )


# =========================
# Duplicate Asset Classes
# One risk series should represent each economic exposure.
# =========================

def test_duplicate_asset_classes_rejected():

    first = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    second = make_series(
        AssetClass.EQUITIES,
        "QQQ",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    with pytest.raises(
        ValueError
    ):
        align_historical_prices(
            [
                first,
                second,
            ]
        )


# =========================
# Minimum Common History
# Sample statistics need at least two aligned returns.
# =========================

def test_three_common_dates_required():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 2), Decimal("101")),
            (date(2026, 1, 3), Decimal("102")),
        ],
    )

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "BOND",
        "USD",
        HistoricalFrequency.DAILY,
        [
            (date(2026, 1, 1), Decimal("100")),
            (date(2026, 1, 3), Decimal("102")),
            (date(2026, 1, 4), Decimal("103")),
        ],
    )

    with pytest.raises(
        ValueError
    ):
        align_historical_prices(
            [
                equities,
                bonds,
            ]
        )