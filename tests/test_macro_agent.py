from datetime import date
from decimal import Decimal

from agents.macro_agent import macro_agent
from models.macro import (
    MacroObservation,
    MacroSnapshot,
    TrendDirection,
)


# =========================
# Fake LLM
# =========================

class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self):
        self.messages = None

    def invoke(self, messages):
        self.messages = messages

        return FakeResponse(
            "Macro environment interpreted."
        )


# =========================
# Scenario 1 — Macro Agent Runs
# =========================

def test_macro_agent_runs(
    monkeypatch,
):
    monkeypatch.setattr(
        "agents.macro_agent.retrieve_knowledge",
        lambda **kwargs: "Macro knowledge",
    )

    snapshot = MacroSnapshot(
        geography="United Kingdom",
        geography_code="GB",
        as_of_date=date(2026, 9, 14),
        growth=MacroObservation(
            indicator="Real GDP Growth",
            latest_value=Decimal("0.4"),
            previous_value=Decimal("0.6"),
            unit="percent",
            latest_period="2026-Q2",
            previous_period="2026-Q1",
            direction=TrendDirection.FALLING,
            source="OECD Data Explorer",
        ),
        inflation=MacroObservation(
            indicator="Consumer Price Inflation",
            latest_value=Decimal("3.1"),
            previous_value=Decimal("2.8"),
            unit="percent",
            latest_period="2026-07",
            previous_period="2026-06",
            direction=TrendDirection.RISING,
            source="OECD Data Explorer",
        ),
        policy_rate=MacroObservation(
            indicator="Central Bank Policy Rate",
            latest_value=Decimal("3.75"),
            previous_value=Decimal("3.75"),
            unit="percent",
            latest_period="2026-08",
            previous_period="2026-07",
            direction=TrendDirection.STABLE,
            source="BIS Data Portal",
        ),
    )

    llm = FakeLLM()

    result = macro_agent(
        {
            "user_query": (
                "What is happening in the economy?"
            ),
            "macro_snapshot": snapshot,
            "llm_calls": 0,
        },
        llm,
    )

    assert result["macro_results"] == (
        "Macro environment interpreted."
    )
    assert result["llm_calls"] == 1
    assert result["messages"][0].content == (
        "Macro analysis generated."
    )

    prompt = llm.messages[1].content

    assert "United Kingdom" in prompt
    assert "Real GDP Growth" in prompt
    assert "Consumer Price Inflation" in prompt
    assert "Central Bank Policy Rate" in prompt


# =========================
# Scenario 2 — Missing Macro Snapshot
# =========================

def test_macro_agent_without_snapshot(
    monkeypatch,
):
    monkeypatch.setattr(
        "agents.macro_agent.retrieve_knowledge",
        lambda **kwargs: "Macro knowledge",
    )

    llm = FakeLLM()

    result = macro_agent(
        {
            "user_query": (
                "Explain the macro environment."
            ),
            "llm_calls": 2,
        },
        llm,
    )

    assert result["macro_results"] == (
        "Macro environment interpreted."
    )
    assert result["llm_calls"] == 3