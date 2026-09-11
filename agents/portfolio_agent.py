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
        ],
        max_sections=5,
        max_chars=7500,
    )

    prompt = f"""
You are the Portfolio Specialist for EducosysDalio.

Your job is to produce compact specialist findings about the STRUCTURE
of the investor's current portfolio.

These findings will later be combined with Market, Risk and Allocation
analysis by a separate final education layer.

Investor Request:
{state.get("user_query", "")}

Investor Profile:
{profile_data}

Current Portfolio:
{portfolio_data}

Relevant EducosysDalio Knowledge:
{portfolio_knowledge}

Return ONLY these four sections:

1. OBSERVED STRUCTURE
- Total supplied portfolio value and capital weights.
- Asset classes directly visible in the supplied portfolio.

2. CONCENTRATION & DIVERSIFICATION
- Structural concentration visible directly from supplied data.
- Structural diversification visible directly from supplied data.

3. POTENTIAL EXPOSURES TO VERIFY
- Only flag possible overlaps or economic exposures.
- If verification requires current security, index, sector,
  geographic or currency information, explicitly assign it
  to the Market Agent.

4. NOT YET ESTABLISHED
- Quantitative risk information requiring the Risk Agent.
- Relevant investor information that has not been supplied.

BOUNDARIES:

Use only facts supplied in InvestorProfile and Portfolio.

EducosysDalio knowledge provides investment PRINCIPLES.
It is not evidence about the current characteristics of a specific security.

Do NOT supply or estimate:
- index constituent weights
- sector or geographic weights not supplied
- currency exposures not supplied
- concentration thresholds
- volatility
- correlation
- covariance
- drawdown
- risk contribution
- quantified diversification benefit

Do NOT recommend:
- purchases
- sales
- target weights
- rebalancing
- a new allocation

Market facts belong to the Market Agent.
Quantitative risk belongs to the Risk Agent.
Portfolio changes belong to the Allocation Agent.

Use short bullets.
Maximum two high-signal bullets per section.
No introduction, conclusion or table.
Complete all four sections.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Portfolio Specialist for EducosysDalio. "
                    "Produce compact structural findings only. "
                    "Do not perform Market, Risk, Allocation, or final "
                    "education responsibilities."
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