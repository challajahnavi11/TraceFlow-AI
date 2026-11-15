
import json
from pathlib import Path

import pandas as pd
import streamlit as st


# --------------------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

REPORTS_DIR = (
    PROJECT_ROOT
    / "reports"
    / "combined_investigations"
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="TraceFlow AI",
    page_icon="🔍",
    layout="wide"
)


# --------------------------------------------------
# LOAD LATEST INVESTIGATION REPORT
# --------------------------------------------------

def load_latest_report():

    if not REPORTS_DIR.exists():
        return None

    report_files = list(
        REPORTS_DIR.glob("combined_investigation_*.json")
    )

    if not report_files:
        return None

    latest_file = max(
        report_files,
        key=lambda file: file.stat().st_mtime
    )

    with latest_file.open("r", encoding="utf-8") as file:
        report = json.load(file)

    return report


# --------------------------------------------------
# DASHBOARD HEADER
# --------------------------------------------------

st.title("🔍 TraceFlow AI")

st.subheader("Intelligent Data Pipeline Investigator")

st.write(
    "An AI-powered system that detects data-quality "
    "issues and investigates their possible root causes."
)

st.divider()


# --------------------------------------------------
# LOAD REPORT
# --------------------------------------------------

try:
    report = load_latest_report()

except Exception as error:
    st.error(f"Unable to load investigation report: {error}")
    st.stop()


if report is None:

    st.warning(
        "No combined investigation report found. "
        "Run the combined investigation engine first."
    )

    st.stop()


results = report.get(
    "combined_investigation_results", []
)


# --------------------------------------------------
# SUMMARY METRICS
# --------------------------------------------------

total_incidents = report.get(
    "total_incidents", len(results)
)

rule_successes = report.get(
    "successful_rule_based_analyses", 0
)

llm_successes = report.get(
    "successful_llm_analyses", 0
)

high_severity = sum(
    result.get("original_incident", {}).get("severity") == "HIGH"
    for result in results
)

medium_severity = sum(
    result.get("original_incident", {}).get("severity") == "MEDIUM"
    for result in results
)

low_severity = sum(
    result.get("original_incident", {}).get("severity") == "LOW"
    for result in results
)

# --------------------------------------------------
# RUN NEW INVESTIGATION
# --------------------------------------------------

st.header("Run New Investigation")

if st.button("🚀 Run Investigation", type="primary"):

    with st.spinner("Running TraceFlow AI investigation..."):

        import subprocess
        import sys

        engine_path = (
            PROJECT_ROOT
            / "src"
            / "investigator"
            / "combined_investigation_engine.py"
        )

        try:
            result = subprocess.run(
                [sys.executable, str(engine_path)],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=300
            )

            if result.returncode == 0:
                st.success("Investigation completed successfully!")

                with st.expander("Execution details"):
                    st.code(result.stdout)

                st.rerun()

            else:
                st.error("Investigation failed.")

                with st.expander("Error details"):
                    st.code(result.stderr)

        except subprocess.TimeoutExpired:
            st.error("Investigation timed out after 5 minutes.")

        except Exception as error:
            st.error(f"Unexpected error: {error}")

st.header("Investigation Overview")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Incidents",
    total_incidents
)

col2.metric(
    "High Severity",
    high_severity
)

col3.metric(
    "Rule-Based Success",
    f"{rule_successes}/{total_incidents}"
)

col4.metric(
    "LLM Success",
    f"{llm_successes}/{total_incidents}"
)


# --------------------------------------------------
# SEVERITY BREAKDOWN
# --------------------------------------------------

st.subheader("Incident Severity Breakdown")

severity_data = pd.DataFrame({
    "Severity": ["HIGH", "MEDIUM", "LOW"],
    "Count": [
        high_severity,
        medium_severity,
        low_severity
    ]
})

st.bar_chart(
    data=severity_data,
    x="Severity",
    y="Count",
    horizontal=True
)

st.divider()


# --------------------------------------------------
# INCIDENT SUMMARY TABLE
# --------------------------------------------------

st.header("Detected Incidents")

table_data = []

