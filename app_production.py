"""
Financial Forecasting Platform - Production Version
Three-layer architecture: Data Foundation → Forecasting Engine → Reporting
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Import Layer 1: Data Foundation
from column_mapper import ColumnMapper
from data_validation_engine import DataValidationEngine

# Import Layer 2: Forecasting Engine
from management_information_view import ManagementInformationView
from dynamic_reporting_view import DynamicReportingView
from scenario_manager import ScenarioManager

# Import new revenue forecasting components
from revenue_forecasting_dashboard import RevenueForecastingDashboard

# Import existing components
from data_transformer import DataTransformer

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
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .layer-header {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0px 0px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'workflow_stage' not in st.session_state:
    st.session_state.workflow_stage = 'upload'  # upload, validate, forecast, report

if 'uploaded_df' not in st.session_state:
    st.session_state.uploaded_df = None

if 'mapped_df' not in st.session_state:
    st.session_state.mapped_df = None

if 'validated_df' not in st.session_state:
    st.session_state.validated_df = None

if 'validation_results' not in st.session_state:
    st.session_state.validation_results = None

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 style="margin: 0;">📊 Financial Forecasting Platform</h1>
    <p style="margin: 0; opacity: 0.9;">Three-Layer Architecture: Upload → Forecast → Report</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Navigation and Status
with st.sidebar:
    st.markdown("## 🎯 Workflow Progress")
    
    # Progress indicator
    stages = {
        'upload': '📥 Upload & Map',
        'validate': '✓ Validate',
        'mi': '📊 Management Information',
        'forecast': '🎯 Scenario Planning',
        'report': '📈 Report'
    }
    
    current_stage = st.session_state.workflow_stage
    
    for stage_key, stage_label in stages.items():
        if stage_key == current_stage:
            st.markdown(f"**→ {stage_label}** ⏳")
        elif list(stages.keys()).index(stage_key) < list(stages.keys()).index(current_stage):
            st.markdown(f"✅ {stage_label}")
        else:
            st.markdown(f"⚪ {stage_label}")
    
    st.markdown("---")
    
    # Data status
    st.markdown("## 📊 Data Status")
    
    if st.session_state.uploaded_df is not None:
        st.success(f"✓ Data uploaded ({len(st.session_state.uploaded_df)} rows)")
    else:
        st.info("No data uploaded")
    
    if st.session_state.mapped_df is not None:
        st.success("✓ Columns mapped")
    else:
        st.info("Columns not mapped")
    
    if st.session_state.validated_df is not None:
        st.success("✓ Data validated")
    else:
        st.info("Data not validated")
    
    st.markdown("---")
    
    # Quick actions
    st.markdown("## ⚡ Quick Actions")
    
    if st.button("🔄 Reset All", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key not in ['scenarios', 'active_scenario']:
                del st.session_state[key]
        st.session_state.workflow_stage = 'upload'
        st.rerun()
    
    if st.session_state.validated_df is not None:
        if st.button("⏭️ Skip to Forecasting", use_container_width=True):
            st.session_state.workflow_stage = 'forecast'
            st.rerun()
    
    st.markdown("---")
    st.markdown("### ℹ️ Platform Info")
    st.markdown("""
    **Version:** 2.0 Production  
    **Status:** ✅ Active  
    **Layers:** 2 of 3 Complete
    """)

# Main Content Area
# ==================== LAYER 1: DATA FOUNDATION ====================

if st.session_state.workflow_stage == 'upload':
    st.markdown('<div class="layer-header"><h2>📥 Layer 1: Data Foundation - Upload & Map</h2></div>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload your financial data and map columns to the required fields. 
    The system will auto-detect column mappings with high accuracy.
    """)
    
    # File upload
    uploaded_file = st.file_uploader(
        "📁 Upload Your Data (CSV or Excel)",
        type=['csv', 'xlsx', 'xls'],
        help="Upload transaction-level or quarterly financial data"
    )
    
    if uploaded_file:
        try:
            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.uploaded_df = df
            
            # Show preview
            with st.expander("📋 Data Preview", expanded=True):
                st.dataframe(df.head(10), use_container_width=True)
                st.info(f"📊 Loaded {len(df)} rows and {len(df.columns)} columns")
            
            st.markdown("---")
            
            # Column Mapping
            mapper = ColumnMapper()
            validated = mapper.render_mapping_interface(df)
            
            if validated:
                # Get mapped dataframe
                mapped_df, mapping_info = mapper.get_mapped_dataframe(df)
                st.session_state.mapped_df = mapped_df
                st.session_state.mapping_info = mapping_info
                
                # Automatically proceed to validation
                st.session_state.workflow_stage = 'validate'
                st.rerun()
        
        except Exception as e:
            st.error(f"❌ Error loading file: {e}")
            st.info("💡 Please ensure your file is a valid CSV or Excel file")
    
    else:
        st.info("👆 Upload a file to get started")
        
        # Sample data option
        st.markdown("---")
        st.markdown("### 📦 Or Try Sample Data")
        
        if st.button("📥 Load Sample Transaction Data", use_container_width=True):
            # Create sample data matching CRM structure
            sample_data = {
                'Account Name': ['Acme Corp', 'TechStart Inc', 'Global Bank', 'HealthCo', 'Retail Giant'],
                'Opportunity ID': ['OPP-001', 'OPP-002', 'OPP-003', 'OPP-004', 'OPP-005'],
                'Opportunity Name': ['Enterprise Platform Deal', 'Cloud Migration', 'Digital Transform', 'AI Solution', 'Data Analytics'],
                'Master Period': ['FY26-Q2', 'FY26-Q2', 'FY26-Q3', 'FY26-Q3', 'FY26-Q4'],
                'Close Date': ['2025-12-15', '2025-11-30', '2026-02-28', '2026-01-15', '2026-03-31'],
                'Industry Vertical': ['Banking', 'Technology', 'Banking', 'Healthcare', 'Retail'],
                'Product Name': ['Platform Suite', 'Cloud Services', 'Consulting', 'AI Platform', 'Analytics'],
                'Revenue TCV USD': [2500000, 1200000, 3000000, 1800000, 950000],
                'IYR USD': [1000000, 600000, 1200000, 900000, 475000],
                'Margin USD': [750000, 360000, 900000, 540000, 285000]
            }
            df = pd.DataFrame(sample_data)
            st.session_state.uploaded_df = df
            st.success("✅ Sample CRM data loaded!")
            st.rerun()

