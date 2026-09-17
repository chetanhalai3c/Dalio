from datetime import date # Creates fixed historical dates for our test data.
from decimal import Decimal # Keeps financial calculations precise.
import pytest # Lets us prove invalid risk inputs are deliberately rejected.

from models.market import AssetClass # Uses the same asset classes as the real system.
from models.risk_market_data import (
    HistoricalAssetSeries, # Validated historical series for one asset-class proxy.
    HistoricalFrequency, # Makes the observation frequency explicit.
    HistoricalPricePoint, # One dated historical price.
)
from tools.portfolio_risk_builder import (
    build_portfolio_risk_snapshot, # The deterministic builder we are testing.
)


# =========================
# Test Helper
# Creates a small weekly historical proxy series for one asset class.
# =========================

def make_series(
    asset_class,
    symbol,
    prices,
):

    dates = [
        date(2026, 1, 2),
        date(2026, 1, 9),
        date(2026, 1, 16),
        date(2026, 1, 23),
    ] # Four aligned weekly dates give us three return observations.

    return HistoricalAssetSeries(
        asset_class=asset_class, # Economic exposure represented by this proxy.
        symbol=symbol, # Proxy ticker used in the risk analysis.
        proxy_name=f"{symbol} Proxy", # Human-readable proxy description.
        currency="USD", # All series must use the same currency.
        frequency=HistoricalFrequency.WEEKLY, # All series must use the same frequency.
        source="Example Provider", # Test-only data source.
        observations=[
            HistoricalPricePoint(
                observation_date=observation_date,
                price=price,
            )
            for observation_date, price
            in zip(
                dates,
                prices,
            )
        ], # Converts our four prices into validated dated observations.
    )


# =========================
# Complete Portfolio Risk Snapshot
# Proves the separate deterministic risk pieces can be assembled into one object.
# =========================

def test_build_portfolio_risk_snapshot():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        [
            Decimal("100"),
            Decimal("120"),
            Decimal("120"),
            Decimal("96"),
        ],
    ) # Produces equity returns of +20%, 0%, -20%.

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "IEF",
        [
            Decimal("100"),
            Decimal("110"),
            Decimal("110"),
            Decimal("99"),
        ],
    ) # Produces bond returns of +10%, 0%, -10%.

    snapshot = build_portfolio_risk_snapshot(
        capital_weights={
            AssetClass.EQUITIES: Decimal("0.5"),
            AssetClass.GOVERNMENT_BONDS: Decimal("0.5"),
        }, # Test portfolio is 50% equities and 50% government bonds.
        series_list=[
            equities,
            bonds,
        ], # Historical evidence corresponding to those two exposures.
    )

    assert snapshot.currency == "USD" # Confirms common measurement currency survived the pipeline.

    assert snapshot.frequency == (
        HistoricalFrequency.WEEKLY
    ) # Confirms the common historical frequency survived the pipeline.

    assert (
        snapshot.aligned_return_observation_count
        == 3
    ) # Four aligned prices correctly become three aligned returns.

    assert (
        snapshot.portfolio_period_volatility
        == Decimal("0.15")
    ) # Confirms the risk maths was actually run and packaged.

    assert len(
        snapshot.asset_metrics
    ) == 2 # One deterministic risk record for each asset class.

    assert len(
        snapshot.pairwise_relationships
    ) == 1 # Two assets produce exactly one unique pair.

# =========================
# Risk Contribution
# Proves capital weight and actual risk contribution are separate concepts.
# =========================

def test_snapshot_contains_risk_contributions():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        [
            Decimal("100"),
            Decimal("120"),
            Decimal("120"),
            Decimal("96"),
        ],
    ) # Equity returns are +20%, 0%, -20%.

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "IEF",
        [
            Decimal("100"),
            Decimal("110"),
            Decimal("110"),
            Decimal("99"),
        ],
    ) # Bond returns are +10%, 0%, -10%.

    snapshot = build_portfolio_risk_snapshot(
        capital_weights={
            AssetClass.EQUITIES: Decimal("0.5"),
            AssetClass.GOVERNMENT_BONDS: Decimal("0.5"),
        }, # Capital is split equally: 50% equities / 50% bonds.
        series_list=[
            equities,
            bonds,
        ],
    )

    metrics = {
        metric.asset_class: metric
        for metric in snapshot.asset_metrics
    } # Makes each asset's risk metrics easy to retrieve.

    assert (
        metrics[
            AssetClass.EQUITIES
        ].component_risk_contribution
        == Decimal("0.10")
    ) # Equities contribute 0.10 of the portfolio's 0.15 volatility.

    assert (
        metrics[
            AssetClass.GOVERNMENT_BONDS
        ].component_risk_contribution
        == Decimal("0.05")
    ) # Bonds contribute only 0.05 despite having the same 50% capital weight.

    assert abs(
        metrics[
            AssetClass.EQUITIES
        ].relative_risk_contribution
        - Decimal(
            "0.6666666666666666666666666667"
        )
    ) < Decimal("0.000000000001")
    # Equities contribute roughly 66.7% of total portfolio risk,
    # even though they represent only 50% of invested capital.
# =========================
# Missing Historical Evidence
# Every weighted asset must have matching historical data before risk is calculated.
# =========================

def test_builder_requires_matching_assets():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        [
            Decimal("100"),
            Decimal("120"),
            Decimal("120"),
            Decimal("96"),
        ],
    ) # We deliberately provide history for equities only.

    with pytest.raises(
        ValueError
    ):
        build_portfolio_risk_snapshot(
            capital_weights={
                AssetClass.EQUITIES: Decimal("0.5"),
                AssetClass.GOVERNMENT_BONDS: Decimal("0.5"),
            }, # Portfolio claims to contain both equities and bonds.
            series_list=[
                equities,
            ], # But historical risk evidence exists only for equities.
        )

# =========================
# Invalid Capital Weights
# Portfolio weights must represent the whole portfolio before risk is calculated.
# =========================

def test_builder_rejects_invalid_weight_total():

    equities = make_series(
        AssetClass.EQUITIES,
        "SPY",
        [
            Decimal("100"),
            Decimal("120"),
            Decimal("120"),
            Decimal("96"),
        ],
    ) # Valid historical equity evidence.

    bonds = make_series(
        AssetClass.GOVERNMENT_BONDS,
        "IEF",
        [
            Decimal("100"),
            Decimal("110"),
            Decimal("110"),
            Decimal("99"),
        ],
    ) # Valid historical bond evidence.

    with pytest.raises(
        ValueError
    ):
        build_portfolio_risk_snapshot(
            capital_weights={
                AssetClass.EQUITIES: Decimal("0.6"),
                AssetClass.GOVERNMENT_BONDS: Decimal("0.3"),
            }, # These weights total only 0.9, so the portfolio is incomplete.
            series_list=[
                equities,
                bonds,
            ],
        )