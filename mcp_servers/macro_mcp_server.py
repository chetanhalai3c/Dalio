import csv
from datetime import date
from decimal import Decimal
from io import StringIO

import requests

from models.macro import (
    MacroObservation,
    TrendDirection,
)


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

# =========================
# OECD Inflation Fetcher
# =========================

def fetch_oecd_inflation(
    geography_code: str,
):
    country_code = geography_code.upper()

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
        f"{country_code}.M.N.CPI.PA._T.N.GY"
    )

    start_period = f"{date.today().year - 1}-01"

    response = requests.get(
        url,
        params={
            "startPeriod": start_period,
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )

    if not observations:
        raise ValueError(
            f"No OECD inflation data found for "
            f"{country_code}."
        )

    latest = observations[-1]

    previous = (
        observations[-2]
        if len(observations) >= 2
        else None
    )

    latest_value = Decimal(
        latest["OBS_VALUE"]
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )

    return build_macro_observation(
        indicator="Consumer Price Inflation",
        latest_value=latest_value,
        previous_value=previous_value,
        unit="percent",
        latest_period=latest["TIME_PERIOD"],
        previous_period=(
            previous["TIME_PERIOD"]
            if previous is not None
            else None
        ),
        source="OECD Data Explorer",
        source_url=response.url,
    )

# =========================
# OECD Inflation Fetcher
# =========================

def fetch_oecd_inflation(
    geography_code: str,
) -> MacroObservation:
    country_code = geography_code.upper()

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
        f"{country_code}.M.N.CPI.PA._T.N.GY"
    )

    response = requests.get(
        url,
        params={
            "startPeriod": f"{date.today().year - 1}-01",
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )

    if not observations:
        raise ValueError(
            f"No OECD inflation data found for "
            f"{country_code}."
        )

    latest = observations[-1]

    previous = (
        observations[-2]
        if len(observations) >= 2
        else None
    )

    latest_value = Decimal(
        latest["OBS_VALUE"]
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )

    return build_macro_observation(
        indicator="Consumer Price Inflation",
        latest_value=latest_value,
        previous_value=previous_value,
        unit="percent",
        latest_period=latest["TIME_PERIOD"],
        previous_period=(
            previous["TIME_PERIOD"]
            if previous is not None
            else None
        ),
        source="OECD Data Explorer",
        source_url=response.url,
    )

# =========================
# OECD GDP Growth Fetcher
# =========================

def fetch_oecd_growth(
    geography_code: str,
) -> MacroObservation:
    country_code = geography_code.upper()

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.NAD,"
        "DSD_NAMAIN1@DF_QNA_EXPENDITURE_GROWTH_OECD,1.1/"
        f"Q..{country_code}.S1..B1GQ......G1."
    )

    response = requests.get(
        url,
        params={
            "startPeriod": f"{date.today().year - 1}-Q1",
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )

    if not observations:
        raise ValueError(
            f"No OECD GDP growth data found for "
            f"{country_code}."
        )

    latest = observations[-1]

    previous = (
        observations[-2]
        if len(observations) >= 2
        else None
    )

    latest_value = Decimal(
        latest["OBS_VALUE"]
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )

    return build_macro_observation(
        indicator="Real GDP Growth",
        latest_value=latest_value,
        previous_value=previous_value,
        unit="percent",
        latest_period=latest["TIME_PERIOD"],
        previous_period=(
            previous["TIME_PERIOD"]
            if previous is not None
            else None
        ),
        source="OECD Data Explorer",
        source_url=response.url,
    )