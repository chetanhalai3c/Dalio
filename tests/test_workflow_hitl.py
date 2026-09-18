from decimal import Decimal # Precise allocation percentages.

from langgraph.checkpoint.memory import InMemorySaver # Stores paused graph state during the test.

from backend.workflow import (
    build_finance_graph, # Builds the interruptible LangGraph workflow.
    resume_finance_workflow, # Resumes the exact same paused thread.
    run_finance_workflow, # Starts the workflow.
)
from models.allocation import (
    AllocationBasis,
    AllocationTarget,
    ProposedAllocation,
)
from models.hitl import ReviewDecision # Canonical approve / modify / reject decision.
from models.market import AssetClass


# =========================
# Test Allocation
# Provides a valid proposal for the real HITL graph.
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
# Real LangGraph HITL
# Proves interrupt → pause → Command(resume) → approved workflow.
# =========================

def test_finance_workflow_pauses_and_resumes_after_approval(
    monkeypatch,
):

    proposal = build_test_proposal()

    def fake_cio_workflow(
        state,
    ):
        return {
            **state,
            "guardrail_allowed": True,
            "proposed_allocation": proposal,
            "allocation_guardrail_allowed": True,
            "allocation_guardrail_reason": "",
            "approval_request": "Please review this allocation.",
        }
        # Skip live agents in this test and enter the graph
        # at the exact state required for HITL.

    monkeypatch.setattr(
        "backend.workflow.run_cio_workflow",
        fake_cio_workflow,
    )

    checkpointer = InMemorySaver()

    graph = build_finance_graph(
        checkpointer
    )

    thread_id = "allocation-hitl-test"

    paused_result = run_finance_workflow(
        graph,
        {
            "user_query": "How should I allocate my portfolio?"
        },
        thread_id,
    )

    assert "__interrupt__" in paused_result
    # The graph did not finish — it paused for human review.

    resumed_result = resume_finance_workflow(
        graph,
        thread_id,
        ReviewDecision.APPROVE,
    )

    assert (
        resumed_result["human_review"].decision
        == ReviewDecision.APPROVE
    )
    # The structured HumanReview records the investor's decision.

    assert resumed_result["approved"] is True
    # Approval is now explicit workflow state.

    assert resumed_result["human_feedback"] == ""
    # Approval does not require modification feedback.
    