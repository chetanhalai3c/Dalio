from decimal import Decimal # Precise portfolio and allocation weights.
from types import SimpleNamespace # Lightweight fake historical-series objects.

from backend.orchestrator import (
    run_allocation_guardrail,
    run_allocation_specialist,
    run_cio_workflow, # Executes the CIO-selected workflow in dependency-safe order.
    run_portfolio_risk_data,
    run_portfolio_specialist,
    run_risk_specialist,
)
from models.allocation import (
    AllocationBasis,
    AllocationTarget,
    ProposedAllocation,
)
from models.market import AssetClass
from tools.portfolio_risk_adapter import (
    build_risk_capital_weights,
)


# =========================
# Portfolio → Risk Adapter
# Proves detailed portfolio classes collapse into broad risk-engine exposures.
# =========================

def test_build_risk_capital_weights_maps_equity_classes(
    monkeypatch,
):

    monkeypatch.setattr(
        "tools.portfolio_risk_adapter.calculate_asset_class_weights",
        lambda portfolio: {
            "equity": Decimal("25"),
            "equity_fund": Decimal("75"),
        },
    )

    result = build_risk_capital_weights(
        object()
    )

    assert result == {
        AssetClass.EQUITIES: Decimal("1")
    }
    # 25% individual equity + 75% equity fund becomes
    # one 100% broad EQUITIES exposure for risk modelling.


# =========================
# Portfolio Specialist Orchestration
# Proves the orchestrator delegates portfolio analysis to the existing agent.
# =========================

def test_run_portfolio_specialist(
    monkeypatch,
):

    fake_llm = object()

    monkeypatch.setattr(
        "backend.orchestrator.specialist_llm",
        fake_llm,
    )

    def fake_portfolio_agent(
        state,
        llm,
    ):
        assert llm is fake_llm
        assert state["user_query"] == "Analyse my portfolio."

        return {
            "portfolio_results": "portfolio analysis"
        }

    monkeypatch.setattr(
        "backend.orchestrator.portfolio_agent",
        fake_portfolio_agent,
    )

    result = run_portfolio_specialist(
        {
            "user_query": "Analyse my portfolio."
        }
    )

    assert result == {
        "portfolio_results": "portfolio analysis"
    }


# =========================
# Portfolio Risk Data Orchestration
# Proves capital weights and relevant historical proxies reach the risk builder.
# =========================

def test_run_portfolio_risk_data(
    monkeypatch,
):

    portfolio = object()

    capital_weights = {
        AssetClass.EQUITIES: Decimal("0.60"),
        AssetClass.GOVERNMENT_BONDS: Decimal("0.40"),
    }

    equity_series = SimpleNamespace(
        asset_class=AssetClass.EQUITIES
    )

    bond_series = SimpleNamespace(
        asset_class=AssetClass.GOVERNMENT_BONDS
    )

    gold_series = SimpleNamespace(
        asset_class=AssetClass.GOLD
    )

    fake_snapshot = object()

    monkeypatch.setattr(
        "backend.orchestrator.build_risk_capital_weights",
        lambda supplied_portfolio: capital_weights,
    )

    monkeypatch.setattr(
        "backend.orchestrator.build_traditional_risk_proxy_universe",
        lambda: [
            equity_series,
            bond_series,
            gold_series,
        ],
    )

    def fake_build_portfolio_risk_snapshot(
        *,
        capital_weights,
        series_list,
    ):

        assert capital_weights == {
            AssetClass.EQUITIES: Decimal("0.60"),
            AssetClass.GOVERNMENT_BONDS: Decimal("0.40"),
        }

        assert series_list == [
            equity_series,
            bond_series,
        ]
        # GOLD must be filtered because the investor has no gold exposure.

        return fake_snapshot

    monkeypatch.setattr(
        "backend.orchestrator.build_portfolio_risk_snapshot",
        fake_build_portfolio_risk_snapshot,
    )

    result = run_portfolio_risk_data(
        {
            "portfolio": portfolio
        }
    )

    assert result == {
        "portfolio_risk_snapshot": fake_snapshot
    }


# =========================
# Risk Specialist Orchestration
# Proves the existing Risk Agent is called through the orchestrator.
# =========================

def test_run_risk_specialist(
    monkeypatch,
):

    fake_llm = object()

    monkeypatch.setattr(
        "backend.orchestrator.specialist_llm",
        fake_llm,
    )

    def fake_risk_agent(
        state,
        llm,
    ):
        assert llm is fake_llm
        assert state["portfolio_risk_snapshot"] == "risk snapshot"

        return {
            "risk_results": "risk analysis"
        }

    monkeypatch.setattr(
        "backend.orchestrator.risk_agent",
        fake_risk_agent,
    )

    result = run_risk_specialist(
        {
            "portfolio_risk_snapshot": "risk snapshot"
        }
    )

    assert result == {
        "risk_results": "risk analysis"
    }


# =========================
# Allocation Specialist Orchestration
# Proves the existing Allocation Agent is called through the orchestrator.
# =========================

