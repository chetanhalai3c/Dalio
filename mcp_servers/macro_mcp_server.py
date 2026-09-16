import csv  # Parses CSV data returned by OECD/BIS APIs.

from datetime import date  # Gives us today's date.
from decimal import Decimal  # Precise numeric type for economic values.
from io import StringIO  # Makes downloaded text behave like a file for csv.DictReader.

import pycountry  # Converts country codes such as GB into country information.
import requests  # Sends HTTP requests to OECD and BIS APIs.


from models.macro import (
    MacroObservation,  # Blueprint for ONE standardised macro indicator.
    MacroSnapshot,     # Blueprint for the complete macro evidence package.
    TrendDirection,    # Allowed trend values: rising/falling/stable/unknown.
)


from mcp.server.mcpserver import MCPServer  # Framework used to expose functions as MCP tools.



# =========================
# MCP Server
# Creates the service that will expose our macro-data tools.
# =========================

mcp = MCPServer(
    "EducosysDalio Macro Server"  # Human-readable name for this MCP server.
)


# =========================
# Trend Direction Helper
# Compares latest vs previous value and labels the direction.
# =========================

def calculate_direction(
    latest_value: Decimal,                 # Newest economic value.
    previous_value: Decimal | None,        # Previous value, if one exists.
) -> TrendDirection:                       # Returns one of our TrendDirection values.

    if previous_value is None:             # No comparison point available.
        return TrendDirection.UNKNOWN

    if latest_value > previous_value:      # Latest number increased.
        return TrendDirection.RISING

    if latest_value < previous_value:      # Latest number decreased.
        return TrendDirection.FALLING

    return TrendDirection.STABLE           # Values are equal.


# =========================
# Macro Observation Builder
# Converts cleaned economic data into our standard MacroObservation structure.
# =========================

def build_macro_observation(
    indicator: str,                        # What economic indicator this is.
    latest_value: Decimal,                 # Latest measurement.
    previous_value: Decimal | None,        # Previous measurement.
    unit: str,                             # %, index, etc.
    latest_period: str,                    # Period of latest measurement.
    previous_period: str | None,           # Period of previous measurement.
    source: str,                           # Organisation supplying the data.
    source_url: str | None = None,         # Original source URL if available.
):

    return MacroObservation(               # Create an actual MacroObservation object.
        indicator=indicator,
        latest_value=latest_value,
        previous_value=previous_value,
        unit=unit,
        latest_period=latest_period,
        previous_period=previous_period,

        direction=calculate_direction(     # Derive trend rather than asking the LLM.
            latest_value,
            previous_value,
        ),

        source=source,
        source_url=source_url,
    )


# =========================
# OECD Inflation Fetcher
# Fetches inflation data, cleans it, then creates a MacroObservation.
# NOTE: another function with this same name appears below and replaces this one.
# =========================

