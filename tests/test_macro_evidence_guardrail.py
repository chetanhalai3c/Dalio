from backend.guardrails.macro_evidence_guardrail import (
    build_safe_macro_fallback,
    macro_analysis_is_grounded,
)


# =========================
# Grounded Analysis
# =========================

def test_grounded_macro_analysis_passes():
    analysis = (
        "Growth is falling while inflation is rising. "
        "The policy rate is unchanged between the "
        "two supplied observations."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is True


# =========================
# Unsupported Analysis
# =========================

def test_unsupported_macro_analysis_fails():
    analysis = (
        "The economy appears to be in a "
        "later-stage short-term cycle."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is False


# =========================
# Safe Fallback
# =========================

def test_safe_macro_fallback_uses_snapshot():
    snapshot_data = {
        "growth": {
            "latest_value": "0.42",
            "unit": "percent",
            "direction": "falling",
        },
        "inflation": {
            "latest_value": "3.1",
            "unit": "percent",
            "direction": "rising",
        },
        "policy_rate": {
            "latest_value": "3.75",
            "unit": "percent",
            "direction": "stable",
        },
    }

    result = build_safe_macro_fallback(
        snapshot_data
    )

    assert "0.42 percent" in result
    assert "3.1 percent" in result
    assert "3.75 percent" in result

    assert (
        "specific economic regime and its causes "
        "are not established"
    ) in result

# =========================
# Live Failure Modes
# =========================

def test_later_stages_of_cycle_is_rejected():
    analysis = (
        "The pattern often appears in the "
        "later stages of a cycle."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is False


def test_stagflation_classification_is_rejected():
    analysis = (
        "This is a classic stagflation-type signal."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is False


def test_deleveraging_inference_is_rejected():
    analysis = (
        "The economy may be approaching "
        "a deleveraging phase."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is False


def test_uncertain_cycle_statement_is_allowed():
    analysis = (
        "The current position within the "
        "economic cycle is not established."
    )

    assert macro_analysis_is_grounded(
        analysis
    ) is True