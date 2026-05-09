import streamlit as st
import pandas as pd
import plotly.express as px
import os
import httpx

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
ADMIN_EMAIL = "admin@nust.edu.pk"

st.set_page_config(page_title="User Directory", page_icon="👥", layout="wide")

st.title("👥 Stakeholder Management")
st.markdown("Comprehensive directory of students and staff members.")

def get_data(endpoint):
    try:
        res = httpx.get(f"{BACKEND_URL}{endpoint}", params={"email": ADMIN_EMAIL})
        return res.json() if res.status_code == 200 else None
    except: return None

users = get_data("/admin/students/all")

if users:
    df_users = pd.DataFrame(users)
    
    # Overview
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Users", len(df_users))
    col2.metric("Students", len(df_users[df_users['Account_Type']=='Student']))
    col3.metric("Staff/Admins", len(df_users[df_users['Account_Type']!='Student']))
    
    st.markdown("---")
    
    tab_students, tab_staff = st.tabs(["🎓 Students", "🏢 Staff & Admin"])
    
    with tab_students:
        df_students = df_users[df_users['Account_Type'] == 'Student']
        
        col_list, col_details = st.columns([1, 1])
        
        with col_list:
            st.subheader("Directory")
            search = st.text_input("🔍 Search Student", placeholder="Name or Email...")
            if search:
                df_students = df_students[df_students['First_Name'].str.contains(search, case=False) | 
                                          df_students['Email'].str.contains(search, case=False)]
            
            # Selection for details
            selected_student_name = st.selectbox("Select Student for Details", 
                                                df_students['First_Name'] + " (" + df_students['Email'] + ")")
            selected_email = selected_student_name.split("(")[1].split(")")[0]
            student_row = df_students[df_students['Email'] == selected_email].iloc[0]
            
            st.dataframe(df_students[['UserID', 'First_Name', 'Last_Name', 'Email']], use_container_width=True)

        with col_details:
            st.subheader("Student Profile Card")
            with st.container(border=True):
                st.write(f"### {student_row['First_Name']} {student_row['Last_Name']}")
                st.write(f"📧 **Email:** {student_row['Email']}")
                st.write(f"🆔 **User ID:** {student_row['UserID']}")
                
                # Fetch specific billing info
                bills = get_data(f"/admin/{student_row['UserID']}/bill_status")
                if bills:
                    st.write("---")
                    st.write("#### 💸 Recent Billing Status")
                    df_bills = pd.DataFrame(bills)
                    
                    # Status coloring
                    def color_status(val):
                        color = '#10b981' if val == 'Paid' else '#ef4444'
                        return f'color: {color}; font-weight: bold'
                    
                    st.dataframe(df_bills[['Month', 'Amount', 'Status']].style.applymap(color_status, subset=['Status']), 
                                 use_container_width=True)
                else:
                    st.info("No billing history found for this student.")

    with tab_staff:
        df_staff = df_users[df_users['Account_Type'] != 'Student']
        st.subheader("Staff & Administrative Personnel")
        
        st.dataframe(df_staff, use_container_width=True)
        
        selected_staff = st.selectbox("Detailed Staff Info", df_staff['UserID'], 
                                      format_func=lambda x: df_staff[df_staff['UserID']==x]['First_Name'].values[0])
        
        staff_details = get_data(f"/admin/staff/details/{selected_staff}")
        if staff_details:
            st.json(staff_details)
        else:
            st.info("Select a staff member to see their contract details and working hours.")

else:
    st.error("Unable to load user directory. Please check backend connectivity.")
