import re


# =========================
# Unsupported Market Concepts
# Detects claims that are not established by the current MarketSnapshot.
# =========================

UNSUPPORTED_MARKET_PATTERNS = (
    # Unsupported investor-behaviour / sentiment claims.
    r"\brisk[- ]on\b",
    r"\brisk[- ]off\b",
    r"\brisk appetite\b",
    r"\binvestor sentiment\b",
    r"\binvestor positioning\b",

    # Unsupported expectations.
    r"\bmarket expectations?\b",
    r"\bmarkets? expect(?:s|ed|ing)?\b",
    r"\brate[- ]cut expectations?\b",
    r"\brate[- ]hike expectations?\b",

    # Unsupported macro conclusions from market prices.
    r"\brecession probability\b",
    r"\brecession risk\b",
    r"\brecession fears?\b",
    r"\bstagflation\b",

    # Metrics that are not currently calculated by the data layer.
    r"\bcorrelation(?:s)?\b",
    r"\bcorrelated\b",
    r"\bvolatility\b",
    r"\bdrawdown(?:s)?\b",
    r"\brelative strength\b",
    r"\breal yields?\b",

    # Unsupported performance / forecasting claims.
    r"\boutperform(?:s|ed|ing)?\b",
    r"\bunderperform(?:s|ed|ing)?\b",
    r"\bexpected return(?:s)?\b",
    r"\breturn forecast(?:s)?\b",
    r"\bprice target(?:s)?\b",

    # Portfolio actions belong to the Allocation Agent.
    r"\btarget weights?\b",
    r"\brebalanc(?:e|ed|ing)\b",
    r"\bshould buy\b",
    r"\bshould sell\b",
)


# =========================
# Unsupported Causal Claims
# Stops the model from explaining market moves without supplied evidence.
# =========================

UNSUPPORTED_CAUSAL_PATTERNS = (
    r"\b(?:rose|fell|rising|falling|declined|increased|decreased)"
    r".*?\b(?:because|due to|driven by)\b",

    r"\b(?:because|due to|driven by)"
    r".*?\b(?:rose|fell|rising|falling|declined|increased|decreased)\b",
)


# =========================
# Uncertainty Markers
# Restricted concepts are allowed when explicitly described as unknown.
# =========================

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
# Checks whether the Market Agent stayed within evidence boundaries.
# =========================

def market_analysis_is_grounded(
    analysis: str,
) -> bool:

    analysis_lower = analysis.lower()

    statements = re.split(
        r"(?<=[.!?])\s+|\n+",
        analysis_lower,
    ) # Validate each statement independently.

    for statement in statements:
        statement = statement.strip()

        if not statement:
            continue

        contains_uncertainty = any(
            marker in statement
            for marker in UNCERTAINTY_MARKERS
        )

        if contains_uncertainty:
            continue # Explicit uncertainty is safe.

        contains_unsupported_concept = any(
            re.search(
                pattern,
                statement,
            )
            for pattern in UNSUPPORTED_MARKET_PATTERNS
        )

        if contains_unsupported_concept:
            return False

        contains_unsupported_cause = any(
            re.search(
                pattern,
                statement,
            )
            for pattern in UNSUPPORTED_CAUSAL_PATTERNS
        )

        if contains_unsupported_cause:
            return False

    return True


# =========================
# Safe Market Fallback
# Builds a deterministic response using only trusted MarketSnapshot facts.
# =========================

def build_safe_market_fallback(
    snapshot_data: dict,
) -> str:

    observations = snapshot_data.get(
        "observations",
        [],
    )

    lines = [
        "1. CURRENT MARKET SNAPSHOT",
        "",
    ]

    if observations:
        for observation in observations:

            asset_name = observation.get(
                "asset_name",
                "Unknown asset",
            )

            latest_value = observation.get(
                "latest_value",
                "unknown",
            )

            unit = observation.get(
                "unit",
                "",
            )

            measurement_type = observation.get(
                "measurement_type",
                "unknown",
            )

            direction = observation.get(
                "direction",
                "unknown",
            )

            latest_period = observation.get(
                "latest_period",
                "unknown",
            )

            lines.append(
                f"- {asset_name}: {latest_value} {unit}, "
                f"measurement {measurement_type}, "
                f"direction {direction}, "
                f"period {latest_period}."
            )

    else:
        lines.append(
            "- No validated market observations are currently available."
        )

    lines.extend(
        [
            "",
            "2. CROSS-ASSET INTERPRETATION",
            "",
            (
                "- The supplied observations can be compared only at "
                "the level explicitly supported by the snapshot, such "
                "as their observed directions and metadata."
            ),
            (
                "- Broader market regime, causation, investor sentiment, "
                "correlation and relative performance are not established "
                "by this snapshot alone."
            ),
            "",
            "3. DALIO-STYLE EDUCATION",
            "",
            (
                "- A diversified framework considers economically distinct "
                "asset exposures rather than treating one recent market move "
                "as a portfolio timing signal."
            ),
            (
                "- Current market observations provide context but do not "
                "by themselves justify forecasts or allocation changes."
            ),
            "",
            "4. NOT YET ESTABLISHED",
            "",
            "- Causes of the observed market movements.",
            "- Market-wide investor sentiment or risk appetite.",
            "- Market expectations for future policy changes.",
            "- Volatility or drawdown conditions.",
            "- Correlations between assets.",
            "- Relative performance across incompatible measurements.",
            "- Future asset returns or price targets.",
            "- Recommended portfolio allocation or trades.",
        ]
    )

    return "\n".join(
        lines
    )
