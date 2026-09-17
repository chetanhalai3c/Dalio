from decimal import Decimal # Precise allocation percentages and policy limits.

import pytest # Lets us test invalid guardrail configuration.

from backend.guardrails.allocation_guardrail import (
    evaluate_allocation_guardrail, # Deterministically checks allocation-policy rules.
)
from models.allocation import (
    AllocationBasis, # Identifies the type of allocation proposal.
    AllocationTarget, # Represents one target asset-class weight.
    ProposedAllocation, # Validated allocation produced by the Allocation Agent.
)
from models.market import AssetClass # Canonical economic asset classes.


# =========================
# Test Proposal
# Provides one valid allocation used across guardrail scenarios.
# =========================

def build_test_proposal() -> ProposedAllocation:

    return ProposedAllocation(
        basis=AllocationBasis.EDUCATIONAL_BASELINE,
        targets=[
            AllocationTarget(
                asset_class=AssetClass.EQUITIES,
                target_weight_pct=Decimal("60"),
                rationale="Long-term growth exposure.",
            ),
            AllocationTarget(
                asset_class=AssetClass.GOVERNMENT_BONDS,
                target_weight_pct=Decimal("40"),
                rationale="Defensive exposure.",
            ),
        ],
        assumptions=[],
        uncertainties=[],
    )


# =========================
# Scenario 1 — No Configured Limits
# Proves the guardrail does not invent allocation policy.
# =========================

def test_allocation_guardrail_passes_without_configured_limits():

    proposal = build_test_proposal()

    result = evaluate_allocation_guardrail(
        proposal
    )

    assert result.passed is True

    assert result.violations == ()
    # No explicit policy exists, so the guardrail must not invent one.


# =========================
# Scenario 2 — Proposal Within Explicit Limit
# Proves an explicitly configured ceiling is enforced correctly.
# =========================

def test_allocation_guardrail_passes_within_configured_limit():

    proposal = build_test_proposal()

    result = evaluate_allocation_guardrail(
        proposal,
        max_weight_by_asset_class={
            AssetClass.EQUITIES: Decimal("70"),
        },
    )

    assert result.passed is True

    assert result.violations == ()
    # 60% equities is below the explicitly configured 70% ceiling.


# =========================
# Scenario 3 — Proposal Exceeds Explicit Limit
# Proves a policy violation is detected deterministically.
# =========================

def test_allocation_guardrail_rejects_weight_above_configured_limit():

    proposal = build_test_proposal()

    result = evaluate_allocation_guardrail(
        proposal,
        max_weight_by_asset_class={
            AssetClass.EQUITIES: Decimal("50"),
        },
    )

    assert result.passed is False

    assert len(
        result.violations
    ) == 1

    assert (
        "equities"
        in result.violations[0]
    )

    assert (
        "60"
        in result.violations[0]
    )

    assert (
        "50"
        in result.violations[0]
    )
    # The failure explains the actual target and the configured ceiling.


# =========================
# Scenario 4 — Invalid Guardrail Configuration
# Proves impossible policy limits fail before proposal evaluation.
# =========================

def test_allocation_guardrail_rejects_invalid_configured_limit():

    proposal = build_test_proposal()

    with pytest.raises(
        ValueError
    ):
        evaluate_allocation_guardrail(
            proposal,
            max_weight_by_asset_class={
                AssetClass.EQUITIES: Decimal("110"),
            },
        )
    # A product policy cannot define an asset-class maximum above 100%.