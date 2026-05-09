import streamlit as st
import pandas as pd
import plotly.express as px
import os
import httpx
from datetime import date

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ADMIN_EMAIL = "admin@nust.edu.pk"

st.set_page_config(page_title="Kitchen & Menu", page_icon="🍽️", layout="wide")

st.title("🍽️ Kitchen Operations & Menu Insights")
st.markdown("Analyze food popularity, weekly schedules, and dish ratings.")

def get_data(endpoint):
    try:
        res = httpx.get(f"{BACKEND_URL}{endpoint}", params={"email": ADMIN_EMAIL})
        return res.json() if res.status_code == 200 else None
    except: return None

# Fetch Data
weekly_menu = get_data("/menu/weekly")
poll_results = get_data("/admin/poll/results")
food_costs = get_data("/admin/food/costs")

tab1, tab2, tab3 = st.tabs(["📅 Weekly Schedule", "🔥 Voting & Polls", "📈 Food Performance"])

with tab1:
    st.subheader("Current Weekly Menu")
    if weekly_menu:
        df_menu = pd.DataFrame(weekly_menu)
        if not df_menu.empty:
            # Pivoting for a cleaner view
            df_pivot = df_menu.pivot_table(index="Date", columns="meal_type", values="Food_Item_Name", aggfunc=lambda x: ", ".join(x))
            st.dataframe(df_pivot, use_container_width=True)
        else:
            st.info("Menu schedule is empty for the current period.")
    else:
        st.error("Could not load weekly menu.")

with tab2:
    st.subheader("Real-time Poll Analysis")
    if poll_results and "results" in poll_results:
        df_poll = pd.DataFrame(poll_results["results"])
        if not df_poll.empty:
            col_a, col_b = st.columns([2, 1])
            with col_a:
                fig_poll = px.bar(df_poll, x="Name", y="Vote_Count", color="Vote_Count",
                                 title="Total Votes by Item", color_continuous_scale="Plotly3")
                st.plotly_chart(fig_poll, use_container_width=True)
            with col_b:
                st.write("#### 🏆 Current Winner")
                winner = df_poll.iloc[0]
                st.success(f"**{winner['Name']}** with {winner['Vote_Count']} votes!")
                st.metric("Lead Margin", int(winner['Vote_Count'] - (df_poll.iloc[1]['Vote_Count'] if len(df_poll)>1 else 0)))
        else:
            st.info("No active polls or voting data found.")
    else:
        st.info("Poll results will appear here once a poll is started and votes are cast.")

with tab3:
    st.subheader("Food Cost vs Popularity")
    if food_costs:
        df_costs = pd.DataFrame(food_costs)
        # Mocking some ratings for visualization since we don't have a direct "all food ratings" list
        # We can use the 'Rating' from menu today if available, but let's stick to costs
        fig_scatter = px.scatter(df_costs, x="Name", y="Estimated_Cost", size="Estimated_Cost",
                                color="Estimated_Cost", hover_name="Name",
                                title="Dish Production Cost Analysis")
        st.plotly_chart(fig_scatter, use_container_width=True)
        
        st.subheader("Production Cost Efficiency")
        st.dataframe(df_costs.sort_values(by="Estimated_Cost", ascending=False), use_container_width=True)
    else:
        st.warning("Production cost data unavailable. Ensure ingredients and recipes are linked.")

st.markdown("---")
st.info("💡 **Staff Tip:** High-cost items should be rotated less frequently or balanced with higher-popularity votes to optimize budget.")
