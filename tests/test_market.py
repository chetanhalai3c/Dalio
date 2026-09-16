from datetime import date # Used to create fixed snapshot dates in tests.
from decimal import Decimal # Creates precise numeric market values.

import pytest # Testing framework; also lets us assert that specific errors should happen.
from pydantic import ValidationError # Error expected when Pydantic model validation fails.

from models.market import (
    AssetClass, # Allowed asset categories.
    MarketDirection, # Allowed market direction values.
    MarketObservation, # Model for ONE market observation.
    MarketSnapshot, # Model containing multiple observations.
    MeasurementType, # Defines whether value is price/index/yield/rate.
)


# =========================
# Market Observation
# Valid data should successfully create a MarketObservation.
# =========================

def test_market_observation(): # Tests that a normal valid market observation is created correctly.

    observation = MarketObservation( # Create one test market observation.
        asset_name="Example Equity Index", # Example instrument name.
        asset_class=AssetClass.EQUITIES, # Must use an allowed AssetClass.
        symbol="TEST", # Example ticker.
        geography="US", # Market geography.
        measurement_type=MeasurementType.INDEX, # Value represents an index level.
        latest_value=Decimal("100"), # Latest test value.
        previous_value=Decimal("95"), # Previous test value.
        unit="index_points", # Unit describing the numbers.
        currency="USD", # Currency context.
        latest_period="2026-09-15", # Latest observation date.
        previous_period="2026-09-14", # Previous observation date.
        direction=MarketDirection.RISING, # Explicitly mark the test trend as rising.
        source="Example Provider", # Example evidence source.
    )

    assert observation.asset_class == AssetClass.EQUITIES # Check asset class was stored correctly.
    assert observation.direction == MarketDirection.RISING # Check direction was stored correctly.
    assert observation.latest_value == Decimal("100") # Check numeric value was preserved correctly.


# =========================
# Market Snapshot
# A snapshot should successfully contain MarketObservation objects.
# =========================

def test_market_snapshot(): # Tests that observations can be grouped inside MarketSnapshot.

    observation = MarketObservation( # First create one valid observation.
        asset_name="Example Gold Price",
        asset_class=AssetClass.GOLD,
        measurement_type=MeasurementType.PRICE,
        latest_value=Decimal("100"),
        previous_value=Decimal("98"),
        unit="price",
        currency="USD",
        latest_period="2026-09-15",
        previous_period="2026-09-14",
        direction=MarketDirection.RISING,
        source="Example Provider",
    )

    snapshot = MarketSnapshot( # Put the observation inside a broader market snapshot.
        as_of_date=date(2026, 9, 15), # Date represented by this market snapshot.
        investor_country="GB", # Investor context.
        base_currency="GBP", # Investor's base currency.
        observations=[observation], # Store our MarketObservation inside the list.
    )

    assert len(snapshot.observations) == 1 # Confirm exactly one observation was stored.
    assert snapshot.observations[0].asset_class == AssetClass.GOLD # Confirm that observation is gold.


# =========================
# Empty Snapshot
# Snapshot should safely default to an empty observations list.
# =========================

def test_empty_market_snapshot(): # Tests Field(default_factory=list) behaviour.

    snapshot = MarketSnapshot(
        as_of_date=date(2026, 9, 15),
    )
    # No observations supplied.

    assert snapshot.observations == [] # Model should automatically create an empty list.


# =========================
# Strict Validation
# Unexpected fields should be rejected rather than entering trusted state.
# =========================

def test_unknown_fields_rejected(): # Tests StrictBaseModel's extra="forbid" rule.

    with pytest.raises(
        ValidationError
    ): # The test PASSES only if Pydantic raises ValidationError.

        MarketObservation(
            asset_name="Example Asset",
            asset_class="equities",
            measurement_type="price",
            latest_value=Decimal("100"),
            unit="USD",
            latest_period="2026-09-15",
            source="Example Provider",
            unknown_field="should fail", # Not defined in MarketObservation, so must be rejected.
        )


# =========================
# Asset Class Validation
# Values outside the AssetClass enum should be rejected.
# =========================

def test_unknown_asset_class_rejected(): # Tests that arbitrary asset categories cannot enter the model.

    with pytest.raises(
        ValidationError
    ): # Again, ValidationError means this test is behaving correctly.

        MarketObservation(
            asset_name="Example Asset",
            asset_class="unknown_asset_class", # Invalid because this is not in AssetClass.
            measurement_type="price",
            latest_value=Decimal("100"),
            unit="USD",
            latest_period="2026-09-15",
            source="Example Provider",
        )