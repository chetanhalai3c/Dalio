# models/investor_profile.py

from datetime import date, datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    computed_field,
    field_validator,
    model_validator,
)
# =========================
# Strict base model
# =========================

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

# =========================
# Shared enums
# =========================

class ValueType(str, Enum):
    EXACT = "exact"
    APPROXIMATE = "approximate"
    RANGE = "range"


class ContributionFrequency(str, Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    IRREGULAR = "irregular"


class GoalType(str, Enum):
    CAPITAL_PRESERVATION = "capital_preservation"
    LONG_TERM_GROWTH = "long_term_growth"
    RETIREMENT = "retirement"
    INCOME = "income"
    HOME_PURCHASE = "home_purchase"
    EDUCATION = "education"
    WEALTH_TRANSFER = "wealth_transfer"
    GENERAL_WEALTH_BUILDING = "general_wealth_building"
    OTHER = "other"


class InvestmentHorizon(str, Enum):
    UNDER_1_YEAR = "under_1_year"
    ONE_TO_THREE_YEARS = "1_to_3_years"
    THREE_TO_FIVE_YEARS = "3_to_5_years"
    FIVE_TO_TEN_YEARS = "5_to_10_years"
    TEN_PLUS_YEARS = "10_plus_years"


class IncomeStability(str, Enum):
    UNSTABLE = "unstable"
    VARIABLE = "variable"
    FAIRLY_STABLE = "fairly_stable"
    STABLE = "stable"
    VERY_STABLE = "very_stable"


class LiabilityType(str, Enum):
    MORTGAGE = "mortgage"
    PERSONAL_LOAN = "personal_loan"
    STUDENT_LOAN = "student_loan"
    CREDIT_CARD = "credit_card"
    BUSINESS_DEBT = "business_debt"
    MARGIN_DEBT = "margin_debt"
    OTHER = "other"


class RateType(str, Enum):
    FIXED = "fixed"
    FLOATING = "floating"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class RiskCapacityBand(str, Enum):
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class DrawdownResponse(str, Enum):
    SELL_MOST = "sell_most"
    REDUCE_RISK = "reduce_risk"
    HOLD = "hold"
    INVEST_MORE = "invest_more"
    UNSURE = "unsure"


class InvestmentExperience(str, Enum):
    NONE = "none"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    EXPERIENCED = "experienced"
    ADVANCED = "advanced"


class EmergencyAccessRequirement(str, Enum):
    IMMEDIATE = "immediate"
    WITHIN_DAYS = "within_days"
    WITHIN_WEEKS = "within_weeks"
    WITHIN_MONTHS = "within_months"
    NO_KNOWN_REQUIREMENT = "no_known_requirement"


class ForcedSaleRiskBand(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class ComplexityTolerance(str, Enum):
    SIMPLE_ONLY = "simple_only"
    STANDARD = "standard"
    ADVANCED = "advanced"
    NO_PREFERENCE = "no_preference"


class IncomeGrowthPreference(str, Enum):
    INCOME = "income"
    BALANCED = "balanced"
    GROWTH = "growth"
    NO_PREFERENCE = "no_preference"


class AccountCategory(str, Enum):
    TAXABLE_BROKERAGE = "taxable_brokerage"
    TAX_ADVANTAGED = "tax_advantaged"
    RETIREMENT = "retirement"
    BANK_INVESTMENT = "bank_investment"
    WORKPLACE_INVESTMENT = "workplace_investment"
    OTHER = "other"


class AccessibleAssetClass(str, Enum):
    CASH = "cash"
    EQUITIES = "equities"
    ETFS = "etfs"
    MUTUAL_FUNDS = "mutual_funds"
    GOVERNMENT_BONDS = "government_bonds"
    CORPORATE_BONDS = "corporate_bonds"
    BOND_FUNDS = "bond_funds"
    INFLATION_LINKED_BONDS = "inflation_linked_bonds"
    GOLD_EXCHANGE_TRADED = "gold_exchange_traded"
    PHYSICAL_GOLD = "physical_gold"
    COMMODITIES = "commodities"
    REITS = "reits"
    PROPERTY_FUNDS = "property_funds"
    CRYPTO = "crypto"
    OTHER = "other"


class DataSource(str, Enum):
    QUESTIONNAIRE = "questionnaire"
    DOCUMENT_EXTRACTION = "document_extraction"
    MANUAL_ENTRY = "manual_entry"
    SYSTEM_CALCULATION = "system_calculation"


# =========================
# Shared value models
# =========================

class MoneyValue(StrictBaseModel):
    value_type: ValueType
    currency: str
    amount: Optional[Decimal] = Field(default=None, ge=0)
    minimum_amount: Optional[Decimal] = Field(default=None, ge=0)
    maximum_amount: Optional[Decimal] = Field(default=None, ge=0)

    @field_validator("currency")
    @classmethod
    def normalise_currency(cls, value: str) -> str:
        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError("Currency must use a 3-letter ISO-style code.")

        return value

    @model_validator(mode="after")
    def validate_money_value(self):
        if self.value_type in {ValueType.EXACT, ValueType.APPROXIMATE}:
            if self.amount is None:
                raise ValueError(
                    "Exact or approximate money values require amount."
                )

            if self.minimum_amount is not None or self.maximum_amount is not None:
                raise ValueError(
                    "Exact or approximate money values cannot include "
                    "minimum_amount or maximum_amount."
                )

        if self.value_type == ValueType.RANGE:
            if self.minimum_amount is None or self.maximum_amount is None:
                raise ValueError(
                    "Range values require minimum_amount and maximum_amount."
                )

            if self.amount is not None:
                raise ValueError(
                    "Range values cannot include amount."
                )

            if self.minimum_amount > self.maximum_amount:
                raise ValueError(
                    "minimum_amount cannot exceed maximum_amount."
                )

        return self


class PercentageRange(StrictBaseModel):
    minimum: Decimal = Field(ge=0, le=100)
    maximum: Decimal = Field(ge=0, le=100)

    @model_validator(mode="after")
    def validate_range(self):
        if self.minimum > self.maximum:
            raise ValueError("minimum cannot exceed maximum.")

        return self


class FinancialNeed(StrictBaseModel):
    purpose: Optional[str] = None
    amount: Optional[MoneyValue] = None
    timing: Optional[date] = None
    timing_description: Optional[str] = None
    flexible: Optional[bool] = None


class RecurringContribution(StrictBaseModel):
    amount: MoneyValue
    frequency: ContributionFrequency


# =========================
# Metadata
# =========================

class FieldProvenance(StrictBaseModel):
    source: DataSource
    confirmed_by_user: bool = False
    captured_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class ProfileMetadata(StrictBaseModel):
    schema_version: str = "1.0"
    last_updated: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    # Informational only — never used as an onboarding gate.
    profile_completeness: Optional[int] = Field(
        default=None,
        ge=0,
        le=100,
    )

    # Key is the canonical field path, e.g.
    # "risk.chosen_risk_preference"
    field_provenance: dict[str, FieldProvenance] = Field(
        default_factory=dict
    )


# =========================
# 1. Jurisdiction & currency
# =========================

class JurisdictionCurrency(StrictBaseModel):
    country_of_residence: Optional[str] = None
    tax_residences: list[str] = Field(default_factory=list)
    spending_currency: Optional[str] = None
    income_currencies: list[str] = Field(default_factory=list)
    investment_currencies: list[str] = Field(default_factory=list)

    @field_validator("country_of_residence")
    @classmethod
    def normalise_country(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 2:
            raise ValueError(
                "Country should use a 2-letter ISO-style country code."
            )

        return value

    @field_validator("tax_residences")
    @classmethod
    def normalise_tax_residences(
        cls,
        values: list[str],
    ) -> list[str]:
        result = []

        for value in values:
            value = value.upper().strip()

            if len(value) != 2:
                raise ValueError(
                    "Tax residence should use a 2-letter country code."
                )

            result.append(value)

        return result

    @field_validator(
        "spending_currency",
    )
    @classmethod
    def normalise_optional_currency(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError(
                "Currency should use a 3-letter ISO-style code."
            )

        return value

    @field_validator(
        "income_currencies",
        "investment_currencies",
    )
    @classmethod
    def normalise_currency_lists(
        cls,
        values: list[str],
    ) -> list[str]:
        result = []

        for value in values:
            value = value.upper().strip()

            if len(value) != 3:
                raise ValueError(
                    "Currency should use a 3-letter ISO-style code."
                )

            result.append(value)

        return result


# =========================
# 2. Goals & horizon
# =========================

class Goal(StrictBaseModel):
    goal_type: GoalType
    description: Optional[str] = None


class PortfolioIncomeRequirement(StrictBaseModel):
    amount: MoneyValue
    frequency: ContributionFrequency


class GoalsHorizon(StrictBaseModel):
    primary_goal: Optional[Goal] = None
    secondary_goals: list[Goal] = Field(default_factory=list)

    investment_horizon: Optional[InvestmentHorizon] = None
    target_date: Optional[date] = None

    planned_withdrawals: list[FinancialNeed] = Field(
        default_factory=list
    )

    portfolio_income_requirement: Optional[
        PortfolioIncomeRequirement
    ] = None


# =========================
# 3. Financial circumstances
# =========================

class EmergencyReserve(StrictBaseModel):
    amount: Optional[MoneyValue] = None

    months_of_essential_spending: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )


class Liability(StrictBaseModel):
    liability_type: LiabilityType
    description: Optional[str] = None

    balance: Optional[MoneyValue] = None

    interest_rate_percent: Optional[Decimal] = Field(
        default=None,
        ge=0,
    )

    rate_type: RateType = RateType.UNKNOWN

    monthly_payment: Optional[MoneyValue] = None
    refinancing_or_reset_date: Optional[date] = None


class HouseholdExposure(StrictBaseModel):
    exposure_type: str
    description: Optional[str] = None
    estimated_value: Optional[MoneyValue] = None


class FinancialCircumstances(StrictBaseModel):
    investable_capital: Optional[MoneyValue] = None

    recurring_contributions: list[RecurringContribution] = Field(
        default_factory=list
    )

    income: Optional[MoneyValue] = None
    income_stability: Optional[IncomeStability] = None

    emergency_reserve: Optional[EmergencyReserve] = None

    liabilities: list[Liability] = Field(default_factory=list)

    dependants: Optional[int] = Field(
        default=None,
        ge=0,
    )

    future_obligations: list[FinancialNeed] = Field(
        default_factory=list
    )

    major_household_exposures: list[HouseholdExposure] = Field(
        default_factory=list
    )


# =========================
# 4. Risk
# =========================

class CalculatedRiskCapacity(StrictBaseModel):
    band: RiskCapacityBand

    # Optional because we may choose to expose bands rather than
    # false-precision numerical scoring.
    score: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
    )

    reasons: list[str] = Field(default_factory=list)
    method_version: Optional[str] = None


class LossCapacity(StrictBaseModel):
    amount: Optional[MoneyValue] = None

    percentage: Optional[Decimal] = Field(
        default=None,
        ge=0,
        le=100,
    )

    percentage_range: Optional[PercentageRange] = None

    @model_validator(mode="after")
    def validate_loss_capacity(self):
        provided_values = sum(
            value is not None
            for value in (
                self.amount,
                self.percentage,
                self.percentage_range,
            )
        )

        if provided_values > 1:
            raise ValueError(
                "Loss capacity must use only one representation: "
                "amount, percentage, or percentage_range."
            )

        return self


class RiskProfile(StrictBaseModel):
    # System-derived.
    calculated_risk_capacity: Optional[
        CalculatedRiskCapacity
    ] = None

    # Directly chosen by the investor.
    chosen_risk_preference: Optional[int] = Field(
        default=None,
        ge=1,
        le=10,
    )

    behavioural_drawdown_response: Optional[
        DrawdownResponse
    ] = None

    loss_capacity: Optional[LossCapacity] = None

    investment_experience: Optional[
        InvestmentExperience
    ] = None


# =========================
# 5. Liquidity
# =========================

class ForcedSaleRisk(StrictBaseModel):
    band: ForcedSaleRiskBand
    reasons: list[str] = Field(default_factory=list)
    method_version: Optional[str] = None


class LiquidityProfile(StrictBaseModel):
    near_term_cash_needs: list[FinancialNeed] = Field(
        default_factory=list
    )

    emergency_access_requirement: Optional[
        EmergencyAccessRequirement
    ] = None

    # System-derived.
    forced_sale_risk: Optional[ForcedSaleRisk] = None


# =========================
# 6. Preferences & constraints
# =========================

class PreferencesConstraints(StrictBaseModel):
    excluded_assets: list[str] = Field(default_factory=list)

    ethical_preferences: list[str] = Field(default_factory=list)

    complexity_tolerance: Optional[
        ComplexityTolerance
    ] = None

    income_vs_growth_preference: Optional[
        IncomeGrowthPreference
    ] = None

    # Investor preference only.
    # This does NOT override EducosysDalio's no-leverage policy.
    leverage_preference: Optional[bool] = None

    other_constraints: list[str] = Field(default_factory=list)


# =========================
# 7. Market access
# =========================

class AccountType(StrictBaseModel):
    category: AccountCategory
    local_name: Optional[str] = None


class PlatformAccess(StrictBaseModel):
    # Free text intentionally supports global retail brokers.
    platform_name: str

    country: Optional[str] = None
    account_type: Optional[AccountType] = None
    primary_currency: Optional[str] = None

    @field_validator("country")
    @classmethod
    def normalise_platform_country(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 2:
            raise ValueError(
                "Country should use a 2-letter country code."
            )

        return value

    @field_validator("primary_currency")
    @classmethod
    def normalise_platform_currency(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        if value is None:
            return None

        value = value.upper().strip()

        if len(value) != 3:
            raise ValueError(
                "Currency should use a 3-letter code."
            )

        return value


class MarketAccess(StrictBaseModel):
    platforms_used: list[PlatformAccess] = Field(
        default_factory=list
    )

    account_types: list[AccountType] = Field(
        default_factory=list
    )

    accessible_asset_classes: list[
        AccessibleAssetClass
    ] = Field(default_factory=list)

    supported_currencies: list[str] = Field(
        default_factory=list
    )

    access_unknown: bool = False

    @field_validator("supported_currencies")
    @classmethod
    def normalise_supported_currencies(
        cls,
        values: list[str],
    ) -> list[str]:
        result = []

        for value in values:
            value = value.upper().strip()

            if len(value) != 3:
                raise ValueError(
                    "Currency should use a 3-letter code."
                )

            result.append(value)

        return result


# =========================
# Canonical InvestorProfile
# =========================

class InvestorProfile(StrictBaseModel):
    metadata: ProfileMetadata = Field(
        default_factory=ProfileMetadata
    )

    jurisdiction_currency: JurisdictionCurrency = Field(
        default_factory=JurisdictionCurrency
    )

    goals_horizon: GoalsHorizon = Field(
        default_factory=GoalsHorizon
    )

    financial_circumstances: FinancialCircumstances = Field(
        default_factory=FinancialCircumstances
    )

    risk: RiskProfile = Field(
        default_factory=RiskProfile
    )

    liquidity: LiquidityProfile = Field(
        default_factory=LiquidityProfile
    )

    preferences_constraints: PreferencesConstraints = Field(
        default_factory=PreferencesConstraints
    )

    market_access: MarketAccess = Field(
        default_factory=MarketAccess
    )

    # Derived rather than stored twice.
    @computed_field
    @property
    def expected_withdrawals(self) -> list[FinancialNeed]:
        return (
            self.goals_horizon.planned_withdrawals
            + self.liquidity.near_term_cash_needs
        )