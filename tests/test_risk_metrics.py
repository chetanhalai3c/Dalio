from decimal import Decimal

import pytest

from tools.risk_metrics import (
    calculate_component_risk_contributions,
    calculate_marginal_risk_contributions,
    calculate_portfolio_volatility,
    calculate_relative_risk_contributions,
    calculate_sample_correlation,
    calculate_sample_covariance,
    calculate_sample_volatility,
    calculate_simple_returns,
)

# =========================
# Simple Returns
# Calculates period-to-period percentage changes.
# =========================

def test_calculate_simple_returns():

    prices = [
        Decimal("100"),
        Decimal("110"),
        Decimal("99"),
    ]

    result = calculate_simple_returns(
        prices
    )

    assert result == [
        Decimal("0.1"),
        Decimal("-0.1"),
    ]


# =========================
# Unchanged Price
# No price movement should produce a zero return.
# =========================

def test_unchanged_price_returns_zero():

    prices = [
        Decimal("100"),
        Decimal("100"),
    ]

    result = calculate_simple_returns(
        prices
    )

    assert result == [
        Decimal("0"),
    ]


# =========================
# Insufficient History
# A return requires at least two observations.
# =========================

def test_return_series_requires_two_prices():

    with pytest.raises(
        ValueError
    ):
        calculate_simple_returns(
            [
                Decimal("100"),
            ]
        )


# =========================
# Invalid Prices
# Zero or negative prices cannot form valid financial returns.
# =========================

def test_zero_price_rejected():

    with pytest.raises(
        ValueError
    ):
        calculate_simple_returns(
            [
                Decimal("100"),
                Decimal("0"),
            ]
        )


def test_negative_price_rejected():

    with pytest.raises(
        ValueError
    ):
        calculate_simple_returns(
            [
                Decimal("100"),
                Decimal("-10"),
            ]
        )

# =========================
# Sample Volatility
# Symmetric returns around zero should produce predictable volatility.
# =========================

def test_calculate_sample_volatility():

    returns = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    result = calculate_sample_volatility(
        returns
    )

    assert result == Decimal("0.1")


# =========================
# Zero Volatility
# Identical returns have no dispersion.
# =========================

def test_identical_returns_have_zero_volatility():

    returns = [
        Decimal("0.05"),
        Decimal("0.05"),
        Decimal("0.05"),
    ]

    result = calculate_sample_volatility(
        returns
    )

    assert result == Decimal("0")


# =========================
# Insufficient Returns
# Sample volatility requires at least two return observations.
# =========================

def test_volatility_requires_two_returns():

    with pytest.raises(
        ValueError
    ):
        calculate_sample_volatility(
            [
                Decimal("0.05"),
            ]
        )

# =========================
# Positive Covariance
# Identical return series should have positive covariance.
# =========================

def test_positive_sample_covariance():

    returns_a = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    returns_b = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    result = calculate_sample_covariance(
        returns_a,
        returns_b,
    )

    assert result == Decimal("0.01")


# =========================
# Negative Covariance
# Opposite return series should have negative covariance.
# =========================

def test_negative_sample_covariance():

    returns_a = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    returns_b = [
        Decimal("-0.1"),
        Decimal("0"),
        Decimal("0.1"),
    ]

    result = calculate_sample_covariance(
        returns_a,
        returns_b,
    )

    assert result == Decimal("-0.01")


# =========================
# Mismatched Return Series
# Covariance requires paired observations.
# =========================

def test_covariance_requires_equal_length():

    with pytest.raises(
        ValueError
    ):
        calculate_sample_covariance(
            [
                Decimal("0.1"),
                Decimal("0"),
                Decimal("-0.1"),
            ],
            [
                Decimal("0.1"),
                Decimal("0"),
            ],
        )


# =========================
# Insufficient Return Pairs
# Sample covariance requires at least two paired observations.
# =========================

def test_covariance_requires_two_observations():

    with pytest.raises(
        ValueError
    ):
        calculate_sample_covariance(
            [
                Decimal("0.1"),
            ],
            [
                Decimal("0.1"),
            ],
        )

# =========================
# Positive Correlation
# Identical return patterns should produce perfect positive correlation.
# =========================

def test_perfect_positive_correlation():

    returns_a = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    returns_b = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    result = calculate_sample_correlation(
        returns_a,
        returns_b,
    )

    assert result == Decimal("1")


# =========================
# Negative Correlation
# Opposite return patterns should produce perfect negative correlation.
# =========================

def test_perfect_negative_correlation():

    returns_a = [
        Decimal("0.1"),
        Decimal("0"),
        Decimal("-0.1"),
    ]

    returns_b = [
        Decimal("-0.1"),
        Decimal("0"),
        Decimal("0.1"),
    ]

    result = calculate_sample_correlation(
        returns_a,
        returns_b,
    )

    assert result == Decimal("-1")


# =========================
# Zero Correlation
# Orthogonal return patterns should produce zero covariance and correlation.
# =========================

def test_zero_correlation():

    returns_a = [
        Decimal("0.1"),
        Decimal("-0.1"),
        Decimal("0.1"),
        Decimal("-0.1"),
    ]

    returns_b = [
        Decimal("0.1"),
        Decimal("0.1"),
        Decimal("-0.1"),
        Decimal("-0.1"),
    ]

    result = calculate_sample_correlation(
        returns_a,
        returns_b,
    )

    assert result == Decimal("0")


