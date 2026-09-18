from decimal import Decimal # Precise allocation percentages.

import pytest # Tests invalid HITL decisions.
from pydantic import ValidationError # Expected when structured human review is invalid.

from backend.hitl import (
    apply_human_review, # Applies approve / modify / reject decisions.
    prepare_allocation_review, # Creates the review request after allocation safety passes.
)
from models.allocation import (
    AllocationBasis,
    AllocationTarget,
    ProposedAllocation,
)
from models.hitl import (
    HumanReview,
    ReviewDecision,
)
from models.market import AssetClass


# =========================
# Test Allocation
# Provides one valid proposal for HITL review.
# =========================

def build_test_proposal() -> ProposedAllocation:

    return ProposedAllocation(
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
    )


# =========================
# Scenario 1 — Prepare Review
# A safe allocation is allowed to reach the investor.
# =========================

def test_prepare_allocation_review():

    result = prepare_allocation_review(
        {
            "proposed_allocation": build_test_proposal(),
            "allocation_guardrail_allowed": True,
        }
    )

    assert result["approval_request"] != ""

    assert len(
        result["messages"]
    ) == 1


# =========================
# Scenario 2 — Guardrail Failure
# Unsafe proposals must never reach human approval.
# =========================

def test_prepare_allocation_review_stops_when_guardrail_fails():

    result = prepare_allocation_review(
        {
            "proposed_allocation": build_test_proposal(),
            "allocation_guardrail_allowed": False,
        }
    )

    assert result == {
        "approval_request": ""
    }


# =========================
# Scenario 3 — Approve
# Human approval becomes explicit structured workflow state.
# =========================

def test_apply_human_review_approve():

    result = apply_human_review(
        {
            "proposed_allocation": build_test_proposal(),
            "allocation_guardrail_allowed": True,
        },
        ReviewDecision.APPROVE,
    )

    assert isinstance(
        result["human_review"],
        HumanReview,
    )

    assert (
        result["human_review"].decision
        == ReviewDecision.APPROVE
    )

    assert result["approved"] is True

    assert result["human_feedback"] == ""


# =========================
# Scenario 4 — Modify
# Modification requires explicit investor feedback.
# =========================

def test_apply_human_review_modify():

    result = apply_human_review(
        {
            "proposed_allocation": build_test_proposal(),
            "allocation_guardrail_allowed": True,
        },
        ReviewDecision.MODIFY,
        "Reduce equity exposure.",
    )

    assert (
        result["human_review"].decision
        == ReviewDecision.MODIFY
    )

    assert result["approved"] is False

    assert (
        result["human_feedback"]
        == "Reduce equity exposure."
    )


# =========================
# Scenario 5 — Modify Without Feedback
# Prevents an ambiguous modification request.
# =========================

def test_modify_requires_feedback():

    with pytest.raises(
        ValidationError
    ):
        apply_human_review(
            {
                "proposed_allocation": build_test_proposal(),
                "allocation_guardrail_allowed": True,
            },
            ReviewDecision.MODIFY,
        )


# =========================
# Scenario 6 — Reject
# Rejection is distinct from modification.
# =========================

def test_apply_human_review_reject():

    result = apply_human_review(
        {
            "proposed_allocation": build_test_proposal(),
            "allocation_guardrail_allowed": True,
        },
        ReviewDecision.REJECT,
        "I do not want to proceed with this allocation.",
    )

    assert (
        result["human_review"].decision
        == ReviewDecision.REJECT
    )

    assert result["approved"] is False

    assert (
        result["human_feedback"]
        == "I do not want to proceed with this allocation."
    )