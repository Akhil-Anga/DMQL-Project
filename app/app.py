import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & STYLING
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Executive Dashboard",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Modern Header & Visible Metrics
st.markdown("""
    <style>
    /* Main Background */
    .main {
        background-color: #0E1117;
    }
    
    /* -------------------------
       CUSTOM HEADER STYLING 
       ------------------------- */
    .header-container {
        display: flex;
        align-items: center;
        background: linear-gradient(90deg, rgba(20,20,30,1) 0%, rgba(33,40,55,1) 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #2C3E50;
        box-shadow: 0 4px 15px rgba(0, 201, 255, 0.1);
        margin-bottom: 30px;
    }
    
    .logo-img {
        width: 60px;
        height: 60px;
        margin-right: 20px;
    }
    
    .header-text-box {
        display: flex;
        flex-direction: column;
    }
    
    .header-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 32px;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #00C9FF, #92FE9D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .header-subtitle {
        font-family: 'Arial', sans-serif;
        font-size: 14px;
        color: #B0B8C6;
        margin-top: 5px;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* -------------------------
       METRIC CARD STYLING 
       ------------------------- */
    div[data-testid="stMetric"], .stMetric {
        background-color: #F0F2F6 !important; 
        border: 1px solid #d6d6d6;
        padding: 20px !important;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        color: #000000 !important; 
        height: 140px; 
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    div[data-testid="stMetric"] label {
        color: #31333F !important;
        font-size: 1.1rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #000000 !important;
        font-size: 2rem !important;
        font-weight: bold;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: #28a745 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATABASE CONNECTION
# -----------------------------------------------------------------------------
DB_URL = "postgresql://postgres:Ramaseshu1%40@localhost:5432/postgres"

@st.cache_resource
def get_connection():
    return create_engine(DB_URL)

def load_data():
    try:
        engine = get_connection()
        query = "SELECT * FROM analytics_staging.fact_admissions"
        with st.spinner(' Connecting to Data Warehouse...'):
            df = pd.read_sql(query, engine)
            
        df.columns = [c.lower() for c in df.columns]
        
        date_col = 'admission_date' if 'admission_date' in df.columns else 'date_of_admission'
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col])
        
        if 'discharge_date' in df.columns:
            df['discharge_date'] = pd.to_datetime(df['discharge_date'])
            
        return df, date_col
    except Exception as e:
        st.error(f" Database Connection Failed: {e}")
        return pd.DataFrame(), None

# -----------------------------------------------------------------------------
# 3. CUSTOM HTML HEADER (New Logo & Branding)
# -----------------------------------------------------------------------------

logo_url = "https://cdn-icons-png.flaticon.com/512/3063/3063176.png"

st.markdown(f"""
    <div class="header-container">
        <img src="{logo_url}" class="logo-img">
        <div class="header-text-box">
            <h1 class="header-title">Healthcare Executive Dashboard</h1>
            <div class="header-subtitle">Operational Overview & Financial Performance</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. MAIN DASHBOARD LOGIC
# -----------------------------------------------------------------------------

df, date_col = load_data()

if not df.empty and date_col:
    
    # --- SIDEBAR FILTERS ---
    with st.sidebar:
        st.markdown("### ⚙️ Dashboard Controls")
        st.divider()
        
        # --- PROPER DATE FILTERING ---
        # 1. Convert timestamp series to python date objects for the widget
        min_date_obj = df[date_col].min().date()
        max_date_obj = df[date_col].max().date()
        
        st.markdown(" **Select Time Period**")
        
        # 2. Two separate inputs prevent the "Range Tuple" crash
        start_date = st.date_input(
            "Start Date", 
            value=min_date_obj, 
            min_value=min_date_obj, 
            max_value=max_date_obj
        )
        
        end_date = st.date_input(
            "End Date", 
            value=max_date_obj, 
            min_value=min_date_obj, 
            max_value=max_date_obj
        )
        
        # Validation
        if start_date > end_date:
            st.error(" Start Date cannot be after End Date")
            
        st.divider()

        if 'admission_type' in df.columns:
            all_types = df['admission_type'].unique().tolist()
            selected_types = st.multiselect(" Filter by Admission Type", all_types, default=all_types)
        else:
            selected_types = []

    # --- APPLY FILTERS ---
    mask = pd.Series([True] * len(df))
    
    # Filter by Date (Comparing Date objects to Date objects)
    mask = mask & (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
    
    if 'admission_type' in df.columns and selected_types:
        mask = mask & (df['admission_type'].isin(selected_types))
    
    filtered_df = df.loc[mask]

    # --- TOP ROW: KPI METRICS ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_visits = len(filtered_df)
    total_revenue = filtered_df['billing_amount'].sum() if 'billing_amount' in filtered_df.columns else 0
    avg_billing = filtered_df['billing_amount'].mean() if 'billing_amount' in filtered_df.columns else 0
    
    if 'discharge_date' in filtered_df.columns and date_col in filtered_df.columns:
        avg_los = (filtered_df['discharge_date'] - filtered_df[date_col]).dt.days.mean()
    else:
        avg_los = 0

    col1.metric("Total Admissions", f"{total_visits:,}")
    col2.metric("Total Revenue", f"${total_revenue:,.0f}")
    col3.metric("Avg. Bill per Patient", f"${avg_billing:,.2f}")
    col4.metric("Avg. Length of Stay", f"{avg_los:.1f} Days")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- MIDDLE ROW: CHARTS ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader(" Revenue by Admission Type")
        if 'admission_type' in filtered_df.columns and 'billing_amount' in filtered_df.columns:
            fig_bar = px.bar(
                filtered_df.groupby("admission_type")["billing_amount"].sum().reset_index(),
                x="admission_type",
                y="billing_amount",
                color="admission_type",
                text_auto='.2s',
                title="Financial Performance",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_bar.update_layout(xaxis_title="", yaxis_title="Revenue ($)", font=dict(size=14))
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Insufficient data for Revenue Chart.")

    with chart_col2:
        st.subheader("Admission Distribution")
        if 'admission_type' in filtered_df.columns:
            fig_pie = px.pie(
                filtered_df, 
                names='admission_type', 
                hole=0.4,
                title="Patient Distribution by Type",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_pie.update_traces(textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Insufficient data for Distribution Chart.")

    # --- BOTTOM ROW: TIME SERIES ---
    st.subheader("Revenue Trends Over Time")
    if date_col and 'billing_amount' in filtered_df.columns:
        daily_revenue = filtered_df.groupby(date_col)['billing_amount'].sum().reset_index()
        fig_area = px.area(
            daily_revenue,
            x=date_col,
            y="billing_amount",
            title="Daily Revenue Trend",
            color_discrete_sequence=["#00C9FF"]
        )
        fig_area.update_layout(xaxis_title="Date", yaxis_title="Daily Revenue ($)")
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.info("Insufficient data for Time Series.")

    # --- RAW DATA EXPANDER ---
    with st.expander("View Detailed Patient Records"):
        if date_col in filtered_df.columns:
            st.dataframe(filtered_df.sort_values(by=date_col, ascending=False).head(100), use_container_width=True)
        else:
            st.dataframe(filtered_df.head(100), use_container_width=True)

else:
    st.warning(" No data found. Please check your database tables or run 'dbt run'.")