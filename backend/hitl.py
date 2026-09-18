from typing import Any # Supports workflow-compatible state update dictionaries.

from langchain_core.messages import AIMessage # Records HITL status in workflow history.
from langgraph.types import interrupt # Pauses LangGraph execution until the investor responds.
from backend.state import InvestorState # Shared workflow state.
from models.hitl import (
    HumanReview, # Validated human-review contract.
    ReviewDecision, # Approve / modify / reject.
)


# =========================
# Prepare Allocation Review
# Creates the human review request only after allocation safety passes.
# =========================

def prepare_allocation_review(
    state: InvestorState,
) -> dict[str, Any]:

    proposal = state.get(
        "proposed_allocation"
    ) # Allocation produced by the Allocation Agent.

    if proposal is None:
        return {
            "approval_request": "",
        }
        # Nothing exists for the investor to review.

    if not state.get(
        "allocation_guardrail_allowed",
        False,
    ):
        return {
            "approval_request": "",
        }
        # A proposal that failed deterministic policy checks must not reach approval.

    approval_request = (
        "Please review the proposed allocation. "
        "You may approve it, request modifications with feedback, "
        "or reject it."
    )

    return {
        "approval_request": approval_request,
        "messages": [
            AIMessage(
                content="Allocation proposal is ready for human review."
            )
        ],
    }


# =========================
# Apply Human Review
# Converts the investor's decision into validated workflow state.
# =========================

def apply_human_review(
    state: InvestorState,
    decision: ReviewDecision,
    feedback: str = "",
) -> dict[str, Any]:

    if not state.get(
        "allocation_guardrail_allowed",
        False,
    ):
        raise ValueError(
            "Human approval cannot be applied before the allocation guardrail passes."
        )

    if state.get(
        "proposed_allocation"
    ) is None:
        raise ValueError(
            "Human approval requires a proposed allocation."
        )

    review = HumanReview(
        decision=decision,
        feedback=feedback.strip(),
    ) # Validate the investor's decision before updating shared state.

    approved = (
        review.decision == ReviewDecision.APPROVE
    )

    return {
        "human_review": review,
        "approved": approved,
        "human_feedback": review.feedback,
        "messages": [
            AIMessage(
                content=(
                    f"Human review completed: "
                    f"{review.decision.value}."
                )
            )
        ],
    }

# =========================
# Human Review Node
# Pauses the LangGraph workflow until the investor approves, modifies or rejects.
# =========================

def human_review_node(
    state: InvestorState,
) -> dict[str, Any]:

    proposal = state.get(
        "proposed_allocation"
    )

    if proposal is None:
        raise ValueError(
            "Human review requires a proposed allocation."
        )

    if not state.get(
        "allocation_guardrail_allowed",
        False,
    ):
        raise ValueError(
            "Human review cannot begin before the allocation guardrail passes."
        )

    review = interrupt(
        {
            "question": "What would you like to do with this proposed allocation?",
            "approval_request": state.get(
                "approval_request",
                "",
            ),
            "proposed_allocation": proposal.model_dump(
                mode="json"
            ),
            "expected_response": {
                "decision": "approve | modify | reject",
                "feedback": "Required when requesting modification.",
            },
        }
    )
    # Do not wrap interrupt() in try/except.
    # LangGraph uses the interrupt internally to pause execution.

    decision = ReviewDecision(
        str(
            review.get(
                "decision",
                "",
            )
        ).strip().lower()
    )

    feedback = str(
        review.get(
            "feedback",
            "",
        )
    ).strip()

    return apply_human_review(
        state,
        decision,
        feedback,
    )