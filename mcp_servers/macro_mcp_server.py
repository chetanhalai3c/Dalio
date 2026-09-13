from decimal import Decimal

from models.macro import TrendDirection


# =========================
# Trend Direction Helper
# =========================

def calculate_direction(
    latest_value: Decimal,
    previous_value: Decimal | None,
) -> TrendDirection:
    if previous_value is None:
        return TrendDirection.UNKNOWN

    if latest_value > previous_value:
        return TrendDirection.RISING

    if latest_value < previous_value:
        return TrendDirection.FALLING

    return TrendDirection.STABLE

# =========================
# Macro Observation Builder
# =========================

def build_macro_observation(
    indicator: str,
    latest_value: Decimal,
    previous_value: Decimal | None,
    unit: str,
    latest_period: str,
    previous_period: str | None,
    source: str,
    source_url: str | None = None,
):
    from models.macro import MacroObservation

    return MacroObservation(
        indicator=indicator,
        latest_value=latest_value,
        previous_value=previous_value,
        unit=unit,
        latest_period=latest_period,
        previous_period=previous_period,
        direction=calculate_direction(
            latest_value,
            previous_value,
        ),
        source=source,
        source_url=source_url,
    )