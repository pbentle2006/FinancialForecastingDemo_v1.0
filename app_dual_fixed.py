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
from pl_processor import PLDataProcessor

# Page configuration
st.set_page_config(
    page_title="Integrated Forecast & P&L Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #2ca02c);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .file-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .pl-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2ca02c;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables"""
    if 'forecast_file_uploaded' not in st.session_state:
        st.session_state.forecast_file_uploaded = False
    if 'pl_file_uploaded' not in st.session_state:
        st.session_state.pl_file_uploaded = False
    if 'forecast_df' not in st.session_state:
        st.session_state.forecast_df = None
    if 'pl_df_raw' not in st.session_state:
        st.session_state.pl_df_raw = None
    if 'forecast_monthly_cols' not in st.session_state:
        st.session_state.forecast_monthly_cols = None
    if 'pl_detection_results' not in st.session_state:
        st.session_state.pl_detection_results = None

def show_workflow_sidebar():
    """Enhanced sidebar with dual file workflow status"""
    st.sidebar.markdown("## 🎯 Workflow Status")
    
    # Forecast file status
    st.sidebar.markdown("### 📊 Forecast Data")
    forecast_uploaded = hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed
    st.sidebar.markdown(f"{'✅' if forecast_uploaded else '⏳'} Forecast File")
    
    # P&L file status
    st.sidebar.markdown("### 💰 P&L Data")
    pl_uploaded = hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed
    st.sidebar.markdown(f"{'✅' if pl_uploaded else '⏳'} P&L File")
    
    # Integration status
    st.sidebar.markdown("### 🔗 Integration")
    integrated = hasattr(st.session_state, 'data_integrated') and st.session_state.data_integrated
    st.sidebar.markdown(f"{'✅' if integrated else '⏳'} Data Aggregation")
    
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
    """Smart file reader"""
    try:
        # Reset file pointer
        file.seek(0)
        
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = None
            for header_row in [0, 1, 2]:
                try:
                    file.seek(0)
                    test_df = pd.read_excel(file, header=header_row)
                    unnamed_count = sum(1 for col in test_df.columns if 'Unnamed' in str(col))
                    if unnamed_count < len(test_df.columns) * 0.3:
                        df = test_df
                        break
                except:
                    continue
            if df is None:
                file.seek(0)
                df = pd.read_excel(file, header=0)
        return df
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return None

def find_monthly_columns(df):
    """Find monthly columns in forecast data"""
    monthly_patterns = ['FY202', 'FY203', '2024-', '2025-', '2026-', '2027-', '2028-', '2029-', '2030-', 'Q1 ', 'Q2 ', 'Q3 ', 'Q4 ']
    monthly_cols = []
    current_year = datetime.now().year
    
    for col in df.columns:
        col_str = str(col)
        if any(pattern in col_str for pattern in monthly_patterns):
            try:
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0:
                    year = extract_year_from_column(col)
                    monthly_cols.append({
                        'name': col,
                        'year': year,
                        'is_future': year > current_year,
                        'is_historical': year <= current_year
                    })
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

def process_forecast_data(df, mapping, monthly_cols):
    """Process forecast data"""
    projects = []
    for idx, row in df.iterrows():
        project = {
            'project_id': row.get(mapping.get('id', ''), f"PROJ_{idx+1}"),
            'name': row.get(mapping.get('name', ''), f"Project {idx+1}"),
            'client': row.get(mapping.get('client', ''), "Unknown"),
            'status': row.get(mapping.get('status', ''), "Active"),
            'offering': row.get(mapping.get('offering', ''), "Not Specified"),
            'industry': row.get(mapping.get('industry', ''), "Not Specified"),
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
    """Parse date from column name"""
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

def main():
    """Main application with dual file upload"""
    
    init_session_state()
    show_workflow_sidebar()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Integrated Forecast & P&L Platform</h1>
        <p>Upload and analyze forecast revenue and P&L data together</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if both files are processed
    both_processed = (hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed and
                     hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed)
    
    if not both_processed:
        show_dual_upload_section()
    else:
        show_integrated_analysis()

def show_dual_upload_section():
    """Show dual file upload interface with fixed state management"""
    
    st.markdown("## 📁 Data Upload & Mapping")
    
    # Create two columns for dual upload
    col1, col2 = st.columns(2)
    
    # ==================== FORECAST FILE SECTION ====================
    with col1:
        st.markdown('<div class="file-section">', unsafe_allow_html=True)
        st.markdown("### 📊 Forecast Revenue Data")
        
        # Step 1: File Upload
        if not st.session_state.forecast_file_uploaded:
            st.markdown("**Step 1: Upload File**")
            forecast_file = st.file_uploader(
                "Choose Forecast File",
                type=['csv', 'xlsx', 'xls'],
                key="forecast_uploader",
                help="Upload file with project revenue forecasts"
            )
            
            if forecast_file:
                with st.spinner("Reading forecast file..."):
                    df = read_file_smart(forecast_file)
                    if df is not None:
                        st.session_state.forecast_df = df
                        st.session_state.forecast_monthly_cols = find_monthly_columns(df)
                        st.session_state.forecast_file_uploaded = True
                        st.success("✅ File uploaded successfully!")
                        st.rerun()
        
        # Step 2: Show Preview and Mapping
        elif st.session_state.forecast_file_uploaded and not hasattr(st.session_state, 'forecast_processed'):
            st.success("✅ File uploaded")
            
            df = st.session_state.forecast_df
            monthly_cols = st.session_state.forecast_monthly_cols
            
            # Data preview
            with st.expander("👀 Data Preview", expanded=False):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Rows", len(df))
                with col_b:
                    st.metric("Columns", len(df.columns))
                with col_c:
                    st.metric("Monthly Cols", len(monthly_cols) if monthly_cols else 0)
                st.dataframe(df.head(10), use_container_width=True)
            
            # Mapping interface
            st.markdown("**Step 2: Map Columns**")
            
            col_options = ["[Skip]"] + list(df.columns)
            
            # Create form to prevent reruns
            with st.form("forecast_mapping_form"):
                map_col1, map_col2 = st.columns(2)
                
                with map_col1:
                    id_col = st.selectbox("🆔 Project ID", col_options, key="f_id")
                    name_col = st.selectbox("📝 Project Name", col_options, key="f_name")
                    client_col = st.selectbox("🏢 Client", col_options, key="f_client")
                    value_col = st.selectbox("💵 Total Value", col_options, key="f_value")
                
                with map_col2:
                    status_col = st.selectbox("📊 Status", col_options, key="f_status")
                    offering_col = st.selectbox("🎯 Offering", col_options, key="f_offering")
                    industry_col = st.selectbox("🏭 Industry", col_options, key="f_industry")
                
                if monthly_cols:
                    st.info(f"✅ Detected {len(monthly_cols)} monthly columns")
                
                submitted = st.form_submit_button("✅ Process Forecast Data", type="primary")
                
                if submitted:
                    # Create mapping
                    mapping = {}
                    for field, col in [('id', id_col), ('name', name_col), ('client', client_col),
                                       ('total_value', value_col), ('status', status_col),
                                       ('offering', offering_col), ('industry', industry_col)]:
                        if col != "[Skip]":
                            mapping[field] = col
                    
                    if mapping and monthly_cols:
                        with st.spinner("Processing forecast data..."):
                            try:
                                projects_df, monthly_df = process_forecast_data(df, mapping, monthly_cols)
                                
                                st.session_state.forecast_projects_df = projects_df
                                st.session_state.forecast_monthly_df = monthly_df
                                st.session_state.forecast_processed = True
                                
                                st.success("✅ Forecast data processed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error processing: {e}")
                    else:
                        st.error("Please map at least the ID column and ensure monthly columns are detected")
            
            # Reset button
            if st.button("🔄 Upload Different File", key="reset_forecast"):
                st.session_state.forecast_file_uploaded = False
                st.session_state.forecast_df = None
                st.session_state.forecast_monthly_cols = None
                st.rerun()
        
        # Step 3: Show completion status
        elif hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed:
            st.success("✅ Forecast data loaded and processed")
            st.metric("Projects", len(st.session_state.forecast_projects_df))
            st.metric("Revenue Periods", st.session_state.forecast_monthly_df['period'].nunique())
            
            if st.button("🔄 Upload New Forecast File", key="new_forecast"):
                st.session_state.forecast_file_uploaded = False
                st.session_state.forecast_processed = False
                st.session_state.forecast_df = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== P&L FILE SECTION ====================
    with col2:
        st.markdown('<div class="pl-section">', unsafe_allow_html=True)
        st.markdown("### 💰 Profit & Loss Data")
        
        # Step 1: File Upload
        if not st.session_state.pl_file_uploaded:
            st.markdown("**Step 1: Upload File**")
            pl_file = st.file_uploader(
                "Choose P&L File",
                type=['csv', 'xlsx', 'xls'],
                key="pl_uploader",
                help="Upload P&L file with revenue, costs, and profit data"
            )
            
            if pl_file:
                with st.spinner("Reading P&L file..."):
                    df = read_file_smart(pl_file)
                    if df is not None:
                        pl_processor = PLDataProcessor()
                        detection_results = pl_processor.find_pl_columns(df)
                        
                        st.session_state.pl_df_raw = df
                        st.session_state.pl_detection_results = detection_results
                        st.session_state.pl_file_uploaded = True
                        st.success("✅ File uploaded successfully!")
                        st.rerun()
        
        # Step 2: Show Preview and Mapping
        elif st.session_state.pl_file_uploaded and not hasattr(st.session_state, 'pl_processed'):
            st.success("✅ File uploaded")
            
            df = st.session_state.pl_df_raw
            detection_results = st.session_state.pl_detection_results
            
            # Data preview
            with st.expander("👀 Data Preview", expanded=False):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("Rows", len(df))
                with col_b:
                    st.metric("Columns", len(df.columns))
                st.dataframe(df.head(10), use_container_width=True)
            
            # Show detected categories
            if detection_results.get('categorized_items'):
                with st.expander("🔍 Detected P&L Categories", expanded=False):
                    for category, items in detection_results['categorized_items'].items():
                        st.markdown(f"**{category.replace('_', ' ').title()}:** {len(items)} items")
            
            # Mapping interface
            st.markdown("**Step 2: Map Columns**")
            
            col_options = ["[Skip]"] + list(df.columns)
            
            # Create form to prevent reruns
            with st.form("pl_mapping_form"):
                line_item_default = detection_results.get('line_item_column', '[Skip]')
                if line_item_default and line_item_default in col_options:
                    default_idx = col_options.index(line_item_default)
                else:
                    default_idx = 0
                
                line_item_col = st.selectbox(
                    "📝 Line Item / Account Name",
                    col_options,
                    index=default_idx,
                    key="pl_line_item"
                )
                
                entity_col = st.selectbox(
                    "🏢 Entity / Department (Optional)",
                    col_options,
                    key="pl_entity"
                )
                
                monthly_cols = detection_results.get('monthly_columns', [])
                if monthly_cols:
                    st.info(f"✅ Detected {len(monthly_cols)} monthly columns")
                
                submitted = st.form_submit_button("✅ Process P&L Data", type="primary")
                
                if submitted:
                    # Create mapping
                    mapping = {
                        'line_item': line_item_col if line_item_col != "[Skip]" else None,
                        'entity': entity_col if entity_col != "[Skip]" else None
                    }
                    
                    if mapping['line_item'] and monthly_cols:
                        with st.spinner("Processing P&L data..."):
                            try:
                                pl_processor = PLDataProcessor()
                                pl_df, pl_summary_df = pl_processor.process_pl_data(df, mapping, monthly_cols)
                                
                                st.session_state.pl_df = pl_df
                                st.session_state.pl_summary_df = pl_summary_df
                                st.session_state.pl_processed = True
                                
                                st.success("✅ P&L data processed!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error processing: {e}")
                    else:
                        st.error("Please map the line item column and ensure monthly columns are detected")
            
            # Reset button
            if st.button("🔄 Upload Different File", key="reset_pl"):
                st.session_state.pl_file_uploaded = False
                st.session_state.pl_df_raw = None
                st.session_state.pl_detection_results = None
                st.rerun()
        
        # Step 3: Show completion status
        elif hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed:
            st.success("✅ P&L data loaded and processed")
            st.metric("Line Items", len(st.session_state.pl_df['line_item'].unique()))
            st.metric("Periods", st.session_state.pl_df['period'].nunique())
            
            if st.button("🔄 Upload New P&L File", key="new_pl"):
                st.session_state.pl_file_uploaded = False
                st.session_state.pl_processed = False
                st.session_state.pl_df_raw = None
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== INTEGRATION BUTTON ====================
    if (hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed and
        hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed and
        not hasattr(st.session_state, 'data_integrated')):
        
        st.markdown("---")
        st.markdown("## 🔗 Ready to Integrate!")
        
        if st.button("🚀 Integrate & Analyze Data", type="primary", use_container_width=True):
            with st.spinner("Integrating datasets..."):
                try:
                    pl_processor = PLDataProcessor()
                    
                    # Aggregate data
                    combined_df = pl_processor.aggregate_forecast_and_pl(
                        st.session_state.forecast_monthly_df,
                        st.session_state.pl_df
                    )
                    
                    # Generate insights
                    insights = pl_processor.generate_integrated_insights(
                        st.session_state.forecast_monthly_df,
                        st.session_state.pl_df,
                        st.session_state.pl_summary_df
                    )
                    
                    st.session_state.combined_df = combined_df
                    st.session_state.insights = insights
                    st.session_state.data_integrated = True
                    
                    st.success("✅ Data integrated successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Integration error: {e}")

def show_integrated_analysis():
    """Show integrated analysis dashboard"""
    
    st.markdown("## 🔗 Integrated Analysis Dashboard")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Executive Summary",
        "📈 Revenue Analysis", 
        "💰 P&L Analysis",
        "🔍 Variance Analysis",
        "🎯 Forecasting"
    ])
    
    with tab1:
        show_executive_summary()
    
    with tab2:
        show_revenue_analysis()
    
    with tab3:
        show_pl_analysis()
    
    with tab4:
        show_variance_analysis()
    
    with tab5:
        show_integrated_forecasting()

