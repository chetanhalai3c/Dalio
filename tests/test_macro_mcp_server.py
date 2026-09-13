from decimal import Decimal

from mcp_servers.macro_mcp_server import (
    build_macro_observation,
    calculate_direction,
)
from models.macro import TrendDirection


# =========================
# Scenario 1 — Rising
# =========================

def test_direction_rising():
    result = calculate_direction(
        Decimal("3.1"),
        Decimal("2.8"),
    )

    assert result == TrendDirection.RISING


# =========================
# Scenario 2 — Falling
# =========================

def test_direction_falling():
    result = calculate_direction(
        Decimal("2.8"),
        Decimal("3.1"),
    )

    assert result == TrendDirection.FALLING


# =========================
# Scenario 3 — Stable
# =========================

def test_direction_stable():
    result = calculate_direction(
        Decimal("3.0"),
        Decimal("3.0"),
    )

    assert result == TrendDirection.STABLE


# =========================
# Scenario 4 — Unknown
# =========================

def test_direction_unknown():
    result = calculate_direction(
        Decimal("3.0"),
        None,
    )

    assert result == TrendDirection.UNKNOWN

# =========================
# Scenario 5 — Build Observation
# =========================

def test_build_macro_observation():
    observation = build_macro_observation(
        indicator="Consumer Price Inflation",
        latest_value=Decimal("2.8"),
        previous_value=Decimal("3.1"),
        unit="percent",
        latest_period="2026-08",
        previous_period="2026-07",
        source="Official Statistics Agency",
        source_url="https://example.com",
    )

    assert observation.indicator == "Consumer Price Inflation"
    assert observation.latest_value == Decimal("2.8")
    assert observation.previous_value == Decimal("3.1")
    assert observation.direction == TrendDirection.FALLING
    assert observation.source == "Official Statistics Agency"


# =========================
# Scenario 6 — Observation Without Previous Value
# =========================

def test_build_observation_without_previous_value():
    observation = build_macro_observation(
        indicator="Policy Rate",
        latest_value=Decimal("4.0"),
        previous_value=None,
        unit="percent",
        latest_period="2026-09",
        previous_period=None,
        source="Central Bank",
    )

    assert observation.latest_value == Decimal("4.0")
    assert observation.previous_value is None
    assert observation.direction == TrendDirection.UNKNOWN