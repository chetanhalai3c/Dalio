from langchain_core.messages import AIMessage

from agents.portfolio_agent import portfolio_agent
from models.investor_profile import InvestorProfile
from models.portfolio import Portfolio


# =========================
# Fake LLM
# =========================

class FakeLLM:
    def invoke(self, messages):
        return AIMessage(
            content=(
                "1. Portfolio Structure\n"
                "Portfolio is 75% VUSA and 25% NVDA.\n\n"
                "2. Concentration and Diversification\n"
                "The supplied portfolio is 100% equity-based.\n\n"
                "3. Potential Overlapping or Economic Exposures\n"
                "Any instrument-level overlap requires Market Agent verification.\n\n"
                "4. What Cannot Yet Be Established\n"
                "Volatility, correlation and risk contribution require Risk Agent calculations."
            )
        )


# =========================
# Scenario 1 — Portfolio Agent runs
# =========================

def test_portfolio_agent_runs():
    portfolio = Portfolio(
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

    result = portfolio_agent(
        {
            "user_query": "Is my portfolio too concentrated?",
            "investor_profile": InvestorProfile(),
            "portfolio": portfolio,
            "llm_calls": 0,
        },
        FakeLLM(),
    )

    assert "portfolio_results" in result
    assert "75% VUSA" in result["portfolio_results"]
    assert result["llm_calls"] == 1


# =========================
# Scenario 2 — Missing Portfolio handled
# =========================

def test_portfolio_agent_without_portfolio():
    result = portfolio_agent(
        {
            "user_query": "Analyse my portfolio.",
            "investor_profile": InvestorProfile(),
            "llm_calls": 0,
        },
        FakeLLM(),
    )

    assert "portfolio_results" in result
    assert result["llm_calls"] == 1