"""
Unified Financial Forecasting Platform
Combines project-based forecasting with quarterly dashboard capabilities
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from io import BytesIO

# Import engines and processors
from validation_engine import ForecastValidationEngine
from advanced_analytics import AdvancedAnalytics
from data_transformer import DataTransformer
from insights_engine import FinancialInsightsEngine
from pl_processor import PLDataProcessor

# Import tab modules
from advanced_analytics_tab import show_advanced_analytics_tab
from master_assumptions_tab import show_master_assumptions_tab

# Page configuration
st.set_page_config(
    page_title="Financial Forecasting Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 24px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.mode = 'quarterly'  # 'quarterly' or 'project'
    st.session_state.data_loaded = False
    st.session_state.sample_data_loaded = False
    st.session_state.quarterly_data = None
    st.session_state.project_data = None

# Helper functions for quarterly dashboard
def get_fiscal_quarter_info():
    """Return fiscal quarter information (April-March fiscal year)"""
    return {
        'Q1': 'Apr-Jun',
        'Q2': 'Jul-Sep',
        'Q3': 'Oct-Dec',
        'Q4': 'Jan-Mar',
        'FY': 'Full Year'
    }

def create_sample_quarterly_data():
    """Create sample quarterly financial data"""
    line_items = [
        'IYR Live', 'ABR Live*', 'TCV Live*', 'P2 Live*',
        'Revenue', 'Backlog', 'Sell and Bill', 
        'Services Revenue', 'Resale Revenue',
        'Contract Margin', 'Contract Margin%',
        'Services CM', 'Services CM%',
        'Resale CM', 'Resale CM%'
    ]
    
    forecast_data = {
        'Line Item': line_items,
        'Q1': [254.4, 40.3, 70.4, 1.3, 548.3, 548.3, 71.5, 498.1, 50.2, 149.5, 27.3, 144.5, 29.0, 5.0, 9.9],
        'Q2': [256.0, 304.3, 495.1, 0.9, 559.9, 559.9, 71.5, 508.2, 51.8, 156.0, 27.9, 151.0, 29.7, 5.0, 9.7],
        'Q3': [285.3, 605.9, 59.6, 1.1, 566.0, 494.5, 71.5, 511.5, 54.5, 159.1, 28.1, 154.6, 30.2, 4.5, 8.3],
        'Q4': [140.8, 1176.0, 203.3, 0.4, 552.9, 380.9, 172.0, 506.2, 46.7, 158.9, 28.7, 154.4, 30.5, 4.4, 9.5],
        'FY': [1014.5, 2489.3, 1998.4, 0.9, 2227.1, 1983.6, 243.5, 2024.0, 203.2, 623.4, 28.0, 604.5, 29.9, 18.9, 9.3]
    }
    
    budget_data = {
        'Line Item': line_items,
        'Q1': [408.4, 0, 657.7, 0, 565.7, 472.8, 91.0, 513.4, 50.4, 156.3, 29.1, 158.5, 30.9, 5.8, 11.4],
        'Q2': [394.7, 0, 675.6, 0, 574.7, 382.8, 191.9, 523.6, 51.1, 167.1, 29.1, 161.2, 30.8, 5.9, 11.6],
        'Q3': [399.2, 0, 636.4, 0, 594.4, 330.2, 264.2, 532.4, 62.0, 184.7, 31.1, 176.5, 33.2, 8.1, 13.1],
        'Q4': [404.8, 0, 664.5, 0, 590.1, 283.5, 306.6, 539.0, 51.1, 181.2, 30.7, 174.7, 32.4, 6.5, 12.7],
        'FY': [1607.1, 0, 2634.2, 0, 2322.9, 1469.3, 853.6, 2108.4, 214.5, 697.2, 30.0, 670.9, 31.8, 26.3, 12.3]
    }
    
    return pd.DataFrame(forecast_data), pd.DataFrame(budget_data)

def export_to_excel(dataframes_dict):
    """Export multiple dataframes to Excel"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 style="margin: 0;">📊 Financial Forecasting Platform</h1>
    <p style="margin: 0; opacity: 0.9;">Unified Project Forecasting & Quarterly Analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Mode Selection
