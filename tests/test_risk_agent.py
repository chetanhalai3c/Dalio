from langchain_core.messages import AIMessage

from agents.risk_agent import risk_agent
from models.investor_profile import InvestorProfile
from models.portfolio import Portfolio


# =========================
# Fake LLM
# =========================

class FakeLLM:
    def invoke(self, messages):
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
# Shared Portfolio
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