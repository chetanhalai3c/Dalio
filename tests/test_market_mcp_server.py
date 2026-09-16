from decimal import Decimal # Precise numeric values for market tests.
from mcp_servers.market_mcp_server import (
    build_market_observation,
    calculate_market_direction,
    fetch_equity_market, # Fetches real-provider-style equity data.
)
from models.market import (
    AssetClass, # Used to verify asset classification.
    MarketDirection, # Expected deterministic direction.
    MeasurementType, # Expected type of market measurement.
)

from mcp_servers.market_mcp_server import (
    build_market_observation, # Converts provider-style values into our contract.
    calculate_market_direction, # Calculates rising/falling/stable/unknown.
)


# =========================
# Rising Direction
# Latest value above previous value should be RISING.
# =========================

def test_direction_rising(): # Tests deterministic upward movement.

    direction = calculate_market_direction(
        latest_value=Decimal("105"),
        previous_value=Decimal("100"),
    )

    assert direction == MarketDirection.RISING


# =========================
# Falling Direction
# Latest value below previous value should be FALLING.
# =========================

def test_direction_falling(): # Tests deterministic downward movement.

    direction = calculate_market_direction(
        latest_value=Decimal("95"),
        previous_value=Decimal("100"),
    )

    assert direction == MarketDirection.FALLING


# =========================
# Stable Direction
# Equal values should be STABLE.
# =========================

def test_direction_stable(): # Tests unchanged market data.

    direction = calculate_market_direction(
        latest_value=Decimal("100"),
        previous_value=Decimal("100"),
    )

    assert direction == MarketDirection.STABLE


# =========================
# Unknown Direction
# Missing previous value means direction cannot yet be calculated.
# =========================

def test_direction_unknown(): # Tests safe behaviour when comparison data is unavailable.

    direction = calculate_market_direction(
        latest_value=Decimal("100"),
        previous_value=None,
    )

    assert direction == MarketDirection.UNKNOWN


# =========================
# Market Observation Builder
# Normalised provider data should become a valid MarketObservation.
# =========================

def test_build_market_observation(): # Tests the bridge between provider data and our model.

    observation = build_market_observation(
        asset_name="Example Equity Index",
        asset_class=AssetClass.EQUITIES,
        measurement_type=MeasurementType.INDEX,
        latest_value=Decimal("105"),
        previous_value=Decimal("100"),
        unit="index_points",
        latest_period="2026-09-16",
        previous_period="2026-09-15",
        source="Example Provider",
        symbol="TEST",
        geography="US",
        currency="USD",
    )

    assert observation.asset_name == "Example Equity Index"
    assert observation.asset_class == AssetClass.EQUITIES
    assert observation.measurement_type == MeasurementType.INDEX
    assert observation.direction == MarketDirection.RISING
    assert observation.latest_value == Decimal("105")


# =========================
# Observation Without Previous Value
# Missing comparison data should still create a valid observation.
# =========================

def test_build_observation_without_previous_value(): # Tests partial but valid market data.

    observation = build_market_observation(
        asset_name="Example Gold Price",
        asset_class=AssetClass.GOLD,
        measurement_type=MeasurementType.PRICE,
        latest_value=Decimal("2500"),
        previous_value=None,
        unit="price",
        latest_period="2026-09-16",
        previous_period=None,
        source="Example Provider",
        currency="USD",
    )

    assert observation.previous_value is None
    assert observation.direction == MarketDirection.UNKNOWN

# =========================
# Equity Market Fetcher
# Provider data should become a validated EQUITIES MarketObservation.
# =========================

def test_fetch_equity_market(
    monkeypatch,
): # Tests provider parsing without making a real internet request.

    class FakeResponse: # Simulates the HTTP response from Alpha Vantage.
        text = (
            "timestamp,open,high,low,close,volume\n"
            "2026-09-16,100,106,99,105,1000\n"
            "2026-09-15,96,101,95,100,900\n"
        )

        def raise_for_status(
            self,
        ): # Simulated successful HTTP response.
            return None

    def fake_get(
        url,
        params,
        timeout,
    ): # Replaces requests.get during this test.
        assert params["function"] == "TIME_SERIES_DAILY"
        assert params["symbol"] == "TEST"
        assert params["apikey"] == "test-key"

        return FakeResponse()

    monkeypatch.setattr(
        "mcp_servers.market_mcp_server.requests.get",
        fake_get,
    )

    observation = fetch_equity_market(
        symbol="TEST",
        asset_name="Example Equity Market",
        geography="US",
        currency="USD",
        api_key="test-key",
    )

    assert observation.asset_class == AssetClass.EQUITIES
    assert observation.measurement_type == MeasurementType.PRICE
    assert observation.latest_value == Decimal("105")
    assert observation.previous_value == Decimal("100")
    assert observation.direction == MarketDirection.RISING
    assert observation.latest_period == "2026-09-16"


# =========================
# Invalid Equity Provider Response
# Bad provider data should not enter trusted Market state.
# =========================

def test_fetch_equity_market_rejects_invalid_data(
    monkeypatch,
): # Tests safe failure when provider data does not match expectations.

    class FakeResponse:
        text = '{"Information": "Provider error"}'

        def raise_for_status(
            self,
        ):
            return None

    def fake_get(
        url,
        params,
        timeout,
    ):
        return FakeResponse()

    monkeypatch.setattr(
        "mcp_servers.market_mcp_server.requests.get",
        fake_get,
    )

    import pytest

    with pytest.raises(
        ValueError
    ):
        fetch_equity_market(
            symbol="TEST",
            asset_name="Example Equity Market",
            geography="US",
            currency="USD",
            api_key="test-key",
        )