with st.sidebar:
    st.markdown("## 🎯 Analysis Mode")
    
    mode = st.radio(
        "Select Analysis Type:",
        ["📊 Quarterly Dashboard", "📈 Project Forecasting"],
        key="mode_selector"
    )
    
    if "Quarterly" in mode:
        st.session_state.mode = 'quarterly'
    else:
        st.session_state.mode = 'project'
    
    st.markdown("---")
    
    # Mode-specific options
    if st.session_state.mode == 'quarterly':
        st.markdown("### 📅 Fiscal Year Calendar")
        quarter_info = get_fiscal_quarter_info()
        st.markdown(f"""
        **Q1:** {quarter_info['Q1']} (Apr-Jun)  
        **Q2:** {quarter_info['Q2']} (Jul-Sep)  
        **Q3:** {quarter_info['Q3']} (Oct-Dec)  
        **Q4:** {quarter_info['Q4']} (Jan-Mar)  
        **FY:** April - March
        """)
    else:
        st.markdown("### 📈 Forecasting Options")
        st.markdown("""
        - Project-based forecasting
        - 3 contract types
        - Validation engine
        - Advanced analytics
        """)
    
    st.markdown("---")
    st.markdown("### ℹ️ Platform Info")
    st.markdown(f"""
    **Mode:** {st.session_state.mode.title()}  
    **Status:** ✅ Active  
    **Version:** 2.0 Unified
    """)
    
    if st.button("🔄 Reset All Data"):
        for key in list(st.session_state.keys()):
            if key not in ['initialized', 'mode']:
                del st.session_state[key]
        st.rerun()

