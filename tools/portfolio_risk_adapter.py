from decimal import Decimal # Precise portfolio-weight calculations.

from models.market import AssetClass # Broad asset classes understood by the historical risk engine.
from models.portfolio import Portfolio # Investor's actual portfolio model.
from tools.risk_tools import calculate_asset_class_weights # Existing deterministic capital-weight calculation.


# =========================
# Portfolio → Risk Asset Mapping
# Converts detailed portfolio labels into the broad risk-engine asset classes.
# =========================

PORTFOLIO_TO_RISK_ASSET_CLASS: dict[
    str,
    AssetClass,
] = {
    "equity": AssetClass.EQUITIES,
    "equity_fund": AssetClass.EQUITIES,
    "equities": AssetClass.EQUITIES,

    "government_bond": AssetClass.GOVERNMENT_BONDS,
    "government_bonds": AssetClass.GOVERNMENT_BONDS,
    "government_bond_fund": AssetClass.GOVERNMENT_BONDS,

    "cash": AssetClass.CASH,
    "cash_equivalent": AssetClass.CASH,

    "gold": AssetClass.GOLD,
    "physical_gold": AssetClass.GOLD,
    "gold_fund": AssetClass.GOLD,

    "commodity": AssetClass.COMMODITIES,
    "commodities": AssetClass.COMMODITIES,
    "commodity_fund": AssetClass.COMMODITIES,
}


# =========================
# Asset-Class Name Normalisation
# Allows either Enum or string keys from the Portfolio risk tools.
# =========================

def _asset_class_name(
    asset_class: object,
) -> str:

    value = getattr(
        asset_class,
        "value",
        asset_class,
    )

    return str(
        value
    ).strip().lower()


# =========================
# Risk Capital Weights
# Aggregates portfolio capital into the asset classes supported by the risk engine.
# =========================

def build_risk_capital_weights(
    portfolio: Portfolio,
) -> dict[
    AssetClass,
    Decimal,
]:

    raw_weights = calculate_asset_class_weights(
        portfolio
    ) # Reuse the existing deterministic portfolio-weight calculation.

    if not raw_weights:
        raise ValueError(
            "Portfolio does not contain enough valued holdings "
            "to calculate risk capital weights."
        )

    broad_weights: dict[
        AssetClass,
        Decimal,
    ] = {}

    for portfolio_asset_class, raw_weight in raw_weights.items():

        asset_class_name = _asset_class_name(
            portfolio_asset_class
        )

        risk_asset_class = PORTFOLIO_TO_RISK_ASSET_CLASS.get(
            asset_class_name
        )

        if risk_asset_class is None:
            raise ValueError(
                (
                    "Portfolio asset class "
                    f"'{asset_class_name}' is not yet supported "
                    "by the historical proxy risk engine."
                )
            )
            # Fail closed rather than pretending an unsupported
            # holding belongs to a different economic asset class.

        broad_weights[risk_asset_class] = (
            broad_weights.get(
                risk_asset_class,
                Decimal("0"),
            )
            + Decimal(
                str(raw_weight)
            )
        )
        # Multiple holdings such as equity + equity_fund collapse
        # into one broad EQUITIES risk exposure.

    total_weight = sum(
        broad_weights.values(),
        Decimal("0"),
    )

    tolerance = Decimal(
        "0.000001"
    )

    if abs(
        total_weight - Decimal("100")
    ) <= tolerance:

        broad_weights = {
            asset_class: weight / Decimal("100")
            for asset_class, weight in broad_weights.items()
        }
        # Support an existing risk tool returning percentage weights.

    elif abs(
        total_weight - Decimal("1")
    ) > tolerance:

        raise ValueError(
            (
                "Portfolio asset-class weights must sum to "
                f"1 or 100, received {total_weight}."
            )
        )
        # Never silently normalise malformed portfolio mathematics.

    return broad_weights
