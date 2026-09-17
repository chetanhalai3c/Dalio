from datetime import date
from decimal import Decimal

from agents.market_agent import market_agent
from models.market import (
    AssetClass,
    MarketDirection,
    MarketObservation,
    MarketSnapshot,
    MeasurementType,
)


# =========================
# Fake LLM
# Lets us test Market Agent behaviour without calling a real model.
# =========================

class FakeResponse:
    def __init__(
        self,
        content: str,
    ):
        self.content = content


class FakeLLM:
    def __init__(
        self,
    ):
        self.messages = None

    def invoke(
        self,
        messages,
    ):
        self.messages = messages

        return FakeResponse(
            "Market environment interpreted."
        )


# =========================
# Market Agent Runs
# Confirms MarketSnapshot evidence reaches the LLM prompt.
# =========================

def test_market_agent_runs(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.market_agent.retrieve_knowledge",
        lambda **kwargs: "Market knowledge",
    )

    snapshot = MarketSnapshot(
        as_of_date=date(
            2026,
            9,
            16,
        ),
        investor_country="GB",
        base_currency="GBP",
        observations=[
            MarketObservation(
                asset_name="SPDR S&P 500 ETF Trust",
                asset_class=AssetClass.EQUITIES,
                symbol="SPY",
                geography="US",
                measurement_type=MeasurementType.PRICE,
                latest_value=Decimal("754.13"),
                previous_value=Decimal("755.00"),
                unit="price",
                currency="USD",
                latest_period="2026-09-16",
                previous_period="2026-09-15",
                direction=MarketDirection.FALLING,
                source="Alpha Vantage",
            ),
            MarketObservation(
                asset_name="US 10-Year Treasury Yield",
                asset_class=AssetClass.GOVERNMENT_BONDS,
                symbol="US10Y",
                geography="US",
                measurement_type=MeasurementType.YIELD,
                latest_value=Decimal("4.97"),
                previous_value=Decimal("4.96"),
                unit="percent",
                latest_period="2026-09-14",
                previous_period="2026-09-11",
                direction=MarketDirection.RISING,
                source="Alpha Vantage",
            ),
            MarketObservation(
                asset_name="Gold",
                asset_class=AssetClass.GOLD,
                symbol="GOLD",
                geography="GLOBAL",
                measurement_type=MeasurementType.PRICE,
                latest_value=Decimal("4285.38"),
                previous_value=Decimal("4345.90"),
                unit="price",
                currency="USD",
                latest_period="2026-09-15",
                previous_period="2026-09-14",
                direction=MarketDirection.FALLING,
                source="Alpha Vantage",
            ),
        ],
    )

    llm = FakeLLM()

    result = market_agent(
        {
            "user_query": (
                "What are markets doing?"
            ),
            "market_snapshot": snapshot,
            "llm_calls": 0,
        },
        llm,
    )

    assert result["market_results"] == (
        "Market environment interpreted."
    )

    assert result["llm_calls"] == 1

    assert result["messages"][0].content == (
        "Market analysis generated."
    )

    prompt = llm.messages[1].content

    assert "SPDR S&P 500 ETF Trust" in prompt
    assert "US 10-Year Treasury Yield" in prompt
    assert "Gold" in prompt


# =========================
# Missing Market Snapshot
# Market Agent should still run safely when no market evidence is available.
# =========================

def test_market_agent_without_snapshot(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.market_agent.retrieve_knowledge",
        lambda **kwargs: "Market knowledge",
    )

    llm = FakeLLM()

    result = market_agent(
        {
            "user_query": (
                "Explain current markets."
            ),
            "llm_calls": 2,
        },
        llm,
    )

    assert result["market_results"] == (
        "Market environment interpreted."
    )

    assert result["llm_calls"] == 3

# =========================
# Unsupported Market Analysis
# Unsafe LLM claims should be replaced by the deterministic market fallback.
# =========================

def test_market_agent_replaces_unsupported_analysis(
    monkeypatch,
):

    monkeypatch.setattr(
        "agents.market_agent.retrieve_knowledge",
        lambda **kwargs: "Market knowledge",
    )

    snapshot = MarketSnapshot(
        as_of_date=date(
            2026,
            9,
            16,
        ),
        observations=[
            MarketObservation(
                asset_name="SPDR S&P 500 ETF Trust",
                asset_class=AssetClass.EQUITIES,
                symbol="SPY",
                geography="US",
                measurement_type=MeasurementType.PRICE,
                latest_value=Decimal("754.13"),
                previous_value=Decimal("755.00"),
                unit="price",
                currency="USD",
                latest_period="2026-09-16",
                previous_period="2026-09-15",
                direction=MarketDirection.FALLING,
                source="Alpha Vantage",
            ),
        ],
    )

    class UnsafeFakeLLM:
        def invoke(
            self,
            messages,
        ):
            return FakeResponse(
                "Markets are clearly moving into a risk-off environment."
            )

    result = market_agent(
        {
            "user_query": (
                "What are markets doing?"
            ),
            "market_snapshot": snapshot,
            "llm_calls": 0,
        },
        UnsafeFakeLLM(),
    )

    assert (
        result["market_results"]
        != "Markets are clearly moving into a risk-off environment."
    )

    assert (
        "SPDR S&P 500 ETF Trust: 754.13 price"
        in result["market_results"]
    )

    assert (
        "not established"
        in result["market_results"].lower()
    )

    assert result["llm_calls"] == 1