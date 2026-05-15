import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="NUST's Kitchen - Admin")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("Welcome to NUST's Kitchen Admin")
st.write("Manage mess operations, view analytics, and handle user requests.")