for result in results:

    incident = result.get("original_incident", {})

    table_data.append({
        "Order ID": result.get("order_id", "Unknown"),
        "Category": result.get("incident_category", "Unknown"),
        "Severity": incident.get("severity", "Unknown"),
        "Rule-Based": result.get("rule_based_status", "Unknown"),
        "LLM": result.get("llm_status", "Unknown"),
        "Human Review": result.get("requires_human_review", True)
    })


if table_data:

    st.dataframe(
     pd.DataFrame(table_data),
     width="stretch",
     hide_index=True
)


# --------------------------------------------------
# DETAILED INCIDENT INVESTIGATION
# --------------------------------------------------

st.divider()

st.header("Detailed Incident Investigation")

if results:

    incident_options = [
        (
            f"{result.get('order_id', 'Unknown')} - "
            f"{result.get('incident_category', 'Unknown')}"
        )
        for result in results
    ]

    selected_incident = st.selectbox(
        "Select an incident to investigate",
        incident_options
    )

    selected_index = incident_options.index(
        selected_incident
    )

    selected_result = results[selected_index]

    original_incident = selected_result.get(
        "original_incident", {}
    )

    rule_analysis = selected_result.get(
        "rule_based_analysis"
    )

    llm_analysis = selected_result.get(
        "llm_analysis"
    )


    # Original incident
    st.subheader("1. Original Data-Quality Incident")

    st.json(original_incident)


    # Rule-based analysis
    st.subheader("2. Rule-Based Investigation")

    if rule_analysis:

        st.write(
            "**Probable Root Cause:**",
            rule_analysis.get(
                "probable_root_cause", "Not available"
            )
        )

        st.write(
            "**Detection Confidence:**",
            rule_analysis.get(
                "detection_confidence", "Unknown"
            )
        )

        st.write(
            "**Root Cause Confidence:**",
            rule_analysis.get(
                "root_cause_confidence", "Unknown"
            )
        )

        st.write("**Evidence:**")

        for evidence in rule_analysis.get("evidence", []):
            st.write(f"- {evidence}")

    else:

        st.warning("Rule-based analysis was unsuccessful.")


    # LLM analysis
    st.subheader("3. AI-Powered Investigation")

    if llm_analysis:

        st.write("**Incident Summary:**")

        st.write(
            llm_analysis.get(
                "incident_summary", "Not available"
            )
        )

        st.write("**Observed Evidence:**")

        for evidence in llm_analysis.get(
            "observed_evidence", []
        ):
            st.write(f"- {evidence}")

        st.write("**Possible Root Causes:**")

        for cause in llm_analysis.get(
            "possible_root_causes", []
        ):
            st.write(f"- {cause}")

        st.write("**AI Recommended Actions:**")

        for action in llm_analysis.get(
            "recommended_actions", []
        ):
            st.write(f"- {action}")

        st.write(
            "**Root Cause Confidence:**",
            llm_analysis.get(
                "root_cause_confidence", "Unknown"
            )
        )

        st.caption(
            llm_analysis.get(
                "confidence_reason", ""
            )
        )

    else:

        st.warning("LLM investigation was unsuccessful.")


    # Combined recommendations
    st.subheader("4. Combined Recommendations")

    recommendations = selected_result.get(
        "combined_recommendations", []
    )

    if recommendations:

        for recommendation in recommendations:

            source = recommendation.get(
                "source", "Unknown"
            )

            action = recommendation.get(
                "action", ""
            )

            st.write(f"**{source}:** {action}")

    else:

        st.info("No recommendations available.")


    # Human review
    st.divider()

    st.warning(
        "Human review required: "
        "All AI-generated root-cause suggestions are "
        "hypotheses until independently verified."
    )


# --------------------------------------------------
# REPORT INFORMATION
# --------------------------------------------------

st.divider()

st.header("Report Information")

info_col1, info_col2 = st.columns(2)

info_col1.write(
    "**Investigation ID:** "
    + str(report.get("investigation_id", "Unknown"))
)

info_col1.write(
    "**Source Report ID:** "
    + str(report.get("source_report_id", "Unknown"))
)

info_col2.write(
    "**Dataset:** "
    + str(report.get("dataset", "Unknown"))
)

info_col2.write(
    "**Generated At:** "
    + str(report.get("generated_at", "Unknown"))
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "TraceFlow AI | Intelligent Data Pipeline Investigator"
)
