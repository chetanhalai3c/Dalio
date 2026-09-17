from decimal import Decimal
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from models.market import AssetClass


# =========================
# Strict Base Model
# Rejects unexpected fields instead of silently accepting them.
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )


# =========================
# Allocation Basis
# Distinguishes personalised advice from a lower-information baseline.
# =========================

class AllocationBasis(str, Enum):
    PERSONALISED = "personalised"
    EDUCATIONAL_BASELINE = "educational_baseline"


# =========================
# Allocation Target
# Represents ONE desired economic exposure.
# =========================

class AllocationTarget(StrictBaseModel):
    asset_class: AssetClass # Economic exposure, not a specific ETF or ticker.

    target_weight_pct: Decimal = Field(
        ge=Decimal("0"),
        le=Decimal("100"),
    ) # Percentage of the proposed portfolio.

    rationale: str | None = None # Why this exposure has a role in the portfolio.


# =========================
# Proposed Allocation
# Structured output the future Allocation Agent must produce.
# =========================

class ProposedAllocation(StrictBaseModel):
    basis: AllocationBasis # Personalised or educational baseline.

    targets: list[AllocationTarget] = Field(
        min_length=1
    ) # Complete set of desired asset-class exposures.

    assumptions: list[str] = Field(
        default_factory=list
    ) # Important assumptions caused by missing or uncertain information.

    uncertainties: list[str] = Field(
        default_factory=list
    ) # Important facts that remain unresolved.

    @model_validator(mode="after")
    def validate_allocation(
        self,
    ) -> "ProposedAllocation":

        asset_classes = [
            target.asset_class
            for target in self.targets
        ]

        if len(
            asset_classes
        ) != len(
            set(asset_classes)
        ):
            raise ValueError(
                "Allocation cannot contain duplicate asset classes."
            )

        total_weight = sum(
            (
                target.target_weight_pct
                for target in self.targets
            ),
            Decimal("0"),
        )

        if total_weight != Decimal("100"):
            raise ValueError(
                "Allocation target weights must sum to 100%."
            )

        return self