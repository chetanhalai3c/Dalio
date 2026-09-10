from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import Field, field_validator, model_validator

from .investor_profile import MoneyValue, StrictBaseModel


# =========================
# Portfolio enums
# =========================

class PortfolioDataSource(str, Enum):
    MANUAL = "manual"
    DOCUMENT = "document"
    SCREENSHOT = "screenshot"
    API = "api"


class AssetClass(str, Enum):
    CASH = "cash"
    EQUITY = "equity"
    EQUITY_FUND = "equity_fund"
    GOVERNMENT_BOND = "government_bond"
    CORPORATE_BOND = "corporate_bond"
    BOND_FUND = "bond_fund"
    INFLATION_LINKED_BOND = "inflation_linked_bond"
    GOLD = "gold"
    COMMODITY = "commodity"
    REIT = "reit"
    PROPERTY_FUND = "property_fund"
    CRYPTO = "crypto"
    OTHER = "other"
    UNKNOWN = "unknown"


# =========================
# Portfolio metadata
# =========================

class PortfolioMetadata(StrictBaseModel):
    as_of_date: Optional[date] = None
    base_currency: Optional[str] = None
    data_source: Optional[PortfolioDataSource] = None

    @field_validator("base_currency")
    @classmethod
    def normalise_base_currency(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError(
                "Base currency must use a 3-letter ISO-style code."
            )

        return value


# =========================
# Portfolio account
# =========================

class PortfolioAccount(StrictBaseModel):
    account_id: str
    account_name: Optional[str] = None
    platform: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None

    @field_validator("account_id")
    @classmethod
    def validate_account_id(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("account_id cannot be empty.")

        return value

    @field_validator("currency")
    @classmethod
    def normalise_currency(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError(
                "Currency must use a 3-letter ISO-style code."
            )

        return value


# =========================
# Portfolio holding
# =========================

class Holding(StrictBaseModel):
    holding_id: str
    name: str
    ticker: Optional[str] = None
    identifier: Optional[str] = None
    asset_class: Optional[AssetClass] = None
    quantity: Optional[Decimal] = Field(default=None, ge=0)
    current_price: Optional[MoneyValue] = None
    current_value: MoneyValue
    cost_basis: Optional[MoneyValue] = None
    currency: str
    account_id: Optional[str] = None

    @field_validator("holding_id", "name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Required text fields cannot be empty.")

        return value

    @field_validator("ticker", "identifier", "account_id")
    @classmethod
    def normalise_optional_text(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        value = value.strip()

        return value or None

    @field_validator("currency")
    @classmethod
    def normalise_currency(cls, value: str) -> str:
        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError(
                "Currency must use a 3-letter ISO-style code."
            )

        return value


# =========================
# Complete portfolio
# =========================

class Portfolio(StrictBaseModel):
    metadata: Optional[PortfolioMetadata] = None
    accounts: list[PortfolioAccount] = Field(default_factory=list)
    holdings: list[Holding] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_portfolio_relationships(self):
        account_ids = [account.account_id for account in self.accounts]
        holding_ids = [holding.holding_id for holding in self.holdings]

        if len(account_ids) != len(set(account_ids)):
            raise ValueError("account_id values must be unique.")

        if len(holding_ids) != len(set(holding_ids)):
            raise ValueError("holding_id values must be unique.")

        known_accounts = set(account_ids)

        for holding in self.holdings:
            if (
                holding.account_id is not None
                and holding.account_id not in known_accounts
            ):
                raise ValueError(
                    f"Holding {holding.holding_id} references an "
                    f"unknown account_id: {holding.account_id}."
                )

        return self