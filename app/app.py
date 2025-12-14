import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# 1. SETUP PAGE
st.set_page_config(page_title="Healthcare Dashboard", layout="wide")
st.title("🏥 Healthcare Management Dashboard (Phase 3)")

# 2. DATABASE CONNECTION
# This matches the credentials that worked in your check_db.py script
DB_URL = "postgresql://postgres:Ramaseshu1%40@localhost:5432/postgres"

@st.cache_resource
def get_connection():
    return create_engine(DB_URL)

try:
    engine = get_connection()
    
    # 3. SIDEBAR FILTERS
    st.sidebar.header("Filter Options")
    
    # --- CRITICAL FIX ---
    # We found 'fact_admissions' (Plural) in your check_db.py output (Row 5).
    # We select * to grab all columns first, so we don't crash on column names.
    query = """
    SELECT *
    FROM analytics_staging.fact_admissions
    """
    
    # Load Data
    with st.spinner('Fetching data from analytics_staging.fact_admissions...'):
        df = pd.read_sql(query, engine)
    
    # 4. DASHBOARD LOGIC
    if not df.empty:
        # Standardize Column Names (Lowercase) to avoid "KeyError"
        df.columns = [c.lower() for c in df.columns]
        
        # Identify the Date Column (It might be 'admission_date' or 'date_of_admission')
        date_col = 'admission_date' if 'admission_date' in df.columns else 'date_of_admission'
        
        if date_col not in df.columns:
            st.error(f"⚠️ Could not find date column. Available columns: {list(df.columns)}")
        else:
            # FILTERS
            all_types = df['admission_type'].unique().tolist() if 'admission_type' in df.columns else []
            selected_types = st.sidebar.multiselect("Select Admission Type", all_types, default=all_types)
            
            # Apply Filter
            if 'admission_type' in df.columns:
                filtered_df = df[df['admission_type'].isin(selected_types)]
            else:
                filtered_df = df

            # KPI METRICS
            st.subheader("Key Performance Indicators")
            col_kpi1, col_kpi2 = st.columns(2)
            col_kpi1.metric("Total Visits", len(filtered_df))
            
            if 'billing_amount' in df.columns:
                col_kpi2.metric("Total Billing", f"${filtered_df['billing_amount'].sum():,.2f}")
            
            st.divider()

            # VISUALIZATIONS
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Billing by Admission Type")
                if 'billing_amount' in df.columns and 'admission_type' in df.columns:
                    grouped = filtered_df.groupby("admission_type")["billing_amount"].mean()
                    st.bar_chart(grouped)
                else:
                    st.info("Billing or Admission Type data missing.")

            with col2:
                st.subheader("Admissions Timeline")
                filtered_df[date_col] = pd.to_datetime(filtered_df[date_col])
                daily = filtered_df.groupby(date_col).size()
                st.line_chart(daily)

            # RAW DATA
            with st.expander("View Source Data"):
                st.dataframe(filtered_df.head(100))
            
    else:
        st.warning("✅ Connection successful, but the table 'analytics_staging.fact_admissions' is empty.")

except Exception as e:
    st.error("❌ Connection Error")
    st.text(f"Error details: {e}")