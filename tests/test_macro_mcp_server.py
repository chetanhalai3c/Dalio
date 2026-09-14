from decimal import Decimal
from unittest.mock import patch

import pytest

from mcp_servers.macro_mcp_server import (
    build_macro_observation,
    calculate_direction,
    fetch_oecd_growth,
    fetch_oecd_inflation,
)

from models.macro import TrendDirection

# =========================
# Fake HTTP Response
# =========================

class FakeResponse:
    def __init__(
        self,
        text: str,
        url: str = "https://example.com/oecd",
    ):
        self.text = text
        self.url = url

    def raise_for_status(self):
        return None

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

# =========================
# Scenario 7 — OECD Inflation Fetch
# =========================

def test_fetch_oecd_inflation():
    csv_data = (
        "TIME_PERIOD,OBS_VALUE\n"
        "2026-07,4.0\n"
        "2026-08,3.8\n"
    )

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        observation = fetch_oecd_inflation(
            "GBR"
        )

    assert observation.indicator == (
        "Consumer Price Inflation"
    )
    assert observation.latest_value == Decimal("3.8")
    assert observation.previous_value == Decimal("4.0")
    assert observation.latest_period == "2026-08"
    assert observation.previous_period == "2026-07"
    assert observation.direction == TrendDirection.FALLING
    assert observation.source == "OECD Data Explorer"


# =========================
# Scenario 8 — No OECD Data
# =========================

def test_fetch_oecd_inflation_without_data():
    csv_data = "TIME_PERIOD,OBS_VALUE\n"

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        with pytest.raises(
            ValueError,
            match="No OECD inflation data found",
        ):
            fetch_oecd_inflation(
                "GBR"
            )

# =========================
# Scenario 9 — OECD GDP Growth Fetch
# =========================

def test_fetch_oecd_growth():
    csv_data = (
        "TIME_PERIOD,OBS_VALUE\n"
        "2026-Q1,0.2\n"
        "2026-Q2,0.4\n"
    )

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        observation = fetch_oecd_growth(
            "GBR"
        )

    assert observation.indicator == "Real GDP Growth"
    assert observation.latest_value == Decimal("0.4")
    assert observation.previous_value == Decimal("0.2")
    assert observation.latest_period == "2026-Q2"
    assert observation.previous_period == "2026-Q1"
    assert observation.direction == TrendDirection.RISING
    assert observation.source == "OECD Data Explorer"


# =========================
# Scenario 10 — No OECD GDP Data
# =========================

def test_fetch_oecd_growth_without_data():
    csv_data = "TIME_PERIOD,OBS_VALUE\n"

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        with pytest.raises(
            ValueError,
            match="No OECD GDP growth data found",
        ):
            fetch_oecd_growth(
                "GBR"
            )