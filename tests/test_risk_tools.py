import pytest
from models.portfolio import Portfolio
from tools.risk_tools import (
    calculate_total_value,
    calculate_holding_weights,
    calculate_asset_class_weights,
    calculate_largest_position_weight,
    calculate_hhi,
    calculate_portfolio_structure_metrics,
)


# =========================
# Shared Test Portfolio
# =========================

def build_test_portfolio():
    return Portfolio(
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "S&P 500 ETF",
                "ticker": "VUSA",
                "asset_class": "equity_fund",
                "current_value": {
                    "value_type": "exact",
                    "amount": 15000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            },
            {
                "holding_id": "holding_2",
                "name": "Nvidia",
                "ticker": "NVDA",
                "asset_class": "equity",
                "current_value": {
                    "value_type": "exact",
                    "amount": 5000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            },
        ]
    )


# =========================
# Scenario 1 — Total Value
# =========================

def test_total_portfolio_value():
    portfolio = build_test_portfolio()

    assert calculate_total_value(portfolio) == 20000


# =========================
# Scenario 2 — Holding Weights
# =========================

def test_holding_weights():
    portfolio = build_test_portfolio()

    weights = calculate_holding_weights(portfolio)

    assert weights["holding_1"] == 0.75
    assert weights["holding_2"] == 0.25


# =========================
# Scenario 3 — Asset-Class Weights
# =========================

def test_asset_class_weights():
    portfolio = build_test_portfolio()

    weights = calculate_asset_class_weights(portfolio)

    assert weights["equity_fund"] == 0.75
    assert weights["equity"] == 0.25


# =========================
# Scenario 4 — Largest Position
# =========================

def test_largest_position_weight():
    portfolio = build_test_portfolio()

    assert calculate_largest_position_weight(portfolio) == 0.75


# =========================
# Scenario 5 — HHI Concentration
# =========================

def test_hhi():
    portfolio = build_test_portfolio()

    assert calculate_hhi(portfolio) == 0.625


# =========================
# Scenario 6 — Complete Metrics
# =========================

def test_portfolio_structure_metrics():
    portfolio = build_test_portfolio()

    metrics = calculate_portfolio_structure_metrics(portfolio)

    assert metrics["total_value"] == 20000.0
    assert metrics["holding_weights"]["holding_1"] == 0.75
    assert metrics["largest_position_weight"] == 0.75
    assert metrics["hhi"] == 0.625


# =========================
# Scenario 7 — Empty Portfolio
# =========================

def test_empty_portfolio():
    portfolio = Portfolio()

    metrics = calculate_portfolio_structure_metrics(portfolio)

    assert metrics["total_value"] == 0.0
    assert metrics["holding_weights"] == {}
    assert metrics["asset_class_weights"] == {}
    assert metrics["largest_position_weight"] == 0.0
    assert metrics["hhi"] == 0

# =========================
# Scenario 8 — Currency Preserved
# =========================

def test_portfolio_currency_preserved():
    portfolio = build_test_portfolio()

    metrics = calculate_portfolio_structure_metrics(portfolio)

    assert metrics["currency"] == "GBP"


# =========================
# Scenario 9 — Mixed Currencies Rejected
# =========================

def test_mixed_currencies_rejected():
    portfolio = Portfolio(
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "UK Holding",
                "asset_class": "equity",
                "current_value": {
                    "value_type": "exact",
                    "amount": 10000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            },
            {
                "holding_id": "holding_2",
                "name": "US Holding",
                "asset_class": "equity",
                "current_value": {
                    "value_type": "exact",
                    "amount": 10000,
                    "currency": "USD",
                },
                "currency": "USD",
            },
        ]
    )

    with pytest.raises(
        ValueError,
        match="multiple currencies",
    ):
        calculate_portfolio_structure_metrics(portfolio)