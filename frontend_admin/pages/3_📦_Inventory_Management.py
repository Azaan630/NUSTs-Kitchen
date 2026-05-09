import streamlit as st
import pandas as pd
import plotly.express as px
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ADMIN_EMAIL = "admin@nust.edu.pk"

st.set_page_config(page_title="Inventory Management", page_icon="📦", layout="wide")

st.title("📦 Inventory & Recipe Management")
st.markdown("Track your stock levels, ingredient costs, and recipe compositions.")

def get_data(endpoint):
    try:
        res = httpx.get(f"{BACKEND_URL}{endpoint}", params={"email": ADMIN_EMAIL})
        return res.json() if res.status_code == 200 else None
    except: return None

ingredients = get_data("/analytics/ingredients")
recipes = get_data("/recipes")

if ingredients:
    df_ing = pd.DataFrame(ingredients)
    
    # KPIs
    low_stock_count = len(df_ing[df_ing['Total_Quantity'] < 20])
    total_value = (df_ing['Total_Quantity'] * df_ing['Unit_cost']).sum()
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Ingredients", len(df_ing))
    c2.metric("Total Inventory Value", f"Rs. {total_value:,.0f}")
    c3.metric("Low Stock Items", low_stock_count, delta=-low_stock_count, delta_color="inverse")

    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Stock Levels by Ingredient")
        fig = px.bar(df_ing, x="Name", y="Total_Quantity", color="Total_Quantity",
                     color_continuous_scale="GnBu", text="Total_Quantity",
                     labels={"Total_Quantity": "Quantity (kg/L)"})
        st.plotly_chart(fig, use_container_width=True)
        
    with col_right:
        st.subheader("Cost Distribution")
        fig_pie = px.pie(df_ing, values="Unit_cost", names="Name", hole=0.5,
                         title="Unit Cost Comparison")
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("📋 Ingredient Audit Table")
    st.dataframe(df_ing.style.highlight_min(axis=0, subset=['Total_Quantity'], color='#ffcccc'), use_container_width=True)

if recipes:
    st.markdown("---")
    st.subheader("🍲 Recipe Composition Explorer")
    df_rec = pd.DataFrame(recipes)
    
    food_item = st.selectbox("Select Dish to View Recipe", df_rec['Name'].unique())
    dish_data = df_rec[df_rec['Name'] == food_item]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_rec = px.bar(dish_data, x="Ingredient_Quantity", y="Name_1", orientation='h',
                         labels={"Name_1": "Ingredient", "Ingredient_Quantity": "Amount per Serving"},
                         title=f"Recipe Details: {food_item}")
        st.plotly_chart(fig_rec, use_container_width=True)
    
    with col2:
        st.info("💡 **Staff Tip:** Ensure ingredients are updated in the inventory before marking a meal as cooked to maintain accurate stock records.")
        st.table(dish_data[['Name_1', 'Ingredient_Quantity', 'Unit']])
else:
    st.warning("No recipe data available. Add recipes in the Admin Panel to see analytics.")
