import json
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage


# =========================
# Input Guardrail
# =========================

def _json_from_llm(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")

    return json.loads(text[start : end + 1])


def evaluate_input_guardrail(
    user_query: str,
    llm: Any,
) -> dict[str, Any]:

    prompt = f"""
Determine whether this request belongs to the EducosysDalio
investment-advisory and financial-education system.

Valid requests include:
- investing
- asset allocation
- portfolio analysis
- diversification
- investment risk
- economic and market cycles
- inflation, growth and interest rates
- asset classes
- long-term financial planning

Do not reject a valid investment request merely because the
InvestorProfile or Portfolio is incomplete.

Block:
- clearly unrelated requests
- financial fraud
- deception
- market manipulation
- illegal financial activity

Return strict JSON only:

{{
  "allowed": true,
  "reason": ""
}}

User request:
{user_query}
"""

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are the input guardrail for EducosysDalio. "
                        "Return strict JSON only."
                    )
                ),
                HumanMessage(content=prompt),
            ]
        )

        parsed = _json_from_llm(str(response.content))

        return {
            "allowed": bool(parsed.get("allowed", True)),
            "reason": str(parsed.get("reason", "")).strip(),
        }

    except Exception as exc:
        print(f"Input guardrail fallback used: {exc}")

        return {
            "allowed": True,
            "reason": "Guardrail fallback allowed the request.",
        }