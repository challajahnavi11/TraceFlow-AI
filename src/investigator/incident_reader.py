
import json
from pathlib import Path


# Find the main project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Folder containing individual incident reports
REPORTS_DIR = PROJECT_ROOT / "reports" / "incidents"


def find_latest_report(reports_dir: Path = REPORTS_DIR) -> Path:
    """Find the most recently generated incident report."""

    report_files = list(reports_dir.glob("report_*.json"))

    if not report_files:
        raise FileNotFoundError(
            f"No incident reports found in: {reports_dir}"
        )

    latest_report = max(
        report_files,
        key=lambda file: file.stat().st_mtime
    )

    return latest_report


def load_incident_report(report_path: Path | None = None) -> dict:
    """Load and validate an incident report."""

    if report_path is None:
        report_path = find_latest_report()

    with report_path.open("r", encoding="utf-8") as file:
        report = json.load(file)

    if not isinstance(report, dict):
        raise ValueError("Invalid report: expected a JSON object.")

    required_fields = [
        "report_id",
        "dataset",
        "total_incidents",
        "incidents",
        "status"
    ]

    for field in required_fields:
        if field not in report:
            raise ValueError(
                f"Invalid report: missing field '{field}'."
            )

    if not isinstance(report["incidents"], list):
        raise ValueError("Invalid report: incidents must be a list.")

    return report


def display_incident_report(report: dict) -> None:
    """Display a readable summary of the incident report."""

    print("\n========== TRACEFLOW AI ==========")
    print("       INCIDENT INVESTIGATOR")
    print("=================================")

    print(f"Dataset          : {report['dataset']}")
    print(f"Report ID        : {report['report_id']}")
    print(f"Status           : {report['status']}")
    print(f"Total Incidents  : {report['total_incidents']}")

    print("\n---------- DETECTED INCIDENTS ----------")

    if not report["incidents"]:
        print("No incidents found.")

    for number, incident in enumerate(report["incidents"], start=1):
        print(f"\nIncident {number}")
        print(f"Category         : {incident.get('category', 'Unknown')}")
        print(f"Severity         : {incident.get('severity', 'Unknown')}")
        print(f"Order ID         : {incident.get('order_id', 'Unknown')}")
        print(f"Message          : {incident.get('message', 'No message')}")
        print(
            f"Suggested Action : "
            f"{incident.get('suggested_resolution', 'Not available')}"
        )

    print("\n========================================")


if __name__ == "__main__":
    try:
        latest_report = find_latest_report()
        incident_report = load_incident_report(latest_report)

        print(f"\nLoaded report from: {latest_report}")
        display_incident_report(incident_report)

    except (FileNotFoundError, json.JSONDecodeError, ValueError) as error:
        print(f"\nError: {error}")
