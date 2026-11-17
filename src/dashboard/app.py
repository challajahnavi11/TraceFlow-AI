import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ============================================================
# TRACEFLOW AI — DASHBOARD PRESENTATION
# Existing investigation engine and JSON report structure kept.
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = PROJECT_ROOT / "reports" / "combined_investigations"
ENGINE_PATH = PROJECT_ROOT / "src" / "investigator" / "combined_investigation_engine.py"

st.set_page_config(
    page_title="TraceFlow AI | Investigator",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ------------------------- Visual system -------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --ink: #18263d;
        --muted: #77849a;
        --line: #e7ebf2;
        --canvas: #f5f7fb;
        --blue: #315eea;
        --blue-soft: #edf2ff;
        --green: #16835d;
        --green-soft: #e9f7f0;
        --red: #c44250;
        --red-soft: #fff0f1;
        --amber: #a96d16;
        --amber-soft: #fff6e7;
    }

    html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
    .stApp { background: var(--canvas); color: var(--ink); }
    .block-container { max-width: 1500px; padding: 1.5rem 2rem 3rem; }

    [data-testid="stSidebar"] {
        background: #142139;
        border-right: 1px solid #263752;
    }
    [data-testid="stSidebar"] * { color: #edf2fa; }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] { color: #a7b4c8; }
    [data-testid="stSidebar"] hr { border-color: #30405a; }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: .42rem .15rem;
        font-weight: 650;
    }

    h1, h2, h3, h4 { color: var(--ink); letter-spacing: -.035em; }
    h1 { font-weight: 800; }
    h2 { font-size: 1.42rem; font-weight: 800; }
    h3 { font-size: 1.02rem; font-weight: 800; }
    p { color: #526078; }

    [data-testid="stMetric"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1rem 1.1rem;
        box-shadow: 0 5px 18px rgba(26, 44, 74, .035);
    }
    [data-testid="stMetricLabel"] {
        color: #78869b;
        font-size: .75rem;
        font-weight: 750;
    }
    [data-testid="stMetricValue"] {
        color: var(--ink);
        font-size: 1.8rem;
        font-weight: 800;
    }

    .brand {
        font-size: 1.25rem;
        font-weight: 800;
        letter-spacing: -.045em;
        color: white;
    }
    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 30px;
        height: 30px;
        margin-right: 8px;
        border-radius: 9px;
        color: white;
        background: #315eea;
        font-weight: 800;
    }
    .side-kicker {
        color: #91a2bc;
        font-size: .65rem;
        font-weight: 800;
        letter-spacing: .15em;
        margin-top: 3px;
    }
    .eyebrow {
        color: #63769a;
        font-size: .67rem;
        font-weight: 800;
        letter-spacing: .16em;
        text-transform: uppercase;
        margin-bottom: .45rem;
    }
    .page-title {
        color: var(--ink);
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -.065em;
        line-height: 1.12;
        margin: 0;
    }
    .page-description {
        color: #7b879a;
        font-size: .91rem;
        margin-top: .55rem;
        max-width: 780px;
    }
    .topline {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        padding-bottom: 1.15rem;
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
    }
    .surface {
        background: white;
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.05rem 1.15rem;
        height: 100%;
    }
    .surface-heading {
        color: var(--ink);
        font-size: .96rem;
        font-weight: 800;
        margin-bottom: .2rem;
    }
    .surface-caption {
        color: #8a96a8;
        font-size: .75rem;
        margin-bottom: .8rem;
    }
    .step {
        display: flex;
        gap: .8rem;
        align-items: flex-start;
        padding: .72rem 0;
        border-bottom: 1px solid #edf0f5;
    }
    .step:last-child { border-bottom: 0; }
    .step-number {
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 27px;
        width: 27px;
        height: 27px;
        border-radius: 8px;
        background: var(--blue-soft);
        color: var(--blue);
        font-family: 'DM Mono', monospace;
        font-size: .7rem;
        font-weight: 700;
    }
    .step-title { color: var(--ink); font-size: .83rem; font-weight: 800; }
    .step-detail { color: #8a96a8; font-size: .73rem; margin-top: .12rem; }
    .pill {
        display: inline-block;
        border-radius: 99px;
        padding: .28rem .62rem;
        font-size: .67rem;
        font-weight: 800;
        letter-spacing: .035em;
    }
    .pill-blue { background: var(--blue-soft); color: #3155bd; }
    .pill-green { background: var(--green-soft); color: var(--green); }
    .pill-red { background: var(--red-soft); color: var(--red); }
    .pill-amber { background: var(--amber-soft); color: var(--amber); }
    .pill-neutral { background: #eef1f5; color: #66748a; }
    .mono { font-family: 'DM Mono', monospace; font-size: .75rem; color: #64738a; }
    .evidence {
        border-left: 3px solid #cbd7ec;
        padding: .2rem 0 .25rem .8rem;
        margin: .45rem 0;
        color: #43536c;
        font-size: .86rem;
    }
    .callout {
        border: 1px solid #f0dcae;
        background: #fff9ec;
        border-radius: 12px;
        padding: .85rem 1rem;
        color: #805b1b;
        font-size: .83rem;
    }
    [data-testid="stDataFrame"] {
        border: 1px solid var(--line);
        border-radius: 12px;
        overflow: hidden;
        background: white;
    }
    [data-testid="stExpander"] {
        background: white;
        border: 1px solid var(--line);
        border-radius: 11px;
    }
    .stButton button {
        border-radius: 9px;
        font-weight: 750;
        min-height: 2.55rem;
    }
    .stButton button[kind="primary"] {
        background: var(--blue);
        border-color: var(--blue);
    }
    hr { border-color: var(--line) !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ------------------------- Existing report logic -------------------------
def load_latest_report():
    if not REPORTS_DIR.exists():
        return None

    report_files = list(REPORTS_DIR.glob("combined_investigation_*.json"))
    if not report_files:
        return None

    latest_file = max(report_files, key=lambda file: file.stat().st_mtime)
    with latest_file.open("r", encoding="utf-8") as file:
        return json.load(file)


def page_heading(section, title, description):
    st.markdown(f'<div class="eyebrow">{section}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="page-description">{description}</div>', unsafe_allow_html=True)
    st.write("")


def tag(label, tone="neutral"):
    st.markdown(f'<span class="pill pill-{tone}">{label}</span>', unsafe_allow_html=True)


def severity_tone(severity):
    value = str(severity).upper()
    if value == "HIGH":
        return "red"
    if value == "MEDIUM":
        return "amber"
    if value == "LOW":
        return "green"
    return "neutral"


def show_list(items, empty_text="No information recorded."):
    if items:
        for item in items:
            st.markdown(f'<div class="evidence">{item}</div>', unsafe_allow_html=True)
    else:
        st.caption(empty_text)


def run_investigation():
    if not ENGINE_PATH.exists():
        st.error(f"Investigation engine not found: {ENGINE_PATH}")
        return

    with st.spinner("Running the TraceFlow investigation engine..."):
        try:
            result = subprocess.run(
                [sys.executable, str(ENGINE_PATH)],
                capture_output=True,
                text=True,
                cwd=str(PROJECT_ROOT),
                timeout=300,
            )

            if result.returncode == 0:
                st.success("Investigation engine completed.")
                with st.expander("Execution details"):
                    st.code(result.stdout or "No standard output.")
                st.rerun()
            else:
                st.error("Investigation engine returned an error.")
                with st.expander("Error details", expanded=True):
                    st.code(result.stderr or result.stdout or "No error output.")

        except subprocess.TimeoutExpired:
            st.error("Investigation timed out after 5 minutes.")
        except Exception as error:
            st.error(f"Unable to run the investigation: {error}")


# ------------------------- Sidebar -------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">T</span>TraceFlow AI</div>'
        '<div class="side-kicker">INTELLIGENT DATA INVESTIGATION</div>',
        unsafe_allow_html=True,
    )
    st.divider()
    st.markdown("**WORKSPACE**")
    current_page = st.radio(
        "Navigate",
        ["Overview", "Incident Explorer", "AI Investigation", "Report Details"],
        label_visibility="collapsed",
    )
    st.divider()
    st.markdown("**INVESTIGATION ENGINE**")
    st.caption("Rule-based analysis")
    st.caption("Groq-powered LLM analysis")
    st.caption("Evidence-led recommendations")
    st.divider()
    st.markdown('<div class="side-kicker">LOCAL ENVIRONMENT</div>', unsafe_allow_html=True)
    st.caption("Streamlit · Python · Pandas")
    st.caption("TraceFlow AI / v1")


# ------------------------- Load report -------------------------
try:
    report = load_latest_report()
except Exception as error:
    st.error(f"Unable to load investigation report: {error}")
    st.stop()

if report is None:
    page_heading(
        "TRACEFLOW / INVESTIGATION CONSOLE",
        "Your investigation workspace",
        "Run the combined investigation engine to generate the first report and populate this workspace.",
    )
    st.info("No combined investigation report found.")
    if st.button("Run investigation", type="primary"):
        run_investigation()
    st.stop()

results = report.get("combined_investigation_results", [])

total_incidents = report.get("total_incidents", len(results))
rule_successes = report.get("successful_rule_based_analyses", 0)
llm_successes = report.get("successful_llm_analyses", 0)

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


# ------------------------- Top application header -------------------------
left, right = st.columns([5, 1.5], vertical_alignment="center")
with left:
    st.markdown('<div class="eyebrow">DATA PIPELINE INTELLIGENCE</div>', unsafe_allow_html=True)
    st.markdown("## TraceFlow AI", help="Intelligent Data Pipeline Investigator")
    st.caption("Detect data-quality incidents. Investigate possible causes. Review evidence-backed actions.")
with right:
    if st.button("↻  Run investigation", type="primary", width="stretch"):
        run_investigation()

st.markdown('<div class="topline"></div>', unsafe_allow_html=True)


# ============================================================
# WORKSPACE 1 — OVERVIEW
# ============================================================
if current_page == "Overview":
    page_heading(
        "WORKSPACE / OVERVIEW",
        "Investigation overview",
        "A concise view of the latest combined investigation and the incidents that need attention.",
    )

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total incidents", total_incidents)
    metric_cols[1].metric("High severity", high_severity)
    metric_cols[2].metric("Rule-based success", f"{rule_successes}/{total_incidents}")
    metric_cols[3].metric("LLM success", f"{llm_successes}/{total_incidents}")

    st.write("")
    left_col, right_col = st.columns([1.15, 1], gap="large")

    with left_col:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="surface-heading">Investigation workflow</div>', unsafe_allow_html=True)
        st.markdown('<div class="surface-caption">How TraceFlow processes a data-quality incident</div>', unsafe_allow_html=True)

        workflow = [
            ("01", "Data quality detection", "Identify invalid, missing, duplicate or inconsistent records."),
            ("02", "Incident report", "Capture the affected record, field, evidence and expected value."),
            ("03", "Rule-based investigation", "Apply deterministic logic to classify the issue and assess evidence."),
            ("04", "LLM investigation", "Ask Groq to produce possible causes and recommendations from supplied evidence."),
            ("05", "Human review", "Verify hypotheses before taking corrective action."),
        ]
        for number, title, detail in workflow:
            st.markdown(
                f'<div class="step"><div class="step-number">{number}</div>'
                f'<div><div class="step-title">{title}</div>'
                f'<div class="step-detail">{detail}</div></div></div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with right_col:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="surface-heading">Incident severity profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="surface-caption">Severity distribution in the latest investigation</div>', unsafe_allow_html=True)

        severity_data = pd.DataFrame({
            "Severity": ["HIGH", "MEDIUM", "LOW"],
            "Incidents": [high_severity, medium_severity, low_severity],
        })
        st.bar_chart(severity_data, x="Severity", y="Incidents", horizontal=True)
        st.markdown(
            f'{tag(f"{high_severity} HIGH", "red")} '
            f'{tag(f"{medium_severity} MEDIUM", "amber")} '
            f'{tag(f"{low_severity} LOW", "green")}',
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("### Incidents requiring attention")
    table_data = []
    for item in results:
        incident = item.get("original_incident", {})
        table_data.append({
            "Order ID": item.get("order_id", "Unknown"),
            "Incident category": item.get("incident_category", "Unknown"),
            "Severity": incident.get("severity", "Unknown"),
            "Rule analysis": item.get("rule_based_status", "Unknown"),
            "LLM analysis": item.get("llm_status", "Unknown"),
            "Human review": "Required" if item.get("requires_human_review", True) else "Not flagged",
        })

    if table_data:
        st.dataframe(pd.DataFrame(table_data), width="stretch", hide_index=True)
    else:
        st.info("The latest report contains no investigation results.")


# ============================================================
# WORKSPACE 2 — INCIDENT EXPLORER
# ============================================================
elif current_page == "Incident Explorer":
    page_heading(
        "WORKSPACE / INCIDENT MANAGEMENT",
        "Incident explorer",
        "Move from the incident list into the original data-quality evidence for an individual record.",
    )

    if not results:
        st.info("No incidents are available in the latest combined investigation report.")
    else:
        table_data = []
        for index, item in enumerate(results):
            incident = item.get("original_incident", {})
            table_data.append({
                "index": index,
                "Order ID": item.get("order_id", "Unknown"),
                "Category": item.get("incident_category", "Unknown"),
                "Severity": incident.get("severity", "Unknown"),
                "Rule analysis": item.get("rule_based_status", "Unknown"),
                "LLM analysis": item.get("llm_status", "Unknown"),
            })

        frame = pd.DataFrame(table_data)
        filter_col1, filter_col2 = st.columns([1, 2])
        severity_options = sorted(frame["Severity"].dropna().unique().tolist())
        category_options = sorted(frame["Category"].dropna().unique().tolist())

        with filter_col1:
            selected_severities = st.multiselect(
                "Filter by severity",
                severity_options,
                default=severity_options,
            )
        with filter_col2:
            selected_categories = st.multiselect(
                "Filter by category",
                category_options,
                default=category_options,
            )

        filtered = frame[
            frame["Severity"].isin(selected_severities)
            & frame["Category"].isin(selected_categories)
        ]
        st.caption(f"{len(filtered)} incidents shown")
        st.dataframe(
            filtered.drop(columns=["index"]),
            width="stretch",
            hide_index=True,
        )

        if not filtered.empty:
            labels = [
                f'{row["Order ID"]}  ·  {row["Category"]}  ·  {row["Severity"]}'
                for _, row in filtered.iterrows()
            ]
            selected_label = st.selectbox("Inspect incident", labels)
            selected_position = labels.index(selected_label)
            selected_index = int(filtered.iloc[selected_position]["index"])
            selected_result = results[selected_index]
            original_incident = selected_result.get("original_incident", {})

            st.write("")
            st.markdown("### Original incident evidence")
            tag(
                str(original_incident.get("severity", "UNKNOWN")).upper(),
                severity_tone(original_incident.get("severity")),
            )
            st.write(original_incident.get("message", "No incident message recorded."))

            detail1, detail2, detail3 = st.columns(3)
            detail1.markdown("**Affected field**")
            detail1.code(str(original_incident.get("affected_field", "Unknown")))
            detail2.markdown("**Actual value**")
            detail2.write(str(original_incident.get("actual_value", "Unknown")))
            detail3.markdown("**Expected value**")
            detail3.write(str(original_incident.get("expected_value", "Unknown")))

            st.markdown("**Suggested resolution**")
            st.write(original_incident.get("suggested_resolution", "No suggested resolution recorded."))

            with st.expander("View complete incident record"):
                st.json(original_incident)


# ============================================================
# WORKSPACE 3 — AI INVESTIGATION
# ============================================================
elif current_page == "AI Investigation":
    page_heading(
        "WORKSPACE / ROOT-CAUSE ANALYSIS",
        "AI investigation",
        "Compare deterministic findings with Groq-generated hypotheses while keeping the evidence and confidence visible.",
    )

    if not results:
        st.info("No investigation results are available.")
    else:
        incident_options = [
            f'{item.get("order_id", "Unknown")} · {item.get("incident_category", "Unknown")}'
            for item in results
        ]
        selected_incident = st.selectbox("Select an incident", incident_options)
        selected_index = incident_options.index(selected_incident)
        selected_result = results[selected_index]

        original_incident = selected_result.get("original_incident", {})
        rule_analysis = selected_result.get("rule_based_analysis")
        llm_analysis = selected_result.get("llm_analysis")

        st.markdown(f"### {selected_result.get('incident_category', 'Incident')} investigation")
        st.caption(f"Order ID: {selected_result.get('order_id', 'Unknown')}")
        st.write(original_incident.get("message", "No original incident message recorded."))

        status_cols = st.columns(3)
        status_cols[0].metric("Rule-based analysis", selected_result.get("rule_based_status", "Unknown"))
        status_cols[1].metric("LLM analysis", selected_result.get("llm_status", "Unknown"))
        status_cols[2].metric(
            "Human review",
            "Required" if selected_result.get("requires_human_review", True) else "Not flagged",
        )

        rule_tab, ai_tab, recommendation_tab = st.tabs([
            "Rule-based reasoning",
            "Groq AI findings",
            "Recommendations",
        ])

        with rule_tab:
            if rule_analysis:
                st.markdown('<div class="surface">', unsafe_allow_html=True)
                st.markdown('<div class="surface-heading">Deterministic investigation</div>', unsafe_allow_html=True)
                st.markdown('<div class="surface-caption">Rule-based analysis derived from incident attributes and validation evidence</div>', unsafe_allow_html=True)
                st.markdown("**Probable root cause**")
                st.write(rule_analysis.get("probable_root_cause", "Not available"))

                confidence_cols = st.columns(2)
                confidence_cols[0].metric(
                    "Detection confidence",
                    rule_analysis.get("detection_confidence", "Unknown"),
                )
                confidence_cols[1].metric(
                    "Root-cause confidence",
                    rule_analysis.get("root_cause_confidence", "Unknown"),
                )
                st.markdown("**Evidence used**")
                show_list(rule_analysis.get("evidence", []))
                if rule_analysis.get("confidence_reason"):
                    st.caption(rule_analysis.get("confidence_reason"))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("Rule-based analysis was unsuccessful or is not present in this report.")

        with ai_tab:
            if llm_analysis:
                st.markdown('<div class="surface">', unsafe_allow_html=True)
                st.markdown('<div class="surface-heading">Groq-powered investigation</div>', unsafe_allow_html=True)
                st.markdown('<div class="surface-caption">LLM output grounded in the incident details supplied to the model</div>', unsafe_allow_html=True)
                st.markdown("**Incident summary**")
                st.write(llm_analysis.get("incident_summary", "Not available"))

                evidence_col, causes_col = st.columns(2)
                with evidence_col:
                    st.markdown("**Observed evidence**")
                    show_list(llm_analysis.get("observed_evidence", []))
                with causes_col:
                    st.markdown("**Possible root causes**")
                    show_list(llm_analysis.get("possible_root_causes", []))

                st.markdown("**AI recommended actions**")
                show_list(llm_analysis.get("recommended_actions", []))
                st.metric(
                    "AI root-cause confidence",
                    llm_analysis.get("root_cause_confidence", "Unknown"),
                )
                st.caption(llm_analysis.get("confidence_reason", ""))
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning("LLM investigation was unsuccessful or is not present in this report.")

        with recommendation_tab:
            recommendations = selected_result.get("combined_recommendations", [])
            if recommendations:
                for recommendation in recommendations:
                    source = recommendation.get("source", "Unknown")
                    action = recommendation.get("action", "")
                    with st.container(border=True):
                        st.caption(str(source).replace("_", " ").upper())
                        st.write(action)
            else:
                st.info("No combined recommendations are available.")

            st.markdown(
                '<div class="callout"><strong>Human review required.</strong> '
                'AI-generated root-cause suggestions are hypotheses until independently verified.</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# WORKSPACE 4 — REPORT DETAILS
# ============================================================
elif current_page == "Report Details":
    page_heading(
        "WORKSPACE / REPORT METADATA",
        "Investigation report",
        "Trace the latest combined investigation back to its source report and generated dataset.",
    )

    meta_left, meta_right = st.columns(2)
    with meta_left:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="surface-heading">Report identity</div>', unsafe_allow_html=True)
        st.markdown('<div class="surface-caption">Identifiers recorded by the investigation engine</div>', unsafe_allow_html=True)
        st.markdown("**Investigation ID**")
        st.code(str(report.get("investigation_id", "Unknown")))
        st.markdown("**Source report ID**")
        st.code(str(report.get("source_report_id", "Unknown")))
        st.markdown("</div>", unsafe_allow_html=True)

    with meta_right:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        st.markdown('<div class="surface-heading">Dataset context</div>', unsafe_allow_html=True)
        st.markdown('<div class="surface-caption">Source information recorded in the report</div>', unsafe_allow_html=True)
        st.markdown("**Dataset**")
        st.write(report.get("dataset", "Unknown"))
        st.markdown("**Generated at**")
        st.write(report.get("generated_at", "Unknown"))
        st.markdown("**Total incidents**")
        st.write(total_incidents)
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("### Full combined investigation output")
    with st.expander("Open report JSON"):
        st.json(report)

    st.caption(f"Loaded from: {REPORTS_DIR}")


# ------------------------- Footer -------------------------
st.markdown(
    """
    <div style="text-align:center;color:#9aa6b5;font-size:.7rem;padding:2.4rem 0 .4rem">
        TRACEFLOW AI &nbsp;·&nbsp; INTELLIGENT DATA PIPELINE INVESTIGATOR
    </div>
    """,
    unsafe_allow_html=True,
)
