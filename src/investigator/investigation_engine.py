
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from incident_reader import load_incident_report
from root_cause_analyzer import analyze_report, display_investigation_results


# Main project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folder where investigation results will be saved
INVESTIGATIONS_DIR = PROJECT_ROOT / "reports" / "investigations"


def run_investigation() -> dict:
    """
    Run the complete incident investigation workflow.
    """

    print("\nStarting TraceFlow AI Investigation...")

    # Step 1: Read the latest incident report
    print("\nStep 1: Loading incident report...")

    incident_report = load_incident_report()

    print(f"Dataset: {incident_report['dataset']}")
    print(f"Incidents found: {incident_report['total_incidents']}")

    # Step 2: Analyze all incidents
    print("\nStep 2: Analyzing incidents...")

    investigation_results = analyze_report(incident_report)

    # Step 3: Prepare consolidated investigation report
    print("\nStep 3: Preparing investigation summary...")

    investigation_report = {
        "investigation_id": str(uuid4()),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_report_id": incident_report["report_id"],
        "dataset": incident_report["dataset"],
        "total_incidents_analyzed": len(investigation_results),
        "investigation_results": investigation_results
    }

    # Step 4: Save the investigation report
    INVESTIGATIONS_DIR.mkdir(parents=True, exist_ok=True)

    filename = (
        f"investigation_"
        f"{investigation_report['investigation_id']}.json"
    )

    output_path = INVESTIGATIONS_DIR / filename

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(investigation_report, file, indent=4)

    print("\nStep 4: Investigation report saved.")
    print(f"Saved location: {output_path}")

    return investigation_report


if __name__ == "__main__":

    try:
        final_report = run_investigation()

        # Display the investigation results
        display_investigation_results(
            final_report["investigation_results"]
        )

        print("\n========== INVESTIGATION SUMMARY ==========")
        print(
            "Total incidents analyzed:",
            final_report["total_incidents_analyzed"]
        )
        print("Investigation completed successfully.")
        print("===========================================")

    except (FileNotFoundError, ValueError, json.JSONDecodeError) as error:
        print(f"\nInvestigation failed: {error}")
