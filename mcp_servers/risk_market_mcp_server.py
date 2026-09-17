from datetime import date
from decimal import Decimal
import csv
import os
from io import StringIO

import requests

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalAssetSeries,
    HistoricalFrequency,
    HistoricalPricePoint,
)


# =========================
# Alpha Vantage Configuration
# Historical proxy data enters the risk pipeline through this provider.
# =========================

ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"


# =========================
# Historical Proxy Fetcher
# Fetches weekly adjusted prices for ONE asset-class proxy.
# =========================

def fetch_historical_proxy_series(
    symbol: str,
    asset_class: AssetClass,
    proxy_name: str,
    currency: str = "USD",
    api_key: str | None = None,
) -> HistoricalAssetSeries:

    resolved_api_key = (
        api_key
        or os.getenv("ALPHA_VANTAGE_API_KEY")
    )

    if not resolved_api_key:
        raise ValueError(
            "ALPHA_VANTAGE_API_KEY is required."
        )

    params = {
        "function": "TIME_SERIES_WEEKLY_ADJUSTED",
        "symbol": symbol,
        "datatype": "csv",
        "apikey": resolved_api_key,
    }

    response = requests.get(
        ALPHA_VANTAGE_URL,
        params=params,
        timeout=20,
    )

    response.raise_for_status()

    reader = csv.DictReader(
        StringIO(response.text)
    )

    rows = list(
        reader
    )

    required_fields = {
        "timestamp",
        "adjusted close",
    }

    if (
        not rows
        or not required_fields.issubset(
            set(reader.fieldnames or [])
        )
    ):
        raise ValueError(
            f"No valid historical proxy data returned for symbol: {symbol}"
        )

    observations = []

    for row in rows:

        adjusted_close = row.get(
            "adjusted close"
        )

        if adjusted_close in (
            None,
            "",
            ".",
        ):
            continue

        try:
            observation = HistoricalPricePoint(
                observation_date=date.fromisoformat(
                    row["timestamp"]
                ),
                price=Decimal(
                    adjusted_close
                ),
            )

        except (
            ValueError,
            ArithmeticError,
        ) as exc:
            raise ValueError(
                f"Invalid historical proxy data returned for symbol: {symbol}"
            ) from exc

        observations.append(
            observation
        )

    if len(observations) < 2:
        raise ValueError(
            f"Insufficient historical proxy data returned for symbol: {symbol}"
        )

    observations.sort(
        key=lambda observation:
        observation.observation_date
    )

    return HistoricalAssetSeries(
        asset_class=asset_class,
        symbol=symbol,
        proxy_name=proxy_name,
        currency=currency,
        frequency=HistoricalFrequency.WEEKLY,
        source="Alpha Vantage",
        observations=observations,
    )

# =========================
# Traditional Risk Proxies
# Standardised USD-listed proxies for major economic exposures.
# =========================

TRADITIONAL_RISK_PROXIES = (
    {
        "symbol": "SPY",
        "asset_class": AssetClass.EQUITIES,
        "proxy_name": "SPDR S&P 500 ETF Trust",
        "currency": "USD",
    },
    {
        "symbol": "IEF",
        "asset_class": AssetClass.GOVERNMENT_BONDS,
        "proxy_name": "iShares 7-10 Year Treasury Bond ETF",
        "currency": "USD",
    },
    {
        "symbol": "GLD",
        "asset_class": AssetClass.GOLD,
        "proxy_name": "SPDR Gold Shares",
        "currency": "USD",
    },
    {
        "symbol": "DBC",
        "asset_class": AssetClass.COMMODITIES,
        "proxy_name": "Invesco DB Commodity Index Tracking Fund",
        "currency": "USD",
    },
    {
        "symbol": "BIL",
        "asset_class": AssetClass.CASH,
        "proxy_name": "SPDR Bloomberg 1-3 Month T-Bill ETF",
        "currency": "USD",
    },
)


# =========================
# Traditional Risk Universe
# Fetches comparable weekly histories for five economic exposures.
# =========================

def build_traditional_risk_proxy_universe(
    api_key: str | None = None,
) -> list[HistoricalAssetSeries]:

    series_list = []

    for proxy in TRADITIONAL_RISK_PROXIES:

        series = fetch_historical_proxy_series(
            symbol=proxy["symbol"],
            asset_class=proxy["asset_class"],
            proxy_name=proxy["proxy_name"],
            currency=proxy["currency"],
            api_key=api_key,
        )

        series_list.append(
            series
        )

    return series_list