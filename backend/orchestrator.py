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
        model="qwen/qwen3.6-27b",
        api_key=GROQ_API_KEY,
        max_tokens=300,
        reasoning_effort="none",
        reasoning_format="hidden",
    )
    if GROQ_API_KEY
    else None
)


# =========================
# Specialist LLM Configuration
# =========================

specialist_llm = (
    ChatGroq(
        model="qwen/qwen3.6-27b",
        api_key=GROQ_API_KEY,
        max_tokens=950,
        reasoning_effort="none",
        reasoning_format="hidden",
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