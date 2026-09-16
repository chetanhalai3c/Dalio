from decimal import Decimal # Precise numeric values for market tests.

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