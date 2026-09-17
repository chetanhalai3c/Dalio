from datetime import date # Fixed dates for deterministic historical risk evidence.
from decimal import Decimal # Precise financial values for risk metrics.

from langchain_core.messages import AIMessage

from agents.risk_agent import risk_agent
from models.investor_profile import InvestorProfile
from models.market import AssetClass # Economic asset classes used by PortfolioRiskSnapshot.
from models.portfolio import Portfolio
from models.portfolio_risk import (
    AssetRiskMetrics, # Deterministic risk evidence for one economic exposure.
    PortfolioRiskSnapshot, # Trusted risk package consumed by the Risk Agent.
)
from models.risk_market_data import (
    HistoricalFrequency, # Frequency used to calculate the historical risk evidence.
)


# =========================
# Fake LLM
# Returns a predictable response so Risk Agent behaviour can be tested without a live model.
# =========================

class FakeLLM:

    def invoke(
        self,
        messages,
    ):
        return AIMessage(
            content=(
                "1. CALCULATED RISK STRUCTURE\n"
                "Largest position weight is 75% and HHI is 0.625.\n\n"
                "2. RISK INTERPRETATION\n"
                "The portfolio is structurally concentrated.\n\n"
                "3. RISK NOT YET CALCULATED\n"
                "Volatility, correlation and drawdown require market data.\n\n"
                "4. INVESTOR CONTEXT LIMITS\n"
                "Risk capacity and time horizon are not yet known."
            )
        )


# =========================
# Capturing Fake LLM
# Stores the Risk Agent prompt so tests can inspect what evidence reached the LLM.
# =========================

class CapturingFakeLLM:

    def __init__(
        self,
    ):
        self.messages = None # Will store the messages supplied by risk_agent().

    def invoke(
        self,
        messages,
    ):
        self.messages = messages # Capture the exact prompt before returning a fake response.

        return AIMessage(
            content=(
                "Risk analysis generated from deterministic risk evidence."
            )
        )


# =========================
# Shared Portfolio
# Reusable portfolio fixture for Risk Agent tests.
# =========================

def build_test_portfolio():

    return Portfolio(
        holdings=[
            {
                "holding_id": "holding_1",
                "name": "S&P 500 ETF",
                "ticker": "VUSA",
                "asset_class": "equity_fund",
                "current_value": {
                    "value_type": "exact",
                    "amount": 15000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            },
            {
                "holding_id": "holding_2",
                "name": "Nvidia",
                "ticker": "NVDA",
                "asset_class": "equity",
                "current_value": {
                    "value_type": "exact",
                    "amount": 5000,
                    "currency": "GBP",
                },
                "currency": "GBP",
            },
        ]
    )


# =========================
# Scenario 1 — Risk Agent Runs
# Confirms the existing Risk Agent path still works with a normal portfolio.
# =========================

def test_risk_agent_runs():

    portfolio = build_test_portfolio()

    result = risk_agent(
        {
            "user_query": "Is my portfolio too risky?",
            "investor_profile": InvestorProfile(),
            "portfolio": portfolio,
            "llm_calls": 0,
        },
        FakeLLM(),
    )

    assert "risk_results" in result
    assert "HHI is 0.625" in result["risk_results"]
    assert result["llm_calls"] == 1


# =========================
# Scenario 2 — Missing Portfolio
# Confirms the Risk Agent still runs when portfolio information is absent.
# =========================

def test_risk_agent_without_portfolio():

    result = risk_agent(
        {
            "user_query": "How risky is my portfolio?",
            "investor_profile": InvestorProfile(),
            "llm_calls": 0,
        },
        FakeLLM(),
    )

    assert "risk_results" in result
    assert result["llm_calls"] == 1


# =========================
# Scenario 3 — Portfolio Risk Snapshot Reaches Prompt
# Proves deterministic volatility and risk-contribution evidence reaches the Risk Agent.
# =========================

def test_risk_agent_receives_portfolio_risk_snapshot():

    portfolio = build_test_portfolio() # Existing investor portfolio used by the Risk Agent.

    portfolio_risk_snapshot = PortfolioRiskSnapshot(
        as_of_date=date(
            2026,
            9,
            16,
        ),
        currency="USD", # Historical risk proxies are measured in a common currency.
        frequency=HistoricalFrequency.WEEKLY, # Risk metrics were calculated from weekly observations.
        observation_start_date=date(
            2025,
            9,
            12,
        ),
        observation_end_date=date(
            2026,
            9,
            16,
        ),
        aligned_return_observation_count=52, # Number of synchronized historical return observations.
        portfolio_period_volatility=Decimal(
            "0.12"
        ), # Trusted deterministic portfolio volatility.
        asset_metrics=[
            AssetRiskMetrics(
                asset_class=AssetClass.EQUITIES,
                proxy_symbol="SPY", # Historical proxy used for the equity exposure.
                proxy_name="SPDR S&P 500 ETF Trust",
                capital_weight=Decimal(
                    "1"
                ), # This simplified test snapshot contains 100% equity exposure.
                period_volatility=Decimal(
                    "0.12"
                ), # Deterministic standalone equity volatility.
                marginal_risk_contribution=Decimal(
                    "0.12"
                ), # Effect of the equity exposure on portfolio volatility.
                component_risk_contribution=Decimal(
                    "0.12"
                ), # Absolute portfolio-risk contribution from equities.
                relative_risk_contribution=Decimal(
                    "1"
                ), # Equities contribute 100% of risk in this one-asset example.
            )
        ],
        limitations=[
            (
                "Historical proxy behaviour does not "
                "guarantee future behaviour."
            )
        ], # Risk evidence carries its own limitations into the agent.
    )

    fake_llm = CapturingFakeLLM()

    result = risk_agent(
        {
            "user_query": (
                "Where is my portfolio risk coming from?"
            ),
            "investor_profile": InvestorProfile(),
            "portfolio": portfolio,
            "portfolio_risk_snapshot": portfolio_risk_snapshot,
            "llm_calls": 0,
        },
        fake_llm,
    )

    prompt = (
        fake_llm.messages[-1].content
    ) # The final HumanMessage contains the complete Risk Agent prompt.

    assert (
        "Deterministic Portfolio Risk Snapshot:"
        in prompt
    ) # Confirms the new trusted risk-evidence section reached the prompt.

    assert (
        "portfolio_period_volatility"
        in prompt
    ) # Confirms calculated portfolio volatility reached the Risk Agent.

    assert (
        "relative_risk_contribution"
        in prompt
    ) # Confirms calculated risk-contribution evidence reached the Risk Agent.

    assert (
        "0.12"
        in prompt
    ) # Confirms the deterministic numerical values themselves reached the prompt.

    assert result["llm_calls"] == 1