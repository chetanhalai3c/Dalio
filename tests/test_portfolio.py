import pytest
from pydantic import ValidationError

from models.portfolio import Portfolio


# =========================
# Scenario 1 — Empty portfolio is valid
# =========================

def test_empty_portfolio_valid():
    portfolio = Portfolio()

    assert portfolio.accounts == []
    assert portfolio.holdings == []


# =========================
# Scenario 2 — Realistic UK portfolio
# =========================

def test_realistic_uk_portfolio():
    portfolio = Portfolio(
        metadata={
            "base_currency": "gbp",
            "data_source": "manual",
        },
        accounts=[
            {
                "account_id": "account_1",
                "account_name": "Stocks ISA",
                "platform": "Trading 212",
                "account_type": "ISA",
                "currency": "GBP",
            }
        ],
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "Vanguard S&P 500 ETF",
                "ticker": "VUSA",
                "asset_class": "equity_fund",
                "quantity": 100,
                "current_price": {
                    "value_type": "exact",
                    "amount": 80,
                    "currency": "GBP",
                },
                "current_value": {
                    "value_type": "exact",
                    "amount": 8000,
                    "currency": "GBP",
                },
                "currency": "GBP",
                "account_id": "account_1",
            }
        ],
    )

    assert portfolio.metadata.base_currency == "GBP"
    assert portfolio.holdings[0].ticker == "VUSA"


# =========================
# Scenario 3 — Quantity can be unknown
# =========================

def test_holding_without_quantity_valid():
    portfolio = Portfolio(
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "Gold ETF",
                "asset_class": "gold",
                "current_value": {
                    "value_type": "approximate",
                    "amount": 5000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            }
        ]
    )

    assert portfolio.holdings[0].quantity is None
    assert portfolio.holdings[0].current_value.amount == 5000


# =========================
# Scenario 4 — International portfolio
# =========================

def test_international_multicurrency_portfolio():
    portfolio = Portfolio(
        metadata={
            "base_currency": "INR",
            "data_source": "api",
        },
        accounts=[
            {
                "account_id": "zerodha",
                "platform": "Zerodha",
                "currency": "INR",
            }
        ],
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "Indian Equity Fund",
                "asset_class": "equity_fund",
                "current_value": {
                    "value_type": "exact",
                    "amount": 500000,
                    "currency": "INR",
                },
                "currency": "INR",
                "account_id": "zerodha",
            }
        ],
    )

    assert portfolio.metadata.base_currency == "INR"
    assert portfolio.accounts[0].platform == "Zerodha"


# =========================
# Scenario 5 — Unknown account rejected
# =========================

def test_unknown_account_reference_rejected():
    with pytest.raises(ValidationError):
        Portfolio(
            holdings=[
                {
                    "holding_id": "holding_1",
                    "name": "S&P 500 ETF",
                    "current_value": {
                        "value_type": "exact",
                        "amount": 10000,
                        "currency": "GBP",
                    },
                    "currency": "GBP",
                    "account_id": "missing_account",
                }
            ]
        )


# =========================
# Scenario 6 — Duplicate account IDs rejected
# =========================

def test_duplicate_account_ids_rejected():
    with pytest.raises(ValidationError):
        Portfolio(
            accounts=[
                {
                    "account_id": "account_1",
                },
                {
                    "account_id": "account_1",
                },
            ]
        )


# =========================
# Scenario 7 — Duplicate holding IDs rejected
# =========================

def test_duplicate_holding_ids_rejected():
    holding = {
        "holding_id": "holding_1",
        "name": "Cash",
        "asset_class": "cash",
        "current_value": {
            "value_type": "exact",
            "amount": 5000,
            "currency": "GBP",
        },
        "currency": "GBP",
    }

    with pytest.raises(ValidationError):
        Portfolio(
            holdings=[
                holding,
                holding,
            ]
        )


# =========================
# Scenario 8 — Unknown fields rejected
# =========================

def test_unknown_portfolio_field_rejected():
    with pytest.raises(ValidationError):
        Portfolio(
            holdings=[
                {
                    "holding_id": "holding_1",
                    "name": "Gold ETF",
                    "current_value": {
                        "value_type": "exact",
                        "amount": 3000,
                        "currency": "GBP",
                    },
                    "currency": "GBP",
                    "random_risk_score": 99,
                }
            ]
        )