from decimal import Decimal # Precise numeric values for market data.

from mcp.server.mcpserver import MCPServer # Exposes market functions as MCP tools later.

from models.market import (
    AssetClass, # Controlled asset categories.
    MarketDirection, # Rising / falling / stable / unknown.
    MarketObservation, # Trusted model for ONE market observation.
    MeasurementType, # Price / index / yield / rate.
)


# =========================
# MCP Server
# Creates the Market MCP server that will later expose market-data tools.
# =========================

mcp = MCPServer(
    "EducosysDalio Market Server"
)


# =========================
# Market Direction
# Converts numeric change into a deterministic market direction.
# =========================

def calculate_market_direction(
    latest_value: Decimal,
    previous_value: Decimal | None,
) -> MarketDirection: # LLM does not decide whether the market rose or fell.

    if previous_value is None: # Cannot compare when only one observation exists.
        return MarketDirection.UNKNOWN

    if latest_value > previous_value: # Latest value is higher than previous value.
        return MarketDirection.RISING

    if latest_value < previous_value: # Latest value is lower than previous value.
        return MarketDirection.FALLING

    return MarketDirection.STABLE # Equal values mean no change.


# =========================
# Market Observation Builder
# Converts normalised provider data into our trusted MarketObservation contract.
# =========================

def build_market_observation(
    asset_name: str,
    asset_class: AssetClass,
    measurement_type: MeasurementType,
    latest_value: Decimal,
    previous_value: Decimal | None,
    unit: str,
    latest_period: str,
    previous_period: str | None,
    source: str,
    symbol: str | None = None,
    geography: str | None = None,
    currency: str | None = None,
    source_url: str | None = None,
) -> MarketObservation: # One reusable builder keeps provider outputs consistent.

    direction = calculate_market_direction(
        latest_value=latest_value,
        previous_value=previous_value,
    ) # Derive factual direction before data reaches the LLM.

    return MarketObservation(
        asset_name=asset_name,
        asset_class=asset_class,
        symbol=symbol,
        geography=geography,
        measurement_type=measurement_type,
        latest_value=latest_value,
        previous_value=previous_value,
        unit=unit,
        currency=currency,
        latest_period=latest_period,
        previous_period=previous_period,
        direction=direction,
        source=source,
        source_url=source_url,
    ) # Return data already validated against models/market.py.