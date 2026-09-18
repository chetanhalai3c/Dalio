from enum import Enum # Defines the three explicit human decisions.

from pydantic import (
    BaseModel,
    ConfigDict,
    model_validator,
) # Validates human-review data before it enters workflow state.


# =========================
# Strict Base Model
# Rejects unexpected HITL fields.
# =========================

class StrictBaseModel(BaseModel):

    model_config = ConfigDict(
        extra="forbid"
    )


# =========================
# Review Decision
# Human remains the final decision-maker.
# =========================

class ReviewDecision(
    str,
    Enum,
):

    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"


# =========================
# Human Review
# Structured result of the investor's review decision.
# =========================

class HumanReview(StrictBaseModel):

    decision: ReviewDecision # Approve, modify or reject the proposed allocation.

    feedback: str = "" # Optional explanation; mandatory when requesting modification.

    @model_validator(
        mode="after"
    )
    def validate_review(
        self,
    ):

        if (
            self.decision == ReviewDecision.MODIFY
            and not self.feedback.strip()
        ):
            raise ValueError(
                "Feedback is required when requesting an allocation modification."
            )

        return self