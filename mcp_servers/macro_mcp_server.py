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