def fetch_oecd_inflation(
    geography_code: str,                   # OECD country code supplied to the function.
):

    country_code = geography_code.upper()  # Normalise e.g. "gbr" → "GBR".

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
        f"{country_code}.M.N.CPI.PA._T.N.GY"
    )
    # Build the OECD API endpoint for monthly CPI inflation.

    start_period = f"{date.today().year - 1}-01"
    # Ask for data beginning January of the previous year.

    response = requests.get(
        url,
        params={
            "startPeriod": start_period,
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,                         # Stop waiting after 20 seconds.
    )

    response.raise_for_status()             # Raise an error if the API request failed.

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )
    # API returns CSV text.
    # StringIO makes it file-like.
    # DictReader converts each CSV row into a dictionary.

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")             # Keep rows containing an actual value.
        and row.get("TIME_PERIOD")          # And an associated period.
    ]

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]  # Sort observations chronologically.
    )

    if not observations:                    # No usable data was returned.
        raise ValueError(
            f"No OECD inflation data found for "
            f"{country_code}."
        )

    latest = observations[-1]               # Last row = newest observation.

    previous = (
        observations[-2]                    # Second-last row = previous observation.
        if len(observations) >= 2
        else None
    )

    latest_value = Decimal(
        latest["OBS_VALUE"]                 # Convert text number → precise Decimal.
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )

    return build_macro_observation(         # Convert raw OECD data → our standard model.
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
# Same job as above; because it has the same name, THIS definition replaces the earlier one.
# =========================

def fetch_oecd_inflation(
    geography_code: str,
) -> MacroObservation:                     # Explicitly states that this returns MacroObservation.

    country_code = geography_code.upper()  # Normalise the supplied country code.

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.TPS,DSD_PRICES@DF_PRICES_ALL,1.0/"
        f"{country_code}.M.N.CPI.PA._T.N.GY"
    )
    # OECD endpoint for monthly CPI inflation.

    response = requests.get(
        url,
        params={
            "startPeriod": f"{date.today().year - 1}-01",
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()             # Fail if OECD returned an HTTP error.

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )
    # Convert CSV response → list of dictionaries.

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]
    # Remove unusable rows.

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )
    # Put data into chronological order.

    if not observations:
        raise ValueError(
            f"No OECD inflation data found for "
            f"{country_code}."
        )

    latest = observations[-1]               # Most recent observation.

    previous = (
        observations[-2]                    # Observation immediately before it.
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
    # Final output = standardised MacroObservation rather than raw OECD data.


# =========================
# OECD GDP Growth Fetcher
# Fetches growth data and converts it into the same MacroObservation structure.
# =========================

def fetch_oecd_growth(
    geography_code: str,
) -> MacroObservation:

    country_code = geography_code.upper()  # Normalise e.g. "gbr" → "GBR".

    url = (
        "https://sdmx.oecd.org/public/rest/data/"
        "OECD.SDD.NAD,"
        "DSD_NAMAIN1@DF_QNA_EXPENDITURE_GROWTH_OECD,1.1/"
        f"Q..{country_code}.S1..B1GQ......G1."
    )
    # OECD API endpoint for quarterly real GDP growth.

    response = requests.get(
        url,
        params={
            "startPeriod": f"{date.today().year - 1}-Q1",
            "dimensionAtObservation": "AllDimensions",
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()             # Fail if the external request failed.

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )
    # Convert returned CSV → Python dictionaries.

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]
    # Keep only valid observations.

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )
    # Oldest → newest.

    if not observations:
        raise ValueError(
            f"No OECD GDP growth data found for "
            f"{country_code}."
        )

    latest = observations[-1]               # Latest GDP observation.

    previous = (
        observations[-2]
        if len(observations) >= 2
        else None
    )
    # Previous GDP observation if one exists.

    latest_value = Decimal(
        latest["OBS_VALUE"]
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )
    # Convert values from CSV strings → Decimal.

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
    # Output is identical in structure to inflation despite coming from different OECD data.


# =========================
# BIS Policy Rate Fetcher
# Fetches central-bank rates from BIS and normalises them into MacroObservation.
# =========================

def fetch_bis_policy_rate(
    geography_code: str,
) -> MacroObservation:

    country_code = geography_code.upper()  # BIS uses the supplied 2-letter country code.

    url = (
        "https://stats.bis.org/api/v2/data/"
        "dataflow/BIS/WS_CBPOL/1.0/"
        f"M.{country_code}"
    )
    # BIS API endpoint for monthly central-bank policy rates.

    response = requests.get(
        url,
        params={
            "lastNObservations": 2,         # We only need latest + previous.
            "format": "csvfile",
        },
        timeout=20,
    )

    response.raise_for_status()             # Raise an error for failed HTTP responses.

    rows = list(
        csv.DictReader(
            StringIO(response.text)
        )
    )
    # Parse BIS CSV into Python dictionaries.

    observations = [
        row
        for row in rows
        if row.get("OBS_VALUE")
        and row.get("TIME_PERIOD")
    ]
    # Keep only valid measurements.

    observations.sort(
        key=lambda row: row["TIME_PERIOD"]
    )

    if not observations:
        raise ValueError(
            f"No BIS policy-rate data found for "
            f"{country_code}."
        )

    latest = observations[-1]               # Newest central-bank rate.

    previous = (
        observations[-2]
        if len(observations) >= 2
        else None
    )
    # Previous rate lets us determine direction.

    latest_value = Decimal(
        latest["OBS_VALUE"]
    )

    previous_value = (
        Decimal(previous["OBS_VALUE"])
        if previous is not None
        else None
    )

    return build_macro_observation(
        indicator="Central Bank Policy Rate",
        latest_value=latest_value,
        previous_value=previous_value,
        unit="percent",
        latest_period=latest["TIME_PERIOD"],

        previous_period=(
            previous["TIME_PERIOD"]
            if previous is not None
            else None
        ),

        source="BIS Data Portal",
        source_url=response.url,
    )
    # Raw BIS data now looks exactly like the OECD observations to downstream code.


# =========================
# Macro Country Resolution
# Translates one user country code into the codes needed by each data provider.
# =========================

