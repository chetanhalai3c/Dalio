from typing import Any # Any lets the function accept whichever LLM implementation is passed in.

from langchain_core.messages import (
    AIMessage,      # Message written back into workflow/chat history.
    HumanMessage,   # Carries the actual user task/prompt to the LLM.
    SystemMessage,  # Defines the LLM's role and hard behavioural rules.
)

from backend.knowledge import retrieve_knowledge # Retrieves only the relevant Dalio knowledge sections for this macro task.

from backend.state import InvestorState # Shared workflow state containing inputs, evidence, and previous results.

from backend.guardrails.macro_evidence_guardrail import (
    build_safe_macro_fallback,   # Creates a safe deterministic answer if LLM output fails.
    macro_analysis_is_grounded,  # Checks whether LLM analysis stays within evidence boundaries.
)


# =========================
# Macro Knowledge
# Defines which knowledge files this specialist is allowed to reason from.
# =========================

MACRO_KNOWLEDGE_FILES = [
    "economic_regimes.md",  # Dalio-style regime interpretation.
    "debt_cycles.md",       # Debt-cycle framework.
    "all_weather.md",       # All Weather / economic environment principles.
]


# =========================
# Macro Agent
# Reads macro evidence + knowledge, asks the LLM to interpret it, then validates the result.
# =========================

def macro_agent(
    state: InvestorState,  # Shared workflow state.
    llm: Any,              # LLM supplied by the wider application.
) -> dict[str, Any]:

    macro_snapshot = state.get(
        "macro_snapshot"
    )
    # Read the already-collected MacroSnapshot from shared state.

    snapshot_data = (
        macro_snapshot.model_dump(
            mode="json"
        )
        if macro_snapshot is not None
        else {}
    )
    # Convert Pydantic MacroSnapshot → JSON-friendly dictionary.
    # If no snapshot exists, use an empty dictionary.

    macro_knowledge = retrieve_knowledge(
        query=state.get(
            "user_query",
            "",
        ),
        # Use the user's question to decide which knowledge sections are relevant.

        filenames=MACRO_KNOWLEDGE_FILES,
        # Search only the macro-related Dalio files.

        keywords=[
            "growth",
            "inflation",
            "interest rates",
            "economic regime",
            "debt cycle",
        ],
        # Extra retrieval signals for relevant macro concepts.

        max_sections=6,
        # Limit how many knowledge sections are returned.

        max_chars=8000,
        # Prevent too much knowledge from bloating the prompt.
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
    # Build one tightly constrained prompt containing:
    # 1) user question
    # 2) current macro evidence
    # 3) permitted Dalio knowledge
    # 4) strict rules limiting what the LLM may claim


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
            # SystemMessage establishes the specialist's permanent role
            # and highest-level reasoning restrictions.

            HumanMessage(
                content=prompt
            ),
            # HumanMessage contains this specific task, evidence, and knowledge.
        ]
    )


    # Capture the LLM's proposed macro analysis.
    analysis = str(
        response.content
    )
    # Important: this is still only a DRAFT at this point.


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
        # Write the approved/safe macro analysis back to shared state.

        "messages": [
            AIMessage(
                content=(
                    "Macro analysis generated."
                )
            )
        ],
        # Add a lightweight workflow message confirming completion.

        "llm_calls": (
            state.get(
                "llm_calls",
                0,
            )
            + 1
        ),
        # Increment the running count of LLM calls.
    }