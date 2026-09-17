from typing import Any # Accepts whichever LLM implementation the wider app supplies.

from langchain_core.messages import (
    AIMessage,      # Writes completion status back into workflow history.
    HumanMessage,   # Carries the specific market-analysis task.
    SystemMessage,  # Defines the Market Agent's hard reasoning boundaries.
)

from backend.knowledge import retrieve_knowledge # Retrieves relevant Dalio-style market knowledge.
from backend.state import InvestorState # Shared LangGraph state containing market evidence and user context.
from backend.guardrails.market_evidence_guardrail import (
    build_safe_market_fallback, # Creates a deterministic response when the LLM overreaches.
    market_analysis_is_grounded, # Checks whether the draft stays inside MarketSnapshot evidence.
)

# =========================
# Market Knowledge
# Defines which knowledge files this specialist may use for interpretation.
# =========================

MARKET_KNOWLEDGE_FILES = [
    "asset_roles.md",      # Asset-class drivers, sensitivities, and role limitations.
    "diversification.md",  # Cross-asset diversification principles.
    "all_weather.md",      # Economic-driver diversification framework.
]


# =========================
# Market Agent
# Interprets validated cross-asset facts without making allocation decisions.
# =========================

def market_agent(
    state: InvestorState, # Shared workflow state.
    llm: Any,             # LLM supplied by the wider application.
) -> dict[str, Any]:

    market_snapshot = state.get(
        "market_snapshot"
    ) # Read the already-collected MarketSnapshot from shared state.

    snapshot_data = (
        market_snapshot.model_dump(
            mode="json"
        )
        if market_snapshot is not None
        else {}
    ) # Convert Pydantic MarketSnapshot into JSON-friendly evidence.

    market_knowledge = retrieve_knowledge(
        query=state.get(
            "user_query",
            "",
        ),
        filenames=MARKET_KNOWLEDGE_FILES,
        keywords=[
            "equities",
            "government bonds",
            "gold",
            "commodities",
            "cash",
            "crypto",
            "diversification",
            "asset roles",
        ],
        max_sections=8,
        max_chars=10000,
    ) # Retrieve only market-relevant knowledge rather than loading everything.

    prompt = f"""
USER QUESTION:
{state.get("user_query", "")}

MARKET SNAPSHOT:
{snapshot_data}

DALIO KNOWLEDGE:
{market_knowledge}

Analyse the supplied market observations.

Use the Market Snapshot as the only factual source for current
market conditions.

Use the supplied Dalio knowledge only to interpret those facts.

Do NOT invent:

- missing asset prices
- missing yields
- missing market observations
- volatility
- correlations
- drawdowns
- valuation metrics
- market expectations
- investor positioning
- economic causes
- future market performance
- return forecasts

Do NOT recommend:

- purchases
- sales
- target portfolio weights
- rebalancing
- tactical trades
- a new allocation

Those decisions belong to the Allocation Agent.

STRICT EVIDENCE BOUNDARIES:

Treat only values and metadata explicitly contained in the
Market Snapshot as current market facts.

Do NOT generalise a proxy beyond what the snapshot actually contains.

For example:

- an SPY observation is evidence about that instrument, not all global equities
- a US 10-year Treasury yield is a yield observation, not a government-bond price
- a US 3-month Treasury yield is a cash-like proxy, not every form of cash
- Bitcoin is evidence about Bitcoin, not the entire crypto market

Do NOT compare absolute numeric values across incompatible measurements.

For example:

- equity price versus bond yield
- gold price versus commodity index
- Bitcoin price versus Treasury yield

Do NOT calculate new market metrics inside the LLM, including:

- percentage returns
- spreads
- correlations
- volatility
- drawdowns
- relative-strength scores
- real yields

If such calculations become useful, they must first be calculated
deterministically by the data/tool layer.

You MAY compare directly observed directions when clearly labelled.

For example:

- one supplied observation is rising while another is falling
- two supplied observations are both rising
- one supplied observation is unchanged

Respect the observation period.

Do NOT treat monthly commodity data as if it were directly comparable
to a daily observation over the same time interval.

For government bonds:

- if the snapshot contains a YIELD observation, describe the yield
- do not convert that automatically into a bond-price claim

Clearly distinguish:

- observed market facts
- interpretation from the supplied knowledge
- information that is not yet established

Do NOT claim that one asset caused another asset to move.

Do NOT infer macroeconomic conditions from market prices alone.

Do NOT infer investor sentiment, risk appetite, policy expectations,
or recession probabilities unless explicitly supplied.

When evidence is insufficient, state:

"NOT YET ESTABLISHED."

Use these four sections:

1. CURRENT MARKET SNAPSHOT
2. CROSS-ASSET INTERPRETATION
3. DALIO-STYLE EDUCATION
4. NOT YET ESTABLISHED

Use short, high-signal bullets.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Market Specialist for EducosysDalio. "
                    "The Market Snapshot is the only source of current "
                    "market facts. The supplied Dalio knowledge is the only "
                    "framework you may use to interpret those facts. "
                    "Do not invent missing data, calculations, causal claims, "
                    "forecasts, market expectations, or portfolio recommendations. "
                    "Respect the exact instrument, geography, measurement type, "
                    "and observation period supplied in the snapshot."
                )
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )

    analysis = str(
        response.content
    ) # Capture the Market Agent's draft interpretation.

    if not market_analysis_is_grounded(
        analysis
    ): # Reject unsupported market claims before they enter shared state.

        analysis = build_safe_market_fallback(
            snapshot_data
        ) # Replace unsafe LLM interpretation with deterministic snapshot facts.

    return {
        "market_results": analysis, # Only grounded market analysis enters shared state.
        "messages": [
            AIMessage(
                content="Market analysis generated."
            )
        ],
        "llm_calls": (
            state.get(
                "llm_calls",
                0,
            )
            + 1
        ), # Increment workflow LLM-call count.
    }