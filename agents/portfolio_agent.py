from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from backend.state import InvestorState
from backend.knowledge import retrieve_knowledge


# =========================
# Portfolio Knowledge
# =========================

PORTFOLIO_KNOWLEDGE_FILES = [
    "investment_philosophy.md",
    "diversification.md",
    "risk_balancing.md",
    "asset_roles.md",
]


# =========================
# Portfolio Agent
# =========================

def portfolio_agent(
    state: InvestorState,
    llm: Any,
):
    if llm is None:
        raise ValueError(
            "An LLM is required to run the Portfolio Agent."
        )

    portfolio = state.get("portfolio")
    investor_profile = state.get("investor_profile")

    portfolio_data = (
        portfolio.model_dump(mode="json")
        if portfolio is not None
        else {}
    )

    profile_data = (
        investor_profile.model_dump(mode="json")
        if investor_profile is not None
        else {}
    )

    portfolio_knowledge = retrieve_knowledge(
        query=state.get("user_query", ""),
        filenames=PORTFOLIO_KNOWLEDGE_FILES,
        keywords=[
            "concentration",
            "diversification",
            "economic exposure",
            "asset roles",
            "risk balancing",
        ],
        max_sections=6,
        max_chars=9000,
    )

    prompt = f"""
You are the Portfolio Specialist for EducosysDalio.

Your responsibility is to diagnose the STRUCTURE of the investor's
current portfolio.

Investor Request:
{state.get("user_query", "")}

Investor Profile:
{profile_data}

Current Portfolio:
{portfolio_data}

Relevant EducosysDalio Knowledge:
{portfolio_knowledge}

Analyse:

1. Portfolio composition and capital weights
2. Asset-class concentration
3. Single-position concentration
4. Obvious overlapping exposures
5. Structural diversification
6. Important economic exposure patterns
7. Missing information needed for deeper analysis

Rules:

- Use only the portfolio and investor information actually supplied.
- Never invent holdings, values or investor circumstances.
- Clearly distinguish OBSERVED FACTS from INFERENCES.
- If an inference relies on knowledge about an instrument or index,
  clearly label it as an inference.
- Use the supplied EducosysDalio knowledge as the analytical framework.

IMPORTANT BOUNDARY:

You may identify structural concentration from observable portfolio facts.

You must NOT claim or estimate:
- portfolio volatility
- asset correlations
- covariance
- drawdown
- risk contribution
- quantified diversification benefit

Those require deterministic calculations and belong to the Risk Agent.

Do NOT recommend:
- target portfolio weights
- purchases or sales
- rebalancing
- a new allocation

Those decisions belong to the Allocation Agent.

If risk metrics have not been calculated, explicitly say that they
have not yet been established.

If no portfolio has been supplied, state that a personalised portfolio
diagnosis cannot yet be performed.

Keep the analysis concise and complete.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Portfolio Specialist for EducosysDalio. "
                    "Diagnose portfolio structure using the supplied facts "
                    "and EducosysDalio knowledge. Do not perform the Risk "
                    "Agent or Allocation Agent's responsibilities."
                )
            ),
            HumanMessage(content=prompt),
        ]
    )

    return {
        "portfolio_results": str(response.content),
        "messages": [
            AIMessage(
                content="Portfolio analysis generated."
            )
        ],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }