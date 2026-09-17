from decimal import Decimal # Precise decimal maths for financial weights and risk values.
from itertools import combinations # Generates each unique pair of assets once.

from models.market import AssetClass # Canonical economic asset classes used across the system.
from models.portfolio_risk import (
    AssetRiskMetrics, # Stores deterministic risk metrics for one asset class.
    PairwiseRiskRelationship, # Stores covariance/correlation between two asset classes.
    PortfolioRiskSnapshot, # Final trusted package consumed by the Risk and Allocation Agents.
)
from models.risk_market_data import (
    HistoricalAssetSeries, # Validated historical proxy-price series for one asset class.
)
from tools.risk_data_tools import (
    align_historical_prices, # Forces asset histories onto the same dates/frequency/currency.
)
from tools.risk_metrics import (
    calculate_component_risk_contributions, # Amount of portfolio volatility caused by each asset.
    calculate_marginal_risk_contributions, # Sensitivity of portfolio risk to each asset.
    calculate_portfolio_volatility, # Calculates total portfolio volatility.
    calculate_relative_risk_contributions, # Converts component risk into each asset's share of total risk.
    calculate_sample_correlation, # Standardised co-movement between two assets.
    calculate_sample_covariance, # Measures whether two assets move together.
    calculate_sample_volatility, # Measures variability of one asset's returns.
    calculate_simple_returns, # Converts historical prices into period-to-period returns.
)


# =========================
# Portfolio Risk Snapshot Builder
# Orchestrates the deterministic risk pipeline and packages its results.
# =========================

def build_portfolio_risk_snapshot(
    capital_weights: dict[
        AssetClass,
        Decimal,
    ], # Current capital allocation by economic asset class.
    series_list: list[
        HistoricalAssetSeries
    ], # Historical proxy series used to measure how those asset classes behaved.
) -> PortfolioRiskSnapshot:

    if not series_list: # Risk maths cannot run without historical evidence.
        raise ValueError(
            "Historical risk series are required."
        )

    series_asset_classes = {
        series.asset_class
        for series in series_list
    } # Identify which asset classes have historical evidence.

    if set(
        capital_weights
    ) != series_asset_classes: # Every weighted asset must have matching historical data.
        raise ValueError(
            "Capital weights and historical risk series "
            "must contain the same asset classes."
        )

    aligned_dates, aligned_prices = (
        align_historical_prices(
            series_list
        )
    ) # Keep only comparable observations from the same dates.

    returns_by_asset = {
        asset_class:
        calculate_simple_returns(
            prices
        )
        for asset_class, prices
        in aligned_prices.items()
    } # Convert aligned prices into synchronized return series.

    weights = {
        asset_class.value:
        weight
        for asset_class, weight
        in capital_weights.items()
    } # Convert Enum keys into the string keys expected by risk_metrics.py.

    portfolio_volatility = (
        calculate_portfolio_volatility(
            weights,
            returns_by_asset,
        )
    ) # Calculate total portfolio risk from weights + asset co-movement.

    marginal_contributions = (
        calculate_marginal_risk_contributions(
            weights,
            returns_by_asset,
        )
    ) # Measure how sensitive portfolio volatility is to each exposure.

    component_contributions = (
        calculate_component_risk_contributions(
            weights,
            returns_by_asset,
        )
    ) # Calculate how much absolute portfolio risk each exposure contributes.

    relative_contributions = (
        calculate_relative_risk_contributions(
            weights,
            returns_by_asset,
        )
    ) # Express each asset's contribution as a share of total portfolio risk.

    series_by_asset = {
        series.asset_class:
        series
        for series in series_list
    } # Create quick lookup from AssetClass → its historical proxy metadata.

    asset_metrics = [] # Will hold the trusted deterministic risk record for each asset class.

    for asset_class in capital_weights:

        asset_key = (
            asset_class.value
        ) # String key used inside returns/risk dictionaries.

        series = series_by_asset[
            asset_class
        ] # Retrieve the proxy metadata for this economic exposure.

        asset_metrics.append(
            AssetRiskMetrics(
                asset_class=asset_class, # Economic exposure being measured.
                proxy_symbol=series.symbol, # Actual proxy used, e.g. SPY.
                proxy_name=series.proxy_name, # Human-readable proxy description.
                capital_weight=capital_weights[
                    asset_class
                ], # Percentage of portfolio capital allocated to this exposure.
                period_volatility=(
                    calculate_sample_volatility(
                        returns_by_asset[
                            asset_key
                        ]
                    )
                ), # Standalone historical volatility of this exposure.
                marginal_risk_contribution=(
                    marginal_contributions[
                        asset_key
                    ]
                ), # Effect on portfolio risk from slightly increasing this exposure.
                component_risk_contribution=(
                    component_contributions[
                        asset_key
                    ]
                ), # Absolute amount of total portfolio volatility attributable to this exposure.
                relative_risk_contribution=(
                    relative_contributions[
                        asset_key
                    ]
                ), # Share of total portfolio risk attributable to this exposure.
            )
        )

    pairwise_relationships = [] # Will hold covariance/correlation for every unique asset pair.

    for series_a, series_b in combinations(
        series_list,
        2,
    ): # Compare each unique pair once: Equity/Bond, Equity/Gold, Bond/Gold, etc.

        key_a = (
            series_a.asset_class.value
        )

        key_b = (
            series_b.asset_class.value
        )

        pairwise_relationships.append(
            PairwiseRiskRelationship(
                asset_class_a=(
                    series_a.asset_class
                ),
                asset_class_b=(
                    series_b.asset_class
                ),
                covariance=(
                    calculate_sample_covariance(
                        returns_by_asset[
                            key_a
                        ],
                        returns_by_asset[
                            key_b
                        ],
                    )
                ), # Raw statistical co-movement between the two exposures.
                correlation=(
                    calculate_sample_correlation(
                        returns_by_asset[
                            key_a
                        ],
                        returns_by_asset[
                            key_b
                        ],
                    )
                ), # Standardised -1 to +1 measure of how the exposures move together.
            )
        )

    currency = (
        series_list[0].currency
    ) # Alignment layer already guarantees all series use the same currency.

    if currency is None: # Trusted risk evidence requires an explicit common currency.
        raise ValueError(
            "Historical risk series require an explicit currency."
        )

    return PortfolioRiskSnapshot(
        as_of_date=aligned_dates[-1], # Most recent common observation date.
        currency=currency, # Common currency used across all historical proxies.
        frequency=series_list[
            0
        ].frequency, # Common frequency already enforced by the alignment layer.
        observation_start_date=(
            aligned_dates[0]
        ), # Beginning of the common historical measurement window.
        observation_end_date=(
            aligned_dates[-1]
        ), # End of the common historical measurement window.
        aligned_return_observation_count=(
            len(aligned_dates) - 1
        ), # N aligned prices produce N-1 return observations.
        portfolio_period_volatility=(
            portfolio_volatility
        ), # Deterministic total portfolio volatility.
        asset_metrics=asset_metrics, # Per-asset volatility and risk-contribution evidence.
        pairwise_relationships=(
            pairwise_relationships
        ), # Covariance/correlation evidence between exposures.
        limitations=[
            (
                "Historical proxy behaviour does not "
                "guarantee future behaviour."
            ),
            (
                "Proxy instruments are analytical "
                "representations of broader asset classes."
            ),
        ], # Explicit limitations travel with the risk evidence.
    )