import streamlit as st
import os
import pandas as pd

st.set_page_config(page_title="Digi Mess")

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")

st.title("Welcome Admin")


