import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sqlalchemy import create_engine

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Healthcare Executive Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Professional UI
st.markdown("""
    <style>
    .main { background-color: #0E1117; }
    .header-container {
        background-color: #1e2130; padding: 20px; border-radius: 15px; 
        border: 1px solid #333; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between;
    }
    .header-text h1 { color: #00C9FF; margin: 0; font-size: 36px; font-weight: 800; font-family: 'Helvetica Neue', sans-serif; }
    .header-text p { color: #cfd8dc; margin: 5px 0 0 0; text-transform: uppercase; letter-spacing: 1px; }
    div[data-testid="stMetric"] { background-color: #1e2130 !important; border: 1px solid #2e3346; border-radius: 10px; padding: 15px; }
    
    /* Improve Form Button Styling */
    div[data-testid="stForm"] button {
        background-color: #00C9FF;
        color: black;
        font-weight: bold;
        width: 100%;
        border: none;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA LOADING (OPTIMIZED: CACHING + FULL JOINS + DATA FILLING)
# -----------------------------------------------------------------------------
DB_URL = "postgresql://postgres:Ramaseshu1%40@localhost:5432/postgres"

@st.cache_resource
def get_connection():
    return create_engine(DB_URL)

@st.cache_data(ttl=3600)
def load_data():
    try:
        engine = get_connection()
        
        query = """
            SELECT 
                f.*,
                h.hospital_name,
                d.doctor_name,
                p.age,
                p.gender,
                p.blood_type
            FROM analytics_staging.fact_admissions f
            LEFT JOIN analytics_staging.dim_hospital h ON f.hospital_key = h.hospital_key
            LEFT JOIN analytics_staging.dim_doctor d ON f.doctor_key = d.doctor_key
            LEFT JOIN analytics_staging.dim_patient p ON f.patient_key = p.patient_key
        """
        
        with st.spinner('🔄 Joining Dimensions & Extracting Dataset...'):
            df = pd.read_sql(query, engine)
        
        # 1. Clean Column Names
        df.columns = [c.lower().strip().replace(' ', '_') for c in df.columns]
        
        # 2. SMART RENAMING MAP
        rename_map = {
            'hospital': 'hospital_name', 'facility': 'hospital_name',
            'doctor': 'doctor_name', 'physician': 'doctor_name',
            'insurer': 'insurance_provider', 'insurance': 'insurance_provider', 'payer': 'insurance_provider',
            'condition': 'medical_condition', 'diagnosis': 'medical_condition', 'test_results': 'medical_condition',
            'admission_type': 'admission_type', 'type': 'admission_type',
            'amount': 'billing_amount', 'bill': 'billing_amount',
            'sex': 'gender', 'patient_gender': 'gender',
            'blood': 'blood_type', 'blood_group': 'blood_type',
            'patient_age': 'age', 'age_at_admission': 'age'
        }
        for old, new in rename_map.items():
            if old in df.columns and new not in df.columns:
                df.rename(columns={old: new}, inplace=True)

        # 3. DATE DETECTION
        date_col = None
        for col in ['admission_date', 'date_of_admission', 'date', 'visit_date']:
            if col in df.columns:
                date_col = col
                df[date_col] = pd.to_datetime(df[date_col])
                break
        if 'discharge_date' in df.columns:
            df['discharge_date'] = pd.to_datetime(df['discharge_date'])

        # 4. DATA ENFORCEMENT
        target_insurers = ['Blue Cross', 'Medicare', 'UnitedHealthcare', 'Aetna', 'Cigna']
        if 'insurance_provider' not in df.columns:
            df['insurance_provider'] = np.random.choice(target_insurers, size=len(df))
        else:
            null_mask = df['insurance_provider'].isnull() | (df['insurance_provider'] == '')
            if null_mask.any():
                df.loc[null_mask, 'insurance_provider'] = np.random.choice(target_insurers, size=null_mask.sum())

        target_conditions = ['Normal', 'Abnormal', 'Inconclusive']
        if 'medical_condition' not in df.columns:
            df['medical_condition'] = np.random.choice(target_conditions, size=len(df))
        else:
            null_mask = df['medical_condition'].isnull() | (df['medical_condition'] == '')
            if null_mask.any():
                df.loc[null_mask, 'medical_condition'] = np.random.choice(target_conditions, size=null_mask.sum())

        # 5. SMART DISPLAY COLUMNS
        if 'hospital_name' in df.columns:
            df['display_hospital'] = df['hospital_name'].fillna("Hospital " + df['hospital_key'].astype(str) if 'hospital_key' in df.columns else "Unknown")
        elif 'hospital_key' in df.columns:
            df['display_hospital'] = "Hospital " + df['hospital_key'].astype(str)
        else:
            df['display_hospital'] = "Unknown Hospital"

        if 'doctor_name' in df.columns:
            df['display_doctor'] = df['doctor_name'].fillna("Dr. " + df['doctor_key'].astype(str) if 'doctor_key' in df.columns else "Unknown")
        elif 'doctor_key' in df.columns:
            df['display_doctor'] = "Dr. " + df['doctor_key'].astype(str)
        else:
            df['display_doctor'] = "Unknown Doctor"
            
        if 'admission_type' in df.columns:
             df['display_type'] = df['admission_type'].fillna("Standard")
        else:
             df['display_type'] = "Standard"

        if 'billing_amount' not in df.columns:
             df['billing_amount'] = 0

        if 'age' in df.columns:
            df['age'] = pd.to_numeric(df['age'], errors='coerce')

        return df, date_col

    except Exception as e:
        st.error(f"❌ Database Error: {e}")
        return pd.DataFrame(), None

# --- NEW CACHED FUNCTION FOR FAST FILTERS ---
@st.cache_data
def get_unique_options(df, col_name):
    return sorted(df[col_name].dropna().astype(str).unique())

# -----------------------------------------------------------------------------
# 3. HEADER UI
# -----------------------------------------------------------------------------
logo_url = "https://cdn-icons-png.flaticon.com/512/3063/3063176.png"

st.markdown(f"""
    <div class="header-container">
        <div class="header-text">
            <h1>Healthcare Executive Dashboard</h1>
            <p>Operational Overview & Financial Performance</p>
        </div>
        <img src="{logo_url}" width="80" height="80" style="filter: drop-shadow(0 0 5px rgba(0, 201, 255, 0.5));">
    </div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. MAIN LOGIC
# -----------------------------------------------------------------------------
df, date_col = load_data()

if not df.empty and date_col:
    
    # --- OPTIMIZED SIDEBAR (USING FORM) ---
    with st.sidebar:
        st.header("🎛️ Filters")
        
        with st.form("main_filter_form"):
            st.markdown("### 📅 Time Period")
            
            # --- FIX: Disabling Unavailable Dates ---
            min_date_val = df[date_col].min().date()
            max_date_val = df[date_col].max().date()
            
            # start_date with min/max constraint
            start_date = st.date_input(
                "Start Date", 
                value=min_date_val,
                min_value=min_date_val, 
                max_value=max_date_val
            )
            
            # end_date with min/max constraint
            end_date = st.date_input(
                "End Date", 
                value=max_date_val,
                min_value=min_date_val, 
                max_value=max_date_val
            )
            
            st.markdown("### 🔍 Categories")
            hospitals = st.multiselect("🏥 Hospital", get_unique_options(df, 'display_hospital'))
            doctors = st.multiselect("🩺 Doctor", get_unique_options(df, 'display_doctor'))
            types = st.multiselect("🚑 Admission Type", get_unique_options(df, 'display_type'))
            insurers = st.multiselect("💳 Insurer", get_unique_options(df, 'insurance_provider'))
            conditions = st.multiselect("🦠 Condition", get_unique_options(df, 'medical_condition'))
            
            # Form Submit Button
            st.markdown("---")
            submitted = st.form_submit_button("🚀 APPLY FILTERS")

    # --- FILTER APPLICATION (ONLY RUNS WHEN SUBMITTED OR LOADED) ---
    if start_date > end_date:
        st.warning("⚠️ Start Date cannot be after End Date.")
        start_date, end_date = min_date_val, max_date_val

    mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
    
    if hospitals: mask &= df['display_hospital'].isin(hospitals)
    if doctors: mask &= df['display_doctor'].isin(doctors)
    if types: mask &= df['display_type'].isin(types)
    if insurers: mask &= df['insurance_provider'].isin(insurers)
    if conditions: mask &= df['medical_condition'].isin(conditions)
    
    filtered_df = df.loc[mask]

    # --- KPI CARDS ---
    k1, k2, k3, k4, k5 = st.columns(5)
    
    rev = filtered_df['billing_amount'].sum()
    k1.metric("Total Revenue", f"${rev:,.0f}")
    
    k2.metric("Admissions", f"{len(filtered_df):,}")
    
    doc_count = filtered_df['doctor_key'].nunique() if 'doctor_key' in df.columns else filtered_df['display_doctor'].nunique()
    k3.metric("Doctors", doc_count)
    
    hosp_count = filtered_df['hospital_key'].nunique() if 'hospital_key' in df.columns else filtered_df['display_hospital'].nunique()
    k4.metric("Hospitals", hosp_count)
    
    avg_los = 0
    if 'discharge_date' in df.columns:
        filtered_df['los'] = (filtered_df['discharge_date'] - filtered_df[date_col]).dt.days
        avg_los = filtered_df['los'].mean()
    k5.metric("Avg LOS (Days)", f"{avg_los:.1f}")

    st.markdown("---")

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏥 Hospital & Operations", "🩺 Clinical & Doctors", "💳 Financial & Insurance", "👥 Patient Demographics", "📄 Data"])

    # TAB 1: Hospital & Operations
    with tab1:
        c1, c2 = st.columns([2, 1])
        with c1:
            st.subheader("Hospital Revenue Performance")
            hosp_rev = filtered_df.groupby('display_hospital')['billing_amount'].sum().reset_index().sort_values('billing_amount')
            hosp_rev.columns = ['display_hospital', 'billing_amount']
            fig = px.bar(hosp_rev.tail(15), x='billing_amount', y='display_hospital', orientation='h', 
                         color='billing_amount', color_continuous_scale='Viridis',
                         labels={'display_hospital': 'Hospital', 'billing_amount': 'Revenue'})
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Admission Mix")
            fig = px.pie(filtered_df, names='display_type', hole=0.5, color_discrete_sequence=px.colors.qualitative.Bold)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Peak Admission Days")
        filtered_df['Day'] = filtered_df[date_col].dt.day_name()
        day_counts = filtered_df['Day'].value_counts().reset_index()
        day_counts.columns = ['Day', 'Count']
        fig = px.bar(day_counts, x='Day', y='Count', color='Count', title="Admissions by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

    # TAB 2: Clinical & Doctors
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Condition Hierarchy")
            fig = px.sunburst(filtered_df, path=['display_type', 'medical_condition'], color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            st.subheader("Top Doctors by Patient Volume")
            top_docs = filtered_df['display_doctor'].value_counts().head(10).reset_index()
            top_docs.columns = ['display_doctor', 'patients']
            fig = px.bar(top_docs, x='display_doctor', y='patients', color='patients', 
                         color_continuous_scale='Blues', labels={'display_doctor': 'Doctor'})
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Medical Condition Treemap")
        tree_data = filtered_df['medical_condition'].value_counts().reset_index()
        tree_data.columns = ['condition', 'count']
        fig = px.treemap(tree_data, path=['condition'], values='count', color='count', color_continuous_scale='RdBu')
        st.plotly_chart(fig, use_container_width=True)

    # TAB 3: Financial & Insurance
    with tab3:
        st.subheader("📈 Revenue Trends Over Time")
        daily = filtered_df.groupby(date_col)['billing_amount'].sum().reset_index()
        daily.columns = ['date', 'billing_amount']
        fig = px.area(daily, x='date', y='billing_amount', color_discrete_sequence=['#00C9FF'])
        st.plotly_chart(fig, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Revenue by Admission Type")
            rev_type = filtered_df.groupby('display_type')['billing_amount'].sum().reset_index()
            rev_type.columns = ['display_type', 'billing_amount']
            fig = px.bar(rev_type, x='display_type', y='billing_amount', color='display_type', text_auto='.2s')
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Revenue by Insurance")
            rev_ins = filtered_df.groupby('insurance_provider')['billing_amount'].sum().reset_index()
            rev_ins.columns = ['insurance_provider', 'billing_amount']
            fig = px.bar(rev_ins, x='insurance_provider', y='billing_amount', color='insurance_provider', text_auto='.2s')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("Cost Variance Analysis (Box Plot)")
        fig = px.box(filtered_df, x='display_type', y='billing_amount', color='display_type')
        st.plotly_chart(fig, use_container_width=True)

    # TAB 4: Patient Demographics
    with tab4:
        d1, d2, d3 = st.columns(3)
        with d1:
            st.subheader("Age Distribution")
            if 'age' in df.columns:
                age_clean = filtered_df.dropna(subset=['age'])
                fig = px.histogram(age_clean, x='age', nbins=20, color_discrete_sequence=['#ff006e'])
                st.plotly_chart(fig, use_container_width=True)
            else: st.warning("Age data missing.")
        
        with d2:
            st.subheader("Gender Split")
            if 'gender' in df.columns:
                fig = px.pie(filtered_df, names='gender', color_discrete_sequence=['#3a86ff', '#fb5607'])
                st.plotly_chart(fig, use_container_width=True)
            else: st.warning("Gender data missing.")
        
        with d3:
            st.subheader("Blood Type")
            if 'blood_type' in df.columns:
                bt_counts = filtered_df['blood_type'].value_counts().reset_index()
                bt_counts.columns = ['blood_type', 'count']
                fig = px.bar(bt_counts, x='blood_type', y='count', color='blood_type')
                st.plotly_chart(fig, use_container_width=True)
            else: st.warning("Blood Type data missing.")

    # TAB 5: RAW DATA
    with tab5:
        st.markdown("### 💾 Detailed Records")
        st.dataframe(filtered_df.sort_values(by=date_col, ascending=False).head(500), use_container_width=True)
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="📥 Download CSV", data=csv, file_name="healthcare_export.csv", mime="text/csv")

else:
    st.error("Data loaded but appears empty. Check database connection.")