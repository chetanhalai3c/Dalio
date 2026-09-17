from decimal import Decimal # Precise allocation percentages.
import pytest # Lets us prove structurally invalid allocation output is rejected.
from pydantic import ValidationError # Expected error from the ProposedAllocation contract.
from agents.allocation_agent import allocation_agent
from models.allocation import (
    AllocationBasis, # Identifies personalised vs educational-baseline allocation.
    AllocationTarget, # Represents one target economic exposure.
    ProposedAllocation, # Structured allocation contract the agent must return.
)
from models.market import AssetClass # Canonical asset classes used across the system.


# =========================
# Fake Structured LLM
# Simulates structured-output behaviour without making a real model call.
# =========================

class FakeStructuredLLM:

    def __init__(
        self,
    ):
        self.schema = None # Records which structured-output model the agent requested.
        self.messages = None # Records the prompt/messages sent to the fake model.

    def with_structured_output(
        self,
        schema,
    ):
        self.schema = schema # Capture the schema requested by allocation_agent().

        return self # Behave like LangChain's structured-output wrapper.

    def invoke(
        self,
        messages,
    ):
        self.messages = messages # Capture the complete Allocation Agent prompt.

        return ProposedAllocation(
            basis=AllocationBasis.EDUCATIONAL_BASELINE,
            targets=[
                AllocationTarget(
                    asset_class=AssetClass.EQUITIES,
                    target_weight_pct=Decimal("50"),
                    rationale="Long-term growth exposure.",
                ),
                AllocationTarget(
                    asset_class=AssetClass.GOVERNMENT_BONDS,
                    target_weight_pct=Decimal("50"),
                    rationale="Defensive exposure.",
                ),
            ],
            assumptions=[
                "Investor-specific risk capacity is not established."
            ],
            uncertainties=[
                "Liquidity requirements are not established."
            ],
        ) # Return a valid proposal whose weights sum to 100%.


# =========================
# Scenario 1 — Allocation Agent Runs
# Proves trusted evidence can flow through the agent into ProposedAllocation.
# =========================

def test_allocation_agent_runs(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.allocation_agent.retrieve_knowledge",
        lambda **kwargs: (
            "Diversify across economically distinct exposures."
        ),
    ) # Avoid real knowledge retrieval so this test isolates the Allocation Agent.

    fake_llm = FakeStructuredLLM()

    result = allocation_agent(
        {
            "user_query": "How should I allocate my portfolio?",
            "llm_calls": 0,
        },
        fake_llm,
    )

    assert fake_llm.schema is ProposedAllocation
    # Proves the agent explicitly requested our structured allocation contract.

    assert isinstance(
        result["proposed_allocation"],
        ProposedAllocation,
    )
    # Proves loose LLM prose did not enter shared state.

    assert (
        result["proposed_allocation"].basis
        == AllocationBasis.EDUCATIONAL_BASELINE
    )
    # With our fake response, the validated proposal preserves its allocation basis.

    assert sum(
        (
            target.target_weight_pct
            for target
            in result["proposed_allocation"].targets
        ),
        Decimal("0"),
    ) == Decimal("100")
    # Confirms the final structured proposal represents the whole portfolio.

    assert result["llm_calls"] == 1
    # Confirms exactly one Allocation Agent LLM call was recorded.

# =========================
# Scenario 2 — Specialist Evidence Reaches Prompt
# Proves Portfolio, Risk, Macro and Market interpretations reach the Allocation Agent.
# =========================

