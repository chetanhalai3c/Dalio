from typing import Any # Supports injectable LangGraph checkpointers.

from langgraph.graph import (
    END, # Marks normal workflow completion.
    START, # Marks the graph entry point.
    StateGraph, # Builds the stateful finance workflow.
)
from langgraph.types import Command # Resumes an interrupted workflow.

from backend.hitl import human_review_node # Pauses for approve / modify / reject.
from backend.orchestrator import run_cio_workflow # Runs the full analytical pipeline.
from backend.state import InvestorState # Shared workflow state.
from models.hitl import ReviewDecision # Canonical human-review decisions.


# =========================
# Route After CIO
# Sends allocation proposals to HITL; other requests can finish normally.
# =========================

def route_after_cio(
    state: InvestorState,
) -> str:

    if state.get(
        "approval_request"
    ):
        return "human_review"

    return "end"


# =========================
# Build Finance Graph
# Creates the interruptible workflow using the supplied checkpointer.
# =========================

def build_finance_graph(
    checkpointer: Any,
):

    graph = StateGraph(
        InvestorState
    )

    graph.add_node(
        "cio_workflow",
        run_cio_workflow,
    )

    graph.add_node(
        "human_review",
        human_review_node,
    )

    graph.add_edge(
        START,
        "cio_workflow",
    )

    graph.add_conditional_edges(
        "cio_workflow",
        route_after_cio,
        {
            "human_review": "human_review",
            "end": END,
        },
    )

    graph.add_edge(
        "human_review",
        END,
    )

    return graph.compile(
        checkpointer=checkpointer
    )


# =========================
# Start Finance Workflow
# Starts or continues a stateful workflow thread.
# =========================

def run_finance_workflow(
    graph,
    state: InvestorState,
    thread_id: str,
):

    if not thread_id:
        raise ValueError(
            "thread_id is required."
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return graph.invoke(
        state,
        config=config,
    )


# =========================
# Resume Finance Workflow
# Continues the same paused thread after human review.
# =========================

def resume_finance_workflow(
    graph,
    thread_id: str,
    decision: ReviewDecision,
    feedback: str = "",
):

    if not thread_id:
        raise ValueError(
            "thread_id is required to resume the workflow."
        )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    return graph.invoke(
        Command(
            resume={
                "decision": decision.value,
                "feedback": feedback.strip(),
            }
        ),
        config=config,
    )