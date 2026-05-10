import streamlit as st
import pandas as pd
import requests
import os

# ==============================================================================
# PAGE CONFIGURATION & CUSTOM THEME Styling
# ==============================================================================
st.set_page_config(
    page_title="Admin Data Center | Mess Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a clean, modern card layout and custom metric stylings
st.markdown("""
    <style>
        /* Main background & Font settings */
        .main {
            background-color: #f8f9fa;
        }
        /* Custom card style */
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #4F46E5;
            margin-bottom: 15px;
        }
        .metric-title {
            font-size: 14px;
            color: #6B7280;
            font-weight: 600;
            text-transform: uppercase;
        }
        .metric-value {
            font-size: 24px;
            color: #111827;
            font-weight: 700;
        }
        /* Style Streamlit primary buttons */
        div.stButton > button:first-child {
            background-color: #4F46E5;
            color: white;
            border-radius: 8px;
            font-weight: bold;
            border: none;
            padding: 10px 24px;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #4338CA;
            border: none;
        }
    </style>
""", unsafe_index=True)

# ==============================================================================
# ENVIRONMENT CONFIGURATION
# ==============================================================================
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
USER_EMAIL = "mazaan.bscs25seecs@seecs.edu.pk"


# ==============================================================================
# HELPER DATA FETCHERS
# ==============================================================================
@st.cache_data(show_spinner=False)
def fetch_data(endpoint: str, params: dict = None) -> pd.DataFrame:
    """Generic fetch helper with integrated error state handling."""
    url = f"{BACKEND_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return pd.DataFrame(data) if data else pd.DataFrame()
        else:
            st.error(f"⚠️ Error {response.status_code}: Fetching from `{endpoint}` failed.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ Connection Error: Unable to contact the backend server ({e})")
        return pd.DataFrame()


# ==============================================================================
# SIDEBAR NAVIGATION
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/database.png", width=120)
    st.title("Admin Panel")
    st.markdown("Welcome back, **Admin**")
    st.caption(f"Logged in as: `{USER_EMAIL}`")
    st.divider()

    # Clean selection options mapping to real-time schema structures
    option = st.radio(
        "🗂️ Database Collections",
        options=[
            "Students Profile Data",
            "Staff Details (vw_StaffDetails)",
            "Food & Ingredient Costing",
            "Monthly Billings (vw_MonthlyBillingSummary)",
            "System Transactions",
            "Active Menu Schedule"
        ]
    )
    st.divider()
    st.info("💡 **Tip:** Use the search bar on the right to instant-filter matches.")

# ==============================================================================
# DASHBOARD HEADER
# ==============================================================================
st.markdown(f"# 📊 Mess Management Data Center")
st.markdown("Real-time synchronization with the database schema for administrative operations.")
st.divider()

# ==============================================================================
# LOAD AND FORMAT DATASETS
# ==============================================================================
df = pd.DataFrame()
summary_metrics = {}

if option == "Students Profile Data":
    # Joins Users + Student DB schemas
    df = fetch_data("admin/students/all", {"email": USER_EMAIL})
    if not df.empty:
        summary_metrics = {
            "Total Registered Students": len(df),
            "Departments Active": len(df["Department"].unique()) if "Department" in df else 0,
            "Hostels Served": len(df["Hostel_Name"].unique()) if "Hostel_Name" in df else 0
        }

elif option == "Staff Details (vw_StaffDetails)":
    # Maps directly to vw_StaffDetails
    df = fetch_data("admin/staff/details/all", {"email": USER_EMAIL})
    if not df.empty:
        summary_metrics = {
            "Total Employed Staff": len(df),
            "Active Categories": len(df["Category"].unique()) if "Category" in df else 0,
            "Total Monthly Payroll (PKR)": f'{df["Salary"].astype(float).sum():,.2f}' if "Salary" in df else "0.00"
        }

elif option == "Food & Ingredient Costing":
    # Maps to vw_FoodItemCost View
    df = fetch_data("admin/food/costs", {"email": USER_EMAIL})
    if not df.empty:
        summary_metrics = {
            "Total Recipes": len(df),
            "Highest Costing Item": df.loc[df['Estimated_Cost'].astype(float).idxmax()][
                'Name'] if 'Estimated_Cost' in df else "N/A",
            "Avg Rating Overall": f"{df['Ratings_Average'].astype(float).mean():.2f} ⭐" if "Ratings_Average" in df else "No Ratings"
        }

elif option == "Monthly Billings (vw_MonthlyBillingSummary)":
    # Maps directly to the MySQL view vw_MonthlyBillingSummary
    df = fetch_data("admin/monthly_billing_summary", {"email": USER_EMAIL})
    if not df.empty:
        total_billed = df["Total_Amount"].astype(float).sum() if "Total_Amount" in df else 0
        total_collected = df["Total_Collected"].astype(float).sum() if "Total_Collected" in df else 0
        total_outstanding = df["Outstanding"].astype(float).sum() if "Outstanding" in df else 0

        summary_metrics = {
            "Total Invoiced (PKR)": f"{total_billed:,.2f}",
            "Collected Amount (PKR)": f"{total_collected:,.2f}",
            "Outstanding Dues (PKR)": f"{total_outstanding:,.2f}"
        }

elif option == "System Transactions":
    # Raw Transactions from Database Table
    df = fetch_data("admin/transactions", {"email": USER_EMAIL})
    if not df.empty:
        successful_txs = df[df["Transaction_Status"] == "Success"]
        summary_metrics = {
            "Executed Transactions": len(df),
            "Total Revenue Processed": f"{successful_txs['Amount_Paid'].astype(float).sum():,.2f}" if not successful_txs.empty else "0.00",
            "Failed Transactions": len(df[df["Transaction_Status"] == "Failed"])
        }
    else:
        # Fallback empty UI
        summary_metrics = {"Executed Transactions": 0, "Revenue Processed": "PKR 0.00", "Status": "Ready"}

elif option == "Active Menu Schedule":
    # Maps to view vw_MenuSchedule
    df = fetch_data("menu/weekly")
    if not df.empty:
        summary_metrics = {
            "Scheduled Days": len(df["Date"].unique()) if "Date" in df else 0,
            "Planned Meals": len(df),
            "Cancelled Slots": len(df[df["Slot_Status"] == "Cancelled"]) if "Slot_Status" in df else 0
        }

# ==============================================================================
# RENDER METRICS BANNER
# ==============================================================================
if summary_metrics:
    cols = st.columns(len(summary_metrics))
    for col, (title, val) in zip(cols, summary_metrics.items()):
        with col:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{title}</div>
                    <div class="metric-value">{val}</div>
                </div>
            """, unsafe_allow_html=True)

# ==============================================================================
# DISPLAY INTERACTIVE DATAGRID & SEARCH
# ==============================================================================
st.markdown("### 📋 Table Explorer")

if not df.empty:
    # Header bar with real-time text-search input and manual refresh
    col_search, col_spacer, col_refresh = st.columns([2, 2, 1])

    with col_search:
        search_query = st.text_input("🔍 Filter rows with quick regex-search...",
                                     placeholder="Type student, department, or status...")

    with col_refresh:
        st.write("")  # layout padding alignment
        refresh_button = st.button("🔄 Reload From Source", use_container_width=True)
        if refresh_button:
            st.cache_data.clear()
            st.rerun()

    # Search Logic implementation
    if search_query:
        # Check all column contents for matched strings
        filtered_df = df[df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)]
    else:
        filtered_df = df

    # Data Display Panel
    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "Email": st.column_config.LinkColumn("Email Link"),
            "Status": st.column_config.SelectboxColumn("Status"),
            "Ratings_Average": st.column_config.NumberColumn("Avg Rating", format="%.2f ⭐"),
            "Amount": st.column_config.NumberColumn("Bill Total (PKR)", format="Rs %d"),
        },
        height=450
    )

    # Footer Actions Row
    col_count, col_csv = st.columns([4, 1])
    with col_count:
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} matching database records.**")

    with col_csv:
        csv_bin = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Export Active view to CSV",
            data=csv_bin,
            file_name=f"{option.lower().replace(' ', '_')}_export.csv",
            mime="text/csv",
            use_container_width=True
        )
else:
    # Warning container if table records have zero values or connection failed
    st.warning(
        f"No records found for selection: '{option}'. If this persists, verify your database container setup is seeded.")

    st.markdown("""
    💡 **Seeding check:**
    Please confirm that your container has executed the queries in `init.sql`. You can check this by accessing your FastAPI interactive Swagger at:
    `http://localhost:8000/docs`
    """)