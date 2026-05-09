import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import httpx
from datetime import date

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ADMIN_EMAIL = "admin@nust.edu.pk"

st.set_page_config(page_title="Finance Center", page_icon="💰", layout="wide")

st.title("💰 Revenue & Financial Analytics")
st.markdown("Monitor collections, outstanding balances, and monthly revenue trends.")

def get_data(endpoint):
    try:
        res = httpx.get(f"{BACKEND_URL}{endpoint}", params={"email": ADMIN_EMAIL})
        return res.json() if res.status_code == 200 else None
    except: return None

billing_summary = get_data("/admin/monthly_billing_summary")

if billing_summary:
    df = pd.DataFrame(billing_summary)
    
    # Financial KPIs
    total_rev = df['Total_Amount'].sum()
    total_col = df['Total_Collected'].sum()
    total_out = df['Outstanding'].sum()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Revenue", f"Rs. {total_rev:,.0f}")
    c2.metric("Total Collected", f"Rs. {total_col:,.0f}", delta=f"{(total_col/total_rev)*100:.1f}% Rate")
    c3.metric("Total Outstanding", f"Rs. {total_out:,.0f}", delta=f"-{total_out/total_rev*100:.1f}% Unpaid", delta_color="inverse")
    c4.metric("Active Monthly Bills", df['Total_Bills'].sum())

    st.markdown("---")
    
    # Revenue Trend
    st.subheader("📈 Monthly Revenue vs Collection")
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=df['Billing_Month'], y=df['Total_Amount'], name='Projected Revenue', line=dict(color='#3b82f6', width=4)))
    fig_trend.add_trace(go.Bar(x=df['Billing_Month'], y=df['Total_Collected'], name='Actual Collection', marker_color='#10b981'))
    fig_trend.update_layout(xaxis_title="Month", yaxis_title="Amount (Rs.)")
    st.plotly_chart(fig_trend, use_container_width=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Outstanding by Month")
        fig_out = px.bar(df, x="Billing_Month", y="Outstanding", color="Outstanding",
                         color_continuous_scale="Reds", text_auto='.2s')
        st.plotly_chart(fig_out, use_container_width=True)
        
    with col2:
        st.subheader("📊 Collection Distribution")
        df_pie = pd.melt(df, id_vars=['Billing_Month'], value_vars=['Total_Collected', 'Outstanding'])
        fig_pie = px.pie(df_pie, values="value", names="variable", 
                         color="variable", color_discrete_map={'Total_Collected':'#10b981', 'Outstanding':'#ef4444'},
                         hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📑 Detailed Monthly Summary")
    st.dataframe(df.style.background_gradient(subset=['Outstanding'], cmap='Reds'), use_container_width=True)

else:
    st.error("Financial data unavailable. Please ensure the backend is running and migrations are applied.")
    st.info("💡 **Admin Tip:** Use the 'Generate Bills' procedure in the backend to populate this data for new months.")
