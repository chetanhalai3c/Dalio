from typing import Any # Allows the wider application to supply whichever compatible LLM implementation it uses.

from langchain_core.messages import (
    AIMessage, # Writes completion/status information back into shared workflow history.
    HumanMessage, # Carries the Allocation Agent's evidence and instructions to the LLM.
    SystemMessage, # Defines the Allocation Agent's hard reasoning boundaries.
)

from backend.knowledge import retrieve_knowledge # Retrieves the Dalio-style knowledge relevant to allocation.
from backend.state import InvestorState # Shared state containing investor, portfolio, risk, macro and market evidence.
from models.allocation import ProposedAllocation # Validated structured output the Allocation Agent must eventually produce.

# =========================
# Allocation Knowledge
# Defines which EducosysDalio principles the Allocation Agent may use.
# =========================

ALLOCATION_KNOWLEDGE_FILES = [
    "investment_philosophy.md", # Core long-term investment principles and decision philosophy.
    "diversification.md", # Principles for spreading exposure across economically distinct return drivers.
    "all_weather.md", # Framework for building portfolios intended to remain robust across environments.
    "risk_balancing.md", # Explains why capital weight and risk contribution are different.
    "asset_roles.md", # Defines the economic role and limitations of each asset class.
]

# =========================
# Allocation Agent
# Collects trusted investor, portfolio, risk, macro and market evidence.
# =========================

