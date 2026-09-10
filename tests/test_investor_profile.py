
import pytest
from pydantic import ValidationError

from models.investor_profile import InvestorProfile

# =========================
# Scenario 1 — Minimal UK investor
# =========================

def test_minimal_uk_investor():
    profile = InvestorProfile(
        jurisdiction_currency={
            "country_of_residence": "GB",
            "spending_currency": "GBP",
        },
        financial_circumstances={
            "investable_capital": {
                "value_type": "exact",
                "amount": 10000,
                "currency": "GBP",
            }
        },
        market_access={
            "platforms_used": [
                {
                    "platform_name": "Trading 212",
                    "country": "GB",
                }
            ]
        },
    )

    assert profile.jurisdiction_currency.country_of_residence == "GB"
    assert profile.jurisdiction_currency.spending_currency == "GBP"
    assert profile.financial_circumstances.investable_capital.amount == 10000
    assert profile.market_access.platforms_used[0].platform_name == "Trading 212"

    # Important product rule:
    # The investor can have no goal or risk questionnaire completed.
    assert profile.goals_horizon.primary_goal is None
    assert profile.risk.chosen_risk_preference is None

# =========================
# Scenario 2 — Existing portfolio only
# =========================

def test_existing_portfolio_only():
    # The actual holdings will live in the separate Portfolio model.
    # InvestorProfile must still be valid even if the investor
    # provides no personal information.
    profile = InvestorProfile()

    assert profile.jurisdiction_currency.country_of_residence is None
    assert profile.goals_horizon.primary_goal is None
    assert profile.financial_circumstances.investable_capital is None
    assert profile.risk.chosen_risk_preference is None
    assert profile.market_access.platforms_used == []
    assert profile.expected_withdrawals == []

# =========================
# Scenario 3 — Indian retail investor
# =========================

def test_indian_retail_investor():
    profile = InvestorProfile(
        jurisdiction_currency={
            "country_of_residence": "IN",
            "spending_currency": "INR",
            "income_currencies": ["INR"],
            "investment_currencies": ["INR", "USD"],
        },
        financial_circumstances={
            "recurring_contributions": [
                {
                    "amount": {
                        "value_type": "exact",
                        "amount": 30000,
                        "currency": "INR",
                    },
                    "frequency": "monthly",
                }
            ]
        },
        risk={
            "chosen_risk_preference": 7,
        },
        market_access={
            "platforms_used": [
                {
                    "platform_name": "Zerodha",
                    "country": "IN",
                    "primary_currency": "INR",
                }
            ]
        },
    )

    assert profile.jurisdiction_currency.country_of_residence == "IN"
    assert profile.jurisdiction_currency.spending_currency == "INR"
    assert profile.financial_circumstances.recurring_contributions[0].amount.amount == 30000
    assert profile.risk.chosen_risk_preference == 7
    assert profile.market_access.platforms_used[0].platform_name == "Zerodha"

# =========================
# Scenario 4 — Singapore multi-currency investor
# =========================

def test_singapore_multicurrency_investor():
    profile = InvestorProfile(
        jurisdiction_currency={
            "country_of_residence": "SG",
            "spending_currency": "SGD",
            "income_currencies": ["SGD"],
            "investment_currencies": ["SGD", "USD"],
        },
        goals_horizon={
            "investment_horizon": "10_plus_years",
        },
        financial_circumstances={
            "income_stability": "stable",
            "liabilities": [
                {
                    "liability_type": "mortgage",
                    "balance": {
                        "value_type": "approximate",
                        "amount": 400000,
                        "currency": "SGD",
                    },
                    "rate_type": "floating",
                }
            ],
        },
        risk={
            "chosen_risk_preference": 6,
        },
        market_access={
            "platforms_used": [
                {
                    "platform_name": "Interactive Brokers",
                    "country": "SG",
                    "primary_currency": "SGD",
                }
            ]
        },
    )

    assert profile.jurisdiction_currency.country_of_residence == "SG"
    assert profile.jurisdiction_currency.investment_currencies == ["SGD", "USD"]
    assert profile.goals_horizon.investment_horizon.value == "10_plus_years"
    assert profile.financial_circumstances.liabilities[0].liability_type.value == "mortgage"
    assert profile.financial_circumstances.liabilities[0].balance.currency == "SGD"
    assert profile.financial_circumstances.liabilities[0].rate_type.value == "floating"
    assert profile.risk.chosen_risk_preference == 6

