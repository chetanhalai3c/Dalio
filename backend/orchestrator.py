import os
import json
import certifi
from typing import Any
from dotenv import load_dotenv

from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    SystemMessage,
)
from langchain_groq import ChatGroq

from backend.state import InvestorState
from backend.guardrails.input_guardrail import evaluate_input_guardrail

from agents.macro_agent import macro_agent # Interprets validated macroeconomic evidence.
from agents.market_agent import market_agent # Interprets validated cross-asset market evidence.
from agents.portfolio_agent import portfolio_agent # Interprets the investor's current portfolio structure.
from agents.risk_agent import risk_agent # Interprets structural and deterministic portfolio-risk evidence.
from agents.allocation_agent import allocation_agent # Synthesises evidence into a structured ProposedAllocation.

from backend.guardrails.allocation_guardrail import (
    evaluate_allocation_guardrail, # Deterministically validates explicit allocation-policy rules.
)
from mcp_servers.macro_mcp_server import (
    build_macro_snapshot_for_country,
)
from mcp_servers.market_mcp_server import (
    build_market_snapshot,
)
from mcp_servers.risk_market_mcp_server import (
    build_traditional_risk_proxy_universe, # Fetches historical analytical proxies for the supported broad asset classes.
)

from tools.portfolio_risk_adapter import (
    build_risk_capital_weights, # Converts detailed portfolio holdings into broad risk-engine capital weights.
)

from tools.portfolio_risk_builder import (
    build_portfolio_risk_snapshot, # Combines aligned historical data and deterministic maths into one trusted risk package.
)
# =========================
# Environment
# =========================

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()


# =========================
# API Configuration
# =========================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# =========================
# Router LLM Configuration
# =========================

llm = (
    ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY,
        max_tokens=300,
        reasoning_effort="low",
        
    )
    if GROQ_API_KEY
    else None
)


# =========================
# Specialist LLM Configuration
# =========================

specialist_llm = (
    ChatGroq(
        model="openai/gpt-oss-120b",
        api_key=GROQ_API_KEY,
        max_tokens=4000,
        reasoning_effort="high",
        
    )
    if GROQ_API_KEY
    else None
)


# =========================
# CIO Supervisor Configuration
# =========================

KNOWN_AGENTS = {
    "macro_agent",
    "market_agent",
    "portfolio_agent",
    "risk_agent",
    "allocation_agent",
}

AGENT_ORDER = [
    "macro_agent",
    "market_agent",
    "portfolio_agent",
    "risk_agent",
    "allocation_agent",
]


# =========================
# Shared LLM Helpers
# =========================

def _llm_text(
    system_prompt: str,
    user_prompt: str,
) -> str:
    if llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live LLM calls."
        )

    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )

    return str(response.content)


def _json_from_llm(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(
            "The model did not return a JSON object."
        )

    return json.loads(text[start : end + 1])


# =========================
# CIO Supervisor
# =========================

def cio_supervisor(state: InvestorState):
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)

    guardrail_result = evaluate_input_guardrail(
        query,
        llm,
    )

    llm_calls += 1

    allowed = bool(
        guardrail_result.get("allowed", True)
    )

    guardrail_reason = str(
        guardrail_result.get("reason", "")
    ).strip()

    if not allowed:
        reason = guardrail_reason or (
            "EducosysDalio can only help with "
            "financial and investment-related requests."
        )

        return {
            "guardrail_allowed": False,
            "guardrail_reason": reason,
            "selected_agents": [],
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [
                AIMessage(
                    content=f"Guardrail blocked request: {reason}"
                )
            ],
            "llm_calls": llm_calls,
        }

    supervisor_prompt = f"""
You are the CIO Supervisor for EducosysDalio.

Choose only the specialist agents needed for the investor's request.

Available agents:

- macro_agent:
  economic regimes, inflation, growth, interest rates
  and economic cycles

- market_agent:
  markets, asset classes, instruments and current
  market context

- portfolio_agent:
  holdings, concentration, diversification,
  exposures and portfolio structure

- risk_agent:
  volatility, drawdown, correlation,
  risk contribution and portfolio risk

- allocation_agent:
  portfolio construction, allocation changes,
  rebalancing and capital allocation

Rules:
- Select only agents genuinely needed.
- Do not require allocation_agent unless an allocation
  or rebalancing decision is required.
- Missing InvestorProfile or Portfolio information must
  not prevent useful educational analysis.

Return strict JSON only:

{{
  "selected_agents": [
    "macro_agent",
    "market_agent",
    "portfolio_agent",
    "risk_agent",
    "allocation_agent"
  ],
  "reasoning": ""
}}

Investor request:
{query}
"""

    try:
        raw_response = _llm_text(
            (
                "You are the CIO Supervisor for EducosysDalio. "
                "Return strict JSON only."
            ),
            supervisor_prompt,
        )

        parsed = _json_from_llm(raw_response)

        requested_agents = parsed.get(
            "selected_agents",
            [],
        )

        selected_agents = [
            agent
            for agent in AGENT_ORDER
            if (
                agent in requested_agents
                and agent in KNOWN_AGENTS
            )
        ]

        reasoning = str(
            parsed.get("reasoning", "")
        ).strip()

        llm_calls += 1

    except Exception as exc:
        print(
            f"CIO Supervisor fallback used: {exc}"
        )

        selected_agents = AGENT_ORDER.copy()

        reasoning = (
            "Supervisor parsing failed, so the full "
            "analysis workflow was selected as fallback."
        )

    return {
        "guardrail_allowed": True,
        "guardrail_reason": guardrail_reason,
        "selected_agents": selected_agents,
        "supervisor_reasoning": reasoning,
        "messages": [
            AIMessage(
                content="CIO Supervisor created the analysis plan."
            )
        ],
        "llm_calls": llm_calls,
    }