elif st.session_state.workflow_stage == 'validate':
    st.markdown('<div class="layer-header"><h2>✓ Layer 1: Data Foundation - Validate & Reconcile</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.mapped_df is None:
        st.warning("⚠️ No mapped data available. Please complete the upload and mapping step first.")
        if st.button("← Back to Upload"):
            st.session_state.workflow_stage = 'upload'
            st.rerun()
    else:
        mapped_df = st.session_state.mapped_df
        
        st.markdown("""
        Running comprehensive validation checks on your data including:
        - Data quality checks (missing values, data types, ranges)
        - Reconciliation checks (totals, cross-calculations)
        - Logical consistency checks
        """)
        
        st.markdown("---")
        
        # Data Summary Section
        validator = DataValidationEngine()
        validator.render_data_summary(mapped_df)
        
        st.markdown("---")
        
        # Run validation
        # Determine data type
        has_quarters = all(col in mapped_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY'])
        data_type = 'quarterly' if has_quarters else 'transaction'
        
        with st.spinner("🔍 Validating data..."):
            results = validator.validate_data(mapped_df, data_type=data_type)
        
        st.session_state.validation_results = results
        
        # Display results
        validator.render_validation_results(results, mapped_df)
        
        # Auto-fix option
        if results['auto_fixes']:
            st.markdown("---")
            st.markdown("### 🔧 Auto-Fix Available")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if st.button("✨ Apply Auto-Fixes", type="primary", use_container_width=True):
                    fixed_df = validator.apply_auto_fixes(mapped_df, results['auto_fixes'])
                    st.session_state.mapped_df = fixed_df
                    st.success(f"✅ Applied {len(results['auto_fixes'])} fixes!")
                    st.rerun()
            
            with col2:
                st.info(f"💡 {len(results['auto_fixes'])} issues can be automatically fixed")
        
        # Navigation
        st.markdown("---")
        
        nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
        
        with nav_col1:
            if st.button("← Back to Mapping", use_container_width=True):
                st.session_state.workflow_stage = 'upload'
                st.rerun()
        
        with nav_col2:
            # Allow proceeding even with warnings
            if results['score'] >= 50:
                if st.button("➡️ Proceed to MI", type="primary", use_container_width=True):
                    st.session_state.validated_df = mapped_df
                    st.session_state.workflow_stage = 'mi'
                    st.rerun()
            else:
                st.error("❌ Data quality too low. Please fix errors first.")

# ==================== LAYER 2: MANAGEMENT INFORMATION ====================

elif st.session_state.workflow_stage == 'mi':
    st.markdown('<div class="layer-header"><h2>📊 Management Information</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.validated_df is None:
        st.warning("⚠️ No validated data available. Please complete validation first.")
        if st.button("← Back to Validation"):
            st.session_state.workflow_stage = 'validate'
            st.rerun()
    else:
        # Initialize MI view
        mi_view = ManagementInformationView()
        
        # Render MI view
        mi_view.render_mi_view(st.session_state.validated_df)
        
        # Navigation
        st.markdown("---")
        nav_col1, nav_col2 = st.columns(2)
        
        with nav_col1:
            if st.button("← Back to Validation", use_container_width=True):
                st.session_state.workflow_stage = 'validate'
                st.rerun()
        
        with nav_col2:
            if st.button("➡️ Proceed to Scenario Planning", type="primary", use_container_width=True):
                st.session_state.workflow_stage = 'forecast'
                st.rerun()

# ==================== LAYER 3: SCENARIO PLANNING ====================

elif st.session_state.workflow_stage == 'forecast':
    st.markdown('<div class="layer-header"><h2>🎯 Scenario Planning & Forecasting</h2></div>', unsafe_allow_html=True)
    
    if st.session_state.validated_df is None:
        st.warning("⚠️ No validated data available. Please complete validation first.")
        if st.button("← Back to MI"):
            st.session_state.workflow_stage = 'mi'
            st.rerun()
    else:
        # Initialize components
        scenario_mgr = ScenarioManager()
        dynamic_report = DynamicReportingView()
        sales = SalesView()
        
        # Scenario selector
        st.markdown("### 🎯 Scenario Management")
        active_scenario = scenario_mgr.render_scenario_selector()
        
        # Render dialogs
        scenario_mgr.render_new_scenario_dialog()
        scenario_mgr.render_comparison_view()
        
        st.markdown("---")
        
        # View selector
        view_type = st.radio(
            "Select View",
            ["💰 Revenue Forecasting", "📊 Dynamic Reporting"],
            horizontal=True,
            key="view_selector"
        )
        
        st.markdown("---")
        
        if "Revenue Forecasting" in view_type:
            # Revenue Forecasting View
            validated_df = st.session_state.validated_df
            revenue_dashboard = RevenueForecastingDashboard(validated_df)
            
            # Get assumptions for active scenario
            assumptions = scenario_mgr.get_scenario_assumptions(active_scenario)
            
            if assumptions:
                # Render forecast for current scenario
                forecast_df = revenue_dashboard.render_revenue_forecast_section(active_scenario, assumptions)
                
                # Scenario comparison (if we have multiple scenarios)
                all_scenarios = scenario_mgr.get_scenario_list()
                if len(all_scenarios) > 1:
                    st.markdown("---")
                    
                    # Generate forecasts for all scenarios
                    scenarios_data = {}
                    for scenario in all_scenarios:
                        scenario_assumptions = scenario_mgr.get_scenario_assumptions(scenario)
                        if scenario_assumptions:
                            scenario_forecast = revenue_dashboard.forecaster.forecast_revenue(
                                scenario_assumptions, periods=8, scenario_name=scenario
                            )
                            scenarios_data[scenario] = scenario_forecast
                    
                    if scenarios_data:
                        revenue_dashboard.render_scenario_comparison(scenarios_data)
            else:
                st.warning("No assumptions found for this scenario. Please check scenario configuration.")
        
        elif "Dynamic" in view_type:
            # Dynamic Reporting View
            validated_df = st.session_state.validated_df
            
            # Render dynamic report
            edited_df = dynamic_report.render_dynamic_report(
                validated_df,
                scenario_name=active_scenario,
                editable=True
            )
            
            # Save changes if edited
            if edited_df is not None:
                # Get current dimension selection
                available_dims = dynamic_report.detect_available_dimensions(validated_df)
                if available_dims:
                    selected_dim = st.session_state.get(f"dimension_{active_scenario}", list(available_dims.keys())[0])
                    dynamic_report.set_report_data(edited_df, active_scenario, selected_dim)
        
        # Assumptions editor
        st.markdown("---")
        scenario_mgr.render_assumptions_editor(active_scenario)
        
        # Navigation
        st.markdown("---")
        
        nav_col1, nav_col2 = st.columns([1, 3])
        
        with nav_col1:
            if st.button("← Back to Validation", use_container_width=True):
                st.session_state.workflow_stage = 'validate'
                st.rerun()
        
        with nav_col2:
            st.info("💡 Layer 3 (Reporting & Insights) coming soon! Export and visualization features will be added next.")

# ==================== LAYER 3: REPORTING (Coming Soon) ====================

elif st.session_state.workflow_stage == 'report':
    st.markdown('<div class="layer-header"><h2>📈 Layer 3: Reporting & Insights</h2></div>', unsafe_allow_html=True)
    
    st.info("🚧 **Coming Soon!**")
    
    st.markdown("""
    ### Planned Features:
    
    **Advanced Visualizations:**
    - 📊 Waterfall charts (variance breakdown)
    - 🔥 Heatmaps (performance matrix)
    - 📈 Trend charts with forecasts
    - 🎯 Interactive dashboards
    
    **AI Insights Agent:**
    - 🤖 Natural language queries
    - 💡 Automated insights
    - ⚠️ Recommendations
    - 📊 Mathematical analysis
    
    **Export & Sharing:**
    - 📥 Excel export (formatted)
    - 📄 PDF reports with charts
    - 💾 CSV data exports
    - 🔗 Shareable links
    """)
    
    if st.button("← Back to Forecasting"):
        st.session_state.workflow_stage = 'forecast'
        st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; opacity: 0.6; padding: 1rem;">
    <p>Financial Forecasting Platform v2.0 Production | Three-Layer Architecture | Built with Streamlit</p>
</div>
""", unsafe_allow_html=True)