def resolve_macro_country_codes(
    country_code: str,
) -> dict[str, str]:

    country_code = country_code.upper().strip()
    # " gb " → "GB".

    if len(country_code) != 2:              # Input must be a two-letter country code.
        raise ValueError(
            "Country must use a 2-letter ISO-style code."
        )

    country = pycountry.countries.get(
        alpha_2=country_code
    )
    # Look up the country using the standard ISO alpha-2 code.

    if country is None:                     # Code was two characters but isn't a real country.
        raise ValueError(
            f"Unknown country code: {country_code}"
        )

    return {
        "geography": country.name,           # "United Kingdom"
        "geography_code": country.alpha_2,  # "GB"
        "oecd_code": country.alpha_3,        # "GBR"
        "bis_code": country.alpha_2,         # "GB"
    }
    # One input country code becomes all provider-specific identifiers we need.


# =========================
# Country Macro Snapshot
# Convenience function: country code in → complete MacroSnapshot out.
# =========================

def build_macro_snapshot_for_country(
    country_code: str,
) -> MacroSnapshot:

    codes = resolve_macro_country_codes(
        country_code
    )
    # Resolve one country into the identifiers OECD/BIS require.

    return build_macro_snapshot(
        geography=codes["geography"],
        geography_code=codes["geography_code"],
        oecd_code=codes["oecd_code"],
        bis_code=codes["bis_code"],
    )
    # Pass those resolved codes into the main snapshot builder.


# =========================
# Macro Snapshot Builder
# Fetches all three indicators and combines them into one MacroSnapshot.
# NOTE: a second version below replaces this definition.
# =========================

def build_macro_snapshot(
    geography: str,
    geography_code: str,
    oecd_code: str,
    bis_code: str,
) -> MacroSnapshot:

    growth = fetch_oecd_growth(
        oecd_code
    )
    # Fetch + standardise GDP growth.

    inflation = fetch_oecd_inflation(
        oecd_code
    )
    # Fetch + standardise inflation.

    policy_rate = fetch_bis_policy_rate(
        bis_code
    )
    # Fetch + standardise central-bank rate.

    return MacroSnapshot(
        geography=geography,
        geography_code=geography_code,
        as_of_date=date.today(),
        growth=growth,
        inflation=inflation,
        policy_rate=policy_rate,
    )
    # Combine the three MacroObservation objects into one MacroSnapshot.


# =========================
# Macro Snapshot Builder
# Resilient version: one missing indicator does not destroy the whole snapshot.
# This definition replaces the earlier build_macro_snapshot().
# =========================

def build_macro_snapshot(
    geography: str,
    geography_code: str,
    oecd_code: str,
    bis_code: str,
) -> MacroSnapshot:

    try:
        growth = fetch_oecd_growth(
            oecd_code
        )
    except ValueError:
        growth = None
    # If GDP data is unavailable, keep going with growth=None.

    try:
        inflation = fetch_oecd_inflation(
            oecd_code
        )
    except ValueError:
        inflation = None
    # Inflation failure does not destroy the entire snapshot.

    try:
        policy_rate = fetch_bis_policy_rate(
            bis_code
        )
    except ValueError:
        policy_rate = None
    # Same principle for the policy rate.

    return MacroSnapshot(
        geography=geography,
        geography_code=geography_code,
        as_of_date=date.today(),
        growth=growth,
        inflation=inflation,
        policy_rate=policy_rate,
    )
    # Return the best evidence package available, even if one indicator is missing.


# =========================
# Macro Snapshot MCP Tool
# Exposes snapshot creation so an MCP client/agent can request macro evidence.
# =========================

@mcp.tool()                                  # Register this Python function as an MCP tool.
def get_macro_snapshot(
    geography: str,
    geography_code: str,
    oecd_code: str,
    bis_code: str,
) -> dict:

    snapshot = build_macro_snapshot(
        geography=geography,
        geography_code=geography_code,
        oecd_code=oecd_code,
        bis_code=bis_code,
    )
    # Internally we work with the validated MacroSnapshot object.

    return snapshot.model_dump(
        mode="json"
    )
    # Convert Pydantic MacroSnapshot → JSON-compatible dictionary for MCP transport.


# =========================
# MCP Server Runner
# Starts the macro MCP service when this file is run directly.
# =========================

if __name__ == "__main__":                  # Only run server when this file is executed directly.
    mcp.run()                               # Start server and listen for MCP tool requests.