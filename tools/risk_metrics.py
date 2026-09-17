from decimal import Decimal


# =========================
# Simple Return Series
# Converts ordered historical prices into period-to-period returns.
# =========================

def calculate_simple_returns(
    prices: list[Decimal],
) -> list[Decimal]:

    if len(prices) < 2:
        raise ValueError(
            "At least two prices are required to calculate returns."
        )

    if any(
        price <= Decimal("0")
        for price in prices
    ):
        raise ValueError(
            "Prices must be greater than zero."
        )

    returns = []

    for previous_price, current_price in zip(
        prices,
        prices[1:],
    ):
        period_return = (
            current_price
            / previous_price
        ) - Decimal("1")

        returns.append(
            period_return
        )

    return returns
# =========================
# Sample Volatility
# Measures how widely historical returns vary around their average.
# =========================

def calculate_sample_volatility(
    returns: list[Decimal],
) -> Decimal:

    if len(returns) < 2:
        raise ValueError(
            "At least two returns are required to calculate volatility."
        )

    mean_return = (
        sum(
            returns,
            Decimal("0"),
        )
        / Decimal(
            len(returns)
        )
    )

    squared_deviations = [
        (
            period_return
            - mean_return
        ) ** 2
        for period_return in returns
    ]

    variance = (
        sum(
            squared_deviations,
            Decimal("0"),
        )
        / Decimal(
            len(returns) - 1
        )
    )

    return variance.sqrt()

# =========================
# Sample Covariance
# Measures whether two historical return series move together.
# =========================

def calculate_sample_covariance(
    returns_a: list[Decimal],
    returns_b: list[Decimal],
) -> Decimal:

    if len(returns_a) != len(returns_b):
        raise ValueError(
            "Return series must contain the same number of observations."
        )

    if len(returns_a) < 2:
        raise ValueError(
            "At least two paired returns are required to calculate covariance."
        )

    mean_a = (
        sum(
            returns_a,
            Decimal("0"),
        )
        / Decimal(
            len(returns_a)
        )
    )

    mean_b = (
        sum(
            returns_b,
            Decimal("0"),
        )
        / Decimal(
            len(returns_b)
        )
    )

    covariance_sum = sum(
        (
            (return_a - mean_a)
            * (return_b - mean_b)
        )
        for return_a, return_b in zip(
            returns_a,
            returns_b,
        )
    )

    return (
        covariance_sum
        / Decimal(
            len(returns_a) - 1
        )
    )

# =========================
# Sample Correlation
# Standardises covariance to show the strength and direction of co-movement.
# =========================

def calculate_sample_correlation(
    returns_a: list[Decimal],
    returns_b: list[Decimal],
) -> Decimal:

    covariance = calculate_sample_covariance(
        returns_a,
        returns_b,
    )

    volatility_a = calculate_sample_volatility(
        returns_a
    )

    volatility_b = calculate_sample_volatility(
        returns_b
    )

    if (
        volatility_a == Decimal("0")
        or volatility_b == Decimal("0")
    ):
        raise ValueError(
            "Correlation is undefined when either return series "
            "has zero volatility."
        )

    return (
        covariance
        / (
            volatility_a
            * volatility_b
        )
    )

# =========================
# Portfolio Volatility
# Combines asset weights and co-movement into total portfolio risk.
# =========================

def calculate_portfolio_volatility(
    weights: dict[str, Decimal],
    returns_by_asset: dict[str, list[Decimal]],
) -> Decimal:

    if not weights:
        raise ValueError(
            "At least one portfolio weight is required."
        )

    if set(weights) != set(returns_by_asset):
        raise ValueError(
            "Weights and return series must contain the same assets."
        )

    if any(
        weight < Decimal("0")
        for weight in weights.values()
    ):
        raise ValueError(
            "Portfolio weights cannot be negative."
        )

    total_weight = sum(
        weights.values(),
        Decimal("0"),
    )

    if abs(
        total_weight - Decimal("1")
    ) > Decimal("0.000001"):
        raise ValueError(
            "Portfolio weights must sum to 1."
        )

    portfolio_variance = Decimal("0")

    for asset_i, weight_i in weights.items():
        for asset_j, weight_j in weights.items():

            covariance = calculate_sample_covariance(
                returns_by_asset[asset_i],
                returns_by_asset[asset_j],
            )

            portfolio_variance += (
                weight_i
                * weight_j
                * covariance
            )

    if portfolio_variance < Decimal("0"):
        raise ValueError(
            "Portfolio variance cannot be negative."
        )

    return portfolio_variance.sqrt()

# =========================
# Marginal Risk Contribution
# Measures how much portfolio volatility responds to each asset's exposure.
# =========================

def calculate_marginal_risk_contributions(
    weights: dict[str, Decimal],
    returns_by_asset: dict[str, list[Decimal]],
) -> dict[str, Decimal]:

    portfolio_volatility = calculate_portfolio_volatility(
        weights,
        returns_by_asset,
    )

    if portfolio_volatility == Decimal("0"):
        raise ValueError(
            "Risk contribution is undefined when portfolio volatility is zero."
        )

    marginal_contributions = {}

    for asset_i in weights:

        weighted_covariance_sum = sum(
            (
                weights[asset_j]
                * calculate_sample_covariance(
                    returns_by_asset[asset_i],
                    returns_by_asset[asset_j],
                )
            )
            for asset_j in weights
        )

        marginal_contributions[asset_i] = (
            weighted_covariance_sum
            / portfolio_volatility
        )

    return marginal_contributions


# =========================
# Component Risk Contribution
# Converts marginal risk into the amount of total volatility caused by each asset.
# =========================

def calculate_component_risk_contributions(
    weights: dict[str, Decimal],
    returns_by_asset: dict[str, list[Decimal]],
) -> dict[str, Decimal]:

    marginal_contributions = (
        calculate_marginal_risk_contributions(
            weights,
            returns_by_asset,
        )
    )

    return {
        asset: (
            weights[asset]
            * marginal_contributions[asset]
        )
        for asset in weights
    }


# =========================
# Relative Risk Contribution
# Expresses each component's contribution as a share of total portfolio risk.
# =========================

def calculate_relative_risk_contributions(
    weights: dict[str, Decimal],
    returns_by_asset: dict[str, list[Decimal]],
) -> dict[str, Decimal]:

    portfolio_volatility = calculate_portfolio_volatility(
        weights,
        returns_by_asset,
    )

    component_contributions = (
        calculate_component_risk_contributions(
            weights,
            returns_by_asset,
        )
    )

    return {
        asset: (
            contribution
            / portfolio_volatility
        )
        for asset, contribution
        in component_contributions.items()
    }