def show_executive_summary():
    """Executive summary with key metrics"""
    st.markdown("### 📊 Executive Summary")
    
    insights = st.session_state.insights
    metrics = insights['summary_metrics']
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Forecast Revenue",
            f"${metrics['total_forecast_revenue']:,.0f}",
            help="Total forecasted revenue from project pipeline"
        )
    
    with col2:
        st.metric(
            "P&L Revenue",
            f"${metrics['total_pl_revenue']:,.0f}",
            help="Actual revenue from P&L statement"
        )
    
    with col3:
        variance = metrics['revenue_variance']
        st.metric(
            "Revenue Variance",
            f"${variance:,.0f}",
            f"{metrics['revenue_variance_%']:.1f}%",
            delta_color="normal"
        )
    
    with col4:
        profitability = insights.get('profitability_analysis', {})
        net_margin = profitability.get('avg_net_margin_%', 0)
        st.metric(
            "Avg Net Margin",
            f"{net_margin:.1f}%",
            help="Average net profit margin from P&L"
        )
    
    # Recommendations
    if insights.get('recommendations'):
        st.markdown("### 💡 Key Recommendations")
        for rec in insights['recommendations']:
            if rec['type'] == 'warning':
                st.warning(f"⚠️ **{rec['message']}**\n\n*Action:* {rec['action']}")
            elif rec['type'] == 'alert':
                st.error(f"🚨 **{rec['message']}**\n\n*Action:* {rec['action']}")
            else:
                st.info(f"ℹ️ **{rec['message']}**\n\n*Action:* {rec['action']}")

