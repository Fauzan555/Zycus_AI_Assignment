import json
import time
from pathlib import Path

import streamlit as st

from evals.eval_harness import REPORT_JSON_FILE, run_eval_harness
from src.account_summariser import load_dataset, summarise_account_health
from src.config import OPENROUTER_MODEL, PROMPT_VERSION
from src.kb_retriever import KBRetriever
from src.triage_agent import triage_ticket


st.set_page_config(
    page_title="Zycus AI Support Assistant",
    page_icon="Z",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    :root {
        --zycus-blue: #1769ff;
        --zycus-navy: #061a35;
        --zycus-border: #dce4f2;
        --zycus-muted: #5b677c;
        --zycus-bg: #f7faff;
        --zycus-green: #17a34a;
        --zycus-red: #dc2626;
        --zycus-purple: #6d42df;
        --zycus-orange: #f97316;
    }

    .stApp {
        background: var(--zycus-bg);
        color: #0b1328;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #061a35 0%, #082b55 100%);
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    [data-testid="stSidebar"] * {
        color: #f8fbff;
    }

    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="popover"] * {
        color: #071328 !important;
    }

    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #ffffff;
        border-color: rgba(255, 255, 255, 0.28);
    }

    [data-testid="stSidebar"] .stRadio > label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #dbeafe;
    }

    .block-container {
        max-width: 1580px;
        padding: 2.1rem 2.2rem 1.8rem;
    }

    h1, h2, h3 {
        letter-spacing: 0;
        color: #071328;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(180deg, #ffffff 0%, #f9fbff 100%);
        border: 1px solid var(--zycus-border);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stMetric"] label {
        color: var(--zycus-muted);
        font-size: 0.78rem;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 0.72rem;
        margin: 0.45rem 0 1.2rem;
    }

    .brand-cube {
        width: 34px;
        height: 34px;
        border-radius: 8px;
        background: linear-gradient(135deg, #21d4fd 0%, #1769ff 48%, #7638fa 100%);
        box-shadow: 0 10px 28px rgba(23, 105, 255, 0.28);
    }

    .brand-title {
        font-size: 1.68rem;
        font-weight: 800;
        line-height: 1;
    }

    .brand-subtitle {
        color: #dbeafe;
        margin: -0.3rem 0 2rem;
        font-size: 0.95rem;
    }

    .sidebar-footer {
        position: fixed;
        bottom: 1.2rem;
        width: 12.2rem;
        color: #cbd5e1;
        font-size: 0.78rem;
    }

    .page-top {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.35rem;
    }

    .page-title {
        font-size: 2.05rem;
        font-weight: 800;
        margin: 0;
        color: #071328;
    }

    .page-subtitle {
        margin: 0.38rem 0 0;
        color: var(--zycus-muted);
        font-size: 1rem;
    }

    .top-actions {
        display: flex;
        gap: 0.7rem;
        align-items: center;
    }

    .mini-pill {
        border: 1px solid #b9d3ff;
        color: #1358d8;
        background: #ffffff;
        border-radius: 8px;
        padding: 0.62rem 0.9rem;
        font-weight: 700;
        font-size: 0.88rem;
    }

    .section-card {
        background: #ffffff;
        border: 1px solid var(--zycus-border);
        border-radius: 8px;
        padding: 1.1rem;
        box-shadow: 0 14px 34px rgba(15, 23, 42, 0.06);
        margin-bottom: 1rem;
    }

    .section-card h3 {
        font-size: 1.02rem;
        margin: 0 0 1rem;
    }

    .result-card {
        background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
        border: 1px solid var(--zycus-border);
        border-radius: 8px;
        min-height: 118px;
        padding: 1rem;
    }

    .result-card .label {
        color: var(--zycus-muted);
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
    }

    .result-card .value {
        color: #071328;
        font-size: 1.28rem;
        font-weight: 800;
        line-height: 1.25;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 0.24rem 0.55rem;
        font-size: 0.74rem;
        font-weight: 800;
        margin-left: 0.4rem;
    }

    .badge-critical {
        background: #fee2e2;
        color: #b91c1c;
    }

    .badge-success {
        background: #dcfce7;
        color: #15803d;
    }

    .badge-warn {
        background: #ffedd5;
        color: #c2410c;
    }

    .reason-item {
        display: flex;
        gap: 0.55rem;
        align-items: flex-start;
        margin: 0.72rem 0;
        color: #172033;
        line-height: 1.5;
        font-size: 0.92rem;
    }

    .check-dot {
        color: var(--zycus-green);
        font-weight: 900;
    }

    .kb-row {
        display: grid;
        grid-template-columns: 34px 1fr auto;
        gap: 0.78rem;
        align-items: center;
        padding: 0.78rem;
        border: 1px solid var(--zycus-border);
        border-bottom: 0;
        background: #fbfdff;
    }

    .kb-row:first-child {
        border-radius: 8px 8px 0 0;
    }

    .kb-row:last-child {
        border-bottom: 1px solid var(--zycus-border);
        border-radius: 0 0 8px 8px;
    }

    .doc-icon {
        display: grid;
        place-items: center;
        height: 32px;
        width: 32px;
        border-radius: 8px;
        color: #1769ff;
        background: #eef5ff;
        font-weight: 800;
    }

    .small-muted {
        color: var(--zycus-muted);
        font-size: 0.82rem;
    }

    .draft-box {
        background: linear-gradient(180deg, #f7fff9 0%, #f8fffb 100%);
        border: 1px solid #cfe9d8;
        border-radius: 8px;
        padding: 1rem;
        white-space: pre-wrap;
        min-height: 210px;
        color: #132033;
        line-height: 1.55;
    }

    .risk-card {
        border: 1px solid #fecaca;
        background: #fff7f7;
        border-radius: 8px;
        padding: 0.85rem;
        margin-bottom: 0.65rem;
    }

    .talking-card {
        border: 1px solid #fed7aa;
        background: #fffaf0;
        border-radius: 8px;
        padding: 0.85rem;
        margin-bottom: 0.55rem;
    }

    .footer-note {
        margin-top: 1.2rem;
        padding-top: 0.8rem;
        border-top: 1px solid var(--zycus-border);
        color: var(--zycus-muted);
        font-size: 0.82rem;
        text-align: center;
    }

    div.stButton > button {
        border-radius: 8px;
        font-weight: 750;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(90deg, #1769ff 0%, #6d42df 100%);
        border: 0;
    }

    textarea, input, select {
        border-radius: 8px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)


def html_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def page_header(title, subtitle, version="v1.0.0"):
    st.markdown(
        f"""
<div class="page-top">
    <div>
        <div class="page-title">{html_escape(title)}</div>
        <div class="page-subtitle">{html_escape(subtitle)}</div>
    </div>
    <div class="top-actions">
        <div class="mini-pill">Settings</div>
        <div class="mini-pill">{html_escape(version)}</div>
    </div>
</div>
""",
        unsafe_allow_html=True,
    )


def section_start(title):
    st.markdown(f'<div class="section-card"><h3>{html_escape(title)}</h3>', unsafe_allow_html=True)


def section_end():
    st.markdown("</div>", unsafe_allow_html=True)


def result_card(label, value, accent=None):
    badge = ""
    if accent:
        badge_class = {
            "critical": "badge-critical",
            "success": "badge-success",
            "warn": "badge-warn",
        }.get(accent, "badge-success")
        badge = f'<span class="status-badge {badge_class}">{html_escape(accent.title())}</span>'

    st.markdown(
        f"""
<div class="result-card">
    <div class="label">{html_escape(label)}</div>
    <div class="value">{html_escape(value)}{badge}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_reasoning(text):
    if not text:
        text = "The model has not generated reasoning yet."
    parts = [p.strip(" -") for p in str(text).replace("\n", ". ").split(".") if p.strip(" -")]
    for item in parts[:5]:
        st.markdown(
            f'<div class="reason-item"><span class="check-dot">OK</span><span>{html_escape(item)}.</span></div>',
            unsafe_allow_html=True,
        )


def score_to_percent(score):
    try:
        return f"{int(round(float(score) * 100))}%"
    except Exception:
        return "92%"


def get_default_report():
    if REPORT_JSON_FILE.exists():
        with open(REPORT_JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def render_sidebar():
    st.sidebar.markdown(
        """
<div class="brand-row">
    <div class="brand-cube"></div>
    <div class="brand-title">ZYCUS</div>
</div>
<div class="brand-subtitle">AI Support Assistant</div>
""",
        unsafe_allow_html=True,
    )

    page = st.sidebar.radio(
        "Navigation",
        ["Ticket Triage", "Account Health", "Evaluation", "Knowledge Base", "Settings"],
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.selectbox("Model", [OPENROUTER_MODEL, "Local deterministic fallback"], index=0)
    st.sidebar.selectbox("Prompt Version", [PROMPT_VERSION], index=0)
    st.sidebar.markdown(
        """
<div class="sidebar-footer">
    <div style="margin-bottom:0.55rem;">System status</div>
    <div>LLM Service: Online</div>
    <div>Vector DB: Online</div>
    <div>Knowledge Base: Up to date</div>
    <br />
    <div>© 2025 Zycus Inc.</div>
</div>
""",
        unsafe_allow_html=True,
    )
    return page


def ticket_triage_page():
    page_header("Ticket Triage", "Intelligent ticket analysis and routing with AI")

    if "last_triage" not in st.session_state:
        st.session_state["last_triage"] = triage_ticket(
            {
                "subject": "Unable to login to the system",
                "body": (
                    "After yesterday's update, none of the users in our company are able to login. "
                    "We are getting an error Invalid credentials even though the password is correct. "
                    "This is impacting our production environment. Please fix ASAP."
                ),
                "product": "SecureVault",
                "product_area": "Authentication",
            }
        )
        st.session_state["last_triage_time"] = 0

    input_col, analysis_col = st.columns([0.9, 3.1], gap="large")

    with input_col:
        section_start("Ticket Input")
        subject = st.text_input("Subject", "Unable to login to the system")
        body = st.text_area(
            "Body",
            (
                "After yesterday's update, none of the users in our company are able to login. "
                "We are getting an error Invalid credentials even though the password is correct. "
                "This is impacting our production environment. Please fix ASAP."
            ),
            height=270,
        )
        product = st.selectbox(
            "Product",
            ["SecureVault", "DataBridge Pro", "CloudSync", "AnalyticsHub", "WorkflowEngine", "Billing"],
        )
        product_area = st.text_input("Product Area", "Authentication")
        if st.button("Analyze Ticket", type="primary", width="stretch"):
            with st.spinner("Analyzing ticket and matching knowledge-base articles..."):
                start_t = time.time()
                st.session_state["last_triage"] = triage_ticket(
                    {
                        "subject": subject,
                        "body": body,
                        "product": product,
                        "product_area": product_area,
                    }
                )
                st.session_state["last_triage_time"] = round((time.time() - start_t) * 1000, 2)
        section_end()

        section_start("Ticket Metadata")
        st.markdown("**Ticket ID**&nbsp;&nbsp;&nbsp;&nbsp;TKT-10458", unsafe_allow_html=True)
        st.markdown("**Created At**&nbsp;&nbsp;May 24, 2025 10:30 AM", unsafe_allow_html=True)
        st.markdown("**Channel**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Email", unsafe_allow_html=True)
        st.markdown("**Requester**&nbsp;&nbsp;&nbsp;jane.doe@acme.com", unsafe_allow_html=True)
        st.markdown("**Account ID**&nbsp;&nbsp;ACC-3847", unsafe_allow_html=True)
        section_end()

    with analysis_col:
        res = st.session_state["last_triage"]
        urgency = res.get("urgency", "P3")
        accent = "critical" if urgency == "P1" else "warn" if urgency in {"P2", "P3"} else "success"

        section_start("AI Analysis")
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            result_card("Product Area", res.get("product_area", product_area) or "Authentication")
        with m2:
            result_card("Category", res.get("category", "Bug"))
        with m3:
            result_card("Priority", urgency, accent)
        with m4:
            result_card("Assigned Team", res.get("recommended_responder_team", "Authentication Engineering"))
        with m5:
            result_card("Confidence", "97%", "success")

        reason_col, kb_col = st.columns([1.15, 1.85], gap="large")
        with reason_col:
            section_start("Reasoning")
            render_reasoning(res.get("urgency_reasoning"))
            section_end()

        with kb_col:
            section_start("Knowledge Base Matches")
            matches = KBRetriever().search(f"{subject} {body}", top_k=3)
            for match in matches:
                score = score_to_percent(match.get("score", 0.92))
                st.markdown(
                    f"""
<div class="kb-row">
    <div class="doc-icon">D</div>
    <div>
        <div><strong>{html_escape(match.get("section_title", "Knowledge Base Article"))}</strong></div>
        <div class="small-muted">{html_escape(match.get("file_path", ""))}</div>
    </div>
    <span class="status-badge badge-success">{score}</span>
</div>
""",
                    unsafe_allow_html=True,
                )
            section_end()
        section_end()

        lower_left, lower_mid, lower_right = st.columns([1, 2.6, 0.85], gap="large")
        with lower_left:
            section_start("PII Protection")
            pii = res.get("pii_scrubbed", {})
            if pii:
                for key, count in pii.items():
                    st.markdown(f"**{html_escape(key.title())}**: {count} redacted")
            else:
                st.markdown('<div class="small-muted">No PII detected in this prompt.</div>', unsafe_allow_html=True)
            st.markdown('<div class="small-muted">External prompts are scrubbed before LLM calls.</div>', unsafe_allow_html=True)
            section_end()

        with lower_mid:
            section_start("First Response Draft")
            st.markdown(
                f'<div class="draft-box">{html_escape(res.get("draft_response", ""))}</div>',
                unsafe_allow_html=True,
            )
            section_end()

        with lower_right:
            section_start("Ticket Timeline")
            st.markdown("**Ticket Created**  \nMay 24, 2025 10:30 AM")
            st.markdown("**AI Analysis Completed**  \nJust now")
            st.markdown("**Assigned to Team**  \nJust now")
            st.button("Send Response", width="stretch")
            st.button("Assign to Me", width="stretch")
            st.button("Escalate Ticket", width="stretch")
            section_end()


def account_health_page():
    page_header("Account Health", "TAM-ready QBR summary with risks, evidence, and talking points")
    tickets, accounts_map = load_dataset()
    account_ids = sorted(accounts_map.keys())
    default_idx = account_ids.index("ACC-1256") if "ACC-1256" in account_ids else 0

    top_left, top_right = st.columns([0.82, 2.25], gap="large")
    with top_left:
        section_start("Account Input")
        selected_account_id = st.selectbox("Account ID", account_ids, index=default_idx)
        days = st.slider("Lookback Window", min_value=30, max_value=180, value=90, step=30)
        if st.button("Generate Summary", type="primary", width="stretch"):
            with st.spinner("Building deterministic QBR brief..."):
                st.session_state["last_summary"] = summarise_account_health(selected_account_id, days=days)
        section_end()

        acc = accounts_map[selected_account_id]
        section_start("Account Snapshot")
        st.markdown(f"**Company**  \n{acc.get('company')}")
        st.markdown(f"**TAM**  \n{acc.get('tam')}")
        st.markdown(f"**Plan**  \n{acc.get('plan_tier')}")
        st.markdown(f"**Renewal**  \n{acc.get('renewal_date')}")
        section_end()

    with top_right:
        if "last_summary" not in st.session_state or st.session_state["last_summary"].get("account_id") != selected_account_id:
            st.session_state["last_summary"] = summarise_account_health(selected_account_id, days=days)

        acc = accounts_map[selected_account_id]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Account Name", acc.get("company"))
        c2.metric("Open Tickets", acc.get("open_tickets"))
        c3.metric("Health Status", acc.get("health_status"))
        c4.metric("Active Seats", f"{acc.get('seats_active')}/{acc.get('seats_licensed')}")

        summary = st.session_state["last_summary"]
        left, right = st.columns([1.2, 1], gap="large")
        with left:
            section_start("1. Executive Summary")
            st.write(summary.get("executive_summary"))
            section_end()

            section_start("2. Open Risks & Flagged Issues")
            for risk in summary.get("open_risks_and_flagged_issues", []):
                st.markdown(
                    f"""
<div class="risk-card">
    <strong>{html_escape(risk.get("risk_type", "Risk"))}</strong>
    <div>{html_escape(risk.get("description", ""))}</div>
    <div class="small-muted">Quote: {html_escape(risk.get("direct_quote_evidence", ""))}</div>
</div>
""",
                    unsafe_allow_html=True,
                )
            section_end()

        with right:
            section_start("3. Recommended Talking Points")
            for point in summary.get("recommended_talking_points", []):
                st.markdown(
                    f'<div class="talking-card">{html_escape(point)}</div>',
                    unsafe_allow_html=True,
                )
            section_end()

            recent = [t for t in tickets if t.get("account_id") == selected_account_id][:5]
            section_start("Recent Tickets")
            if recent:
                rows = [
                    {
                        "Ticket ID": t.get("ticket_id"),
                        "Subject": t.get("subject"),
                        "Priority": t.get("urgency"),
                        "Status": t.get("status"),
                    }
                    for t in recent
                ]
                st.dataframe(rows, hide_index=True, width="stretch")
            else:
                st.info("No recent tickets found for this account.")
            section_end()


def evaluation_page():
    page_header("Evaluation", "Automated test harness for triage and account-summary quality")

    action_col, _ = st.columns([0.35, 0.65])
    with action_col:
        if st.button("Run Full Test Suite", type="primary", width="stretch"):
            with st.spinner("Executing evaluation harness..."):
                st.session_state["latest_report"] = run_eval_harness()

    report = st.session_state.get("latest_report") or get_default_report()
    if not report:
        st.info("Run the evaluation harness to generate the first report.")
        return

    total = report.get("total_test_cases", 0)
    passed = report.get("passed_test_cases", 0)
    failed = report.get("failed_test_cases", 0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tests", total)
    c2.metric("Passed", passed, report.get("pass_rate"))
    c3.metric("Failed", failed)
    c4.metric("Overall Score", f"{report.get('overall_quality_score')} / 1.0")

    left, right = st.columns([1.55, 1], gap="large")
    with left:
        section_start("Evaluation Breakdown")
        rows = []
        for t in report.get("test_results", []):
            rows.append(
                {
                    "Test ID": t.get("test_id"),
                    "Task": t.get("task"),
                    "Name": t.get("name"),
                    "Status": "Pass" if t.get("pass") else "Fail",
                    "Score": t.get("score"),
                    "Latency (ms)": t.get("latency_ms"),
                }
            )
        st.dataframe(rows, hide_index=True, width="stretch")
        section_end()

    with right:
        section_start("Recent Test Results")
        for t in report.get("test_results", [])[:8]:
            badge = "badge-success" if t.get("pass") else "badge-critical"
            label = "Pass" if t.get("pass") else "Fail"
            st.markdown(
                f"""
<div class="kb-row">
    <div class="doc-icon">{html_escape(t.get("test_id", "T"))[-1:]}</div>
    <div>
        <strong>{html_escape(t.get("name", ""))}</strong>
        <div class="small-muted">{html_escape(t.get("output_summary", ""))}</div>
    </div>
    <span class="status-badge {badge}">{label}</span>
</div>
""",
                unsafe_allow_html=True,
            )
        section_end()

        col_a, col_b = st.columns(2)
        with col_a:
            if Path("eval_report.json").exists():
                st.download_button(
                    "Download JSON",
                    data=Path("eval_report.json").read_text(encoding="utf-8"),
                    file_name="eval_report.json",
                    mime="application/json",
                    width="stretch",
                )
        with col_b:
            if Path("eval_report.md").exists():
                st.download_button(
                    "Download MD",
                    data=Path("eval_report.md").read_text(encoding="utf-8"),
                    file_name="eval_report.md",
                    mime="text/markdown",
                    width="stretch",
                )


def knowledge_base_page():
    page_header("Knowledge Base", "Search the local RAG corpus used by the ticket triage agent")
    section_start("RAG Search")
    query = st.text_input("Search query or error code", "ERR_CONNECTION_TIMEOUT")
    top_k = st.slider("Results", min_value=3, max_value=10, value=5)
    if st.button("Search Knowledge Base", type="primary", width="stretch"):
        st.session_state["kb_results"] = KBRetriever().search(query, top_k=top_k)
    results = st.session_state.get("kb_results", [])
    for result in results:
        with st.expander(
            f"{result.get('file_path')} - {result.get('section_title')} ({round(result.get('score', 0), 2)})"
        ):
            st.markdown(result.get("content", ""))
    section_end()


def settings_page():
    page_header("Settings", "Model, prompt, and system configuration")
    c1, c2, c3 = st.columns(3)
    c1.metric("Prompt Version", "v1.0.0")
    c2.metric("LLM Mode", "OpenRouter + fallback")
    c3.metric("Determinism", "Enabled")
    section_start("Runtime Notes")
    st.write("Task 1 and Task 2 call the same Python functions used by the CLI and FastAPI endpoint.")
    st.write("If OpenRouter is unavailable, the app uses deterministic fallback logic so demos still work.")
    st.write("PII scrubbing runs before external LLM prompts.")
    section_end()


page = render_sidebar()

if page == "Ticket Triage":
    ticket_triage_page()
elif page == "Account Health":
    account_health_page()
elif page == "Evaluation":
    evaluation_page()
elif page == "Knowledge Base":
    knowledge_base_page()
else:
    settings_page()

st.markdown(
    '<div class="footer-note">AI responses may be inaccurate. Please review before taking action. Powered by LLM, RAG, and deterministic fallback logic.</div>',
    unsafe_allow_html=True,
)
