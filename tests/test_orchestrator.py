from backend import orchestrator
from models.investor_profile import InvestorProfile


# =========================
# Scenario 1 — Blocked request
# =========================

def test_cio_blocks_disallowed_request(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "evaluate_input_guardrail",
        lambda query, llm: {
            "allowed": False,
            "reason": "Request is outside the financial domain.",
        },
    )

    result = orchestrator.cio_supervisor(
        {
            "user_query": "Write me a recipe for pizza.",
            "llm_calls": 0,
        }
    )

    assert result["guardrail_allowed"] is False
    assert result["selected_agents"] == []


# =========================
# Scenario 2 — Portfolio analysis routing
# =========================

def test_cio_routes_portfolio_analysis(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "evaluate_input_guardrail",
        lambda query, llm: {
            "allowed": True,
            "reason": "",
        },
    )

    monkeypatch.setattr(
        orchestrator,
        "_llm_text",
        lambda system_prompt, user_prompt: """
        {
          "selected_agents": [
            "portfolio_agent",
            "risk_agent"
          ],
          "reasoning": "Portfolio concentration requires portfolio and risk analysis."
        }
        """,
    )

    result = orchestrator.cio_supervisor(
        {
            "user_query": "Is my portfolio too concentrated?",
            "llm_calls": 0,
        }
    )

    assert result["guardrail_allowed"] is True
    assert result["selected_agents"] == [
        "portfolio_agent",
        "risk_agent",
    ]


# =========================
# Scenario 3 — Allocation request
# =========================

def test_cio_routes_allocation_request(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "evaluate_input_guardrail",
        lambda query, llm: {
            "allowed": True,
            "reason": "",
        },
    )

    monkeypatch.setattr(
        orchestrator,
        "_llm_text",
        lambda system_prompt, user_prompt: """
        {
          "selected_agents": [
            "macro_agent",
            "market_agent",
            "portfolio_agent",
            "risk_agent",
            "allocation_agent"
          ],
          "reasoning": "The investor is asking for an allocation decision."
        }
        """,
    )

    result = orchestrator.cio_supervisor(
        {
            "user_query": "Where should I allocate £20,000?",
            "llm_calls": 0,
        }
    )

    assert "allocation_agent" in result["selected_agents"]


# =========================
# Scenario 4 — Unknown agents filtered out
# =========================

def test_cio_filters_unknown_agents(monkeypatch):
    monkeypatch.setattr(
        orchestrator,
        "evaluate_input_guardrail",
        lambda query, llm: {
            "allowed": True,
            "reason": "",
        },
    )

    monkeypatch.setattr(
        orchestrator,
        "_llm_text",
        lambda system_prompt, user_prompt: """
        {
          "selected_agents": [
            "portfolio_agent",
            "fake_agent"
          ],
          "reasoning": "Testing routing validation."
        }
        """,
    )

    result = orchestrator.cio_supervisor(
        {
            "user_query": "Analyse my portfolio.",
            "llm_calls": 0,
        }
    )

    assert result["selected_agents"] == [
        "portfolio_agent"
    ]

# =========================
# Macro Specialist Routing
# =========================

def test_run_macro_specialist(
    monkeypatch,
):
    fake_llm = object()

    monkeypatch.setattr(
        orchestrator,
        "specialist_llm",
        fake_llm,
    )

    captured = {}

    def fake_macro_agent(
        state,
        llm,
    ):
        captured["state"] = state
        captured["llm"] = llm

        return {
            "macro_results": "Macro analysis complete."
        }

    monkeypatch.setattr(
        orchestrator,
        "macro_agent",
        fake_macro_agent,
    )

    state = {
        "user_query": "What is happening in the economy?",
        "llm_calls": 0,
    }

    result = orchestrator.run_macro_specialist(
        state
    )

    assert captured["state"] == state
    assert captured["llm"] is fake_llm
    assert result["macro_results"] == (
        "Macro analysis complete."
    )


# =========================
# Macro Data Routing
# =========================

def test_run_macro_data(
    monkeypatch,
):
    fake_snapshot = object()
    captured = {}

    def fake_build_macro_snapshot_for_country(
        country_code,
    ):
        captured["country_code"] = country_code
        return fake_snapshot

    monkeypatch.setattr(
        orchestrator,
        "build_macro_snapshot_for_country",
        fake_build_macro_snapshot_for_country,
    )

    investor_profile = InvestorProfile(
        jurisdiction_currency={
            "country_of_residence": "GB",
        }
    )

    result = orchestrator.run_macro_data(
        {
            "investor_profile": investor_profile,
        }
    )

    assert captured["country_code"] == "GB"
    assert result["macro_snapshot"] is fake_snapshot

# =========================
# Macro Workflow
# =========================

def test_run_macro_workflow(
    monkeypatch,
):
    fake_snapshot = object()
    captured = {}

    def fake_run_macro_data(
        state,
    ):
        return {
            "macro_snapshot": fake_snapshot
        }

    def fake_run_macro_specialist(
        state,
    ):
        captured["state"] = state

        return {
            "macro_results": "Macro analysis complete."
        }

    monkeypatch.setattr(
        orchestrator,
        "run_macro_data",
        fake_run_macro_data,
    )

    monkeypatch.setattr(
        orchestrator,
        "run_macro_specialist",
        fake_run_macro_specialist,
    )

    state = {
        "user_query": "What is happening in the economy?",
        "llm_calls": 0,
    }

    result = orchestrator.run_macro_workflow(
        state
    )

    assert captured["state"]["macro_snapshot"] is fake_snapshot

    assert result["macro_snapshot"] is fake_snapshot

    assert result["macro_results"] == (
        "Macro analysis complete."
    )