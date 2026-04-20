import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from servicenow_pipeline import process_dataframe  # your pipeline

st.set_page_config(layout="wide")
st.title("📊 ServiceNow Ticket Analyzer")

# --- Upload ---
uploaded_file = st.file_uploader("Upload ServiceNow Export", type=["csv", "xlsx"])

if uploaded_file:

    st.success("File uploaded successfully")

    if st.button("Process Data"):
        with st.spinner("Processing..."):

            # Save temp file
            temp_path = "temp_upload.xlsx"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())

            # Run pipeline
            df = process_dataframe(temp_path)

        st.success("Processing complete!")

        # --- Metrics ---
        st.subheader("📌 Overview")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Tickets", len(df))
        col2.metric("Avg Age (days)", round(df["case_age_days"].mean(), 1))
        col3.metric("Open Tickets", df["is_open_case"].sum())

        # --- Category Chart ---
        st.subheader("📊 Tickets by Category")

        category_counts = df["request_category"].value_counts()

        fig, ax = plt.subplots()
        category_counts.plot(kind="bar", ax=ax)
        st.pyplot(fig)

        # --- State Chart ---
        st.subheader("📊 Tickets by State")

        state_counts = df["state_normalized"].value_counts()

        fig2, ax2 = plt.subplots()
        state_counts.plot(kind="bar", ax=ax2)
        st.pyplot(fig2)

        # --- Time Trend ---
        st.subheader("📈 Tickets Over Time")

        df["created_ts"] = pd.to_datetime(df["created_ts"])
        trend = df.groupby(df["created_ts"].dt.date).size()

        fig3, ax3 = plt.subplots()
        trend.plot(ax=ax3)
        st.pyplot(fig3)

        # --- Table ---
        st.subheader("📋 Ticket Data")

        st.dataframe(df)