def allocation_agent(
    state: InvestorState,
    llm: Any,
) -> dict[str, Any]:

    investor_profile = state.get(
        "investor_profile"
    ) # Personal circumstances and constraints that affect suitable allocation.

    portfolio = state.get(
        "portfolio"
    ) # Current holdings and capital structure.

    portfolio_risk_snapshot = state.get(
        "portfolio_risk_snapshot"
    ) # Deterministic volatility, correlation and risk-contribution evidence.

    macro_snapshot = state.get(
        "macro_snapshot"
    ) # Validated current macroeconomic observations.

    market_snapshot = state.get(
        "market_snapshot"
    ) # Validated current cross-asset market observations.

    profile_data = (
        investor_profile.model_dump(
            mode="json"
        )
        if investor_profile is not None
        else {}
    ) # Convert validated InvestorProfile into prompt-ready evidence.

    portfolio_data = (
        portfolio.model_dump(
            mode="json"
        )
        if portfolio is not None
        else {}
    ) # Convert the investor's validated portfolio into prompt-ready evidence.

    portfolio_risk_data = (
        portfolio_risk_snapshot.model_dump(
            mode="json"
        )
        if portfolio_risk_snapshot is not None
        else {}
    ) # Preserve deterministic risk calculations without asking the LLM to recreate them.

    macro_data = (
        macro_snapshot.model_dump(
            mode="json"
        )
        if macro_snapshot is not None
        else {}
    ) # Preserve the validated macro facts separately from Macro Agent interpretation.

    market_data = (
        market_snapshot.model_dump(
            mode="json"
        )
        if market_snapshot is not None
        else {}
    ) # Preserve validated market facts separately from Market Agent interpretation.

    # =========================
    # Specialist Interpretations
    # Brings in the explanations already produced by the other agents.
    # =========================

    portfolio_results = state.get(
        "portfolio_results",
        "",
    ) # Portfolio Agent's interpretation of what the investor currently owns.

    risk_results = state.get(
        "risk_results",
        "",
    ) # Risk Agent's interpretation of the deterministic PortfolioRiskSnapshot.

    macro_results = state.get(
        "macro_results",
        "",
    ) # Macro Agent's interpretation of validated economic evidence.

    market_results = state.get(
        "market_results",
        "",
    ) # Market Agent's interpretation of validated cross-asset evidence.

    # =========================
    # Allocation Knowledge Retrieval
    # Retrieves only the investment principles relevant to this allocation decision.
    # =========================

    allocation_knowledge = retrieve_knowledge(
        query=state.get(
            "user_query",
            "",
        ), # Use the investor's actual question to retrieve the most relevant principles.
        filenames=ALLOCATION_KNOWLEDGE_FILES, # Restrict retrieval to approved Allocation Agent knowledge files.
        keywords=[
            "allocation",
            "diversification",
            "risk balancing",
            "asset roles",
            "all weather",
            "capital preservation",
        ], # Bias retrieval toward concepts relevant to portfolio construction.
        max_sections=8, # Prevent excessive knowledge from overwhelming the decision context.
        max_chars=10000, # Keep the retrieved knowledge bounded and prompt-friendly.
    )

    # =========================
    # Allocation Prompt
    # Combines trusted evidence with approved allocation principles.
    # =========================

    prompt = f"""
USER REQUEST:
{state.get("user_query", "")}

INVESTOR PROFILE:
{profile_data}

CURRENT PORTFOLIO:
{portfolio_data}

PORTFOLIO AGENT FINDINGS:
{portfolio_results}

DETERMINISTIC PORTFOLIO RISK SNAPSHOT:
{portfolio_risk_data}

RISK AGENT FINDINGS:
{risk_results}

VALIDATED MACRO SNAPSHOT:
{macro_data}

MACRO AGENT FINDINGS:
{macro_results}

VALIDATED MARKET SNAPSHOT:
{market_data}

MARKET AGENT FINDINGS:
{market_results}

EDUCOSYSDALIO ALLOCATION KNOWLEDGE:
{allocation_knowledge}

Your task is to propose a long-term asset-class allocation using only
the evidence and principles supplied above.

The proposal must describe desired ECONOMIC EXPOSURES rather than
specific ETFs, funds, securities or trading instructions.

Use the Investor Profile to determine how personalised the proposal
can reasonably be.

If sufficient investor-specific information is available, use:

basis = "personalised"

If important investor-specific information is missing, use:

basis = "educational_baseline"

and explicitly record the important missing assumptions and
uncertainties.

PORTFOLIO RISK:

Treat the Deterministic Portfolio Risk Snapshot as the trusted source
for calculated portfolio-risk statistics.

Do NOT independently calculate or estimate:

- volatility
- covariance
- correlation
- marginal risk contribution
- component risk contribution
- relative risk contribution

Use those values only when explicitly supplied.

Capital allocation and risk contribution are different concepts.

Do not assume that an asset with a large capital weight necessarily
contributes the same proportion of portfolio risk.

MACRO AND MARKET EVIDENCE:

Use validated Macro and Market snapshots as current factual evidence.

Specialist findings may help interpret those facts, but do not treat
unsupported specialist prose as stronger evidence than the underlying
validated snapshots.

Do NOT infer missing current-market facts.

ALLOCATION PRINCIPLES:

Use the supplied EducosysDalio knowledge to reason about:

- diversification across economically distinct exposures
- avoiding domination by one source of portfolio risk
- robustness across different economic environments
- capital preservation
- liquidity
- the economic role of each asset class

Do NOT mechanically force equal capital weights.

Do NOT mechanically force equal risk contributions.

Do NOT make a short-term market-timing allocation solely because of
the current macro or market environment.

Do NOT invent expected returns.

Do NOT use leverage.

Do NOT choose specific implementation products or brokers.

The target asset-class weights must sum to exactly 100%.

Return a proposal matching the ProposedAllocation schema.
"""

    # =========================
    # Structured Allocation Generation
    # Forces the LLM output through the ProposedAllocation contract.
    # =========================

    structured_llm = llm.with_structured_output(
        ProposedAllocation
    ) # Wrap the supplied LLM so its response must match our validated allocation schema.

    proposal = structured_llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Allocation Specialist for EducosysDalio. "
                    "Synthesize the supplied investor, portfolio, deterministic "
                    "risk, macro, market and knowledge evidence into a long-term "
                    "asset-class allocation. Do not invent missing financial "
                    "facts, risk statistics, expected returns or market forecasts. "
                    "Return only a ProposedAllocation."
                )
            ), # Sets the Allocation Agent's hard reasoning boundary.
            HumanMessage(
                content=prompt
            ), # Supplies all trusted evidence and allocation instructions.
        ]
    ) # The expected result is a validated ProposedAllocation object.

    # =========================
    # Allocation Validation
    # Re-validates the structured LLM output before it enters shared state.
    # =========================

    validated_proposal = ProposedAllocation.model_validate(
        proposal
    ) # Ensures weights, asset classes and allocation structure satisfy our deterministic contract.

    # =========================
    # Allocation Agent Output
    # Writes the validated proposal back into the shared workflow state.
    # =========================

    return {
        "proposed_allocation": validated_proposal, # Trusted structured proposal for the guardrail and HITL stages.
        "messages": [
            AIMessage(
                content="Allocation proposal generated."
            )
        ], # Records completion in the shared LangGraph message history.
        "llm_calls": (
            state.get(
                "llm_calls",
                0,
            )
            + 1
        ), # Increment the workflow's LLM-call count.
    }