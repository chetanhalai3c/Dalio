from backend import orchestrator


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