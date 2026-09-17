from backend.guardrails.market_evidence_guardrail import (
    build_safe_market_fallback,
    market_analysis_is_grounded,
)


# =========================
# Grounded Market Analysis
# Direct observations from MarketSnapshot should pass.
# =========================

def test_grounded_market_analysis_passes():

    analysis = (
        "SPY is falling in the supplied observation. "
        "The US 10-year Treasury yield is rising."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is True


# =========================
# Unsupported Sentiment
# Market prices alone do not establish investor behaviour.
# =========================

def test_risk_off_claim_is_rejected():

    analysis = (
        "Markets are clearly moving into a risk-off environment."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is False


# =========================
# Unsupported Correlation
# Correlation must be calculated deterministically first.
# =========================

def test_correlation_claim_is_rejected():

    analysis = (
        "Gold is negatively correlated with equities."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is False


# =========================
# Unsupported Expectations
# Snapshot prices do not establish what markets expect.
# =========================

def test_market_expectations_are_rejected():

    analysis = (
        "Markets expect interest-rate cuts."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is False


# =========================
# Unsupported Causation
# Observed movement does not prove why the movement occurred.
# =========================

def test_causal_market_claim_is_rejected():

    analysis = (
        "Equities fell because investors fear a recession."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is False


# =========================
# Explicit Uncertainty
# Restricted concepts are safe when clearly stated as unknown.
# =========================

def test_uncertain_sentiment_statement_is_allowed():

    analysis = (
        "Investor sentiment is not established by the supplied snapshot."
    )

    assert market_analysis_is_grounded(
        analysis
    ) is True


# =========================
# Safe Fallback
# Fallback must reproduce trusted observations without inventing analysis.
# =========================

def test_safe_market_fallback_uses_snapshot():

    snapshot_data = {
        "observations": [
            {
                "asset_name": "SPDR S&P 500 ETF Trust",
                "latest_value": "754.13",
                "unit": "price",
                "measurement_type": "price",
                "direction": "falling",
                "latest_period": "2026-09-16",
            },
            {
                "asset_name": "US 10-Year Treasury Yield",
                "latest_value": "4.97",
                "unit": "percent",
                "measurement_type": "yield",
                "direction": "rising",
                "latest_period": "2026-09-14",
            },
        ]
    }

    result = build_safe_market_fallback(
        snapshot_data
    )

    assert (
        "SPDR S&P 500 ETF Trust: 754.13 price"
        in result
    )

    assert (
        "US 10-Year Treasury Yield: 4.97 percent"
        in result
    )

    assert (
        "investor sentiment, correlation and relative performance "
        "are not established"
        in result
    )
    