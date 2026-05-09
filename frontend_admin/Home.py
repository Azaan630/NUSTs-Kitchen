import streamlit as st
import pandas as pd
import httpx
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime
import seaborn as sns
import matplotlib.pyplot as plt

# --- CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="RotiRouter Admin | Data Insights",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ADMIN_EMAIL = "admin@nust.edu.pk"  # Default admin for testing

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f8fafc;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7bcf,#2e7bcf);
        color: white;
    }
    h1, h2, h3 {
        color: #1e3a8a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- API CLIENT ---
class AdminAPI:
    @staticmethod
    def get(endpoint, params=None):
        try:
            # We always pass admin email for RBAC as per backend logic
            p = {"email": ADMIN_EMAIL}
            if params:
                p.update(params)
            # Use httpx.get as per original code
            response = httpx.get(f"{BACKEND_URL}{endpoint}", params=p, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"Backend Error ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            st.error(f"Connection Failed: {str(e)}")
            return None

api = AdminAPI()

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🚀 RotiRouter Admin")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📈 Dashboard Overview", "💰 Financial Analytics", "🍽️ Kitchen & Menu", "📦 Inventory & Recipes", "👥 User Management"]
)

st.sidebar.markdown("---")
st.sidebar.info(f"Logged in as: {ADMIN_EMAIL}")

# --- PAGE: DASHBOARD OVERVIEW ---
if page == "📈 Dashboard Overview":
    st.title("📊 Mess Management Overview")
    
    # Hero Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    billing_summary = api.get("/admin/monthly_billing_summary")
    students = api.get("/admin/students/all")
    
    if billing_summary and students:
        df_bills = pd.DataFrame(billing_summary)
        total_outstanding = df_bills['Outstanding'].sum() if 'Outstanding' in df_bills else 0
        total_collected = df_bills['Total_Collected'].sum() if 'Total_Collected' in df_bills else 0
        collection_rate = (total_collected / (total_collected + total_outstanding)) * 100 if (total_collected + total_outstanding) > 0 else 0
        
        col1.metric("Total Students", len(students))
        col2.metric("Monthly Collection", f"Rs. {total_collected:,.0f}")
        col3.metric("Outstanding", f"Rs. {total_outstanding:,.0f}", delta=f"-{total_outstanding:,.0f}", delta_color="inverse")
        col4.metric("Collection Rate", f"{collection_rate:.1f}%")

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🔥 Active Poll Results")
        poll_results = api.get("/admin/poll/results")
        if poll_results and "results" in poll_results:
            df_poll = pd.DataFrame(poll_results["results"])
            if not df_poll.empty:
                fig = px.bar(df_poll, x="Name", y="Vote_Count", 
                             color="Vote_Count", color_continuous_scale="Viridis",
                             title="Votes per Food Item")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No active poll results found.")
        
        st.subheader("📅 Weekly Menu Schedule")
        weekly_menu = api.get("/menu/weekly")
        if weekly_menu:
            df_menu = pd.DataFrame(weekly_menu)
            if not df_menu.empty:
                # Pivot for better visualization
                df_menu_pivot = df_menu.pivot_table(index="Date", columns="meal_type", values="Food_Item_Name", aggfunc=lambda x: ", ".join(x))
                st.dataframe(df_menu_pivot, use_container_width=True)
            else:
                st.info("No menu items scheduled for this week.")

    with col_right:
        st.subheader("⚡ Quick Staff Actions")
        with st.container(border=True):
            st.button("🔄 Sync Backend Cache", use_container_width=True)
            st.button("📢 Broadcast Menu Update", use_container_width=True)
            st.button("⚠️ Trigger Emergency Stock Order", use_container_width=True)
        
        st.subheader("📊 Ingredient Levels")
        ingredients = api.get("/analytics/ingredients")
        if ingredients:
            df_ing = pd.DataFrame(ingredients)
            if not df_ing.empty:
                fig_ing = px.pie(df_ing, names="Name", values="Total_Quantity", 
                                 hole=0.4, title="Stock Distribution")
                st.plotly_chart(fig_ing, use_container_width=True)
                
                # Low stock warning
                low_stock = df_ing[df_ing['Total_Quantity'] < 20]
                if not low_stock.empty:
                    st.warning(f"Low Stock Alert: {', '.join(low_stock['Name'].tolist())}")

# --- PAGE: FINANCIAL ANALYTICS ---
elif page == "💰 Financial Analytics":
    st.title("💰 Revenue & Billing Insights")
    
    billing_summary = api.get("/admin/monthly_billing_summary")
    if billing_summary:
        df = pd.DataFrame(billing_summary)
        
        st.subheader("Monthly Billing Trend")
        fig_trend = px.line(df, x="Billing_Month", y=["Total_Amount", "Total_Collected"], 
                            markers=True, title="Revenue vs Collection")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Outstanding Amount by Month")
            fig_out = px.bar(df, x="Billing_Month", y="Outstanding", color="Outstanding",
                             color_continuous_scale="Reds")
            st.plotly_chart(fig_out, use_container_width=True)
        
        with col_b:
            st.subheader("Collection Breakdown")
            # Assuming we can get more granular data or just use this
            df_pie = pd.melt(df, id_vars=["Billing_Month"], value_vars=["Total_Collected", "Outstanding"])
            fig_pie = px.sunburst(df_pie, path=["Billing_Month", "variable"], values="value",
                                  color="variable", color_discrete_map={'Total_Collected':'#10b981', 'Outstanding':'#ef4444'})
            st.plotly_chart(fig_pie, use_container_width=True)

