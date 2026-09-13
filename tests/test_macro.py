from datetime import date
from decimal import Decimal

import pytest
from pydantic import ValidationError

from models.macro import (
    MacroObservation,
    MacroSnapshot,
    TrendDirection,
)


# =========================
# Scenario 1 — Macro Observation
# =========================

def test_macro_observation():
    observation = MacroObservation(
        indicator="Consumer Price Inflation",
        latest_value=Decimal("2.8"),
        previous_value=Decimal("3.1"),
        unit="percent",
        latest_period="2026-08",
        previous_period="2026-07",
        direction=TrendDirection.FALLING,
        source="Official Statistics Agency",
    )

    assert observation.latest_value == Decimal("2.8")
    assert observation.previous_value == Decimal("3.1")
    assert observation.direction == TrendDirection.FALLING


# =========================
# Scenario 2 — Complete Snapshot
# =========================

def test_macro_snapshot():
    snapshot = MacroSnapshot(
        geography="United Kingdom",
        geography_code="GB",
        as_of_date=date(2026, 9, 13),
        growth=MacroObservation(
            indicator="GDP Growth",
            latest_value=Decimal("0.4"),
            previous_value=Decimal("0.2"),
            unit="percent",
            latest_period="2026-Q2",
            previous_period="2026-Q1",
            direction=TrendDirection.RISING,
            source="Official Statistics Agency",
        ),
        inflation=MacroObservation(
            indicator="Consumer Price Inflation",
            latest_value=Decimal("2.8"),
            previous_value=Decimal("3.1"),
            unit="percent",
            latest_period="2026-08",
            previous_period="2026-07",
            direction=TrendDirection.FALLING,
            source="Official Statistics Agency",
        ),
        policy_rate=MacroObservation(
            indicator="Policy Rate",
            latest_value=Decimal("4.0"),
            previous_value=Decimal("4.25"),
            unit="percent",
            latest_period="2026-09",
            previous_period="2026-08",
            direction=TrendDirection.FALLING,
            source="Central Bank",
        ),
    )

    assert snapshot.geography == "United Kingdom"
    assert snapshot.growth.direction == TrendDirection.RISING
    assert snapshot.inflation.direction == TrendDirection.FALLING
    assert snapshot.policy_rate.latest_value == Decimal("4.0")


# =========================
# Scenario 3 — Partial Snapshot
# =========================

def test_partial_macro_snapshot():
    snapshot = MacroSnapshot(
        geography="India",
        geography_code="IN",
        as_of_date=date(2026, 9, 13),
    )

    assert snapshot.growth is None
    assert snapshot.inflation is None
    assert snapshot.policy_rate is None


# =========================
# Scenario 4 — Unknown Fields Rejected
# =========================

def test_unknown_fields_rejected():
    with pytest.raises(ValidationError):
        MacroSnapshot(
            geography="United States",
            geography_code="US",
            as_of_date=date(2026, 9, 13),
            made_up_field="invalid",
        )


# =========================
# Scenario 5 — Unknown Direction Allowed
# =========================

def test_unknown_direction():
    observation = MacroObservation(
        indicator="GDP Growth",
        latest_value=Decimal("0.2"),
        unit="percent",
        latest_period="2026-Q2",
        direction=TrendDirection.UNKNOWN,
        source="Official Statistics Agency",
    )

    assert observation.direction == TrendDirection.UNKNOWN
    assert observation.previous_value is None