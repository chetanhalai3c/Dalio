from decimal import Decimal # Precise numeric values for market data.
import csv # Parses provider CSV responses into Python rows.
import os # Reads the Alpha Vantage API key from environment variables.
from io import StringIO # Lets csv.DictReader read the HTTP response text.
from datetime import date

import requests # Makes HTTP requests to the external market-data provider.
from mcp.server.mcpserver import MCPServer # Exposes market functions as MCP tools later.

from models.market import (
    AssetClass, # Controlled asset categories.
    MarketDirection, # Rising / falling / stable / unknown.
    MarketObservation, # Trusted model for ONE market observation.
    MeasurementType, # Price / index / yield / rate.
    MarketSnapshot,
)

from decimal import Decimal # Precise numeric values for market data.
# =========================
# MCP Server
# Creates the Market MCP server that will later expose market-data tools.
# =========================

mcp = MCPServer(
    "EducosysDalio Market Server"
)

# =========================
# Alpha Vantage Configuration
# Base endpoint used for external equity/ETF market data.
# =========================

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
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

# =========================
# Equity Market Fetcher
# Fetches real equity/ETF data and converts it into our MarketObservation contract.
# =========================

def fetch_equity_market(
    symbol: str,
    asset_name: str,
    geography: str,
    currency: str,
    api_key: str | None = None,
) -> MarketObservation: # External provider data enters our trusted model here.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can read it from .env/environment.

    if not resolved_api_key: # Never make an external request without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "TIME_SERIES_DAILY", # Request daily market prices.
        "symbol": symbol, # Provider ticker for the equity/ETF.
        "outputsize": "compact", # Only recent observations are required.
        "datatype": "csv", # CSV is simple and deterministic to parse.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch the real provider response.

    response.raise_for_status() # Reject HTTP-level failures.

    reader = csv.DictReader(
        StringIO(response.text)
    ) # Convert CSV response text into dictionary rows.

    rows = list(reader)

    required_fields = {
        "timestamp",
        "close",
    } # Minimum provider fields needed by our MarketObservation.

    if (
        not rows
        or not required_fields.issubset(
            set(reader.fieldnames or [])
        )
    ):
        raise ValueError(
            f"No valid equity data returned for symbol: {symbol}"
        ) # Reject malformed/provider-error responses.

    rows.sort(
        key=lambda row: row["timestamp"],
        reverse=True,
    ) # Ensure newest observation is first regardless of provider ordering.

    latest = rows[0] # Most recent trading observation.

    previous = (
        rows[1]
        if len(rows) > 1
        else None
    ) # Previous observation may be unavailable.

    return build_market_observation(
        asset_name=asset_name,
        asset_class=AssetClass.EQUITIES,
        measurement_type=MeasurementType.PRICE,
        latest_value=Decimal(
            latest["close"]
        ),
        previous_value=(
            Decimal(previous["close"])
            if previous
            else None
        ),
        unit="price",
        latest_period=latest["timestamp"],
        previous_period=(
            previous["timestamp"]
            if previous
            else None
        ),
        source="Alpha Vantage",
        symbol=symbol,
        geography=geography,
        currency=currency,

        # Deliberately do NOT store the request URL because it
        # contains the API key.
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Government Bond Yield Fetcher
# Fetches the US 10Y Treasury yield and converts it into our MarketObservation contract.
# =========================

def fetch_government_bond_yield(
    maturity: str = "10year",
    api_key: str | None = None,
) -> MarketObservation: # Fetches one real government-bond market observation.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can use the .env value.

    if not resolved_api_key: # Never make an external request without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "TREASURY_YIELD", # Alpha Vantage government-bond yield endpoint.
        "interval": "daily", # We want recent daily observations.
        "maturity": maturity, # Default is the benchmark 10-year Treasury yield.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch the real provider response.

    response.raise_for_status() # Reject HTTP-level failures.

    payload = response.json() # Treasury endpoint returns structured JSON.

    rows = payload.get(
        "data",
        []
    ) # Extract the time-series observations.

    valid_rows = [
        row
        for row in rows
        if row.get("value") not in (
            None,
            "",
            ".",
        )
    ] # Ignore missing Treasury observations such as holidays.

    if not valid_rows: # Provider errors or missing data must not enter trusted state.
        raise ValueError(
            f"No valid Treasury yield data returned for maturity: {maturity}"
        )

    valid_rows.sort(
        key=lambda row: row["date"],
        reverse=True,
    ) # Ensure newest observation is first.

    latest = valid_rows[0] # Most recent valid Treasury yield.

    previous = (
        valid_rows[1]
        if len(valid_rows) > 1
        else None
    ) # Previous valid yield may be unavailable.

    return build_market_observation(
        asset_name="US 10-Year Treasury Yield",
        asset_class=AssetClass.GOVERNMENT_BONDS,
        measurement_type=MeasurementType.YIELD,
        latest_value=Decimal(
            latest["value"]
        ),
        previous_value=(
            Decimal(previous["value"])
            if previous
            else None
        ),
        unit="percent",
        latest_period=latest["date"],
        previous_period=(
            previous["date"]
            if previous
            else None
        ),
        source="Alpha Vantage",
        symbol="US10Y",
        geography="US",
        currency=None, # A yield is a percentage, not a currency-denominated price.
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Gold Market Fetcher
# Fetches daily gold prices and converts them into our MarketObservation contract.
# =========================

def fetch_gold_market(
    api_key: str | None = None,
) -> MarketObservation: # Fetches one real gold-market observation.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can use the .env value.

    if not resolved_api_key: # Never call the provider without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "GOLD_SILVER_HISTORY", # Historical precious-metal prices.
        "symbol": "GOLD", # Request gold rather than silver.
        "interval": "daily", # Needed for latest vs previous daily comparison.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch real gold-market data.

    response.raise_for_status() # Reject HTTP-level failures.

    payload = response.json() # Convert provider JSON into Python data.

    rows = payload.get(
        "data",
        []
    ) # Extract historical gold observations.

    valid_rows = [
        row
        for row in rows
        if row.get("price") not in (
            None,
            "",
            ".",
        )
    ] # Remove missing or unusable observations.

    if not valid_rows: # Bad provider data must not enter trusted Market state.
        raise ValueError(
            "No valid gold market data returned."
        )

    valid_rows.sort(
        key=lambda row: row["date"],
        reverse=True,
    ) # Ensure newest gold observation appears first.

    latest = valid_rows[0] # Most recent valid gold price.

    previous = (
        valid_rows[1]
        if len(valid_rows) > 1
        else None
    ) # Previous price may be unavailable.

    return build_market_observation(
        asset_name="Gold",
        asset_class=AssetClass.GOLD,
        measurement_type=MeasurementType.PRICE,
        latest_value=Decimal(
            latest["price"]
        ),
        previous_value=(
            Decimal(previous["price"])
            if previous
            else None
        ),
        unit="price",
        latest_period=latest["date"],
        previous_period=(
            previous["date"]
            if previous
            else None
        ),
        source="Alpha Vantage",
        symbol="GOLD",
        geography="GLOBAL",
        currency="USD",
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Commodity Market Fetcher
# Fetches the broad global commodity index and converts it into our MarketObservation contract.
# =========================

def fetch_commodity_market(
    api_key: str | None = None,
) -> MarketObservation: # Fetches one broad commodity-market observation.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can use the .env value.

    if not resolved_api_key: # Never call the provider without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "ALL_COMMODITIES", # Broad global commodity-price index.
        "interval": "monthly", # Provider supports monthly commodity observations.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch real commodity-market data.

    response.raise_for_status() # Reject HTTP-level failures.

    payload = response.json() # Convert provider JSON into Python data.

    rows = payload.get(
        "data",
        []
    ) # Extract commodity-index observations.

    valid_rows = [
        row
        for row in rows
        if row.get("value") not in (
            None,
            "",
            ".",
        )
    ] # Remove missing or unusable observations.

    if not valid_rows: # Bad provider data must not enter trusted Market state.
        raise ValueError(
            "No valid commodity market data returned."
        )

    valid_rows.sort(
        key=lambda row: row["date"],
        reverse=True,
    ) # Ensure newest observation appears first.

    latest = valid_rows[0] # Most recent valid commodity observation.

    previous = (
        valid_rows[1]
        if len(valid_rows) > 1
        else None
    ) # Previous observation may be unavailable.

    return build_market_observation(
        asset_name="Global Price Index of All Commodities",
        asset_class=AssetClass.COMMODITIES,
        measurement_type=MeasurementType.INDEX,
        latest_value=Decimal(
            latest["value"]
        ),
        previous_value=(
            Decimal(previous["value"])
            if previous
            else None
        ),
        unit=payload.get(
            "unit",
            "index_points",
        ), # Preserve the provider's stated unit where available.
        latest_period=latest["date"],
        previous_period=(
            previous["date"]
            if previous
            else None
        ),
        source="Alpha Vantage",
        symbol="ALL_COMMODITIES",
        geography="GLOBAL",
        currency=None, # Broad commodity index is treated as an index observation.
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Cash Market Fetcher
# Uses the US 3-month Treasury yield as a cash-like market return proxy.
# =========================

def fetch_cash_market(
    api_key: str | None = None,
) -> MarketObservation: # Fetches one short-duration cash-like market observation.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can use the .env value.

    if not resolved_api_key: # Never call the provider without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "TREASURY_YIELD", # Treasury-yield endpoint.
        "interval": "daily", # Recent daily observations.
        "maturity": "3month", # Short-duration Treasury used as our cash proxy.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch real short-term Treasury data.

    response.raise_for_status() # Reject HTTP-level failures.

    payload = response.json() # Convert provider JSON into Python data.

    rows = payload.get(
        "data",
        []
    ) # Extract Treasury observations.

    valid_rows = [
        row
        for row in rows
        if row.get("value") not in (
            None,
            "",
            ".",
        )
    ] # Ignore missing Treasury observations.

    if not valid_rows: # Bad provider data must not enter trusted Market state.
        raise ValueError(
            "No valid cash-proxy market data returned."
        )

    valid_rows.sort(
        key=lambda row: row["date"],
        reverse=True,
    ) # Ensure newest observation appears first.

    latest = valid_rows[0] # Most recent valid short-term Treasury yield.

    previous = (
        valid_rows[1]
        if len(valid_rows) > 1
        else None
    ) # Previous valid yield may be unavailable.

    return build_market_observation(
        asset_name="US 3-Month Treasury Yield",
        asset_class=AssetClass.CASH,
        measurement_type=MeasurementType.YIELD,
        latest_value=Decimal(
            latest["value"]
        ),
        previous_value=(
            Decimal(previous["value"])
            if previous
            else None
        ),
        unit="percent",
        latest_period=latest["date"],
        previous_period=(
            previous["date"]
            if previous
            else None
        ),
        source="Alpha Vantage",
        symbol="US3M",
        geography="US",
        currency=None, # Yield is expressed as a percentage rather than a price.
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Crypto Market Fetcher
# Uses Bitcoin/USD as the initial broad crypto-market proxy.
# =========================

def fetch_crypto_market(
    api_key: str | None = None,
) -> MarketObservation: # Fetches one Bitcoin market-price observation.

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    ) # Tests can inject a key; live code can use the .env value.

    if not resolved_api_key: # Never call the provider without credentials.
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "DIGITAL_CURRENCY_DAILY", # Daily digital-currency endpoint.
        "symbol": "BTC", # Bitcoin is our initial crypto-market proxy.
        "market": "USD", # Price Bitcoin against US dollars.
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    ) # Fetch live Bitcoin market data.

    response.raise_for_status() # Reject HTTP-level failures.

    payload = response.json() # Convert provider JSON into Python data.

    time_series = payload.get(
        "Time Series (Digital Currency Daily)",
        {},
    ) # Extract the date-indexed Bitcoin observations.

    valid_rows = [
        (date, values)
        for date, values in time_series.items()
        if values.get("4. close") not in (
            None,
            "",
            ".",
        )
    ] # Keep only observations with a usable closing price.

    if not valid_rows: # Bad provider data must not enter trusted Market state.
        raise ValueError(
            "No valid crypto market data returned."
        )

    valid_rows.sort(
        key=lambda row: row[0],
        reverse=True,
    ) # ISO dates sort cleanly newest-first.

    latest_date, latest_values = valid_rows[0] # Most recent valid Bitcoin close.

    previous = (
        valid_rows[1]
        if len(valid_rows) > 1
        else None
    ) # Previous trading-day observation may be unavailable.

    previous_date = (
        previous[0]
        if previous
        else None
    )

    previous_values = (
        previous[1]
        if previous
        else None
    )

    return build_market_observation(
        asset_name="Bitcoin",
        asset_class=AssetClass.CRYPTO,
        measurement_type=MeasurementType.PRICE,
        latest_value=Decimal(
            latest_values["4. close"]
        ),
        previous_value=(
            Decimal(previous_values["4. close"])
            if previous_values
            else None
        ),
        unit="price",
        latest_period=latest_date,
        previous_period=previous_date,
        source="Alpha Vantage",
        symbol="BTC",
        geography="GLOBAL",
        currency="USD",
        source_url="https://www.alphavantage.co/",
    )

# =========================
# Market Snapshot Builder
# Combines independently fetched asset-class observations into one cross-asset view.
# =========================

def build_market_snapshot(
    investor_country: str | None = None,
    base_currency: str | None = None,
    api_key: str | None = None,
    as_of_date: date | None = None,
) -> MarketSnapshot: # Builds one cross-asset snapshot from the six market fetchers.

    observations: list[MarketObservation] = []

    fetchers = [
        lambda: fetch_equity_market(
            symbol="SPY",
            asset_name="SPDR S&P 500 ETF Trust",
            geography="US",
            currency="USD",
            api_key=api_key,
        ),
        lambda: fetch_government_bond_yield(
            maturity="10year",
            api_key=api_key,
        ),
        lambda: fetch_gold_market(
            api_key=api_key,
        ),
        lambda: fetch_commodity_market(
            api_key=api_key,
        ),
        lambda: fetch_cash_market(
            api_key=api_key,
        ),
        lambda: fetch_crypto_market(
            api_key=api_key,
        ),
    ] # Existing fetchers remain responsible for each individual market fact.

    for fetcher in fetchers:
        try:
            observation = fetcher()
            observations.append(observation)
        except (
            requests.RequestException,
            ValueError,
        ):
            continue # One unavailable provider feed should not destroy the whole snapshot.

    return MarketSnapshot(
        as_of_date=as_of_date or date.today(),
        investor_country=investor_country,
        base_currency=base_currency,
        observations=observations,
    )

# =========================
# Market Snapshot MCP Tool
# Exposes the combined cross-asset snapshot to MCP clients and agents.
# =========================

@mcp.tool() # Register this Python function as an MCP tool.
def get_market_snapshot(
    investor_country: str | None = None,
    base_currency: str | None = None,
) -> dict:
    snapshot = build_market_snapshot(
        investor_country=investor_country,
        base_currency=base_currency,
    ) # Build the validated cross-asset MarketSnapshot.

    return snapshot.model_dump(
        mode="json"
    ) # Convert Pydantic MarketSnapshot into MCP-safe JSON data.


# =========================
# MCP Server Runner
# Starts the Market MCP service when this file is run directly.
# =========================

if __name__ == "__main__":
    mcp.run()