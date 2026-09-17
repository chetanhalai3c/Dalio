from typing import TypedDict, Annotated
import operator
from langchain_core.messages import AnyMessage

from models.investor_profile import InvestorProfile
from models.portfolio import Portfolio
from models.macro import MacroSnapshot
from models.market import MarketSnapshot # Validated cross-asset market data shared between LangGraph nodes.
from models.portfolio_risk import PortfolioRiskSnapshot # Trusted deterministic portfolio-risk evidence shared between agents.
# =========================
# Shared Investor State
# =========================

class InvestorState(TypedDict, total=False):
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str

    # Investor context
    investor_profile: InvestorProfile
    portfolio: Portfolio

    # Supervisor + input guardrail
    guardrail_allowed: bool
    guardrail_reason: str
    selected_agents: list[str]
    supervisor_reasoning: str

    # Specialist analysis
    # Specialist analysis
    macro_snapshot: MacroSnapshot
    macro_results: str
    market_snapshot: MarketSnapshot # Gives the Market Agent access to validated cross-asset facts.
    market_results: str
    portfolio_results: str
    portfolio_risk_snapshot: PortfolioRiskSnapshot # Makes deterministic risk evidence available to Risk and Allocation Agents.
    risk_results: str

    # Allocation proposal
    proposed_allocation: str

    # Allocation guardrail
    allocation_guardrail_allowed: bool
    allocation_guardrail_reason: str

    # Human-in-the-loop
    approval_request: str
    approved: bool
    human_feedback: str

    # Final output
    final_response: str

    # Diagnostics
    llm_calls: int