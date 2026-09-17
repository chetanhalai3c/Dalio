from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalFrequency,
)


# =========================
# Strict Base Model
# Rejects unexpected risk data.
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


# =========================
# Risk Methodology
# Makes clear how the risk evidence was produced.
# =========================

class RiskMethodology(str, Enum):
    HISTORICAL_PROXY = "historical_proxy"


# =========================
# Asset Risk Metrics
# Deterministic risk evidence for ONE economic exposure.
# =========================

class AssetRiskMetrics(StrictBaseModel):
    asset_class: AssetClass

    proxy_symbol: str
    proxy_name: str

    capital_weight: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("1"),
    )

    period_volatility: Decimal = Field(
        ge=Decimal("0")
    )

    marginal_risk_contribution: Decimal

    component_risk_contribution: Decimal

    relative_risk_contribution: Decimal


# =========================
# Pairwise Risk Relationship
# Stores deterministic covariance and correlation between two exposures.
# =========================

class PairwiseRiskRelationship(StrictBaseModel):
    asset_class_a: AssetClass
    asset_class_b: AssetClass

    covariance: Decimal

    correlation: Decimal = Field(
        ge=Decimal("-1"),
        le=Decimal("1"),
    )

    @model_validator(mode="after")
    def validate_pair(
        self,
    ) -> "PairwiseRiskRelationship":

        if (
            self.asset_class_a
            == self.asset_class_b
        ):
            raise ValueError(
                "Pairwise risk relationship requires two different asset classes."
            )

        return self


# =========================
# Portfolio Risk Snapshot
# One trusted package of deterministic portfolio-risk evidence.
# =========================

class PortfolioRiskSnapshot(StrictBaseModel):
    as_of_date: date

    methodology: RiskMethodology = (
        RiskMethodology.HISTORICAL_PROXY
    )

    currency: str

    frequency: HistoricalFrequency

    observation_start_date: date
    observation_end_date: date

    aligned_return_observation_count: int = Field(
        ge=2
    )

    portfolio_period_volatility: Decimal = Field(
        gt=Decimal("0")
    )

    asset_metrics: list[AssetRiskMetrics] = Field(
        min_length=1
    )

    pairwise_relationships: list[
        PairwiseRiskRelationship
    ] = Field(
        default_factory=list
    )

    limitations: list[str] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_snapshot(
        self,
    ) -> "PortfolioRiskSnapshot":

        tolerance = Decimal("0.000001")

        if (
            self.observation_start_date
            >= self.observation_end_date
        ):
            raise ValueError(
                "Risk observation start date must be before end date."
            )

        asset_classes = [
            metric.asset_class
            for metric in self.asset_metrics
        ]

        if len(
            asset_classes
        ) != len(
            set(asset_classes)
        ):
            raise ValueError(
                "Portfolio risk snapshot cannot contain duplicate asset classes."
            )

        capital_weight_total = sum(
            (
                metric.capital_weight
                for metric in self.asset_metrics
            ),
            Decimal("0"),
        )

        if abs(
            capital_weight_total
            - Decimal("1")
        ) > tolerance:
            raise ValueError(
                "Capital weights must sum to 1."
            )

        for metric in self.asset_metrics:

            expected_component = (
                metric.capital_weight
                * metric.marginal_risk_contribution
            )

            if abs(
                expected_component
                - metric.component_risk_contribution
            ) > tolerance:
                raise ValueError(
                    "Component risk contribution must equal "
                    "capital weight multiplied by marginal risk contribution."
                )

        component_total = sum(
            (
                metric.component_risk_contribution
                for metric in self.asset_metrics
            ),
            Decimal("0"),
        )

        if abs(
            component_total
            - self.portfolio_period_volatility
        ) > tolerance:
            raise ValueError(
                "Component risk contributions must reconcile "
                "to portfolio volatility."
            )

        relative_total = sum(
            (
                metric.relative_risk_contribution
                for metric in self.asset_metrics
            ),
            Decimal("0"),
        )

        if abs(
            relative_total
            - Decimal("1")
        ) > tolerance:
            raise ValueError(
                "Relative risk contributions must sum to 1."
            )

        known_asset_classes = set(
            asset_classes
        )

        seen_pairs = set()

        for relationship in self.pairwise_relationships:

            if (
                relationship.asset_class_a
                not in known_asset_classes
                or relationship.asset_class_b
                not in known_asset_classes
            ):
                raise ValueError(
                    "Pairwise relationship references an asset "
                    "not present in the risk snapshot."
                )

            pair = tuple(
                sorted(
                    (
                        relationship.asset_class_a.value,
                        relationship.asset_class_b.value,
                    )
                )
            )

            if pair in seen_pairs:
                raise ValueError(
                    "Duplicate pairwise risk relationship."
                )

            seen_pairs.add(
                pair
            )

        return self