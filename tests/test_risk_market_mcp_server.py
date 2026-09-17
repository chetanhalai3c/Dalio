from datetime import date
from decimal import Decimal

import pytest

from models.market import AssetClass
from models.risk_market_data import (
    HistoricalFrequency,
)
from mcp_servers.risk_market_mcp_server import (
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
        