# Main Content Area
if st.session_state.mode == 'quarterly':
    # ==================== QUARTERLY DASHBOARD MODE ====================
    
    st.markdown("## 📊 Quarterly Financial Dashboard")
    
    # Filters
    col1, col2, col3, col4 = st.columns([2, 2, 3, 5])
    
    with col1:
        version = st.selectbox("Version", ["Current Forecast", "Prior Forecast", "Budget"])
    
    with col2:
        fiscal_year = st.selectbox("Fiscal Year", ["FY2026", "FY2025", "FY2024"])
    
    with col3:
        units = st.selectbox("Units", ["Millions", "Thousands", "Dollars"])
    
    with col4:
        if st.button("📥 Load Sample Data", type="primary"):
            st.session_state.sample_data_loaded = True
            st.rerun()
    
    st.markdown("---")
    
    # File upload
    uploaded_file = st.file_uploader("📁 Upload Your Data (CSV or Excel)", type=['csv', 'xlsx'])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                preview_df = pd.read_csv(uploaded_file)
            else:
                preview_df = pd.read_excel(uploaded_file)
            
            with st.expander("📋 Preview Uploaded Data", expanded=True):
                st.dataframe(preview_df.head(10), use_container_width=True)
                st.info(f"📊 File contains {len(preview_df)} rows and {len(preview_df.columns)} columns")
            
            # Check if transformation needed
            has_quarters = any(col in preview_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY'])
            
            if not has_quarters:
                st.warning("⚠️ Transaction-level data detected. Transform to quarterly format:")
                
                transformer = DataTransformer()
                date_cols = transformer.detect_date_columns(preview_df)
                value_cols = transformer.detect_value_columns(preview_df)
                group_cols = preview_df.select_dtypes(include=['object']).columns.tolist()
                
                trans_col1, trans_col2, trans_col3 = st.columns(3)
                
                with trans_col1:
                    selected_date_col = st.selectbox("📅 Date Column", date_cols if date_cols else preview_df.columns.tolist())
                
                with trans_col2:
                    selected_value_col = st.selectbox("💰 Value Column", value_cols if value_cols else preview_df.columns.tolist())
                
                with trans_col3:
                    selected_group_col = st.selectbox("📊 Group By", ['None'] + group_cols)
                
                if st.button("🔄 Transform to Quarterly", type="primary"):
                    with st.spinner("Transforming..."):
                        if selected_group_col == 'None':
                            transformed_df = transformer.transform_to_quarterly(
                                preview_df, selected_date_col, selected_value_col
                            )
                        else:
                            transformed_df = transformer.create_detailed_quarterly_view(
                                preview_df, selected_date_col, selected_group_col
                            )
                        
                        st.session_state.quarterly_data = transformed_df
                        st.session_state.data_loaded = True
                        st.success("✅ Transformation complete!")
                        st.rerun()
            else:
                if st.button("📤 Load Quarterly Data", type="primary"):
                    st.session_state.quarterly_data = preview_df
                    st.session_state.data_loaded = True
                    st.success("✅ Data loaded!")
                    st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error: {e}")
    
    # Display quarterly dashboard
    if st.session_state.sample_data_loaded or st.session_state.data_loaded:
        st.markdown("---")
        
        if st.session_state.sample_data_loaded:
            forecast_df, budget_df = create_sample_quarterly_data()
        else:
            forecast_df = st.session_state.quarterly_data
            budget_df = forecast_df.copy()  # Placeholder
        
        # Show fiscal quarter info
        quarter_info = get_fiscal_quarter_info()
        st.info(f"📅 **Fiscal Year Calendar:** Q1: {quarter_info['Q1']} | Q2: {quarter_info['Q2']} | Q3: {quarter_info['Q3']} | Q4: {quarter_info['Q4']}")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "📈 Visualizations", "🤖 AI Insights", "💾 Export"])
        
        with tab1:
            st.markdown("### 📋 Financial Data")
            
            col_a, col_b = st.columns([1, 1])
            
            with col_a:
                st.markdown("#### Current Forecast")
                st.dataframe(forecast_df, use_container_width=True, height=500)
            
            with col_b:
                st.markdown("#### Budget")
                st.dataframe(budget_df, use_container_width=True, height=500)
            
            # Key metrics
            st.markdown("---")
            st.markdown("### 📈 Key Metrics")
            
            metric_cols = st.columns(5)
            
            if 'FY' in forecast_df.columns and len(forecast_df) > 4:
                with metric_cols[0]:
                    st.metric("FY Revenue", f"${forecast_df['FY'].iloc[4]:,.1f}M")
                with metric_cols[1]:
                    st.metric("Contract Margin", f"${forecast_df['FY'].iloc[9]:,.1f}M")
                with metric_cols[2]:
                    st.metric("Margin %", f"{forecast_df['FY'].iloc[10]:.1f}%")
                with metric_cols[3]:
                    st.metric("Services CM", f"${forecast_df['FY'].iloc[11]:,.1f}M")
                with metric_cols[4]:
                    st.metric("Services CM%", f"{forecast_df['FY'].iloc[12]:.1f}%")
        
        with tab2:
            st.markdown("### 📊 Quarterly Visualizations")
            
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                st.markdown("#### Revenue by Quarter")
                
                if all(q in forecast_df.columns for q in ['Q1', 'Q2', 'Q3', 'Q4']) and len(forecast_df) > 4:
                    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                    revenue_values = [forecast_df[q].iloc[4] for q in quarters]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=quarters,
                        y=revenue_values,
                        marker_color='#667eea',
                        text=[f'${v:,.1f}M' for v in revenue_values],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        height=400,
                        xaxis_title="Quarter (Fiscal Year: Apr-Mar)",
                        yaxis_title="Revenue ($M)",
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            with viz_col2:
                st.markdown("#### Margin Trend")
                
                if all(q in forecast_df.columns for q in ['Q1', 'Q2', 'Q3', 'Q4']) and len(forecast_df) > 10:
                    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
                    margin_values = [forecast_df[q].iloc[10] for q in quarters]
                    
                    fig2 = go.Figure()
                    fig2.add_trace(go.Scatter(
                        x=quarters,
                        y=margin_values,
                        mode='lines+markers',
                        line=dict(color='#764ba2', width=3),
                        marker=dict(size=10)
                    ))
                    
                    fig2.update_layout(
                        height=400,
                        xaxis_title="Quarter",
                        yaxis_title="Margin %",
                        yaxis=dict(ticksuffix='%'),
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig2, use_container_width=True)
        
        with tab3:
            st.markdown("### 🤖 AI-Powered Insights")
            
            insights_engine = FinancialInsightsEngine()
            insights = insights_engine.analyze_quarterly_data(forecast_df)
            
            insight_col1, insight_col2 = st.columns(2)
            
            with insight_col1:
                st.markdown("#### 📈 Revenue Insights")
                if insights['revenue_insights']:
                    for insight in insights['revenue_insights']:
                        if insight['type'] == 'positive':
                            st.success(f"✅ {insight['message']}")
                        elif insight['type'] == 'warning':
                            st.warning(f"⚠️ {insight['message']}")
                        else:
                            st.info(f"ℹ️ {insight['message']}")
                else:
                    st.info("No significant revenue insights")
            
            with insight_col2:
                st.markdown("#### 💰 Margin Insights")
                if insights['margin_insights']:
                    for insight in insights['margin_insights']:
                        if insight['type'] == 'positive':
                            st.success(f"✅ {insight['message']}")
                        elif insight['type'] == 'warning':
                            st.warning(f"⚠️ {insight['message']}")
                        else:
                            st.info(f"ℹ️ {insight['message']}")
                else:
                    st.info("No significant margin insights")
            
            if insights['recommendations']:
                st.markdown("---")
                st.markdown("#### ⚠️ Recommendations")
                for rec in insights['recommendations']:
                    priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡"
                    with st.expander(f"{priority_emoji} {rec['category']}: {rec['action']}", expanded=(rec['priority']=='high')):
                        st.markdown(f"**Priority:** {rec['priority'].upper()}")
                        st.markdown(f"**Reason:** {rec['reason']}")
                        st.markdown(f"**Action:** {rec['action']}")
        
        with tab4:
            st.markdown("### 💾 Export Options")
            
            export_col1, export_col2, export_col3 = st.columns(3)
            
            with export_col1:
                excel_data = export_to_excel({
                    'Forecast': forecast_df,
                    'Budget': budget_df
                })
                st.download_button(
                    label="📥 Download Excel",
                    data=excel_data,
                    file_name=f"financial_dashboard_{fiscal_year}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with export_col2:
                csv_data = forecast_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"forecast_{fiscal_year}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with export_col3:
                st.info("💡 Export includes all quarterly data and can be opened in Excel or other tools")

else:
    # ==================== PROJECT FORECASTING MODE ====================
    
    st.markdown("## 📈 Project-Based Forecasting")
    
    # Import and display project forecasting interface
    st.info("🚧 Project forecasting interface will be integrated here")
    st.markdown("""
    ### Available Features:
    - **Project Overview**: Portfolio metrics and status
    - **AI Forecasting**: 3-month revenue predictions
    - **Validation Engine**: Business rule compliance
    - **Advanced Analytics**: Trend analysis and insights
    - **Master Assumptions**: Configurable parameters
    
    **Coming Soon:** Full integration with quarterly dashboard data
    """)
    
    # Placeholder tabs for project mode
    proj_tab1, proj_tab2, proj_tab3 = st.tabs(["📊 Overview", "🤖 Forecasting", "✅ Validation"])
    
    with proj_tab1:
        st.markdown("### Project Portfolio Overview")
        st.info("Load project data to see portfolio metrics")
    
    with proj_tab2:
        st.markdown("### AI-Powered Forecasting")
        st.info("Generate forecasts for individual projects")
    
    with proj_tab3:
        st.markdown("### Validation & Quality Checks")
        st.info("Run validation rules on project data")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6; padding: 1rem;">
    <p>Financial Forecasting Platform v2.0 | Unified Dashboard | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
