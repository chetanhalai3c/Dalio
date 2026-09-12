from decimal import Decimal

from models.portfolio import Portfolio


# =========================
# Holding Value Helper
# =========================

def _holding_value(holding) -> Decimal:
    amount = holding.current_value.amount

    if amount is None:
        raise ValueError(
            f"Holding {holding.holding_id} does not have a usable "
            "current_value amount."
        )

    return amount


# =========================
# Portfolio Currency
# =========================

def _portfolio_currency(
    portfolio: Portfolio,
) -> str | None:
    currencies = {
        holding.current_value.currency
        for holding in portfolio.holdings
    }

    if not currencies:
        return None

    if len(currencies) > 1:
        raise ValueError(
            "Portfolio contains multiple currencies. "
            "Convert holdings to a common currency before "
            "calculating portfolio-level metrics."
        )

    return next(iter(currencies))


# =========================
# Total Portfolio Value
# =========================

def calculate_total_value(
    portfolio: Portfolio,
) -> Decimal:
    _portfolio_currency(portfolio)

    return sum(
        (
            _holding_value(holding)
            for holding in portfolio.holdings
        ),
        Decimal("0"),
    )


# =========================
# Holding Weights
# =========================

def calculate_holding_weights(
    portfolio: Portfolio,
) -> dict[str, float]:
    total_value = calculate_total_value(portfolio)

    if total_value <= 0:
        return {}

    return {
        holding.holding_id: float(
            _holding_value(holding)
            / total_value
        )
        for holding in portfolio.holdings
    }


# =========================
# Asset-Class Weights
# =========================

def calculate_asset_class_weights(
    portfolio: Portfolio,
) -> dict[str, float]:
    total_value = calculate_total_value(portfolio)

    if total_value <= 0:
        return {}

    asset_values: dict[str, Decimal] = {}

    for holding in portfolio.holdings:
        asset_class = (
            holding.asset_class.value
            if holding.asset_class is not None
            else "unknown"
        )

        asset_values[asset_class] = (
            asset_values.get(
                asset_class,
                Decimal("0"),
            )
            + _holding_value(holding)
        )

    return {
        asset_class: float(
            value / total_value
        )
        for asset_class, value
        in asset_values.items()
    }


# =========================
# Largest Position
# =========================

def calculate_largest_position_weight(
    portfolio: Portfolio,
) -> float:
    weights = calculate_holding_weights(
        portfolio
    )

    if not weights:
        return 0.0

    return max(weights.values())


# =========================
# Concentration Index
# =========================

def calculate_hhi(
    portfolio: Portfolio,
) -> float:
    weights = calculate_holding_weights(
        portfolio
    )

    return sum(
        weight ** 2
        for weight in weights.values()
    )


# =========================
# Risk Structure Summary
# =========================

def calculate_portfolio_structure_metrics(
    portfolio: Portfolio,
) -> dict:
    currency = _portfolio_currency(portfolio)

    return {
        "total_value": float(
            calculate_total_value(portfolio)
        ),
        "currency": currency,
        "holding_weights": (
            calculate_holding_weights(portfolio)
        ),
        "asset_class_weights": (
            calculate_asset_class_weights(portfolio)
        ),
        "largest_position_weight": (
            calculate_largest_position_weight(
                portfolio
            )
        ),
        "hhi": calculate_hhi(portfolio),
    }