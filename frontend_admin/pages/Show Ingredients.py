import streamlit as st
import requests
import pandas as pd


BACKEND_URL = "http://backend:8000"

#test email
USER_EMAIL = "mazaan.bscs25seecs@seecs.edu.pk"

st.set_page_config(page_title="RotiRouter - Ingredients", layout="wide")
st.title("🥦 Mess Ingredients & Inventory Manager")
st.write("Manage daily stock, pricing, and raw materials for the NUST SEECS Mess.")


auth_params = {"email": USER_EMAIL}


def load_ingredients():
    try:
        response = requests.get(f"{BACKEND_URL}/analytics/ingredients", params=auth_params)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error {response.status_code}: {response.json().get('detail', 'Unknown error')}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the Backend server. Is FastAPI running?")
        return []


ingredients_list = load_ingredients()

if ingredients_list:
    st.header("📦 Current Inventory")
    st.dataframe(pd.DataFrame(ingredients_list), use_container_width=True)
else:
    st.info("No ingredients found in the system.")


st.write("---")
st.header("🍽️ Today's Menu & Recipe Ingredients")
st.write("Select a meal category to view scheduled items and edit their recipe ingredient requirements.")

col_bf, col_ln, col_dn = st.columns(3)

if "selected_meal" not in st.session_state:
    st.session_state.selected_meal = "Breakfast"

with col_bf:
    if st.button("🍳 Breakfast", use_container_width=True,
                 type="primary" if st.session_state.selected_meal == "Breakfast" else "secondary"):
        st.session_state.selected_meal = "Breakfast"
        st.rerun()

with col_ln:
    if st.button("🍛 Lunch", use_container_width=True,
                 type="primary" if st.session_state.selected_meal == "Lunch" else "secondary"):
        st.session_state.selected_meal = "Lunch"
        st.rerun()

with col_dn:
    if st.button("🍗 Dinner", use_container_width=True,
                 type="primary" if st.session_state.selected_meal == "Dinner" else "secondary"):
        st.session_state.selected_meal = "Dinner"
        st.rerun()

current_meal = st.session_state.selected_meal
st.subheader(f"Current Category: {current_meal}")



@st.cache_data(ttl=10)  # Cache for 10 seconds to keep performance smooth
def fetch_today_menu():
    try:
        response = requests.get(f"{BACKEND_URL}/menu/today", params=auth_params)
        if response.status_code == 200:
            return response.json().get("menu", [])
        return []
    except Exception:
        return []


@st.cache_data(ttl=10)
def fetch_all_recipes():
    try:

        response = requests.get(f"{BACKEND_URL}/recipes", params=auth_params)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception:
        return []



menu_items = fetch_today_menu()
all_recipes = fetch_all_recipes()


filtered_menu = [item for item in menu_items if item.get("meal_type", "").lower() == current_meal.lower()]

if not filtered_menu:
    st.info(f"No items scheduled for {current_meal} today.")
else:

    food_names = [item.get("Name") for item in filtered_menu]
    selected_food_name = st.selectbox("Select a food item to inspect/modify:", food_names)


    selected_food = next((item for item in filtered_menu if item.get("Name") == selected_food_name), None)

    if selected_food:
        item_id = selected_food.get("ItemID") or selected_food.get("Item_ID")
        st.write(f"Showing recipe details for **{selected_food_name}** (Item ID: {item_id})")


        recipe_ingredients = [
            {
                "Ingredient ID": r.get("IngredientID") or r.get("Ingredient_ID"),
                "Ingredient Name": r.get("IngredientName") or r.get("Name"),
                "Quantity Required": r.get("Ingredient_Quantity") or r.get("Quantity", 0.0)
            }
            for r in all_recipes if r.get("Item_ID") == item_id or r.get("ItemID") == item_id
        ]

        if not recipe_ingredients:
            st.warning("No ingredients are currently mapped to this dish recipe.")


            with st.form("add_first_ingredient"):
                st.write("Add an ingredient to this dish:")
                new_ing_id = st.number_input("Ingredient ID", min_value=1, step=1)
                new_ing_qty = st.number_input("Quantity", min_value=0.1, step=0.1)
                add_sub = st.form_submit_button("Link Ingredient")
                if add_sub:
                    add_res = requests.post(
                        f"{BACKEND_URL}/admin/add_recipe/{item_id}/{new_ing_id}/{new_ing_qty}",
                        params=auth_params
                    )
                    if add_res.status_code == 200:
                        st.success("Ingredient linked successfully!")
                        st.cache_data.clear()  # Clear cache to refresh
                        st.rerun()
                    else:
                        st.error("Failed to link ingredient.")
        else:

            df = pd.DataFrame(recipe_ingredients)

            st.write(
                "✏️ **Editable Recipe Board** (Double click cells under 'Quantity Required' to edit, then click Save below)")


            edited_df = st.data_editor(
                df,
                disabled=["Ingredient ID", "Ingredient Name"],
                num_rows="dynamic",
                use_container_width=True,
                key="recipe_editor"
            )

            if st.button("💾 Save Recipe Changes", type="primary"):
                success_count = 0
                error_count = 0



                for index, row in edited_df.iterrows():
                    ing_id = int(row["Ingredient ID"])
                    qty = float(row["Quantity Required"])

                    # Call the PATCH recipe endpoint
                    patch_url = f"{BACKEND_URL}/admin/recipe/update/{item_id}/{ing_id}"
                    payload = {
                                "Ingredient_Quantity": qty
                    }

                    response = requests.patch(patch_url, json=payload, params=auth_params)
                    if response.status_code == 200:
                        success_count += 1
                    else:
                        error_count += 1

                if error_count == 0:
                    st.success(f"Successfully updated all recipe details!")
                    st.cache_data.clear()  # Bust cache so update is pulled fresh next load
                    st.rerun()
                else:
                    st.warning(f"Updated {success_count} fields, but {error_count} updates failed.")