def test_run_allocation_specialist(
    monkeypatch,
):

    fake_llm = object()

    monkeypatch.setattr(
        "backend.orchestrator.specialist_llm",
        fake_llm,
    )

    fake_proposal = ProposedAllocation(
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

    def fake_allocation_agent(
        state,
        llm,
    ):
        assert llm is fake_llm
        assert state["risk_results"] == "risk analysis"

        return {
            "proposed_allocation": fake_proposal
        }

    monkeypatch.setattr(
        "backend.orchestrator.allocation_agent",
        fake_allocation_agent,
    )

    result = run_allocation_specialist(
        {
            "risk_results": "risk analysis"
        }
    )

    assert result == {
        "proposed_allocation": fake_proposal
    }


# =========================
# Allocation Guardrail Orchestration
# Proves a valid structured proposal passes through the deterministic guardrail.
# =========================

def test_run_allocation_guardrail():

    proposal = ProposedAllocation(
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

    result = run_allocation_guardrail(
        {
            "proposed_allocation": proposal
        }
    )

    assert result[
        "allocation_guardrail_allowed"
    ] is True

    assert result[
        "allocation_guardrail_reason"
    ] == ""


# =========================
# Missing Allocation
# Proves the allocation safety boundary fails closed when no proposal exists.
# =========================

def test_run_allocation_guardrail_without_proposal():

    result = run_allocation_guardrail(
        {}
    )

    assert result[
        "allocation_guardrail_allowed"
    ] is False

    assert result[
        "allocation_guardrail_reason"
    ] == (
        "No proposed allocation was available for validation."
    )

# =========================
# CIO Allocation Workflow
# Proves allocation automatically expands its required portfolio and risk dependencies.
# =========================

def test_run_cio_workflow_expands_allocation_dependencies(
    monkeypatch,
):

    calls = []

    monkeypatch.setattr(
        "backend.orchestrator.cio_supervisor",
        lambda state: {
            "guardrail_allowed": True,
            "selected_agents": [
                "allocation_agent"
            ],
            "messages": [],
        },
    )
    # Simulate the CIO selecting only Allocation Agent.

    def fake_portfolio_specialist(
        state,
    ):
        calls.append(
            "portfolio"
        )

        return {
            "portfolio_results": "portfolio analysis"
        }

    def fake_portfolio_risk_data(
        state,
    ):
        calls.append(
            "portfolio_risk"
        )

        return {
            "portfolio_risk_snapshot": "risk snapshot"
        }

    def fake_risk_specialist(
        state,
    ):
        calls.append(
            "risk"
        )

        assert (
            state["portfolio_risk_snapshot"]
            == "risk snapshot"
        )

        return {
            "risk_results": "risk analysis"
        }

    def fake_allocation_specialist(
        state,
    ):
        calls.append(
            "allocation"
        )

        assert (
            state["risk_results"]
            == "risk analysis"
        )

        return {
            "proposed_allocation": "proposal"
        }

    def fake_allocation_guardrail(
        state,
    ):
        calls.append(
            "allocation_guardrail"
        )

        assert (
            state["proposed_allocation"]
            == "proposal"
        )

        return {
            "allocation_guardrail_allowed": True,
            "allocation_guardrail_reason": "",
        }

    monkeypatch.setattr(
        "backend.orchestrator.run_portfolio_specialist",
        fake_portfolio_specialist,
    )

    monkeypatch.setattr(
        "backend.orchestrator.run_portfolio_risk_data",
        fake_portfolio_risk_data,
    )

    monkeypatch.setattr(
        "backend.orchestrator.run_risk_specialist",
        fake_risk_specialist,
    )

    monkeypatch.setattr(
        "backend.orchestrator.run_allocation_specialist",
        fake_allocation_specialist,
    )

    monkeypatch.setattr(
        "backend.orchestrator.run_allocation_guardrail",
        fake_allocation_guardrail,
    )

    result = run_cio_workflow(
        {
            "user_query": "How should I allocate my portfolio?"
        }
    )

    assert calls == [
        "portfolio",
        "portfolio_risk",
        "risk",
        "allocation",
        "allocation_guardrail",
    ]
    # Allocation cannot run before its portfolio and risk dependencies.

    assert (
        result["portfolio_results"]
        == "portfolio analysis"
    )

    assert (
        result["portfolio_risk_snapshot"]
        == "risk snapshot"
    )

    assert (
        result["risk_results"]
        == "risk analysis"
    )

    assert (
        result["proposed_allocation"]
        == "proposal"
    )

    assert (
        result["allocation_guardrail_allowed"]
        is True
    )


# =========================
# CIO Input Guardrail Stop
# Proves blocked requests never reach specialist agents.
# =========================

def test_run_cio_workflow_stops_when_input_guardrail_blocks(
    monkeypatch,
):

    monkeypatch.setattr(
        "backend.orchestrator.cio_supervisor",
        lambda state: {
            "guardrail_allowed": False,
            "guardrail_reason": "Request blocked.",
            "selected_agents": [],
            "final_response": "Request blocked.",
            "messages": [],
        },
    )

    def specialist_should_not_run(
        state,
    ):
        raise AssertionError(
            "Specialist should not run after input guardrail rejection."
        )

    monkeypatch.setattr(
        "backend.orchestrator.run_portfolio_specialist",
        specialist_should_not_run,
    )

    result = run_cio_workflow(
        {
            "user_query": "Blocked request"
        }
    )

    assert result[
        "guardrail_allowed"
    ] is False

    assert result[
        "final_response"
    ] == "Request blocked."


# =========================
# CIO Message Preservation
# Proves node updates do not overwrite existing workflow history.
# =========================

def test_run_cio_workflow_preserves_messages(
    monkeypatch,
):

    monkeypatch.setattr(
        "backend.orchestrator.cio_supervisor",
        lambda state: {
            "guardrail_allowed": True,
            "selected_agents": [],
            "messages": [
                "supervisor message"
            ],
        },
    )

    result = run_cio_workflow(
        {
            "user_query": "Explain my portfolio.",
            "messages": [
                "existing message"
            ],
        }
    )

    assert result[
        "messages"
    ] == [
        "existing message",
        "supervisor message",
    ]