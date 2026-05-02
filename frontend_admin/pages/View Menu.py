import streamlit as st
import pandas as pd
from matplotlib import container


#our session states
if "step" not in st.session_state:
    st.session_state.step = 1

#our call backs yo

def openWeek():
    st.session_state.step = 2

def openDay():
    st.session_state.step = 1

#json that i might receive from the backend during api call

#the daily data
today_Bdummy_data = [{"ID": 101, "Name": "Omelette", "Quantity(kg)": 50, "Day": "Monday", "Rating Avg": 3.5, "Vote Count": 0,
               "item_expenditure": 30000},
              {"ID": 102, "Name": "Tea", "Quantity(kg)": 40, "Day": "Monday", "Rating Avg": 5, "Vote Count": 0,
               "item_expenditure": 10000},
              {"ID": 103, "Name": "Paratha", "Quantity(kg)": 30, "Day": "Monday", "Rating Avg": 3.5, "Vote Count": 0,
               "item_expenditure": 11000}
                ]

today_Ldummy_data = [{"ID": 201, "Name": "Chicken Pulao", "Quantity(kg)": 60, "Day": "Monday", "Rating Avg": 4.5, "Vote Count": 0,
               "item_expenditure": 50000}
                ]

today_Ddummy_data = [{"ID": 301, "Name": "Pakore", "Quantity(kg)": 90, "Day": "Monday", "Rating Avg": 3.5, "Vote Count": 0,
               "item_expenditure": 12000}
                ]
#the weekly data
week_data = [
  {
    "day": "Monday",
    "breakfast": ["Omelette", "Tea", "Paratha"],
    "lunch": ["Chicken Pulao", "Raita", "Salad"],
    "dinner": ["Aloo Palak", "Roti", "Kheer"]
  },
  {
    "day": "Tuesday",
    "breakfast": ["Chana Chaat", "Tea", "Puri"],
    "lunch": ["Daal Chawal", "Shami Kabab"],
    "dinner": ["Chicken Karahi", "Naan", "Raita"]
  },
  {
    "day": "Wednesday",
    "breakfast": ["Fried Egg", "Bread", "Juice"],
    "lunch": ["Mix Vegetable Curry", "Roti", "Yogurt"],
    "dinner": ["Beef Nihari", "Khamiri Roti"]
  },
  {
    "day": "Thursday",
    "breakfast": ["Aloo Paratha", "Lassi", "Pickle"],
    "lunch": ["Biryani", "Cold Drink", "Salad"],
    "dinner": ["Kadhai Paneer", "Roti", "Custard"]
  },
  {
    "day": "Friday",
    "breakfast": ["Halwa Puri", "Chana", "Tea"],
    "lunch": ["Haleem", "Naan", "Lemon"],
    "dinner": ["Fish Fry", "Daal Maash", "Roti"]
  },
  {
    "day": "Saturday",
    "breakfast": ["Boiled Egg", "Cereal", "Milk"],
    "lunch": ["Aloo Keema", "Roti", "Salad"],
    "dinner": ["Chicken Tikka", "Puri Paratha", "Chutney"]
  },
  {
    "day": "Sunday",
    "breakfast": ["Pancakes", "Syrup", "Coffee"],
    "lunch": ["Mutton Kunna", "Naan"],
    "dinner": ["Vegetable Pulao", "Raita", "Gulab Jamun"]
  }
]


#custom CSS for buttons
st.markdown("""
      <style>
      div.stButton > button:first-child {
          background-color: #ffcccb; /* Light Red */
          color: black;
          border: 1px solid #ff9999;
          width: auto;
          padding-left: 20px;
          padding-right: 20px;

      }

      /* Hover effect */
      div.stButton > button:hover {
          background-color: #ffb3b3;
          color: black;
          border: 1px solid #ff7f7f;
      }
      </style>
      """, unsafe_allow_html=True)



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


if st.session_state.step == 1:
    with col2:
        st.title("Today's Menu")



    #my breakfast
    with st.container(border=True):
        col4,col5 = st.columns([1,5])
        with col4:
            st.markdown("### 🍳 \n **Breakfast**")

        with col5:
            breakfast = pd.DataFrame(today_Bdummy_data)
            st.dataframe(breakfast)


    st.divider()
    #my lunch
    with st.container(border=True):
        col6, col7 = st.columns([1,5])

        with col6:
            st.markdown("### 🍗 \n **Lunch**")

        with col7:
            lunch = pd.DataFrame(today_Ldummy_data)
            st.dataframe(lunch)

    st.divider()
    #my dinner
    with st.container(border = True):
        col8, col9 = st.columns([1,5])

        with col8:
            st.markdown("### 🍲 \n **Dinner**")

        with col9:
            dinner = pd.DataFrame(today_Ddummy_data)
            st.dataframe(dinner)


    # 1. Custom CSS to change the button color to light red


    # ... (Your existing table/menu code here) ...

    # 2. Centering the button using columns
    # We create 3 columns; the middle one holds the button
    col10, col20, col30 = st.columns([1, 1, 1])

    with col20:
        st.write(" ")
        st.write(" ")
        st.button("Check Weekly Menu", on_click = openWeek)

else:
    col11,col22,col33 = st.columns([1,2,1])
    with col22:
        st.title("Weekly Menu")

    st.header("With great food comes the great responsibility")


    with st.container(border = True):
        wdata = pd.DataFrame(week_data)

        st.dataframe(wdata, hide_index = True)

    c1,c2,c3 = st.columns([1,1,1])

    with c2:
        st.write(" ")
        st.button("Check Daily Menu", on_click = openDay)


