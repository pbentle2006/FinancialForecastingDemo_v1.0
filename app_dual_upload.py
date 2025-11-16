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
</style>
""", unsafe_allow_html=True)

def show_status_badge(status, label=""):
    """Display status badges"""
    icons = {'complete': '✅', 'pending': '⏳', 'in_progress': '🔄', 'error': '❌'}
    icon = icons.get(status, '❓')
    st.markdown(f'<span class="status-badge status-{status}">{icon} {label}</span>', unsafe_allow_html=True)

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
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = None
            for header_row in [0, 1, 2]:
                try:
                    test_df = pd.read_excel(file, header=header_row)
                    unnamed_count = sum(1 for col in test_df.columns if 'Unnamed' in str(col))
                    if unnamed_count < len(test_df.columns) * 0.3:
                        df = test_df
                        break
                except:
                    continue
            if df is None:
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

def create_forecast_mapping_interface(df, monthly_cols):
    """Create mapping interface for forecast data"""
    st.markdown("### 🔧 Forecast Data Column Mapping")
    
    col_options = ["[Skip this field]"] + list(df.columns)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Core Fields:**")
        id_col = st.selectbox("🆔 Project ID", col_options, key="forecast_id")
        name_col = st.selectbox("📝 Project Name", col_options, key="forecast_name")
        client_col = st.selectbox("🏢 Client", col_options, key="forecast_client")
    
    with col2:
        st.markdown("**💰 Financial Fields:**")
        value_col = st.selectbox("💵 Total Value", col_options, key="forecast_value")
        status_col = st.selectbox("📊 Status", col_options, key="forecast_status")
    
    with col3:
        st.markdown("**🏷️ Business Dimensions:**")
        offering_col = st.selectbox("🎯 Offering", col_options, key="forecast_offering")
        industry_col = st.selectbox("🏭 Industry", col_options, key="forecast_industry")
    
    if monthly_cols:
        st.success(f"✅ **{len(monthly_cols)} monthly columns detected**")
    
    mapping = {}
    for field, col in [('id', id_col), ('name', name_col), ('client', client_col),
                       ('total_value', value_col), ('status', status_col),
                       ('offering', offering_col), ('industry', industry_col)]:
        if col != "[Skip this field]":
            mapping[field] = col
    
    return mapping

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
    """Show dual file upload interface"""
    
    st.markdown("## 📁 Data Upload")
    
    # Create two columns for dual upload
    col1, col2 = st.columns(2)
    
    # FORECAST FILE UPLOAD
    with col1:
        st.markdown('<div class="file-section">', unsafe_allow_html=True)
        st.markdown("### 📊 Forecast Revenue Data")
        st.markdown("*Upload project-based revenue forecast data*")
        
        forecast_file = st.file_uploader(
            "Choose Forecast File",
            type=['csv', 'xlsx', 'xls'],
            key="forecast_uploader",
            help="Upload file with project revenue forecasts"
        )
        
        if forecast_file:
            if st.button("📊 Process Forecast File", key="process_forecast"):
                with st.spinner("Processing forecast data..."):
                    try:
                        df = read_file_smart(forecast_file)
                        if df is not None:
                            st.dataframe(df.head(5), use_container_width=True)
                            
                            monthly_cols = find_monthly_columns(df)
                            if monthly_cols:
                                mapping = create_forecast_mapping_interface(df, monthly_cols)
                                
                                if st.button("✅ Confirm Forecast Mapping", key="confirm_forecast"):
                                    projects_df, monthly_df = process_forecast_data(df, mapping, monthly_cols)
                                    
                                    st.session_state.forecast_projects_df = projects_df
                                    st.session_state.forecast_monthly_df = monthly_df
                                    st.session_state.forecast_processed = True
                                    
                                    st.success("✅ Forecast data processed!")
                                    st.rerun()
                            else:
                                st.warning("No monthly columns detected")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        if hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed:
            st.success("✅ Forecast data loaded")
            st.metric("Projects", len(st.session_state.forecast_projects_df))
            st.metric("Revenue Periods", st.session_state.forecast_monthly_df['period'].nunique())
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # P&L FILE UPLOAD
    with col2:
        st.markdown('<div class="pl-section">', unsafe_allow_html=True)
        st.markdown("### 💰 Profit & Loss Data")
        st.markdown("*Upload P&L statement with actuals*")
        
        pl_file = st.file_uploader(
            "Choose P&L File",
            type=['csv', 'xlsx', 'xls'],
            key="pl_uploader",
            help="Upload P&L file with revenue, costs, and profit data"
        )
        
        if pl_file:
            if st.button("💰 Process P&L File", key="process_pl"):
                with st.spinner("Processing P&L data..."):
                    try:
                        df = read_file_smart(pl_file)
                        if df is not None:
                            st.dataframe(df.head(5), use_container_width=True)
                            
                            pl_processor = PLDataProcessor()
                            detection_results = pl_processor.find_pl_columns(df)
                            
                            mapping, monthly_cols = pl_processor.create_pl_mapping_interface(df, detection_results)
                            
                            if st.button("✅ Confirm P&L Mapping", key="confirm_pl"):
                                pl_df, pl_summary_df = pl_processor.process_pl_data(df, mapping, monthly_cols)
                                
                                st.session_state.pl_df = pl_df
                                st.session_state.pl_summary_df = pl_summary_df
                                st.session_state.pl_processed = True
                                
                                st.success("✅ P&L data processed!")
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        if hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed:
            st.success("✅ P&L data loaded")
            st.metric("Line Items", len(st.session_state.pl_df['line_item'].unique()))
            st.metric("Periods", st.session_state.pl_df['period'].nunique())
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Integration button (only show when both files are processed)
    if (hasattr(st.session_state, 'forecast_processed') and st.session_state.forecast_processed and
        hasattr(st.session_state, 'pl_processed') and st.session_state.pl_processed):
        
        st.markdown("---")
        if st.button("🔗 Integrate & Analyze Data", type="primary", use_container_width=True):
            with st.spinner("Integrating datasets..."):
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
