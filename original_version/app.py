import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import tempfile

from servicenow_pipeline import read_servicenow_file, process_dataframe

st.set_page_config(
    page_title="ServiceNow Leadership Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 2rem;
    padding-right: 2rem;
}
.main-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.25rem;
}
.sub-title {
    color: #6b7280;
    font-size: 1rem;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: #f8fafc;
    padding: 1rem 1.25rem;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.section-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-top: 1.5rem;
    margin-bottom: 0.75rem;
}
.summary-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 16px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">ServiceNow Leadership Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title">Operational visibility for HR service requests: backlog, service areas, aging risk, and cases needing attention.</div>',
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("Upload ServiceNow export", type=["csv", "xlsx", "xls"])

def build_executive_summary(df: pd.DataFrame) -> str:
    total = len(df)
    open_cases = int(df["is_open_case"].sum()) if "is_open_case" in df.columns else total

    state_counts = df["state_normalized"].fillna("Unknown").value_counts()
    category_counts = df["request_category"].fillna("Other").value_counts()

    top_state = state_counts.index[0] if not state_counts.empty else "Unknown"
    top_state_n = int(state_counts.iloc[0]) if not state_counts.empty else 0

    top_category = category_counts.index[0] if not category_counts.empty else "Other"
    top_category_n = int(category_counts.iloc[0]) if not category_counts.empty else 0

    aging_7 = int(df["is_aging_7d"].sum()) if "is_aging_7d" in df.columns else 0

    return (
        f"There are {open_cases} open cases in the current dataset. "
        f"The largest workflow state is {top_state} ({top_state_n} cases), "
        f"and the largest service area is {top_category} ({top_category_n} cases). "
        f"{aging_7} cases are older than 7 days, which suggests a backlog that may require review."
    )

def make_aging_bucket(age):
    if pd.isna(age):
        return "Unknown"
    if age <= 7:
        return "0-7 days"
    if age <= 14:
        return "8-14 days"
    if age <= 30:
        return "15-30 days"
    return "30+ days"