# =========================
# Zero Volatility
# Correlation is undefined when one series never changes.
# =========================

def test_correlation_rejects_zero_volatility():

    with pytest.raises(
        ValueError
    ):
        calculate_sample_correlation(
            [
                Decimal("0.1"),
                Decimal("0"),
                Decimal("-0.1"),
            ],
            [
                Decimal("0.05"),
                Decimal("0.05"),
                Decimal("0.05"),
            ],
        )

# =========================
# Perfect Positive Co-Movement
# Equal-weight assets moving identically should retain the same volatility.
# =========================

def test_portfolio_volatility_positive_correlation():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
        "bonds": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
    }

    result = calculate_portfolio_volatility(
        weights,
        returns_by_asset,
    )

    assert result == Decimal("0.1")


# =========================
# Perfect Negative Co-Movement
# Equal opposite movements should fully offset in this simplified example.
# =========================

def test_portfolio_volatility_negative_correlation():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
        "bonds": [
            Decimal("-0.1"),
            Decimal("0"),
            Decimal("0.1"),
        ],
    }

    result = calculate_portfolio_volatility(
        weights,
        returns_by_asset,
    )

    assert result == Decimal("0")


# =========================
# Invalid Weights
# Portfolio weights must represent the whole portfolio.
# =========================

def test_portfolio_volatility_requires_weights_to_sum_to_one():

    with pytest.raises(
        ValueError
    ):
        calculate_portfolio_volatility(
            {
                "equities": Decimal("0.6"),
                "bonds": Decimal("0.3"),
            },
            {
                "equities": [
                    Decimal("0.1"),
                    Decimal("0"),
                    Decimal("-0.1"),
                ],
                "bonds": [
                    Decimal("0.05"),
                    Decimal("0"),
                    Decimal("-0.05"),
                ],
            },
        )


# =========================
# Asset Alignment
# Every weighted asset must have a corresponding return series.
# =========================

def test_portfolio_volatility_requires_matching_assets():

    with pytest.raises(
        ValueError
    ):
        calculate_portfolio_volatility(
            {
                "equities": Decimal("0.5"),
                "bonds": Decimal("0.5"),
            },
            {
                "equities": [
                    Decimal("0.1"),
                    Decimal("0"),
                    Decimal("-0.1"),
                ],
            },
        )

# =========================
# Marginal Risk Contribution
# Higher-volatility assets should have greater marginal impact when co-moving.
# =========================

def test_marginal_risk_contributions():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.2"),
            Decimal("0"),
            Decimal("-0.2"),
        ],
        "bonds": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
    }

    result = calculate_marginal_risk_contributions(
        weights,
        returns_by_asset,
    )

    assert result["equities"] == Decimal("0.2")
    assert result["bonds"] == Decimal("0.1")


# =========================
# Component Risk Contribution
# Weight multiplied by marginal risk gives contribution to portfolio volatility.
# =========================

def test_component_risk_contributions():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.2"),
            Decimal("0"),
            Decimal("-0.2"),
        ],
        "bonds": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
    }

    result = calculate_component_risk_contributions(
        weights,
        returns_by_asset,
    )

    assert result["equities"] == Decimal("0.10")
    assert result["bonds"] == Decimal("0.05")

    assert sum(
        result.values(),
        Decimal("0"),
    ) == Decimal("0.15")


# =========================
# Relative Risk Contribution
# Component contributions should reconcile to the whole portfolio risk.
# =========================

def test_relative_risk_contributions_sum_to_one():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.2"),
            Decimal("0"),
            Decimal("-0.2"),
        ],
        "bonds": [
            Decimal("0.1"),
            Decimal("0"),
            Decimal("-0.1"),
        ],
    }

    result = calculate_relative_risk_contributions(
        weights,
        returns_by_asset,
    )

    total = sum(
        result.values(),
        Decimal("0"),
    )

    assert abs(
        total - Decimal("1")
    ) < Decimal("0.000000000001")


# =========================
# Diversifying Contribution
# A hedging asset may legitimately make a negative contribution to total risk.
# =========================

def test_component_risk_contribution_can_be_negative():

    weights = {
        "equities": Decimal("0.5"),
        "bonds": Decimal("0.5"),
    }

    returns_by_asset = {
        "equities": [
            Decimal("0.2"),
            Decimal("0"),
            Decimal("-0.2"),
        ],
        "bonds": [
            Decimal("-0.1"),
            Decimal("0"),
            Decimal("0.1"),
        ],
    }

    result = calculate_component_risk_contributions(
        weights,
        returns_by_asset,
    )

    assert result["equities"] == Decimal("0.10")
    assert result["bonds"] == Decimal("-0.05")


# =========================
# Zero Portfolio Risk
# Marginal contribution is undefined when total volatility is zero.
# =========================

def test_risk_contribution_rejects_zero_portfolio_volatility():

    with pytest.raises(
        ValueError
    ):
        calculate_marginal_risk_contributions(
            {
                "equities": Decimal("0.5"),
                "bonds": Decimal("0.5"),
            },
            {
                "equities": [
                    Decimal("0.1"),
                    Decimal("0"),
                    Decimal("-0.1"),
                ],
                "bonds": [
                    Decimal("-0.1"),
                    Decimal("0"),
                    Decimal("0.1"),
                ],
            },
        )