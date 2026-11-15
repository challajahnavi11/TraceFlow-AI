
from typing import Any


def analyze_incident(incident: dict[str, Any]) -> dict[str, Any]:
    """
    Analyze an individual data quality incident.
    Separate detection confidence from root cause confidence.
    """

    category = incident.get("category", "UNKNOWN")
    order_id = incident.get("order_id", "UNKNOWN")

    analysis = {
        "order_id": order_id,
        "incident_category": category,
        "probable_root_cause": "The root cause could not be determined.",
        "evidence": [],
        "recommended_action": "Investigate this incident manually.",
        "detection_confidence": "HIGH",
        "root_cause_confidence": "LOW",
        "confidence_reason": (
            "The data-quality issue is detected, "
            "but its underlying cause has not been verified."
        ),
        "requires_human_review": True
    }

    # Rule 1: Duplicate Order ID
    if category == "DUPLICATE_ORDER_ID":

        analysis["probable_root_cause"] = (
            "The same order ID appears in multiple records. "
            "This may be caused by duplicate source records "
            "or an issue during data ingestion."
        )

        analysis["evidence"] = [
            incident.get("message", ""),
            f"Affected rows: {incident.get('row_numbers', [])}"
        ]

        analysis["recommended_action"] = (
            "Compare the duplicate records with the source system. "
            "Determine whether they represent the same order before "
            "removing or correcting any record."
        )

    # Rule 2: Missing Value
    elif category == "MISSING_VALUE":

        analysis["probable_root_cause"] = (
            "The product field is missing. This may have happened "
            "because the source system did not provide the value "
            "or the value was lost during data processing."
        )

        analysis["evidence"] = [
            incident.get("message", ""),
            f"Affected field: {incident.get('affected_field', 'Unknown')}"
        ]

        analysis["recommended_action"] = (
            "Retrieve the correct product value from the source system. "
            "Do not guess or automatically fill in the missing value."
        )

    # Rule 3: Total Amount Mismatch
    elif category == "TOTAL_MISMATCH":

        expected = incident.get("expected_value")
        actual = incident.get("actual_value")

        analysis["probable_root_cause"] = (
            "The recorded total amount does not match the expected "
            "amount. This may be caused by an incorrect calculation "
            "or incorrect input values."
        )

        analysis["evidence"] = [
            incident.get("message", ""),
            f"Expected total: {expected}",
            f"Actual total: {actual}"
        ]

        analysis["recommended_action"] = (
            "Verify the quantity and unit price, then recalculate "
            "the total amount. Check the source data before updating it."
        )

    # Rule 4: Invalid Payment Status
    elif category == "INVALID_PAYMENT_STATUS":

        analysis["probable_root_cause"] = (
            "The payment status contains a value that is not part "
            "of the accepted payment status list. This may indicate "
            "an invalid source value or a mismatch between systems."
        )

        analysis["evidence"] = [
            incident.get("message", ""),
            f"Unexpected value: {incident.get('actual_value')}",
            f"Allowed values: {incident.get('expected_value')}"
        ]

        analysis["recommended_action"] = (
            "Verify the payment status with the payment source system "
            "and map it to an approved status only after confirmation."
        )

    else:
        analysis["detection_confidence"] = "LOW"
        analysis["root_cause_confidence"] = "LOW"
        analysis["confidence_reason"] = (
            "No investigation rule exists for this incident category."
        )

    return analysis


def analyze_report(report: dict[str, Any]) -> list[dict[str, Any]]:
    """Analyze every incident in an incident report."""

    incidents = report.get("incidents", [])

    investigation_results = []

    for incident in incidents:
        result = analyze_incident(incident)
        investigation_results.append(result)

    return investigation_results


def display_investigation_results(
    results: list[dict[str, Any]]
) -> None:
    """Display investigation results in a readable format."""

    print("\n========== ROOT CAUSE ANALYSIS ==========")

    for number, result in enumerate(results, start=1):

        print(f"\nInvestigation {number}")
        print("-----------------------------------------")

        print(f"Order ID                  : {result['order_id']}")
        print(f"Incident                  : {result['incident_category']}")

        print("\nProbable Root Cause:")
        print(result["probable_root_cause"])

        print("\nEvidence:")

        for evidence in result["evidence"]:
            print(f"- {evidence}")

        print("\nRecommended Action:")
        print(result["recommended_action"])

        print("\nConfidence Assessment:")
        print(f"Detection Confidence      : {result['detection_confidence']}")
        print(f"Root Cause Confidence     : {result['root_cause_confidence']}")
        print(f"Reason                    : {result['confidence_reason']}")

        print(f"\nHuman Review Required     : {result['requires_human_review']}")

    print("\n=========================================")


if __name__ == "__main__":

    from incident_reader import load_incident_report

    try:
        report = load_incident_report()
        results = analyze_report(report)
        display_investigation_results(results)

    except (FileNotFoundError, ValueError) as error:
        print(f"Investigation Error: {error}")