if uploaded_file is not None:
    if st.button("Process Data", type="primary"):
        with st.spinner("Processing data..."):
            suffix = Path(uploaded_file.name).suffix
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getbuffer())
                temp_path = Path(tmp.name)

            raw_df = read_servicenow_file(temp_path)
            result = process_dataframe(raw_df)
            df = result.enriched.copy()
            summary = result.summary

        st.success("Processing complete")

        if "case_age_days" in df.columns:
            df["aging_bucket"] = df["case_age_days"].apply(make_aging_bucket)

        # Sidebar filters
        st.sidebar.header("Filters")

        state_options = ["All"] + sorted(df["state_normalized"].fillna("Unknown").unique().tolist())
        category_options = ["All"] + sorted(df["request_category"].fillna("Other").unique().tolist())
        priority_options = ["All"] + sorted(df["priority_normalized"].fillna("Unknown").unique().tolist())

        selected_state = st.sidebar.selectbox("Workflow status", state_options)
        selected_category = st.sidebar.selectbox("Service area", category_options)
        selected_priority = st.sidebar.selectbox("Priority", priority_options)
        aging_only = st.sidebar.checkbox("Only show cases older than 7 days", value=False)

        filtered = df.copy()

        if selected_state != "All":
            filtered = filtered[filtered["state_normalized"].fillna("Unknown") == selected_state]
        if selected_category != "All":
            filtered = filtered[filtered["request_category"].fillna("Other") == selected_category]
        if selected_priority != "All":
            filtered = filtered[filtered["priority_normalized"].fillna("Unknown") == selected_priority]
        if aging_only:
            filtered = filtered[filtered["is_aging_7d"] == True]

        # Executive summary
        st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{build_executive_summary(filtered)}</div>', unsafe_allow_html=True)

        # KPI row
        open_cases = int(filtered["is_open_case"].sum()) if "is_open_case" in filtered.columns else len(filtered)
        aging_7 = int(filtered["is_aging_7d"].sum()) if "is_aging_7d" in filtered.columns else 0
        avg_age = round(float(filtered["case_age_days"].mean()), 1) if filtered["case_age_days"].notna().any() else 0.0

        top_category = (
            filtered["request_category"].value_counts().index[0]
            if not filtered["request_category"].value_counts().empty else "N/A"
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Open Cases", open_cases)
        c2.metric("Older than 7 Days", aging_7)
        c3.metric("Average Age", f"{avg_age} days")
        c4.metric("Largest Service Area", top_category)

        # Leadership insights
        st.markdown('<div class="section-title">Leadership Insights</div>', unsafe_allow_html=True)
        left, right = st.columns(2)

        with left:
            st.markdown("**Current Workflow Status**")
            state_counts = filtered["state_normalized"].fillna("Unknown").value_counts().sort_values()
            fig, ax = plt.subplots(figsize=(7, 4))
            state_counts.plot(kind="barh", ax=ax)
            ax.set_xlabel("Cases")
            ax.set_ylabel("")
            ax.set_title("")
            st.pyplot(fig)

        with right:
            st.markdown("**Requests by Service Area**")
            category_counts = filtered["request_category"].fillna("Other").value_counts().sort_values()
            fig, ax = plt.subplots(figsize=(7, 4))
            category_counts.plot(kind="barh", ax=ax)
            ax.set_xlabel("Cases")
            ax.set_ylabel("")
            ax.set_title("")
            st.pyplot(fig)

        left2, right2 = st.columns(2)

        with left2:
            st.markdown("**Aging Distribution**")
            aging_counts = filtered["aging_bucket"].value_counts().reindex(
                ["0-7 days", "8-14 days", "15-30 days", "30+ days", "Unknown"],
                fill_value=0
            )
            fig, ax = plt.subplots(figsize=(7, 4))
            aging_counts.plot(kind="bar", ax=ax)
            ax.set_xlabel("")
            ax.set_ylabel("Cases")
            ax.tick_params(axis="x", rotation=0)
            st.pyplot(fig)

        with right2:
            st.markdown("**Weekly Intake Trend**")
            weekly = (
                filtered.dropna(subset=["created_ts"])
                .assign(created_ts=pd.to_datetime(filtered["created_ts"], errors="coerce"))
                .dropna(subset=["created_ts"])
                .set_index("created_ts")
                .resample("W")
                .size()
            )
            fig, ax = plt.subplots(figsize=(7, 4))
            weekly.plot(kind="bar", ax=ax)
            ax.set_xlabel("")
            ax.set_ylabel("Cases")
            st.pyplot(fig)

        # Attention needed
        st.markdown('<div class="section-title">Cases Needing Attention</div>', unsafe_allow_html=True)

        attention = filtered[
            (filtered["is_open_case"] == True) &
            (
                (filtered["is_aging_7d"] == True) |
                (filtered["operational_signal"].isin(["Frustrated / Follow-up", "Blocked / Waiting"]))
            )
        ].copy()

        attention_cols = [
            "case_number",
            "short_description_clean",
            "state_normalized",
            "priority_normalized",
            "request_category",
            "operational_signal",
            "recommended_action",
            "case_age_days",
        ]
        attention_cols = [c for c in attention_cols if c in attention.columns]

        st.dataframe(
            attention[attention_cols].sort_values(by="case_age_days", ascending=False),
            use_container_width=True,
            height=300
        )

        # Full explorer
        st.markdown('<div class="section-title">Case Explorer</div>', unsafe_allow_html=True)

        explorer_cols = [
            "case_number",
            "short_description_clean",
            "state_normalized",
            "priority_normalized",
            "request_category",
            "operational_signal",
            "recommended_action",
            "case_age_days",
            "created_ts",
        ]
        explorer_cols = [c for c in explorer_cols if c in filtered.columns]

        st.dataframe(filtered[explorer_cols], use_container_width=True, height=420)

        csv_data = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download filtered enriched CSV",
            data=csv_data,
            file_name="servicenow_enriched_filtered.csv",
            mime="text/csv",
        )