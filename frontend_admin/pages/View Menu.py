import streamlit as st


# 1. Custom CSS to reduce the top padding
st.markdown("""
    <style>
           .block-container {
                padding-top: 2rem;
                padding-bottom: 0rem;
            }
    </style>
    """, unsafe_allow_html=True)

# 2. Use columns to center the text
# Adjust the ratio [1, 2, 1] to change how 'centered' it looks
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.title("Today's Menu")
