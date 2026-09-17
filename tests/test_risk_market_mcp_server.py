from datetime import date
from decimal import Decimal

import pytest

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalAssetSeries,
    HistoricalFrequency,
    HistoricalPricePoint,
)

from mcp_servers.risk_market_mcp_server import (
    build_traditional_risk_proxy_universe,
    fetch_historical_proxy_series,
)


# =========================
# Fake HTTP Response
# Lets tests validate provider parsing without making live API calls.
# =========================

class FakeResponse:

    def __init__(
        self,
        text,
    ):
        self.text = text

    def raise_for_status(
        self,
    ):
        pass


# =========================
# Historical Proxy Fetcher
# Provider data should become a validated HistoricalAssetSeries.
# =========================

def test_fetch_historical_proxy_series(
    monkeypatch,
):

    provider_response = """timestamp,open,high,low,close,adjusted close,volume,dividend amount
2026-01-16,102,103,100,102,102.50,1000000,0
2026-01-09,100,102,99,101,101.00,900000,0
2026-01-02,98,101,97,100,100.00,800000,0
"""

    captured = {}

    def fake_get(
        url,
        params,
        timeout,
    ):
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout

        return FakeResponse(
            provider_response
        )

    monkeypatch.setattr(
        "mcp_servers.risk_market_mcp_server.requests.get",
        fake_get,
    )

    result = fetch_historical_proxy_series(
        symbol="TEST",
        asset_class=AssetClass.EQUITIES,
        proxy_name="Test Equity Proxy",
        currency="USD",
        api_key="test-key",
    )

    assert result.asset_class == AssetClass.EQUITIES
    assert result.symbol == "TEST"
    assert result.frequency == HistoricalFrequency.WEEKLY
    assert result.currency == "USD"

    assert [
        observation.observation_date
        for observation in result.observations
    ] == [
        date(2026, 1, 2),
        date(2026, 1, 9),
        date(2026, 1, 16),
    ]

    assert [
        observation.price
        for observation in result.observations
    ] == [
        Decimal("100.00"),
        Decimal("101.00"),
        Decimal("102.50"),
    ]

    assert captured["params"]["function"] == (
        "TIME_SERIES_WEEKLY_ADJUSTED"
    )

    assert captured["params"]["symbol"] == "TEST"


# =========================
# Invalid Provider Response
# Missing adjusted-price data must not enter the trusted risk pipeline.
# =========================

def test_historical_proxy_rejects_invalid_provider_data(
    monkeypatch,
):

    provider_response = """timestamp,open,high,low,close
2026-01-16,102,103,100,102
"""

    monkeypatch.setattr(
        "mcp_servers.risk_market_mcp_server.requests.get",
        lambda *args, **kwargs:
        FakeResponse(
            provider_response
        ),
    )

    with pytest.raises(
        ValueError
    ):
        fetch_historical_proxy_series(
            symbol="TEST",
            asset_class=AssetClass.EQUITIES,
            proxy_name="Test Equity Proxy",
            api_key="test-key",
        )


# =========================
# Insufficient History
# Risk calculations need more than one usable price observation.
# =========================

def test_historical_proxy_requires_multiple_observations(
    monkeypatch,
):

    provider_response = """timestamp,open,high,low,close,adjusted close,volume,dividend amount
2026-01-16,102,103,100,102,102.50,1000000,0
"""

    monkeypatch.setattr(
        "mcp_servers.risk_market_mcp_server.requests.get",
        lambda *args, **kwargs:
        FakeResponse(
            provider_response
        ),
    )

    with pytest.raises(
        ValueError
    ):
        fetch_historical_proxy_series(
            symbol="TEST",
            asset_class=AssetClass.EQUITIES,
            proxy_name="Test Equity Proxy",
            api_key="test-key",
        )


# =========================
# API Key
# External historical data cannot be requested without credentials.
# =========================

def test_historical_proxy_requires_api_key(
    monkeypatch,
):

    monkeypatch.delenv(
        "ALPHA_VANTAGE_API_KEY",
        raising=False,
    )

    with pytest.raises(
        ValueError
    ):
        fetch_historical_proxy_series(
            symbol="TEST",
            asset_class=AssetClass.EQUITIES,
            proxy_name="Test Equity Proxy",
        )
# =========================
# Traditional Risk Universe
# All five traditional economic exposures should be fetched consistently.
# =========================

def test_build_traditional_risk_proxy_universe(
    monkeypatch,
):

    captured = []

    def fake_fetch_historical_proxy_series(
        symbol,
        asset_class,
        proxy_name,
        currency="USD",
        api_key=None,
    ):

        captured.append(
            {
                "symbol": symbol,
                "asset_class": asset_class,
                "proxy_name": proxy_name,
                "currency": currency,
                "api_key": api_key,
            }
        )

        return HistoricalAssetSeries(
            asset_class=asset_class,
            symbol=symbol,
            proxy_name=proxy_name,
            currency=currency,
            frequency=HistoricalFrequency.WEEKLY,
            source="Alpha Vantage",
            observations=[
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        2,
                    ),
                    price=Decimal("100"),
                ),
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        9,
                    ),
                    price=Decimal("101"),
                ),
            ],
        )

    monkeypatch.setattr(
        "mcp_servers.risk_market_mcp_server.fetch_historical_proxy_series",
        fake_fetch_historical_proxy_series,
    )

    result = build_traditional_risk_proxy_universe(
        api_key="test-key"
    )

    assert len(result) == 5

    assert [
        series.symbol
        for series in result
    ] == [
        "SPY",
        "IEF",
        "GLD",
        "DBC",
        "BIL",
    ]

    assert {
        series.asset_class
        for series in result
    } == {
        AssetClass.EQUITIES,
        AssetClass.GOVERNMENT_BONDS,
        AssetClass.GOLD,
        AssetClass.COMMODITIES,
        AssetClass.CASH,
    }

    assert all(
        series.currency == "USD"
        for series in result
    )

    assert all(
        call["api_key"] == "test-key"
        for call in captured
    )


# =========================
# Fail Closed
# Incomplete proxy history must not silently become a complete risk universe.
# =========================

def test_traditional_risk_proxy_universe_propagates_failure(
    monkeypatch,
):

    def fake_fetch_historical_proxy_series(
        symbol,
        asset_class,
        proxy_name,
        currency="USD",
        api_key=None,
    ):

        if symbol == "DBC":
            raise ValueError(
                "Historical commodity data unavailable."
            )

        return HistoricalAssetSeries(
            asset_class=asset_class,
            symbol=symbol,
            proxy_name=proxy_name,
            currency=currency,
            frequency=HistoricalFrequency.WEEKLY,
            source="Alpha Vantage",
            observations=[
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        2,
                    ),
                    price=Decimal("100"),
                ),
                HistoricalPricePoint(
                    observation_date=date(
                        2026,
                        1,
                        9,
                    ),
                    price=Decimal("101"),
                ),
            ],
        )

    monkeypatch.setattr(
        "mcp_servers.risk_market_mcp_server.fetch_historical_proxy_series",
        fake_fetch_historical_proxy_series,
    )

    with pytest.raises(
        ValueError
    ):
        build_traditional_risk_proxy_universe(
            api_key="test-key"
        )