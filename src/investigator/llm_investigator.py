
import json
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from groq import Groq


# Locate project root and load API credentials.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

MODEL_NAME = "openai/gpt-oss-120b"


def create_groq_client() -> Groq:
    """Create an authenticated Groq client."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not found. Check the project .env file."
        )

    return Groq(api_key=api_key)


def investigate_with_llm(
    incident: dict[str, Any]
) -> dict[str, Any]:
    """
    Investigate one data-quality incident using an LLM.

    The LLM provides hypotheses, not verified root causes.
    """

    client = create_groq_client()

    prompt = f"""
You are TraceFlow AI, a data pipeline investigation assistant.

Investigate the following data-quality incident.

INCIDENT DETAILS:
{json.dumps(incident, indent=2, default=str)}

Your responsibilities:
1. Explain what data-quality issue occurred.
2. Identify the evidence directly available in the incident.
3. Suggest possible root causes as hypotheses.
4. Recommend practical investigation steps.
5. Clearly distinguish facts from assumptions.

Important rules:
- Never invent missing evidence.
- Never claim a possible cause is verified.
- Do not modify or delete any business data.
- If evidence is insufficient, say so.
- Human review is always required.

Return ONLY a valid JSON object with these keys:

{{
    "incident_summary": "Short explanation",
    "observed_evidence": ["Evidence item 1"],
    "possible_root_causes": ["Possible cause 1"],
    "recommended_actions": ["Action 1"],
    "root_cause_confidence": "LOW",
    "confidence_reason": "Why the root cause is unverified",
    "requires_human_review": true
}}

Use LOW for root_cause_confidence because the underlying
cause has not been independently verified.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_completion_tokens=1000
    )

    response_text = response.choices[0].message.content

    if not response_text:
        raise ValueError("The LLM returned an empty response.")

    # Convert the LLM response into a Python dictionary.
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The LLM did not return valid JSON."
        ) from error

    # Validate the expected response structure.
    required_fields = [
        "incident_summary",
        "observed_evidence",
        "possible_root_causes",
        "recommended_actions",
        "root_cause_confidence",
        "confidence_reason",
        "requires_human_review"
    ]

    missing_fields = [
        field for field in required_fields if field not in result
    ]

    if missing_fields:
        raise ValueError(
            f"LLM response is missing fields: {missing_fields}"
        )

    # Enforce human review for this prototype.
    result["root_cause_confidence"] = "LOW"
    result["requires_human_review"] = True

    return result


if __name__ == "__main__":

    sample_incident = {
        "category": "TOTAL_MISMATCH",
        "order_id": "ORD0004",
        "message": "Expected 12000, found 12100.",
        "affected_field": "total_amount",
        "expected_value": 12000,
        "actual_value": 12100
    }

    try:
        print("Starting TraceFlow AI LLM Investigation...")

        investigation = investigate_with_llm(sample_incident)

        print("\n========== LLM INVESTIGATION ==========")
        print(json.dumps(investigation, indent=4))
        print("\nLLM investigation completed successfully.")

    except Exception as error:
        print("\nLLM investigation failed.")
        print("Error:", str(error))
