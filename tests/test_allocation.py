from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.allocation import (
    AllocationBasis,
    AllocationTarget,
    ProposedAllocation,
)
from models.market import AssetClass


# =========================
# Valid Personalised Allocation
# Complete asset-class allocation should be accepted.
# =========================

def test_personalised_allocation():

    allocation = ProposedAllocation(
        basis=AllocationBasis.PERSONALISED,
        targets=[
            AllocationTarget(
                asset_class=AssetClass.EQUITIES,
                target_weight_pct=Decimal("35"),
                rationale="Long-term growth exposure.",
            ),
            AllocationTarget(
                asset_class=AssetClass.GOVERNMENT_BONDS,
                target_weight_pct=Decimal("35"),
                rationale="Defensive and income exposure.",
            ),
            AllocationTarget(
                asset_class=AssetClass.GOLD,
                target_weight_pct=Decimal("15"),
                rationale="Diversifying store-of-value exposure.",
            ),
            AllocationTarget(
                asset_class=AssetClass.COMMODITIES,
                target_weight_pct=Decimal("10"),
                rationale="Real-asset diversification.",
            ),
            AllocationTarget(
                asset_class=AssetClass.CASH,
                target_weight_pct=Decimal("5"),
                rationale="Liquidity exposure.",
            ),
        ],
    )

    assert allocation.basis == (
        AllocationBasis.PERSONALISED
    )

    assert len(
        allocation.targets
    ) == 5


# =========================
# Educational Baseline
# Minimal investor information must still support a valid framework.
# =========================

def test_educational_baseline_allocation():

    allocation = ProposedAllocation(
        basis=AllocationBasis.EDUCATIONAL_BASELINE,
        targets=[
            AllocationTarget(
                asset_class=AssetClass.EQUITIES,
                target_weight_pct=Decimal("50"),
            ),
            AllocationTarget(
                asset_class=AssetClass.GOVERNMENT_BONDS,
                target_weight_pct=Decimal("50"),
            ),
        ],
        assumptions=[
            "Investor-specific risk capacity is not established."
        ],
        uncertainties=[
            "Liquidity needs are not established."
        ],
    )

    assert allocation.basis == (
        AllocationBasis.EDUCATIONAL_BASELINE
    )

    assert allocation.assumptions


# =========================
# Weight Validation
# A proposed portfolio must represent the whole 100%.
# =========================

def test_allocation_weights_must_sum_to_100():

    with pytest.raises(
        ValidationError
    ):
        ProposedAllocation(
            basis=AllocationBasis.PERSONALISED,
            targets=[
                AllocationTarget(
                    asset_class=AssetClass.EQUITIES,
                    target_weight_pct=Decimal("60"),
                ),
                AllocationTarget(
                    asset_class=AssetClass.GOVERNMENT_BONDS,
                    target_weight_pct=Decimal("30"),
                ),
            ],
        )


# =========================
# Duplicate Asset Classes
# One economic exposure should appear only once.
# =========================

def test_duplicate_asset_classes_rejected():

    with pytest.raises(
        ValidationError
    ):
        ProposedAllocation(
            basis=AllocationBasis.PERSONALISED,
            targets=[
                AllocationTarget(
                    asset_class=AssetClass.EQUITIES,
                    target_weight_pct=Decimal("50"),
                ),
                AllocationTarget(
                    asset_class=AssetClass.EQUITIES,
                    target_weight_pct=Decimal("50"),
                ),
            ],
        )


# =========================
# Weight Boundaries
# Individual targets must remain between 0% and 100%.
# =========================

def test_invalid_target_weight_rejected():

    with pytest.raises(
        ValidationError
    ):
        AllocationTarget(
            asset_class=AssetClass.EQUITIES,
            target_weight_pct=Decimal("120"),
        )


# =========================
# Unknown Fields
# The allocation contract must not silently accept unexpected data.
# =========================

def test_unknown_allocation_field_rejected():

    with pytest.raises(
        ValidationError
    ):
        ProposedAllocation(
            basis=AllocationBasis.EDUCATIONAL_BASELINE,
            targets=[
                AllocationTarget(
                    asset_class=AssetClass.CASH,
                    target_weight_pct=Decimal("100"),
                ),
            ],
            secret_trade="BUY NOW",
        )
        