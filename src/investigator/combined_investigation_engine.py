
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from incident_reader import load_incident_report
from root_cause_analyzer import analyze_incident
from llm_investigator import investigate_with_llm


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "reports" / "combined_investigations"


def combine_recommendations(rule_analysis, llm_analysis):
    """Combine recommendations from both investigation methods."""

    recommendations = []

    rule_action = rule_analysis.get("recommended_action")

    if rule_action:
        recommendations.append({
            "source": "RULE_BASED",
            "action": rule_action
        })

    if llm_analysis:
        for action in llm_analysis.get("recommended_actions", []):
            recommendations.append({
                "source": "LLM",
                "action": action
            })

    return recommendations


def run_combined_investigation():

    print("\nStarting TraceFlow AI Combined Investigation...")

    # Step 1: Load the latest incident report
    report = load_incident_report()
    incidents = report.get("incidents", [])

    if not incidents:
        print("No incidents found.")
        return None

    print(f"\nDataset: {report.get('dataset', 'Unknown')}")
    print(f"Total incidents: {len(incidents)}")

    combined_results = []

    # Step 2: Analyze every incident
    for index, incident in enumerate(incidents, start=1):

        order_id = incident.get("order_id", "Unknown")
        category = incident.get("category", "Unknown")

        print(
            f"\n[{index}/{len(incidents)}] "
            f"Analyzing {order_id} - {category}"
        )

        # Rule-based investigation
        try:
            rule_analysis = analyze_incident(incident)
            rule_status = "SUCCESS"

            print("Rule-based analysis completed.")

        except Exception as error:
            rule_analysis = None
            rule_status = "FAILED"

            print(f"Rule-based analysis failed: {error}")

        # LLM investigation
        try:
            llm_analysis = investigate_with_llm(incident)
            llm_status = "SUCCESS"

            print("LLM analysis completed.")

        except Exception as error:
            llm_analysis = None
            llm_status = "FAILED"

            print(f"LLM analysis failed: {error}")

        # Combine available findings
        combined_results.append({
            "order_id": order_id,
            "incident_category": category,
            "original_incident": incident,

            "rule_based_status": rule_status,
            "rule_based_analysis": rule_analysis,

            "llm_status": llm_status,
            "llm_analysis": llm_analysis,

            "combined_recommendations": combine_recommendations(
                rule_analysis or {},
                llm_analysis
            ),

            "requires_human_review": True
        })

    # Step 3: Calculate summary statistics
    rule_successes = sum(
        result["rule_based_status"] == "SUCCESS"
        for result in combined_results
    )

    llm_successes = sum(
        result["llm_status"] == "SUCCESS"
        for result in combined_results
    )

    # Step 4: Create combined investigation report
    investigation_report = {
        "investigation_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report_id": report.get("report_id"),
        "dataset": report.get("dataset"),

        "total_incidents": len(incidents),

        "successful_rule_based_analyses": rule_successes,
        "successful_llm_analyses": llm_successes,

        "combined_investigation_results": combined_results
    }

    # Step 5: Save report
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR
        / f"combined_investigation_"
          f"{investigation_report['investigation_id']}.json"
    )

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(investigation_report, file, indent=4)

    # Step 6: Display summary
    print("\n========== COMBINED INVESTIGATION SUMMARY ==========")

    print(f"Total incidents: {len(incidents)}")
    print(f"Successful rule-based analyses: {rule_successes}")
    print(f"Successful LLM analyses: {llm_successes}")

    print(f"\nReport saved to:\n{output_file}")

    return investigation_report


if __name__ == "__main__":
    try:
        run_combined_investigation()

    except Exception as error:
        print("\nCombined investigation failed.")
        print("Error:", str(error))
