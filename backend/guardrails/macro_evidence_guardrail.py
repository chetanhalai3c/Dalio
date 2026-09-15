import re


# =========================
# Why This Evidence Gate Exists
# =========================

# The Macro Agent uses an LLM to interpret trusted macroeconomic
# data from the MacroSnapshot.
#
# Live testing showed that even a powerful model can take accurate
# facts and then make plausible-sounding conclusions that are not
# actually established by the supplied evidence.
#
# Example:
#
# MacroSnapshot says:
# - growth is falling
# - inflation is rising
# - policy rate is unchanged
#
# The LLM may then infer:
# - the economy is late-cycle
# - the economy is entering stagflation
# - deleveraging is beginning
# - policymakers have limited room to cut rates
# - debt-servicing pressure is increasing
#
# Those conclusions may be economically plausible, but they are
# not proven by the MacroSnapshot.
#
# This guardrail therefore sits AFTER generation:
#
# MacroSnapshot
#     ↓
# Macro Agent / LLM
#     ↓
# Draft analysis
#     ↓
# Evidence Guardrail
#     ↓
# Grounded analysis OR conservative fallback
#
# The purpose is to separate:
#
# GENERATION
# "What does the LLM think the data means?"
#
# from:
#
# VALIDATION
# "Do we have enough evidence to return that interpretation?"
#
# This is intentionally conservative because EducosysDalio is a
# financial-advice system where unsupported confidence is more
# dangerous than admitting that something is not yet established.


# =========================
# Unsupported Macro Concepts
# =========================

# Exact phrase matching was too brittle because an LLM can express
# the same unsupported idea in many different ways.
#
# These regular-expression patterns therefore detect broader
# unsupported concepts rather than one exact sentence.
UNSUPPORTED_MACRO_PATTERNS = (
    # Unsupported cycle-stage classification.
    r"\b(?:late|later)[ -]?stage(?:s)?(?: of)? "
    r"(?:(?:the|a) )?(?:short-term )?cycle\b",

    r"\b(?:late|later)[ -]?cycle\b",

    # Unsupported regime classification.
    r"\bstagflation(?:ary|-type)?\b",

    # Unsupported deleveraging / adjustment-stage inference.
    r"\bdeleveraging(?: phase)?\b",

    r"\badjustment phase\b",

    # Unsupported claims about room for monetary-policy changes.
    r"\b(?:limited|little|less) room "
    r"(?:for|to).*?(?:cut|eas)",

    r"\broom for conventional easing\b",

    # Policy-bound concepts that are not present in MacroSnapshot.
    r"\beffective lower bound\b",

    r"\bneutral rate\b",

    r"\bpolicy[- ]rate gap\b",

    r"\bpractical policy bounds?\b",

    # Unsupported unconventional-policy inference.
    r"\bbalance[- ]sheet operations?\b",

    r"\bcredit guarantees?\b",

    r"\bquantitative easing\b",

    r"\bunconventional monetary[- ]policy\b",

    # Unsupported application of debt-servicing conclusions.
    r"\bdebt[- ]servicing pressure\b",

    r"\bdebt[- ]service pressure\b",

    r"\bdebt[- ]servicing burden\b",

    r"\bdebt[- ]service burden\b",

    r"\bcapacity to service debt\b",
)


# =========================
# Uncertainty Markers
# =========================

# A restricted concept is allowed when the model is explicitly
# saying that the concept is NOT established by the evidence.
UNCERTAINTY_MARKERS = (
    "not established",
    "cannot be established",
    "cannot determine",
    "cannot be determined",
    "not supplied",
    "not provided",
    "not available",
    "no evidence",
    "insufficient evidence",
    "insufficient data",
    "does not establish",
    "do not establish",
    "unknown",
    "uncertain",
)


# =========================
# Evidence Validation
# =========================

def macro_analysis_is_grounded(
    analysis: str,
) -> bool:
    # Normalise the response so matching is case-insensitive.
    analysis_lower = analysis.lower()

    # Break the response into smaller units.
    # This lets us judge an unsupported concept in the sentence
    # where it appears rather than rejecting based only on one
    # phrase appearing somewhere in the entire answer.
    statements = re.split(
        r"(?<=[.!?])\s+|\n+",
        analysis_lower,
    )

    for statement in statements:
        statement = statement.strip()

        if not statement:
            continue

        # If the model explicitly says something is unknown or
        # not established, allow that statement.
        contains_uncertainty = any(
            marker in statement
            for marker in UNCERTAINTY_MARKERS
        )

        if contains_uncertainty:
            continue

        # Reject the draft if a statement positively introduces
        # one of the unsupported macro concepts.
        contains_unsupported_concept = any(
            re.search(
                pattern,
                statement,
            )
            for pattern in UNSUPPORTED_MACRO_PATTERNS
        )

        if contains_unsupported_concept:
            return False

    return True


# =========================
# Safe Macro Fallback
# =========================

def build_safe_macro_fallback(
    snapshot_data: dict,
) -> str:
    # Pull only facts already present in the trusted MacroSnapshot.
    growth = snapshot_data.get(
        "growth"
    )

    inflation = snapshot_data.get(
        "inflation"
    )

    policy_rate = snapshot_data.get(
        "policy_rate"
    )

    # Build the fallback deterministically rather than asking
    # another LLM to reinterpret the evidence.
    lines = [
        "1. CURRENT MACRO SNAPSHOT",
        "",
    ]

    if growth:
        lines.append(
            f"- Growth: {growth['latest_value']} "
            f"{growth['unit']}, direction "
            f"{growth['direction']}."
        )

    if inflation:
        lines.append(
            f"- Inflation: {inflation['latest_value']} "
            f"{inflation['unit']}, direction "
            f"{inflation['direction']}."
        )

    if policy_rate:
        lines.append(
            f"- Policy rate: {policy_rate['latest_value']} "
            f"{policy_rate['unit']}, direction "
            f"{policy_rate['direction']}."
        )

    # If the richer LLM analysis failed validation, return a
    # deliberately conservative interpretation.
    lines.extend(
        [
            "",
            "2. ECONOMIC REGIME INTERPRETATION",
            "",
            (
                "- The observed growth, inflation and policy-rate "
                "directions can be interpreted together, but the "
                "specific economic regime and its causes are not "
                "established by this snapshot alone."
            ),
            "",
            "3. DALIO-STYLE EDUCATION",
            "",
            (
                "- The Dalio framework evaluates how growth, "
                "inflation and policy interact rather than relying "
                "on a single indicator."
            ),
            (
                "- Current observations should provide context, "
                "not be treated as precise forecasts or timing signals."
            ),
            "",
            "4. NOT YET ESTABLISHED",
            "",
            "- Causes of the growth change.",
            "- Causes of the inflation change.",
            "- Fiscal-policy conditions.",
            "- Labour-market conditions.",
            "- Debt levels and debt-servicing pressure.",
            "- Market expectations.",
            "- Policymaker motives.",
            "- The direction of any tightening or easing cycle.",
            "- Future economic or market outcomes.",
        ]
    )

    return "\n".join(
        lines
    )