from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from backend.state import InvestorState
from backend.knowledge import retrieve_knowledge
from tools.risk_tools import (
    calculate_portfolio_structure_metrics,
)


# =========================
# Risk Knowledge
# =========================

RISK_KNOWLEDGE_FILES = [
    "investment_philosophy.md",
    "diversification.md",
    "risk_balancing.md",
]


# =========================
# Risk Agent
# =========================

def risk_agent(
    state: InvestorState,
    llm: Any,
):
    if llm is None:
        raise ValueError(
            "An LLM is required to run the Risk Agent."
        )

    portfolio = state.get("portfolio")
    investor_profile = state.get(
        "investor_profile"
    )
    portfolio_risk_snapshot = state.get(
    "portfolio_risk_snapshot"
    )    # Retrieve the trusted deterministic risk package from shared InvestorState.

    portfolio_risk_data = (
    portfolio_risk_snapshot.model_dump(
        mode="json"
    )

    if portfolio_risk_snapshot is not None
    else {}
    ) # Convert the validated snapshot into prompt-ready data without recalculating anything.

    risk_metrics = (
        calculate_portfolio_structure_metrics(
            portfolio
        )
        if portfolio is not None
        else {}
    )

    profile_data = (
        investor_profile.model_dump(
            mode="json"
        )
        if investor_profile is not None
        else {}
    )

    risk_knowledge = retrieve_knowledge(
        query=state.get(
            "user_query",
            "",
        ),
        filenames=RISK_KNOWLEDGE_FILES,
        keywords=[
            "risk",
            "concentration",
            "risk balancing",
            "diversification",
            "risk contribution",
            "drawdown",
        ],
        max_sections=5,
        max_chars=7500,
    )

    prompt = f"""
You are the Risk Specialist for EducosysDalio.

Your job is to interpret deterministic portfolio
risk-structure calculations using EducosysDalio
risk principles.

These findings will later be combined with Portfolio,
Market, Macro and Allocation analysis by a separate
final education layer.

Investor Request:
{state.get("user_query", "")}

Investor Profile:
{profile_data}

Portfolio Agent Findings:
{state.get("portfolio_results", "")}

Deterministic Risk Metrics:
{risk_metrics}

Deterministic Portfolio Risk Snapshot:
{portfolio_risk_data}

Relevant EducosysDalio Knowledge:
{risk_knowledge}

Return ONLY these four sections:

1. CALCULATED RISK STRUCTURE

- Explain the deterministic portfolio-structure metrics
  supplied by risk_tools.py.
- Include holding weights, asset-class weights,
  largest-position weight and HHI where available.
- When Deterministic Portfolio Risk Snapshot data is
  available, also report:
  - portfolio period volatility
  - asset period volatility
  - marginal risk contribution
  - component risk contribution
  - relative risk contribution
  - calculated covariance
  - calculated correlation
- Clearly distinguish capital weight from risk contribution.

2. RISK INTERPRETATION

- Explain what the supplied deterministic calculations imply.
- Use EducosysDalio principles to interpret portfolio
  structure and measured risk.
- When risk contribution has been calculated, explain
  whether capital allocation and risk allocation differ.
- When covariance or correlation has been calculated,
  interpret only the relationships explicitly supplied.
- Clearly separate deterministic calculation from
  interpretation.

3. RISK NOT YET CALCULATED

- Identify only quantitative risk metrics that are genuinely
  absent from both Deterministic Risk Metrics and the
  Deterministic Portfolio Risk Snapshot.
- Do NOT describe volatility, covariance, correlation or
  risk contribution as unavailable when those values are
  present in the Portfolio Risk Snapshot.
- Examples of metrics that may remain unestablished include
  historical drawdown, expected return and forward-looking
  risk estimates unless explicitly supplied.

4. INVESTOR CONTEXT LIMITS
- Explain which missing InvestorProfile information
  limits personalised risk assessment.
- Keep risk capacity separate from portfolio risk.

BOUNDARIES:

Deterministic metrics supplied above are trusted
calculations.

When stating portfolio value:
- use the currency exactly as supplied in
  Deterministic Risk Metrics
- write the currency code explicitly, for example
  "20,000 GBP"
- never guess or substitute a currency symbol

Only interpret facts explicitly present in:
- Deterministic Risk Metrics
- Deterministic Portfolio Risk Snapshot
- Investor Profile
- Portfolio Agent Findings

Do NOT independently infer:
- geographic exposure
- sector exposure
- investment style or factor exposure
- leverage
- index composition
- underlying security characteristics
- currency exposure beyond what is supplied
- whether assets will move together
- whether assets are highly or weakly correlated

Do NOT independently calculate, infer or estimate:
- volatility
- correlation
- covariance
- historical drawdown
- marginal risk contribution
- contribution to total risk
- expected return
- future market performance

You MAY report and interpret volatility, correlation,
covariance, marginal risk contribution, component risk
contribution and relative risk contribution when those
values are explicitly supplied in the Deterministic
Portfolio Risk Snapshot.

Never recalculate those values inside the LLM.

If these relationships have not been calculated
from market data, state only that they are
NOT YET ESTABLISHED.

HHI is a deterministic numerical concentration metric.

When discussing HHI:
- report the calculated HHI value
- explain mechanically which capital weights produce it
- do NOT qualitatively interpret the HHI value
- do NOT use words such as high, low, significant, substantial,
  extreme, concentrated, diversified, strong or weak in relation
  to the HHI value
- do NOT infer a concentration category from HHI unless an explicit
  numerical threshold is supplied by the provided knowledge

Example of allowed wording:
"HHI is 0.625, produced by the 75% and 25% capital weights."

Example of prohibited wording:
"HHI of 0.625 indicates substantial concentration."

Do NOT claim that an asset provides or does not provide a hedge,
diversification benefit, downside protection or negative correlation
unless those relationships have been established with market data.

You may state directly observed structural facts such as:
- the portfolio has 100% equity capital exposure
- the portfolio contains no non-equity asset-class exposure

Do NOT classify capital concentration using qualitative labels such as
high, low, substantial, extreme or excessive unless an explicit
numerical threshold is supplied by the provided knowledge.

A large capital weight does NOT establish a large risk contribution.

Do NOT state or imply that a holding:
- dominates portfolio risk
- contributes disproportionately to risk
- drives portfolio volatility
- is the main source of portfolio risk

unless risk contribution has been calculated using the required
volatility and covariance data.

You may state factual capital-allocation observations such as:
- "VUSA represents 75% of portfolio capital."
- "The largest position has a 75% capital weight."
- "The portfolio has 100% equity capital exposure."

Do NOT recommend:
- purchases
- sales
- target weights
- rebalancing
- a new allocation

Those decisions belong to the Allocation Agent.

External facts about securities and markets belong
to the Market Agent.

Market data required for deeper risk calculations
belongs to the Market/Data layer.

Use short, high-signal bullets.
Complete all four sections.
"""

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are the Risk Specialist for "
                    "EducosysDalio. Interpret deterministic "
                    "risk calculations without inventing "
                    "unavailable market-risk statistics or "
                    "performing Allocation Agent "
                    "responsibilities."
                )
            ),
            HumanMessage(
                content=prompt
            ),
        ]
    )

    return {
        "risk_results": str(
            response.content
        ),
        "messages": [
            AIMessage(
                content=(
                    "Risk analysis generated."
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