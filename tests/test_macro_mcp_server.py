from decimal import Decimal

from mcp_servers.macro_mcp_server import (
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