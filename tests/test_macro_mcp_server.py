import asyncio
from datetime import date
from decimal import Decimal
from unittest.mock import patch

import pytest

from mcp_servers.macro_mcp_server import (
    build_macro_observation,
    build_macro_snapshot,
    calculate_direction,
    fetch_bis_policy_rate,
    fetch_oecd_growth,
    fetch_oecd_inflation,
    mcp,
)

from models.macro import (
    MacroObservation,
    TrendDirection,
)

from mcp.server import MCPServer


# =========================
# Macro Snapshot MCP Tool
# =========================

@mcp.tool()
def get_macro_snapshot(
    geography: str,
    geography_code: str,
    oecd_code: str,
    bis_code: str,
) -> dict:
    snapshot = build_macro_snapshot(
        geography=geography,
        geography_code=geography_code,
        oecd_code=oecd_code,
        bis_code=bis_code,
    )

    return snapshot.model_dump(
        mode="json"
    )


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
# =========================
# Scenario 11 — BIS Policy Rate Fetch
# =========================

def test_fetch_bis_policy_rate():
    csv_data = (
        "TIME_PERIOD,OBS_VALUE\n"
        "2026-07,4.25\n"
        "2026-08,4.00\n"
    )

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        observation = fetch_bis_policy_rate(
            "GB"
        )

    assert observation.indicator == (
        "Central Bank Policy Rate"
    )
    assert observation.latest_value == Decimal("4.00")
    assert observation.previous_value == Decimal("4.25")
    assert observation.latest_period == "2026-08"
    assert observation.previous_period == "2026-07"
    assert observation.direction == TrendDirection.FALLING
    assert observation.source == "BIS Data Portal"


# =========================
# Scenario 12 — No BIS Policy Rate Data
# =========================

def test_fetch_bis_policy_rate_without_data():
    csv_data = "TIME_PERIOD,OBS_VALUE\n"

    with patch(
        "mcp_servers.macro_mcp_server.requests.get",
        return_value=FakeResponse(csv_data),
    ):
        with pytest.raises(
            ValueError,
            match="No BIS policy-rate data found",
        ):
            fetch_bis_policy_rate(
                "GB"
            )

# =========================
# Scenario 13 — Complete Macro Snapshot
# =========================

def test_build_complete_macro_snapshot():
    growth = MacroObservation(
        indicator="Real GDP Growth",
        latest_value=Decimal("0.4"),
        previous_value=Decimal("0.2"),
        unit="percent",
        latest_period="2026-Q2",
        previous_period="2026-Q1",
        direction=TrendDirection.RISING,
        source="OECD Data Explorer",
    )

    inflation = MacroObservation(
        indicator="Consumer Price Inflation",
        latest_value=Decimal("3.1"),
        previous_value=Decimal("2.8"),
        unit="percent",
        latest_period="2026-07",
        previous_period="2026-06",
        direction=TrendDirection.RISING,
        source="OECD Data Explorer",
    )

    policy_rate = MacroObservation(
        indicator="Central Bank Policy Rate",
        latest_value=Decimal("3.75"),
        previous_value=Decimal("3.75"),
        unit="percent",
        latest_period="2026-08",
        previous_period="2026-07",
        direction=TrendDirection.STABLE,
        source="BIS Data Portal",
    )

    with patch(
        "mcp_servers.macro_mcp_server.fetch_oecd_growth",
        return_value=growth,
    ), patch(
        "mcp_servers.macro_mcp_server.fetch_oecd_inflation",
        return_value=inflation,
    ), patch(
        "mcp_servers.macro_mcp_server.fetch_bis_policy_rate",
        return_value=policy_rate,
    ):
        snapshot = build_macro_snapshot(
            geography="United Kingdom",
            geography_code="GB",
            oecd_code="GBR",
            bis_code="GB",
        )

    assert snapshot.geography == "United Kingdom"
    assert snapshot.geography_code == "GB"
    assert snapshot.as_of_date == date.today()
    assert snapshot.growth == growth
    assert snapshot.inflation == inflation
    assert snapshot.policy_rate == policy_rate


# =========================
# Scenario 14 — Partial Macro Snapshot
# =========================

def test_build_partial_macro_snapshot():
    inflation = MacroObservation(
        indicator="Consumer Price Inflation",
        latest_value=Decimal("3.1"),
        unit="percent",
        latest_period="2026-07",
        direction=TrendDirection.UNKNOWN,
        source="OECD Data Explorer",
    )

    with patch(
        "mcp_servers.macro_mcp_server.fetch_oecd_growth",
        side_effect=ValueError("No growth data"),
    ), patch(
        "mcp_servers.macro_mcp_server.fetch_oecd_inflation",
        return_value=inflation,
    ), patch(
        "mcp_servers.macro_mcp_server.fetch_bis_policy_rate",
        side_effect=ValueError("No policy-rate data"),
    ):
        snapshot = build_macro_snapshot(
            geography="Example Country",
            geography_code="EX",
            oecd_code="EXM",
            bis_code="EX",
        )

    assert snapshot.growth is None
    assert snapshot.inflation == inflation
    assert snapshot.policy_rate is None

# =========================
# Scenario 15 — MCP Tool Registered
# =========================

def test_macro_snapshot_mcp_tool_registered():
    tools = asyncio.run(
        mcp.list_tools()
    )

    tool_names = [
        tool.name
        for tool in tools
    ]

    assert "get_macro_snapshot" in tool_names