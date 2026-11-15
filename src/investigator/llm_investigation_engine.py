
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from incident_reader import load_incident_report
from llm_investigator import investigate_with_llm


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "reports" / "llm_investigations"


def run_llm_investigation():
    """
    Load the latest incident report, investigate every incident
    using the LLM, and save the results in a separate JSON file.
    """

    print("\nStarting TraceFlow AI LLM Investigation Engine...")

    # Step 1: Load the latest data-quality incident report
    report = load_incident_report()

    incidents = report.get("incidents", [])

    if not incidents:
        print("No incidents found in the report.")
        return None

    print(f"\nDataset: {report.get('dataset', 'Unknown')}")
    print(f"Total incidents found: {len(incidents)}")

    # Step 2: Investigate each incident using the LLM
    investigation_results = []

    for index, incident in enumerate(incidents, start=1):

        order_id = incident.get("order_id", "Unknown")
        category = incident.get("category", "Unknown")

        print(
            f"\n[{index}/{len(incidents)}] "
            f"Investigating {order_id} - {category}..."
        )

        try:
            llm_analysis = investigate_with_llm(incident)

            investigation_results.append({
                "order_id": order_id,
                "incident_category": category,
                "status": "SUCCESS",
                "llm_analysis": llm_analysis
            })

            print("LLM investigation completed successfully.")

        except Exception as error:

            investigation_results.append({
                "order_id": order_id,
                "incident_category": category,
                "status": "FAILED",
                "error": str(error)
            })

            print(f"LLM investigation failed: {error}")

    # Step 3: Create the final investigation report
    successful = sum(
        result["status"] == "SUCCESS"
        for result in investigation_results
    )

    failed = len(investigation_results) - successful

    investigation_report = {
        "investigation_id": str(uuid.uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report_id": report.get("report_id"),
        "dataset": report.get("dataset"),
        "total_incidents": len(incidents),
        "successful_investigations": successful,
        "failed_investigations": failed,
        "investigation_results": investigation_results
    }

    # Step 4: Save the report as a separate JSON file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = (
        OUTPUT_DIR
        / f"llm_investigation_{investigation_report['investigation_id']}.json"
    )

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(investigation_report, file, indent=4)

    # Step 5: Display the final summary
    print("\n========== LLM INVESTIGATION SUMMARY ==========")
    print(f"Total incidents: {len(incidents)}")
    print(f"Successful investigations: {successful}")
    print(f"Failed investigations: {failed}")
    print(f"\nReport saved to:\n{output_file}")

    return investigation_report


if __name__ == "__main__":
    run_llm_investigation()
