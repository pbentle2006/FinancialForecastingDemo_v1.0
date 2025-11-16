import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# CRITICAL: Set page config FIRST
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize session state ONCE
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.data_loaded = False

st.title("📊 Financial Forecast Dashboard")

# Filters at the top
col1, col2, col3 = st.columns([2, 2, 3])
with col1:
    version = st.selectbox("Version", ["Current Forecast", "Prior Forecast", "Budget"])
with col2:
    fiscal_year = st.selectbox("Fiscal Year", ["FY2026", "FY2025", "FY2024"])
with col3:
    units = st.selectbox("Units", ["Millions", "Thousands", "Dollars"])

st.markdown("---")

# Simple file upload without complex processing
uploaded_file = st.file_uploader("Upload CSV or Excel", type=['csv', 'xlsx'])

if uploaded_file and not st.session_state.data_loaded:
    try:
        # Read file ONCE
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Store in session state
        st.session_state.df = df
        st.session_state.data_loaded = True
        st.success(f"✅ Loaded {len(df)} rows")
        
    except Exception as e:
        st.error(f"Error: {e}")

# Display data if loaded
if st.session_state.data_loaded:
    df = st.session_state.df
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Data", "📈 Charts", "📋 Summary"])
    
    with tab1:
        st.dataframe(df, use_container_width=True)
    
    with tab2:
        # Simple chart - no complex processing
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                x_col = st.selectbox("X-axis", df.columns)
            with col2:
                y_col = st.selectbox("Y-axis", numeric_cols)
            
            if st.button("Generate Chart"):
                fig = px.bar(df.head(20), x=x_col, y=y_col)
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.write("### Data Summary")
        st.write(f"**Rows:** {len(df)}")
        st.write(f"**Columns:** {len(df.columns)}")
        st.write("**Column Types:**")
        st.write(df.dtypes)
    
    # Reset button
    if st.button("🔄 Upload New File"):
        st.session_state.data_loaded = False
        st.rerun()