# =========================
# Macro Data Node
# =========================

def run_macro_data(
    state: InvestorState,
) -> dict[str, Any]:
    investor_profile = state.get(
        "investor_profile"
    )

    if investor_profile is None:
        return {}

    country_code = (
        investor_profile
        .jurisdiction_currency
        .country_of_residence
    )

    if country_code is None:
        return {}

    snapshot = build_macro_snapshot_for_country(
        country_code
    )

    return {
        "macro_snapshot": snapshot
    }


# =========================
# Macro Specialist Node
# =========================

def run_macro_specialist(
    state: InvestorState,
) -> dict[str, Any]:
    if specialist_llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live specialist LLM calls."
        )

    return macro_agent(
        state,
        specialist_llm,
    )

# =========================
# Macro Workflow
# =========================

def run_macro_workflow(
    state: InvestorState,
) -> dict[str, Any]:
    macro_data = run_macro_data(
        state
    )

    enriched_state = {
        **state,
        **macro_data,
    }

    macro_analysis = run_macro_specialist(
        enriched_state
    )

    return {
        **macro_data,
        **macro_analysis,
    }
# =========================
# Market Data Node
# =========================

def run_market_data(
    state: InvestorState,
) -> dict[str, Any]:
    investor_profile = state.get(
        "investor_profile"
    )

    investor_country = None
    base_currency = None

    if investor_profile is not None:
        investor_country = (
            investor_profile
            .jurisdiction_currency
            .country_of_residence
        )

        base_currency = (
            investor_profile
            .jurisdiction_currency
            .spending_currency
        )

    snapshot = build_market_snapshot(
        investor_country=investor_country,
        base_currency=base_currency,
    )

    return {
        "market_snapshot": snapshot
    }


# =========================
# Market Specialist Node
# =========================

def run_market_specialist(
    state: InvestorState,
) -> dict[str, Any]:
    if specialist_llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live specialist LLM calls."
        )

    return market_agent(
        state,
        specialist_llm,
    )


# =========================
# Market Workflow
# =========================

def run_market_workflow(
    state: InvestorState,
) -> dict[str, Any]:
    market_data = run_market_data(
        state
    )

    enriched_state = {
        **state,
        **market_data,
    }

    market_analysis = run_market_specialist(
        enriched_state
    )

    return {
        **market_data,
        **market_analysis,
    }

# =========================
# Portfolio Specialist Node
# Runs portfolio analysis using the investor's existing holdings and profile.
# =========================

def run_portfolio_specialist(
    state: InvestorState,
) -> dict[str, Any]:

    if specialist_llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live specialist LLM calls."
        )

    return portfolio_agent(
        state,
        specialist_llm,
    )

# =========================
# Portfolio Risk Data Node
# Builds the trusted deterministic PortfolioRiskSnapshot used by the Risk and Allocation Agents.
# =========================

def run_portfolio_risk_data(
    state: InvestorState,
) -> dict[str, Any]:

    portfolio = state.get(
        "portfolio"
    ) # Retrieve the investor's validated portfolio from shared state.

    if portfolio is None:
        return {}
        # No portfolio means there is no investor-specific portfolio risk snapshot to calculate.

    capital_weights = build_risk_capital_weights(
        portfolio
    ) # Convert detailed holdings into broad economic asset-class weights.

    historical_series = build_traditional_risk_proxy_universe()
    # Fetch the supported historical proxy universe such as equities,
    # government bonds, gold, commodities and cash.

    relevant_series = [
        series
        for series in historical_series
        if series.asset_class in capital_weights
    ]
    # Keep only historical proxies corresponding to asset classes
    # actually present in this investor's portfolio.

    snapshot = build_portfolio_risk_snapshot(
        capital_weights=capital_weights,
        series_list=relevant_series,
    )
    # Align historical observations and run the deterministic risk maths.

    return {
        "portfolio_risk_snapshot": snapshot
    } # Place the trusted risk package into shared InvestorState.