# --- PAGE: MENU & FOOD INSIGHTS ---
elif page == "🍽️ Kitchen & Menu":
    st.title("🍽️ Culinary Analytics")
    
    food_costs = api.get("/admin/food/costs")
    if food_costs:
        df_costs = pd.DataFrame(food_costs)
        
        st.subheader("Food Item Cost Analysis")
        fig_costs = px.scatter(df_costs, x="Name", y="Estimated_Cost", size="Estimated_Cost",
                               color="Estimated_Cost", hover_name="Name", 
                               title="Production Cost per Dish")
        st.plotly_chart(fig_costs, use_container_width=True)
        
        # Rankings and Ratings
        st.subheader("⭐ Top Rated Dishes")
        st.dataframe(df_costs.style.background_gradient(subset=['Estimated_Cost'], cmap='YlOrRd'), use_container_width=True)

# --- PAGE: INVENTORY & RECIPES ---
elif page == "📦 Inventory & Recipes":
    st.title("📦 Supply Chain & Recipe Management")
    
    tab1, tab2 = st.tabs(["Inventory Status", "Recipe Book"])
    
    with tab1:
        ingredients = api.get("/analytics/ingredients")
        if ingredients:
            df_ing = pd.DataFrame(ingredients)
            st.subheader("Current Stock Levels")
            fig_stock = px.bar(df_ing, x="Name", y="Total_Quantity", color="Name",
                               text="Total_Quantity", title="Available Quantity (kg/L)")
            st.plotly_chart(fig_stock, use_container_width=True)
            
            st.subheader("Unit Pricing Distribution")
            fig_price = px.box(df_ing, y="Unit_cost", points="all", title="Ingredient Price Spread")
            st.plotly_chart(fig_price, use_container_width=True)

    with tab2:
        recipes = api.get("/recipes")
        if recipes:
            df_recipes = pd.DataFrame(recipes)
            st.subheader("Recipe Ingredient Breakdown")
            # Filter by food item
            food_items = df_recipes['Name'].unique()
            selected_food = st.selectbox("Select Dish", food_items)
            
            dish_recipe = df_recipes[df_recipes['Name'] == selected_food]
            fig_recipe = px.bar(dish_recipe, x="Ingredient_Quantity", y="Name_1", 
                                orientation='h', labels={"Name_1": "Ingredient"},
                                title=f"Ingredients for {selected_food}")
            st.plotly_chart(fig_recipe, use_container_width=True)

# --- PAGE: USER MANAGEMENT ---
elif page == "👥 User Management":
    st.title("👥 Stakeholder Management")
    
    user_tab, staff_tab = st.tabs(["Students", "Staff Members"])
    
    with user_tab:
        students = api.get("/admin/students/all")
        if students:
            df_students = pd.DataFrame(students)
            st.subheader("Student Directory")
            
            # Search functionality
            search = st.text_input("🔍 Search Student by Name or Email")
            if search:
                df_students = df_students[df_students['First_Name'].str.contains(search, case=False) | 
                                          df_students['Email'].str.contains(search, case=False)]
            
            st.dataframe(df_students, use_container_width=True)
            
            # Detail View
            if not df_students.empty:
                selected_uid = st.selectbox("View Billing History for:", df_students['UserID'], 
                                            format_func=lambda x: df_students[df_students['UserID']==x]['First_Name'].values[0])
                
                bill_status = api.get(f"/admin/{selected_uid}/bill_status")
                if bill_status:
                    st.write(f"### Billing Records for {selected_uid}")
                    st.table(pd.DataFrame(bill_status))

    with staff_tab:
        st.subheader("Staff Administration")
        # Find all users with Account_Type = 'Staff'
        all_users = api.get("/admin/students/all")
        if all_users:
            df_all = pd.DataFrame(all_users)
            staff_users = df_all[df_all['Account_Type'] == 'Staff']
            
            if not staff_users.empty:
                st.dataframe(staff_users, use_container_width=True)
                selected_staff = st.selectbox("Staff Member Details", staff_users['UserID'])
                staff_details = api.get(f"/admin/staff/details/{selected_staff}")
                if staff_details:
                    st.json(staff_details)
            else:
                st.info("No staff members registered.")

# --- FOOTER ---
st.markdown("---")
st.markdown(f"© {date.today().year} RotiRouter Mess Management System | Built with Streamlit 🚀")
