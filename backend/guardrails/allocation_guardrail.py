from dataclasses import dataclass # Provides a small immutable result object for deterministic guardrail checks.
from decimal import Decimal # Precise threshold and weight comparisons for deterministic allocation checks.

from models.allocation import ProposedAllocation # Structured proposal produced by the Allocation Agent.
from models.market import AssetClass # Canonical asset classes the guardrail is allowed to evaluate.


# =========================
# Allocation Guardrail Result
# Records whether a proposal passed and exactly why it was rejected.
# =========================

@dataclass(
    frozen=True,
)
class AllocationGuardrailResult:

    passed: bool # True only when every deterministic allocation rule passes.

    violations: tuple[
        str,
        ...,
    ] = () # Human-readable reasons explaining every failed rule.


# =========================
# Allocation Guardrail
# Applies deterministic allocation-policy checks to a validated proposal.
# =========================

def evaluate_allocation_guardrail(
    proposal: ProposedAllocation,
    max_weight_by_asset_class: dict[
        AssetClass,
        Decimal,
    ] | None = None,
) -> AllocationGuardrailResult:

    violations: list[str] = [] # Collect every deterministic policy violation before returning.

    configured_limits = (
        max_weight_by_asset_class
        if max_weight_by_asset_class is not None
        else {}
    ) # No asset-class ceiling exists unless the product explicitly configures one.

    # =========================
    # Validate Configured Limits
    # Rejects invalid guardrail configuration before evaluating the proposal.
    # =========================

    for asset_class, maximum_weight in configured_limits.items():

        if maximum_weight < Decimal("0"):
            raise ValueError(
                f"Maximum weight for {asset_class.value} cannot be negative."
            )

        if maximum_weight > Decimal("100"):
            raise ValueError(
                f"Maximum weight for {asset_class.value} cannot exceed 100%."
            )

    # =========================
    # Asset-Class Maximums
    # Checks only limits explicitly supplied by product policy.
    # =========================

    for target in proposal.targets:

        maximum_weight = configured_limits.get(
            target.asset_class
        ) # Retrieve an explicit ceiling for this asset class, if one exists.

        if maximum_weight is None:
            continue # No configured rule means the guardrail must not invent one.

        if target.target_weight_pct > maximum_weight:

            violations.append(
                (
                    f"{target.asset_class.value} target weight "
                    f"{target.target_weight_pct}% exceeds the configured "
                    f"maximum of {maximum_weight}%."
                )
            )

    # =========================
    # Guardrail Result
    # Returns one deterministic decision plus all policy violations.
    # =========================

    return AllocationGuardrailResult(
        passed=not violations,
        violations=tuple(
            violations
        ),
    )