# =========================
# Risk Specialist Node
# Interprets structural portfolio risk and the deterministic PortfolioRiskSnapshot.
# =========================

def run_risk_specialist(
    state: InvestorState,
) -> dict[str, Any]:

    if specialist_llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live specialist LLM calls."
        )

    return risk_agent(
        state,
        specialist_llm,
    )

# =========================
# Allocation Specialist Node
# Synthesises investor, portfolio, risk, macro and market evidence into ProposedAllocation.
# =========================

def run_allocation_specialist(
    state: InvestorState,
) -> dict[str, Any]:

    if specialist_llm is None:
        raise ValueError(
            "GROQ_API_KEY is required for live specialist LLM calls."
        )

    return allocation_agent(
        state,
        specialist_llm,
    )
# =========================
# Allocation Guardrail Node
# Checks the proposed allocation against explicit deterministic product policy.
# =========================

def run_allocation_guardrail(
    state: InvestorState,
) -> dict[str, Any]:

    proposal = state.get(
        "proposed_allocation"
    ) # Retrieve the validated proposal produced by the Allocation Agent.

    if proposal is None:
        return {
            "allocation_guardrail_allowed": False,
            "allocation_guardrail_reason": (
                "No proposed allocation was available for validation."
            ),
        }
        # Fail closed because there is nothing for the guardrail to approve.

    guardrail_result = evaluate_allocation_guardrail(
        proposal
    )
    # No numerical asset-class limits are supplied until
    # explicit product policy has approved them.

    reason = (
        "; ".join(
            guardrail_result.violations
        )
        if guardrail_result.violations
        else ""
    ) # Preserve deterministic violation explanations in the existing state field.

    return {
        "allocation_guardrail_allowed": guardrail_result.passed,
        "allocation_guardrail_reason": reason,
    }

# =========================
# Workflow State Merge
# Preserves accumulated messages while applying each node's state updates.
# =========================

def _merge_workflow_update(
    state: InvestorState,
    update: dict[str, Any],
) -> InvestorState:

    existing_messages = state.get(
        "messages",
        [],
    )

    new_messages = update.get(
        "messages",
        [],
    )

    merged_state = {
        **state,
        **update,
    }

    if existing_messages or new_messages:
        merged_state["messages"] = [
            *existing_messages,
            *new_messages,
        ]

    return merged_state


# =========================
# CIO Workflow Executor
# Executes the Supervisor's specialist plan in dependency-safe order.
# =========================

def run_cio_workflow(
    state: InvestorState,
) -> InvestorState:

    # =========================
    # CIO Supervisor
    # Decide which specialist capabilities are required.
    # =========================

    supervisor_update = cio_supervisor(
        state
    )

    working_state = _merge_workflow_update(
        state,
        supervisor_update,
    )

    if not working_state.get(
        "guardrail_allowed",
        True,
    ):
        return working_state
        # Input guardrail blocked the request, so no specialists should run.

    selected_agents = set(
        working_state.get(
            "selected_agents",
            [],
        )
    )

    # =========================
    # Dependency Expansion
    # Allocation requires portfolio and risk understanding first.
    # =========================

    if "allocation_agent" in selected_agents:
        selected_agents.update(
            {
                "portfolio_agent",
                "risk_agent",
            }
        )

    if "risk_agent" in selected_agents:
        selected_agents.add(
            "portfolio_agent"
        )

    # =========================
    # Macro
    # Current economic evidence is gathered only when requested.
    # =========================

    if "macro_agent" in selected_agents:

        macro_update = run_macro_workflow(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            macro_update,
        )

    # =========================
    # Market
    # Current cross-asset evidence is gathered only when requested.
    # =========================

    if "market_agent" in selected_agents:

        market_update = run_market_workflow(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            market_update,
        )

    # =========================
    # Portfolio
    # Analyse the investor's actual holdings before portfolio risk.
    # =========================

    if "portfolio_agent" in selected_agents:

        portfolio_update = run_portfolio_specialist(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            portfolio_update,
        )

    # =========================
    # Portfolio Risk + Risk Specialist
    # Python calculates first; the Risk Agent interprets second.
    # =========================

    if "risk_agent" in selected_agents:

        portfolio_risk_update = run_portfolio_risk_data(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            portfolio_risk_update,
        )

        risk_update = run_risk_specialist(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            risk_update,
        )

    # =========================
    # Allocation
    # Synthesise accumulated evidence into ProposedAllocation.
    # =========================

    if "allocation_agent" in selected_agents:

        allocation_update = run_allocation_specialist(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            allocation_update,
        )

        allocation_guardrail_update = run_allocation_guardrail(
            working_state
        )

        working_state = _merge_workflow_update(
            working_state,
            allocation_guardrail_update,
        )

    return working_state