def test_allocation_agent_receives_specialist_evidence(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.allocation_agent.retrieve_knowledge",
        lambda **kwargs: (
            "Diversify across economically distinct exposures."
        ),
    ) # Keep the test isolated from real knowledge retrieval.

    fake_llm = FakeStructuredLLM()

    result = allocation_agent(
        {
            "user_query": "How should I allocate my portfolio?",
            "portfolio_results": "PORTFOLIO FINDINGS TEST",
            "risk_results": "RISK FINDINGS TEST",
            "macro_results": "MACRO FINDINGS TEST",
            "market_results": "MARKET FINDINGS TEST",
            "llm_calls": 0,
        },
        fake_llm,
    )

    prompt = (
        fake_llm.messages[-1].content
    ) # Capture the complete HumanMessage sent to the Allocation Agent.

    assert (
        "PORTFOLIO FINDINGS TEST"
        in prompt
    ) # Portfolio Agent interpretation reached the Allocation Agent.

    assert (
        "RISK FINDINGS TEST"
        in prompt
    ) # Risk Agent interpretation reached the Allocation Agent.

    assert (
        "MACRO FINDINGS TEST"
        in prompt
    ) # Macro Agent interpretation reached the Allocation Agent.

    assert (
        "MARKET FINDINGS TEST"
        in prompt
    ) # Market Agent interpretation reached the Allocation Agent.

    assert isinstance(
        result["proposed_allocation"],
        ProposedAllocation,
    ) # Specialist evidence still results in a validated allocation object.

# =========================
# Scenario 3 — Deterministic Risk Evidence Reaches Prompt
# Proves the Allocation Agent receives the trusted PortfolioRiskSnapshot directly.
# =========================

def test_allocation_agent_receives_portfolio_risk_snapshot(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.allocation_agent.retrieve_knowledge",
        lambda **kwargs: (
            "Diversify across economically distinct exposures."
        ),
    ) # Keep this test focused on evidence flow.

    class FakeRiskSnapshot:

        def model_dump(
            self,
            mode="json",
        ):
            return {
                "portfolio_period_volatility": "0.12",
                "asset_metrics": [
                    {
                        "asset_class": "equities",
                        "relative_risk_contribution": "0.70",
                    },
                    {
                        "asset_class": "government_bonds",
                        "relative_risk_contribution": "0.30",
                    },
                ],
            }
            # Simulates the trusted deterministic PortfolioRiskSnapshot
            # without rebuilding the full risk model inside this test.

    fake_llm = FakeStructuredLLM()

    result = allocation_agent(
        {
            "user_query": "How should I allocate my portfolio?",
            "portfolio_risk_snapshot": FakeRiskSnapshot(),
            "llm_calls": 0,
        },
        fake_llm,
    )

    prompt = (
        fake_llm.messages[-1].content
    ) # Inspect the actual evidence supplied to the Allocation Agent.

    assert (
        "DETERMINISTIC PORTFOLIO RISK SNAPSHOT:"
        in prompt
    ) # Confirms the trusted risk section exists.

    assert (
        "portfolio_period_volatility"
        in prompt
    ) # Confirms total portfolio volatility reached the Allocation Agent.

    assert (
        "relative_risk_contribution"
        in prompt
    ) # Confirms measured risk allocation reached the Allocation Agent.

    assert (
        "0.70"
        in prompt
    ) # Confirms the deterministic equity risk-contribution value reached the prompt.

    assert isinstance(
        result["proposed_allocation"],
        ProposedAllocation,
    )

# =========================
# Scenario 4 — Invalid Allocation Is Rejected
# Proves malformed LLM output cannot enter shared state.
# =========================

def test_allocation_agent_rejects_invalid_proposal(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.allocation_agent.retrieve_knowledge",
        lambda **kwargs: (
            "Diversify across economically distinct exposures."
        ),
    ) # Keep the test isolated from real knowledge retrieval.

    class InvalidStructuredLLM:

        def with_structured_output(
            self,
            schema,
        ):
            return self # Simulate LangChain's structured-output wrapper.

        def invoke(
            self,
            messages,
        ):
            return {
                "basis": "educational_baseline",
                "targets": [
                    {
                        "asset_class": "equities",
                        "target_weight_pct": "60",
                    },
                    {
                        "asset_class": "government_bonds",
                        "target_weight_pct": "30",
                    },
                ],
                "assumptions": [],
                "uncertainties": [],
            }
            # Invalid proposal: 60% + 30% = only 90%.

    with pytest.raises(
        ValidationError
    ):
        allocation_agent(
            {
                "user_query": "How should I allocate my portfolio?",
                "llm_calls": 0,
            },
            InvalidStructuredLLM(),
        )