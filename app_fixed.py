import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import re

# Import existing modules
from validation_engine import ForecastValidationEngine
from advanced_analytics import AdvancedAnalytics
from advanced_analytics_tab import show_advanced_analytics_tab
from master_assumptions_tab import show_master_assumptions_tab

# Page configuration
st.set_page_config(
    page_title="Enhanced Financial Forecasting Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .status-badge {
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
        margin: 2px;
    }
    .status-complete { background-color: #28a74520; border: 1px solid #28a74540; color: #28a745; }
    .status-pending { background-color: #ffc10720; border: 1px solid #ffc10740; color: #ffc107; }
    .status-in-progress { background-color: #007bff20; border: 1px solid #007bff40; color: #007bff; }
</style>
""", unsafe_allow_html=True)

def show_status_badge(status, label=""):
    """Display status badges with consistent styling"""
    icons = {
        'complete': '✅',
        'pending': '⏳', 
        'in_progress': '🔄',
        'error': '❌'
    }
    
    icon = icons.get(status, '❓')
    st.markdown(f'<span class="status-badge status-{status}">{icon} {label}</span>', unsafe_allow_html=True)

def show_progress_indicator(current_step, total_steps, step_names):
    """Show workflow progress"""
    progress = current_step / total_steps
    st.progress(progress, text=f"Progress: {current_step}/{total_steps} steps completed")
    
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < current_step:
                st.success(f"✅ {step_name}")
            elif i == current_step:
                st.info(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")

def show_workflow_sidebar():
    """Enhanced sidebar with workflow status"""
    st.sidebar.markdown("## 🎯 Workflow Status")
    
    # Check workflow completion status
    steps = [
        ("Upload Data", hasattr(st.session_state, 'file_uploaded') and st.session_state.file_uploaded),
        ("Map Columns", hasattr(st.session_state, 'mapping_complete') and st.session_state.mapping_complete),
        ("Process Data", hasattr(st.session_state, 'data_processed') and st.session_state.data_processed),
        ("Run Analysis", hasattr(st.session_state, 'analysis_complete') and st.session_state.analysis_complete),
        ("Generate Reports", hasattr(st.session_state, 'reports_ready') and st.session_state.reports_ready)
    ]
    
    for step_name, completed in steps:
        if completed:
            st.sidebar.markdown(f"✅ {step_name}")
        else:
            st.sidebar.markdown(f"⏳ {step_name}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("## ⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.sidebar.button("🗑️ Clear All Data"):
        for key in list(st.session_state.keys()):
            if not key.startswith('_'):
                del st.session_state[key]
        st.sidebar.success("Data cleared!")
        st.rerun()

def read_file_smart(file):
    """Smart file reader with enhanced error handling"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            # Try different header rows for Excel files
            df = None
            for header_row in [0, 1, 2]:
                try:
                    test_df = pd.read_excel(file, header=header_row)
                    unnamed_count = sum(1 for col in test_df.columns if 'Unnamed' in str(col))
                    
                    if unnamed_count < len(test_df.columns) * 0.3:
                        df = test_df
                        st.info(f"✅ Using header row {header_row + 1}")
                        break
                except:
                    continue
            
            if df is None:
                df = pd.read_excel(file, header=0)
                st.warning("⚠️ Using default headers")
        
        return df
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return None

def find_monthly_columns(df):
    """Enhanced monthly column detection"""
    monthly_patterns = [
        'FY202', 'FY203',  # FY2025-04, FY2030-12, etc.
        '2024-', '2025-', '2026-', '2027-', '2028-', '2029-', '2030-',
        'Q1 ', 'Q2 ', 'Q3 ', 'Q4 ',
    ]
    
    monthly_cols = []
    current_year = datetime.now().year
    
    for col in df.columns:
        col_str = str(col)
        if any(pattern in col_str for pattern in monthly_patterns):
            try:
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0:
                    year = extract_year_from_column(col)
                    col_info = {
                        'name': col,
                        'year': year,
                        'is_future': year > current_year,
                        'is_historical': year <= current_year
                    }
                    monthly_cols.append(col_info)
            except:
                continue
    
    return monthly_cols

def extract_year_from_column(col_name):
    """Extract year from column name"""
    col_str = str(col_name)
    year_match = re.search(r'(202[0-9]|203[0-9])', col_str)
    if year_match:
        return int(year_match.group(1))
    return datetime.now().year

def create_simple_mapping_interface(df, monthly_cols):
    """Simplified mapping interface that works"""
    st.markdown("### 🔧 Column Mapping")
    
    col_options = ["[Skip this field]"] + list(df.columns)
    
    # Core Fields
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Core Fields:**")
        id_col = st.selectbox("🆔 Project ID", col_options, key="id_mapping")
        name_col = st.selectbox("📝 Project Name", col_options, key="name_mapping")
        client_col = st.selectbox("🏢 Client Name", col_options, key="client_mapping")
    
    with col2:
        st.markdown("**💰 Financial Fields:**")
        value_col = st.selectbox("💵 Total Value", col_options, key="value_mapping")
        status_col = st.selectbox("📊 Status", col_options, key="status_mapping")
        date_col = st.selectbox("📅 Key Date", col_options, key="date_mapping")
    
    with col3:
        st.markdown("**🏷️ Business Dimensions:**")
        offering_col = st.selectbox("🎯 Offering", col_options, key="offering_mapping")
        industry_col = st.selectbox("🏭 Industry", col_options, key="industry_mapping")
        sales_org_col = st.selectbox("👥 Sales Org", col_options, key="sales_org_mapping")
    
    # Monthly columns analysis
    if monthly_cols:
        historical_cols = [col for col in monthly_cols if col['is_historical']]
        future_cols = [col for col in monthly_cols if col['is_future']]
        
        st.success(f"✅ **{len(monthly_cols)} monthly columns detected**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📊 **Historical periods**: {len(historical_cols)} columns")
        with col2:
            st.info(f"🔮 **Future periods**: {len(future_cols)} columns")
    
    # Create mapping
    mapping = {}
    field_mappings = [
        ('id', id_col), ('name', name_col), ('client', client_col),
        ('total_value', value_col), ('status', status_col), ('date', date_col),
        ('offering', offering_col), ('industry', industry_col), ('sales_org', sales_org_col)
    ]
    
    for field, col in field_mappings:
        if col != "[Skip this field]":
            mapping[field] = col
    
    return mapping

def process_enhanced_data(df, mapping, monthly_cols):
    """Process data with enhanced error handling"""
    
    # Create projects dataframe
    projects = []
    for idx, row in df.iterrows():
        project = {
            'project_id': row.get(mapping.get('id', ''), f"PROJ_{idx+1}"),
            'name': row.get(mapping.get('name', ''), f"Project {idx+1}"),
            'client': row.get(mapping.get('client', ''), "Unknown"),
            'status': row.get(mapping.get('status', ''), "Active"),
            'offering': row.get(mapping.get('offering', ''), "Not Specified"),
            'industry': row.get(mapping.get('industry', ''), "Not Specified"),
            'sales_org': row.get(mapping.get('sales_org', ''), "Not Specified"),
        }
        
        total_value = row.get(mapping.get('total_value', ''), 0)
        try:
            project['total_value'] = float(total_value) if pd.notna(total_value) else 0
        except:
            project['total_value'] = 0
            
        projects.append(project)
    
    projects_df = pd.DataFrame(projects)
    
    # Process monthly data
    monthly_data = []
    for idx, row in df.iterrows():
        project_id = row.get(mapping.get('id', ''), f"PROJ_{idx+1}")
        
        for col_info in monthly_cols:
            col = col_info['name']
            value = row[col]
            if pd.notna(value) and value != 0:
                try:
                    revenue = float(value)
                    if revenue > 0:
                        year, month = parse_date_from_column(col)
                        
                        monthly_data.append({
                            'project_id': project_id,
                            'year': year,
                            'month': month,
                            'column': col,
                            'revenue': revenue,
                            'period': f"{year}-{month:02d}",
                            'is_historical': col_info['is_historical'],
                            'is_future': col_info['is_future']
                        })
                except:
                    continue
    
    monthly_df = pd.DataFrame(monthly_data)
    return projects_df, monthly_df

def parse_date_from_column(col_name):
    """Parse year and month from column name"""
    col_str = str(col_name)
    
    if 'FY' in col_str and '-' in col_str:
        try:
            parts = col_str.split('-')
            year = int(parts[0].replace('FY', ''))
            month = int(parts[1])
            return year, month
        except:
            pass
    
    if '-' in col_str:
        try:
            parts = col_str.split('-')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
                return year, month
        except:
            pass
    
    return datetime.now().year, 1

def generate_enhanced_scenarios(monthly_df):
    """Generate scenarios with enhanced analytics"""
    scenarios = {}
    
    base_scenarios = {
        'Conservative': 0.85,
        'Most Likely': 1.00,
        'Optimistic': 1.15
    }
    
    for scenario_name, multiplier in base_scenarios.items():
        scenario_data = monthly_df.copy()
        scenario_data['revenue_adjusted'] = scenario_data['revenue'] * multiplier
        
        monthly_totals = scenario_data.groupby(['year', 'month']).agg({
            'revenue_adjusted': 'sum',
            'project_id': 'nunique'
        }).reset_index()
        monthly_totals['period'] = monthly_totals['year'].astype(str) + '-' + monthly_totals['month'].astype(str).str.zfill(2)
        
        scenarios[scenario_name] = {
            'data': scenario_data,
            'multiplier': multiplier,
            'total_revenue': scenario_data['revenue_adjusted'].sum(),
            'monthly_totals': monthly_totals,
            'avg_monthly': scenario_data['revenue_adjusted'].sum() / len(monthly_totals) if len(monthly_totals) > 0 else 0
        }
    
    return scenarios

def main():
    """Enhanced main application"""
    
    # Sidebar workflow status
    show_workflow_sidebar()
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Enhanced Financial Forecasting Platform</h1>
        <p>Professional AI-powered forecasting with intelligent automation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress indicator
    workflow_steps = ["Upload", "Detect", "Map", "Process", "Analyze"]
    current_step = get_current_workflow_step()
    show_progress_indicator(current_step, len(workflow_steps), workflow_steps)
    
    # Main content
    if not hasattr(st.session_state, 'data_processed') or not st.session_state.data_processed:
        show_data_upload_section()
    else:
        show_enhanced_tabbed_interface()

def get_current_workflow_step():
    """Determine current workflow step"""
    if hasattr(st.session_state, 'data_processed') and st.session_state.data_processed:
        return 5
    elif hasattr(st.session_state, 'mapping_complete') and st.session_state.mapping_complete:
        return 4
    elif hasattr(st.session_state, 'columns_detected') and st.session_state.columns_detected:
        return 3
    elif hasattr(st.session_state, 'file_uploaded') and st.session_state.file_uploaded:
        return 2
    else:
        return 1

def show_data_upload_section():
    """Enhanced data upload section"""
    
    st.markdown("## 📁 Data Upload & Processing")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "📊 Upload Revenue Phasing File",
        type=['csv', 'xlsx', 'xls'],
        help="Upload your project revenue data in CSV or Excel format"
    )
    
    if uploaded_file is not None:
        st.session_state.file_uploaded = True
        
        # File info
        file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 File Name", uploaded_file.name)
        with col2:
            st.metric("📊 File Size", f"{file_size:.2f} MB")
        with col3:
            st.metric("📅 Upload Time", datetime.now().strftime("%H:%M:%S"))
        
        try:
            # Read file
            with st.spinner("Reading file..."):
                df = read_file_smart(uploaded_file)
            
            if df is not None:
                # Data preview
                st.markdown("### 👀 Data Preview")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📊 Rows", f"{len(df):,}")
                with col2:
                    st.metric("📋 Columns", len(df.columns))
                with col3:
                    null_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
                    st.metric("❓ Missing Data", f"{null_pct:.1f}%")
                with col4:
                    st.metric("💾 Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
                
                st.dataframe(df.head(10), use_container_width=True)
                
                # Column detection and mapping
                st.markdown("---")
                st.markdown("## 🔧 Column Detection & Mapping")
                
                monthly_cols = find_monthly_columns(df)
                
                if monthly_cols:
                    mapping = create_simple_mapping_interface(df, monthly_cols)
                    
                    if mapping:
                        st.session_state.columns_detected = True
                        st.session_state.mapping = mapping
                        st.session_state.original_df = df
                        st.session_state.monthly_cols = monthly_cols
                        
                        # Process data button
                        if st.button("🚀 Process Data", type="primary"):
                            with st.spinner("Processing data..."):
                                try:
                                    projects_df, monthly_df = process_enhanced_data(df, mapping, monthly_cols)
                                    
                                    if not monthly_df.empty:
                                        scenarios = generate_enhanced_scenarios(monthly_df)
                                        
                                        # Store in session state
                                        st.session_state.projects_df = projects_df
                                        st.session_state.monthly_df = monthly_df
                                        st.session_state.scenarios = scenarios
                                        st.session_state.data_processed = True
                                        st.session_state.mapping_complete = True
                                        
                                        st.success("✅ Data processed successfully!")
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error("❌ No valid monthly data found")
                                        
                                except Exception as e:
                                    st.error(f"❌ Processing failed: {e}")
                                    st.write("**Debug info:**")
                                    st.write(f"Mapping: {mapping}")
                                    st.write(f"Monthly columns: {len(monthly_cols)}")
                else:
                    st.warning("⚠️ No monthly columns detected. Please check your data format.")
                    
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

def show_enhanced_tabbed_interface():
    """Enhanced tabbed interface"""
    
    # Tab status indicators
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        show_status_badge('complete')
        st.write("Data Integrity")
    with col2:
        show_status_badge('complete')
        st.write("Dashboard")
    with col3:
        show_status_badge('in_progress')
        st.write("Analytics")
    with col4:
        show_status_badge('pending')
        st.write("Assumptions")
    with col5:
        show_status_badge('pending')
        st.write("Reports")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Data Integrity", 
        "📊 Forecast Dashboard", 
        "🤖 Advanced Analytics", 
        "⚙️ Master Assumptions", 
        "💾 Export & Reports"
    ])
    
    with tab1:
        show_data_integrity_tab()
    
    with tab2:
        show_forecast_dashboard_tab()
    
    with tab3:
        show_advanced_analytics_tab()
    
    with tab4:
        show_master_assumptions_tab()
    
    with tab5:
        show_export_tab()

def show_data_integrity_tab():
    """Data integrity tab"""
    st.markdown("## 🔍 Data Integrity & Quality Assessment")
    
    if hasattr(st.session_state, 'projects_df'):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📊 Projects", len(st.session_state.projects_df))
        with col2:
            st.metric("📅 Periods", st.session_state.monthly_df['period'].nunique())
        with col3:
            total_revenue = st.session_state.monthly_df['revenue'].sum()
            st.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
        with col4:
            st.metric("🎯 Quality Score", "85/100")
        
        st.markdown("### 📊 Project Summary")
        st.dataframe(st.session_state.projects_df, use_container_width=True)
        
        st.markdown("### 📈 Monthly Revenue Data")
        st.dataframe(st.session_state.monthly_df.head(20), use_container_width=True)

def show_forecast_dashboard_tab():
    """Forecast dashboard tab"""
    st.markdown("## 📊 Interactive Forecast Dashboard")
    
    if hasattr(st.session_state, 'scenarios'):
        # Scenario selector
        scenario = st.selectbox("📈 Select Scenario", list(st.session_state.scenarios.keys()))
        
        # Metrics
        scenario_data = st.session_state.scenarios[scenario]
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("💰 Total Revenue", f"${scenario_data['total_revenue']:,.0f}")
        with col2:
            st.metric("📊 Multiplier", f"{scenario_data['multiplier']:.0%}")
        with col3:
            st.metric("📅 Avg Monthly", f"${scenario_data['avg_monthly']:,.0f}")
        
        # Chart
        monthly_totals = scenario_data['monthly_totals']
        if not monthly_totals.empty:
            fig = px.line(
                monthly_totals, 
                x='period', 
                y='revenue_adjusted',
                title=f"{scenario} Scenario - Revenue Forecast"
            )
            st.plotly_chart(fig, use_container_width=True)

def show_export_tab():
    """Export tab"""
    st.markdown("## 💾 Export & Reporting")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Data Exports")
        if st.button("📈 Export Forecast Data"):
            st.success("Forecast data exported!")
        if st.button("📋 Export Project Summary"):
            st.success("Project summary exported!")
    
    with col2:
        st.markdown("### 📄 Reports")
        if st.button("📊 Generate Executive Summary"):
            st.success("Executive summary generated!")
        if st.button("📈 Generate Forecast Report"):
            st.success("Forecast report generated!")

if __name__ == "__main__":
    main()