# =========================
# Scenario 5 — Approximate / range values
# =========================

def test_approximate_and_range_values():
    profile = InvestorProfile(
        jurisdiction_currency={
            "country_of_residence": "FR",
            "spending_currency": "EUR",
        },
        financial_circumstances={
            "income": {
                "value_type": "range",
                "minimum_amount": 40000,
                "maximum_amount": 50000,
                "currency": "EUR",
            },
            "liabilities": [
                {
                    "liability_type": "mortgage",
                    "balance": {
                        "value_type": "approximate",
                        "amount": 150000,
                        "currency": "EUR",
                    },
                    "rate_type": "fixed",
                }
            ],
        },
        market_access={
            "access_unknown": True,
        },
    )

    assert profile.financial_circumstances.income.minimum_amount == 40000
    assert profile.financial_circumstances.income.maximum_amount == 50000
    assert profile.financial_circumstances.liabilities[0].balance.amount == 150000
    assert profile.market_access.access_unknown is True

# =========================
# Scenario 6 — Invalid risk preference rejected
# =========================

def test_invalid_risk_preference_rejected():
    with pytest.raises(ValidationError):
        InvestorProfile(
            risk={
                "chosen_risk_preference": 11,
            }
        )

# =========================
# Scenario 7 — Invalid money range rejected
# =========================

def test_invalid_money_range_rejected():
    with pytest.raises(ValidationError):
        InvestorProfile(
            financial_circumstances={
                "income": {
                    "value_type": "range",
                    "minimum_amount": 50000,
                    "maximum_amount": 40000,
                    "currency": "EUR",
                }
            }
        )

# =========================
# Scenario 8 — Expected withdrawals are derived
# =========================

def test_expected_withdrawals_are_derived():
    profile = InvestorProfile(
        goals_horizon={
            "planned_withdrawals": [
                {
                    "purpose": "House deposit",
                    "amount": {
                        "value_type": "approximate",
                        "amount": 40000,
                        "currency": "GBP",
                    },
                    "timing_description": "In around 3 years",
                }
            ]
        },
        liquidity={
            "near_term_cash_needs": [
                {
                    "purpose": "Emergency home repair",
                    "amount": {
                        "value_type": "approximate",
                        "amount": 5000,
                        "currency": "GBP",
                    },
                    "timing_description": "Within the next few months",
                }
            ]
        },
    )

    assert len(profile.expected_withdrawals) == 2
    assert profile.expected_withdrawals[0].purpose == "House deposit"
    assert profile.expected_withdrawals[1].purpose == "Emergency home repair"

# =========================
# Scenario 9 — Unknown fields must not be silently ignored
# =========================

def test_unknown_field_rejected():
    with pytest.raises(ValidationError):
        InvestorProfile(
            jurisdiction_currency={
                "country_of_residence": "GB",
                "spending_curreny": "GBP",  # Intentional typo
            }
        )

# =========================
# Scenario 10 — Contradictory MoneyValue rejected
# =========================

def test_contradictory_money_value_rejected():
    with pytest.raises(ValidationError):
        InvestorProfile(
            financial_circumstances={
                "income": {
                    "value_type": "exact",
                    "amount": 50000,
                    "minimum_amount": 40000,
                    "maximum_amount": 60000,
                    "currency": "GBP",
                }
            }
        )


# =========================
# Scenario 11 — Conflicting LossCapacity rejected
# =========================

def test_conflicting_loss_capacity_rejected():
    with pytest.raises(ValidationError):
        InvestorProfile(
            risk={
                "loss_capacity": {
                    "amount": {
                        "value_type": "exact",
                        "amount": 20000,
                        "currency": "GBP",
                    },
                    "percentage": 30,
                }
            }
        )