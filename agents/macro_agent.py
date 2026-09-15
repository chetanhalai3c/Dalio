from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from backend.knowledge import retrieve_knowledge
from backend.state import InvestorState
from backend.guardrails.macro_evidence_guardrail import (
    build_safe_macro_fallback,
    macro_analysis_is_grounded,
)


# =========================
# Macro Knowledge
# =========================

MACRO_KNOWLEDGE_FILES = [
    "economic_regimes.md",
    "debt_cycles.md",
    "all_weather.md",
]


# =========================
# Macro Agent
# =========================

def macro_agent(
    state: InvestorState,
    llm: Any,
) -> dict[str, Any]:
    macro_snapshot = state.get(
        "macro_snapshot"
    )

    snapshot_data = (
        macro_snapshot.model_dump(
            mode="json"
        )
        if macro_snapshot is not None
        else {}
    )

    macro_knowledge = retrieve_knowledge(
        query=state.get(
            "user_query",
            "",
        ),
        filenames=MACRO_KNOWLEDGE_FILES,
        keywords=[
            "growth",
            "inflation",
            "interest rates",
            "economic regime",
            "debt cycle",
        ],
        max_sections=6,
        max_chars=8000,
    )

    prompt = f"""
USER QUESTION:
{state.get("user_query", "")}

MACRO SNAPSHOT:
{snapshot_data}

DALIO KNOWLEDGE:
{macro_knowledge}

Analyse the current macroeconomic environment.

Use the Macro Snapshot as the factual source for current
economic conditions.

Use the provided Dalio knowledge only to interpret those facts.

Do NOT invent:

- missing macro indicators
- future economic data
- future market performance
- asset returns
- security-specific facts
- regime probabilities
- precise forecasts

Do NOT recommend:

- purchases
- sales
- target portfolio weights
- rebalancing
- a new allocation

Those decisions belong to the Allocation Agent.

Clearly distinguish:

- observed macro facts
- interpretation from the provided knowledge
- information that is not yet established

STRICT EVIDENCE BOUNDARIES:

Treat only values and metadata explicitly contained in the
Macro Snapshot as current economic facts.

Do NOT independently introduce or infer:

- central-bank names
- inflation targets
- unemployment or wage conditions
- fiscal policy stance
- income growth
- market expectations
- exchange-rate conditions
- commodity conditions
- causes of inflation
- motives or intentions of policymakers
- whether monetary policy is restrictive or accommodative
- whether an easing or tightening cycle is underway

Do NOT calculate new economic metrics inside the LLM, including:

- real interest rates
- spreads
- growth differentials
- inflation differentials

If such calculations become useful, they must first be calculated
deterministically by the data/tool layer.

You may interpret combinations that are explicitly observed.

For example:

- growth direction is falling while inflation direction is rising
- the policy rate is unchanged between the two supplied observations

HARD INTERPRETATION RULES:

- Describe a stable policy rate only as unchanged between the
  supplied observations.
- Never describe a stable rate as a pause, tightening cycle,
  easing cycle, reversal, policy stance, or policy signal.
- Never explain why policymakers kept the rate unchanged.
- Never infer previous or future policy actions.
- Never infer the current level of debt, debt stress, fiscal
  conditions, labour-market conditions, or market expectations
  unless those facts are explicitly supplied.
- Use only economic frameworks contained in DALIO KNOWLEDGE.
- Do not introduce outside frameworks, theories, or terminology
  from the LLM's general knowledge.
- A hypothetical framework explanation must not be presented as
  a description of the current economy.
- Never use one supplied indicator as a proxy for another
  unsupplied indicator unless that relationship is explicitly
  defined in DALIO KNOWLEDGE.
- GDP growth must not be treated as income growth, wage growth,
  household income, or debt-servicing capacity.
- A policy rate must not be described as the actual borrowing
  cost faced by households, companies, or governments.
- Do not mention or discuss the neutral rate, effective lower bound,
  practical policy bounds, policy-rate gaps, limits of conventional
  interest-rate policy, or proximity to any policy bound unless
  those values or conditions are explicitly supplied in the
  Macro Snapshot.
- Do not introduce unconventional monetary-policy tools merely
  because the policy rate is stable.

You may explain what the observed combination can mean within the
supplied Dalio framework, but clearly label that as interpretation.

Do NOT state that one observed variable caused another.

Do NOT infer policymaker motives from a policy-rate observation.

When evidence is insufficient, state:
"NOT YET ESTABLISHED."

Use these four sections:

1. CURRENT MACRO SNAPSHOT
2. ECONOMIC REGIME INTERPRETATION
3. DALIO-STYLE EDUCATION
4. NOT YET ESTABLISHED

Use short, high-signal bullets.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Macro Specialist for EducosysDalio. "
                    "The Macro Snapshot is the only source of current "
                    "macroeconomic facts. The supplied Dalio knowledge is "
                    "the only framework you may use to interpret those facts. "
                    "Do not use outside economic knowledge to add current "
                    "facts, named frameworks, calculations, causal claims, "
                    "policy-cycle claims, policymaker motives, forecasts, "
                    "or portfolio recommendations. If something is not "
                    "established by the snapshot or supplied knowledge, "
                    "state that it is not yet established."
                )
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )

    # Capture the LLM's proposed macro analysis.
    analysis = str(
        response.content
    )

    # Check the draft against the evidence guardrail.
    # If it contains unsupported interpretation, replace it
    # with the deterministic safe fallback.
    if not macro_analysis_is_grounded(
        analysis
    ):
        analysis = build_safe_macro_fallback(
            snapshot_data
        )

    return {
        "macro_results": analysis,
        "messages": [
            AIMessage(
                content=(
                    "Macro analysis generated."
                )
            )
        ],
        "llm_calls": (
            state.get(
                "llm_calls",
                0,
            )
            + 1
        ),
    }