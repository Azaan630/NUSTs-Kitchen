import streamlit as st
import httpx
import os
import pandas as pd

st.set_page_config(page_title="RotiRouter Admin")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("Admin Dashboard Test")

if st.button("Sync Data from Backend"):
    try:
        response = httpx.get(f"{BACKEND_URL}/users")
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            st.success(f"Successfully fetched {len(df)} users.")

            # Show raw data table
            st.subheader("Raw User Data")
            st.write(df)

            # Simple chart test
            st.subheader("Account Type Distribution")
            st.bar_chart(df['Account_Type'].value_counts())
        else:
            st.error(f"Backend returned error: {response.status_code}")
    except Exception as e:
        st.error(f"Could not connect to backend: {e}")