def show_revenue_analysis():
    """Revenue analysis from forecast data"""
    st.markdown("### 📈 Revenue Forecast Analysis")
    
    forecast_df = st.session_state.forecast_monthly_df
    
    # Revenue by period chart
    period_revenue = forecast_df.groupby('period')['revenue'].sum().reset_index()
    
    fig = px.bar(
        period_revenue,
        x='period',
        y='revenue',
        title="Forecast Revenue by Period",
        labels={'revenue': 'Revenue ($)', 'period': 'Period'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Project breakdown
    st.markdown("### 📊 Project Revenue Breakdown")
    project_revenue = forecast_df.groupby('project_id')['revenue'].sum().reset_index()
    project_revenue = project_revenue.sort_values('revenue', ascending=False).head(10)
    
    fig2 = px.bar(
        project_revenue,
        x='project_id',
        y='revenue',
        title="Top 10 Projects by Revenue"
    )
    st.plotly_chart(fig2, use_container_width=True)

def show_pl_analysis():
    """P&L analysis"""
    st.markdown("### 💰 Profit & Loss Analysis")
    
    pl_summary = st.session_state.pl_summary_df
    
    if not pl_summary.empty:
        # Display P&L summary table
        st.dataframe(pl_summary, use_container_width=True)
        
        # Margin trends
        if 'gross_margin_%' in pl_summary.columns:
            fig = px.line(
                pl_summary,
                x='period',
                y='gross_margin_%',
                title="Gross Margin Trend",
                labels={'gross_margin_%': 'Gross Margin (%)', 'period': 'Period'}
            )
            st.plotly_chart(fig, use_container_width=True)

def show_variance_analysis():
    """Variance analysis between forecast and P&L"""
    st.markdown("### 🔍 Forecast vs P&L Variance Analysis")
    
    combined_df = st.session_state.combined_df
    
    if not combined_df.empty:
        # Variance chart
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=combined_df['period'],
            y=combined_df['forecast_revenue'],
            name='Forecast Revenue',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            x=combined_df['period'],
            y=combined_df['pl_revenue'],
            name='P&L Revenue',
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title="Forecast vs P&L Revenue Comparison",
            xaxis_title="Period",
            yaxis_title="Revenue ($)",
            barmode='group'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Variance table
        st.markdown("### 📋 Detailed Variance Analysis")
        st.dataframe(combined_df, use_container_width=True)

def show_integrated_forecasting():
    """Integrated forecasting with P&L insights"""
    st.markdown("### 🎯 Integrated Forecasting")
    
    st.info("🚀 **Enhanced Forecasting**: Combining forecast pipeline with P&L actuals for improved accuracy")
    
    # Scenario analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Forecast Scenarios")
        forecast_total = st.session_state.forecast_monthly_df['revenue'].sum()
        
        scenarios = {
            'Conservative (85%)': forecast_total * 0.85,
            'Most Likely (100%)': forecast_total,
            'Optimistic (115%)': forecast_total * 1.15
        }
        
        for scenario, value in scenarios.items():
            st.metric(scenario, f"${value:,.0f}")
    
    with col2:
        st.markdown("#### 💰 P&L-Adjusted Forecast")
        
        # Calculate adjustment based on historical variance
        combined_df = st.session_state.combined_df
        historical = combined_df[combined_df['pl_revenue'] > 0]
        
        if not historical.empty:
            avg_variance = historical['variance_%'].mean()
            adjusted_forecast = forecast_total * (1 + avg_variance/100)
            
            st.metric(
                "P&L-Adjusted Forecast",
                f"${adjusted_forecast:,.0f}",
                f"{avg_variance:.1f}% adjustment"
            )
            
            st.info(f"Based on historical variance of {avg_variance:.1f}% between forecast and P&L actuals")

if __name__ == "__main__":
    main()
