from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.market import AssetClass
from models.portfolio_risk import (
    AssetRiskMetrics,
    PairwiseRiskRelationship,
    PortfolioRiskSnapshot,
    RiskMethodology,
)
from models.risk_market_data import (
    HistoricalFrequency,
)


# =========================
# Test Helper
# Creates a valid deterministic portfolio-risk snapshot.
# =========================

def make_valid_snapshot():

    return PortfolioRiskSnapshot(
        as_of_date=date(
            2026,
            9,
            16,
        ),
        methodology=RiskMethodology.HISTORICAL_PROXY,
        currency="USD",
        frequency=HistoricalFrequency.WEEKLY,
        observation_start_date=date(
            2025,
            9,
            12,
        ),
        observation_end_date=date(
            2026,
            9,
            16,
        ),
        aligned_return_observation_count=52,
        portfolio_period_volatility=Decimal("0.08"),
        asset_metrics=[
            AssetRiskMetrics(
                asset_class=AssetClass.EQUITIES,
                proxy_symbol="SPY",
                proxy_name="Equity Proxy",
                capital_weight=Decimal("0.6"),
                period_volatility=Decimal("0.12"),
                marginal_risk_contribution=Decimal("0.10"),
                component_risk_contribution=Decimal("0.06"),
                relative_risk_contribution=Decimal("0.75"),
            ),
            AssetRiskMetrics(
                asset_class=AssetClass.GOVERNMENT_BONDS,
                proxy_symbol="IEF",
                proxy_name="Government Bond Proxy",
                capital_weight=Decimal("0.4"),
                period_volatility=Decimal("0.04"),
                marginal_risk_contribution=Decimal("0.05"),
                component_risk_contribution=Decimal("0.02"),
                relative_risk_contribution=Decimal("0.25"),
            ),
        ],
        pairwise_relationships=[
            PairwiseRiskRelationship(
                asset_class_a=AssetClass.EQUITIES,
                asset_class_b=AssetClass.GOVERNMENT_BONDS,
                covariance=Decimal("0.001"),
                correlation=Decimal("0.2"),
            ),
        ],
        limitations=[
            "Historical proxy behaviour does not guarantee future behaviour."
        ],
    )


# =========================
# Valid Risk Snapshot
# Mathematically consistent deterministic evidence should pass.
# =========================

def test_valid_portfolio_risk_snapshot():

    snapshot = make_valid_snapshot()

    assert snapshot.currency == "USD"

    assert snapshot.portfolio_period_volatility == (
        Decimal("0.08")
    )

    assert len(
        snapshot.asset_metrics
    ) == 2


# =========================
# Capital Weights
# Portfolio capital weights must reconcile to the whole portfolio.
# =========================

def test_risk_snapshot_weights_must_sum_to_one():

    snapshot_data = make_valid_snapshot().model_dump()

    snapshot_data["asset_metrics"][0][
        "capital_weight"
    ] = Decimal("0.5")

    with pytest.raises(
        ValidationError
    ):
        PortfolioRiskSnapshot(
            **snapshot_data
        )


# =========================
# Component Risk
# Component risk must equal weight multiplied by marginal contribution.
# =========================

def test_component_risk_must_reconcile():

    snapshot_data = make_valid_snapshot().model_dump()

    snapshot_data["asset_metrics"][0][
        "component_risk_contribution"
    ] = Decimal("0.04")

    with pytest.raises(
        ValidationError
    ):
        PortfolioRiskSnapshot(
            **snapshot_data
        )


# =========================
# Portfolio Risk
# Asset component contributions must reconcile to total volatility.
# =========================

def test_components_must_sum_to_portfolio_volatility():

    snapshot_data = make_valid_snapshot().model_dump()

    snapshot_data[
        "portfolio_period_volatility"
    ] = Decimal("0.09")

    with pytest.raises(
        ValidationError
    ):
        PortfolioRiskSnapshot(
            **snapshot_data
        )


# =========================
# Relative Risk
# Relative contributions must describe the whole portfolio risk.
# =========================

def test_relative_risk_must_sum_to_one():

    snapshot_data = make_valid_snapshot().model_dump()

    snapshot_data["asset_metrics"][0][
        "relative_risk_contribution"
    ] = Decimal("0.60")

    with pytest.raises(
        ValidationError
    ):
        PortfolioRiskSnapshot(
            **snapshot_data
        )


# =========================
# Duplicate Asset Classes
# One deterministic risk record should represent each exposure.
# =========================

def test_duplicate_asset_risk_metrics_rejected():

    snapshot_data = make_valid_snapshot().model_dump()

    snapshot_data["asset_metrics"][1][
        "asset_class"
    ] = AssetClass.EQUITIES

    with pytest.raises(
        ValidationError
    ):
        PortfolioRiskSnapshot(
            **snapshot_data
        )


# =========================
# Invalid Pair
# Correlation cannot compare an asset class with itself.
# =========================

def test_pairwise_relationship_requires_two_assets():

    with pytest.raises(
        ValidationError
    ):
        PairwiseRiskRelationship(
            asset_class_a=AssetClass.EQUITIES,
            asset_class_b=AssetClass.EQUITIES,
            covariance=Decimal("0.01"),
            correlation=Decimal("1"),
        )