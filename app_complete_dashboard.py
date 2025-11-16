import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import io
from io import BytesIO
from insights_engine import FinancialInsightsEngine
from data_transformer import DataTransformer

# Page configuration
st.set_page_config(
    page_title="Financial Forecast Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1.5rem;
    }
    /* Filter section */
    .filter-section {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    /* Table styling */
    .stDataFrame {
        font-size: 11px;
    }
    /* Metrics */
    .metric-container {
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
    st.session_state.data_loaded = False
    st.session_state.sample_data_loaded = False

def get_fiscal_quarter_info():
    """Return fiscal quarter information (April-March fiscal year)"""
    return {
        'Q1': 'Apr-Jun',
        'Q2': 'Jul-Sep',
        'Q3': 'Oct-Dec',
        'Q4': 'Jan-Mar',
        'FY': 'Full Year'
    }

def create_sample_data():
    """Create sample financial data matching the target dashboard"""
    
    line_items = [
        'IYR Live', 'ABR Live*', 'TCV Live*', 'P2 Live*',
        'Revenue', 'Backlog', 'Sell and Bill', 
        'Services Revenue', 'Resale Revenue',
        'Contract Margin', 'Contract Margin%',
        'Services CM', 'Services CM%',
        'Resale CM', 'Resale CM%'
    ]
    
    # Current Forecast
    forecast_data = {
        'Line Item': line_items,
        'Q1': [254.4, 40.3, 70.4, 1.3, 548.3, 548.3, 71.5, 498.1, 50.2, 149.5, 27.3, 144.5, 29.0, 5.0, 9.9],
        'Q2': [256.0, 304.3, 495.1, 0.9, 559.9, 559.9, 71.5, 508.2, 51.8, 156.0, 27.9, 151.0, 29.7, 5.0, 9.7],
        'Q3': [285.3, 605.9, 59.6, 1.1, 566.0, 494.5, 71.5, 511.5, 54.5, 159.1, 28.1, 154.6, 30.2, 4.5, 8.3],
        'Q4': [140.8, 1176.0, 203.3, 0.4, 552.9, 380.9, 172.0, 506.2, 46.7, 158.9, 28.7, 154.4, 30.5, 4.4, 9.5],
        'FY': [1014.5, 2489.3, 1998.4, 0.9, 2227.1, 1983.6, 243.5, 2024.0, 203.2, 623.4, 28.0, 604.5, 29.9, 18.9, 9.3]
    }
    
    # Prior Forecast (CFvPF)
    cfvpf_data = {
        'Line Item': line_items,
        'Q1': [403.0, 0, 0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Q2': [304.3, 0, 0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Q3': [605.9, 0, 0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'Q4': [1176.0, 0, 0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        'FY': [2489.3, 0, 0, 0, 0.0, 0.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    }
    
    # Budget
    budget_data = {
        'Line Item': line_items,
        'Q1': [408.4, 0, 657.7, 0, 565.7, 472.8, 91.0, 513.4, 50.4, 156.3, 29.1, 158.5, 30.9, 5.8, 11.4],
        'Q2': [394.7, 0, 675.6, 0, 574.7, 382.8, 191.9, 523.6, 51.1, 167.1, 29.1, 161.2, 30.8, 5.9, 11.6],
        'Q3': [399.2, 0, 636.4, 0, 594.4, 330.2, 264.2, 532.4, 62.0, 184.7, 31.1, 176.5, 33.2, 8.1, 13.1],
        'Q4': [404.8, 0, 664.5, 0, 590.1, 283.5, 306.6, 539.0, 51.1, 181.2, 30.7, 174.7, 32.4, 6.5, 12.7],
        'FY': [1607.1, 0, 2634.2, 0, 2322.9, 1469.3, 853.6, 2108.4, 214.5, 697.2, 30.0, 670.9, 31.8, 26.3, 12.3]
    }
    
    # Variance (CFvWB)
    variance_data = {
        'Line Item': line_items,
        'Q1': [-5.4, 0, 46.3, 0, -15.5, 75.5, -91.0, -15.3, -0.2, -14.8, -1.9, -14.0, -1.9, -0.8, -1.5],
        'Q2': [-90.4, 0, -180.4, 0, -14.7, 177.2, -191.9, -15.4, 0.7, -11.1, -1.2, -10.2, -1.1, -0.9, -2.0],
        'Q3': [206.1, 0, -40.4, 0, -28.4, 164.3, -192.7, -20.9, -7.5, -25.6, -3.0, -21.9, -2.9, -3.6, -4.8],
        'Q4': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        'FY': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    }
    
    return (pd.DataFrame(forecast_data), 
            pd.DataFrame(cfvpf_data), 
            pd.DataFrame(budget_data), 
            pd.DataFrame(variance_data))

def export_to_excel(dataframes_dict, filename="financial_dashboard_export.xlsx"):
    """Export multiple dataframes to Excel with multiple sheets"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output

def export_to_csv(df):
    """Export dataframe to CSV"""
    return df.to_csv(index=False).encode('utf-8')

def calculate_variance(forecast_val, budget_val):
    """Calculate variance between forecast and budget"""
    if pd.isna(forecast_val) or pd.isna(budget_val) or budget_val == 0:
        return 0
    return forecast_val - budget_val

def calculate_variance_pct(forecast_val, budget_val):
    """Calculate variance percentage"""
    if pd.isna(forecast_val) or pd.isna(budget_val) or budget_val == 0:
        return 0
    return ((forecast_val - budget_val) / budget_val) * 100

def format_cell(value, row_name):
    """Format cell values based on type"""
    if pd.isna(value) or value == 0:
        return ""
    
    # Percentage rows
    if '%' in row_name:
        return f"{value:.1f}%"
    
    # Negative values
    if value < 0:
        return f"({abs(value):.1f})"
    
    # Regular numbers
    return f"{value:.1f}"

def style_dataframe(df):
    """Apply styling to dataframe"""
    
    def highlight_rows(row):
        if row['Line Item'] in ['Revenue', 'Contract Margin', 'Services CM', 'Resale CM']:
            return ['background-color: #f0f2f6; font-weight: bold'] * len(row)
        elif '%' in row['Line Item']:
            return ['background-color: #e8eaf6; font-style: italic'] * len(row)
        else:
            return [''] * len(row)
    
    def color_negatives(val):
        if isinstance(val, (int, float)) and val < 0:
            return 'color: red'
        return ''
    
    styled = df.style.apply(highlight_rows, axis=1)
    styled = styled.applymap(color_negatives, subset=df.columns[1:])
    
    return styled

# Header
st.markdown("""
<div class="dashboard-header">
    <h1 style="margin: 0;">📊 Financial Forecast Dashboard</h1>
    <p style="margin: 0; opacity: 0.9;">Quarterly Performance Analysis | Fiscal Year: April - March</p>
</div>
""", unsafe_allow_html=True)

# Filters
st.markdown('<div class="filter-section">', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns([2, 2, 3, 5])

with col1:
    version = st.selectbox("Version", ["Current Forecast", "Prior Forecast", "Budget"])

with col2:
    fiscal_year = st.selectbox("Fiscal Year", ["FY2026", "FY2025", "FY2024"])

with col3:
    units = st.selectbox("$M / $K / $ Selection", ["Millions", "Thousands", "Dollars"])

with col4:
    if st.button("📥 Load Sample Data"):
        st.session_state.sample_data_loaded = True
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# File upload option
st.markdown("---")
uploaded_file = st.file_uploader("📁 Upload Your Data (CSV or Excel)", type=['csv', 'xlsx'])

if uploaded_file:
    # Show file preview
    try:
        if uploaded_file.name.endswith('.csv'):
            preview_df = pd.read_csv(uploaded_file)
        else:
            preview_df = pd.read_excel(uploaded_file)
        
        with st.expander("📋 Preview Uploaded Data", expanded=True):
            st.dataframe(preview_df.head(10), use_container_width=True)
            st.info(f"📊 File contains {len(preview_df)} rows and {len(preview_df.columns)} columns")
        
        # Check if data needs transformation
        has_quarters = any(col in preview_df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY'])
        
        if not has_quarters:
            st.warning("⚠️ No quarterly columns detected. This appears to be transaction-level data.")
            st.info("🔄 **Auto-Transform Available:** We can convert your transaction data into quarterly format!")
            
            # Show transformation options
            transformer = DataTransformer()
            date_cols = transformer.detect_date_columns(preview_df)
            value_cols = transformer.detect_value_columns(preview_df)
            group_cols = preview_df.select_dtypes(include=['object']).columns.tolist()
            
            trans_col1, trans_col2, trans_col3 = st.columns(3)
            
            with trans_col1:
                selected_date_col = st.selectbox(
                    "📅 Date Column",
                    date_cols if date_cols else preview_df.columns.tolist(),
                    help="Column containing dates or periods (e.g., Master Period, Close Date)"
                )
            
            with trans_col2:
                selected_value_col = st.selectbox(
                    "💰 Value Column",
                    value_cols if value_cols else preview_df.columns.tolist(),
                    help="Column containing numeric values to aggregate"
                )
            
            with trans_col3:
                selected_group_col = st.selectbox(
                    "📊 Group By (Optional)",
                    ['None'] + group_cols,
                    help="Column to group by (e.g., Industry Segment, Sales Stage)"
                )
            
            if st.button("🔄 Transform to Quarterly Format", type="primary"):
                try:
                    with st.spinner("Transforming data..."):
                        if selected_group_col == 'None':
                            transformed_df = transformer.transform_to_quarterly(
                                preview_df,
                                date_column=selected_date_col,
                                value_column=selected_value_col
                            )
                        else:
                            transformed_df = transformer.create_detailed_quarterly_view(
                                preview_df,
                                date_column=selected_date_col,
                                group_by_column=selected_group_col
                            )
                        
                        # Get summary
                        summary = transformer.get_transformation_summary(preview_df, transformed_df)
                        
                        # Store transformed data
                        st.session_state.uploaded_df = transformed_df
                        st.session_state.original_df = preview_df
                        st.session_state.transformation_summary = summary
                        st.session_state.data_loaded = True
                        st.session_state.sample_data_loaded = False
                        
                        st.success(f"✅ Transformed {summary['input_rows']} transactions into quarterly format!")
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"❌ Transformation error: {e}")
                    st.info("💡 Try selecting different columns or check your date format")
        
        else:
            # Data already has quarterly columns
            if st.button("📤 Load Quarterly Data", type="primary"):
                try:
                    st.session_state.uploaded_df = preview_df
                    st.session_state.data_loaded = True
                    st.session_state.sample_data_loaded = False
                    
                    st.success(f"✅ Loaded {len(preview_df)} rows with quarterly data!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error: {e}")
    
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")

# Display data
if st.session_state.sample_data_loaded or st.session_state.data_loaded:
    
    if st.session_state.sample_data_loaded:
        # Use sample data
        forecast_df, cfvpf_df, budget_df, variance_df = create_sample_data()
        
        st.markdown("---")
        
        # Show fiscal quarter info
        quarter_info = get_fiscal_quarter_info()
        st.info(f"📅 **Fiscal Year Calendar:** Q1: {quarter_info['Q1']} | Q2: {quarter_info['Q2']} | Q3: {quarter_info['Q3']} | Q4: {quarter_info['Q4']}")
        
        st.markdown("## 📊 Financial Dashboard - FY2026")
        
        # Create 4-column layout
        col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
        
        with col_a:
            st.markdown("### Current Forecast")
            st.dataframe(forecast_df, use_container_width=True, height=600)
        
        with col_b:
            st.markdown("### vs Prior Forecast")
            st.dataframe(cfvpf_df, use_container_width=True, height=600)
        
        with col_c:
            st.markdown("### Budget")
            st.dataframe(budget_df, use_container_width=True, height=600)
        
        with col_d:
            st.markdown("### CFvWB")
            st.dataframe(variance_df, use_container_width=True, height=600)
        
        # Key Metrics
        st.markdown("---")
        st.markdown("### 📈 Key Metrics Summary")
        
        metric_cols = st.columns(5)
        
        with metric_cols[0]:
            st.metric("FY Revenue", "$2,227.1M", "0.0%")
        
        with metric_cols[1]:
            st.metric("Contract Margin", "$623.4M", "0.0%")
        
        with metric_cols[2]:
            st.metric("Margin %", "28.0%", "0.0%")
        
        with metric_cols[3]:
            st.metric("Services CM", "$604.5M", "0.0%")
        
        with metric_cols[4]:
            st.metric("Services CM%", "29.9%", "0.0%")
        
        # Advanced Visualizations
        st.markdown("---")
        st.markdown("### 📊 Advanced Analytics & Visualizations")
        
        viz_col1, viz_col2 = st.columns(2)
        
        with viz_col1:
            st.markdown("#### Quarterly Revenue Comparison")
            
            quarter_info = get_fiscal_quarter_info()
            quarters = [f"Q1<br>({quarter_info['Q1']})", f"Q2<br>({quarter_info['Q2']})", 
                       f"Q3<br>({quarter_info['Q3']})", f"Q4<br>({quarter_info['Q4']})"]
            quarters_simple = ['Q1', 'Q2', 'Q3', 'Q4']
            forecast_revenue = [548.3, 559.9, 566.0, 552.9]
            budget_revenue = [565.7, 574.7, 594.4, 590.1]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                x=quarters,
                y=forecast_revenue,
                name='Current Forecast',
                marker_color='#667eea',
                text=[f'${v}M' for v in forecast_revenue],
                textposition='outside'
            ))
            
            fig.add_trace(go.Bar(
                x=quarters,
                y=budget_revenue,
                name='Budget',
                marker_color='#764ba2',
                text=[f'${v}M' for v in budget_revenue],
                textposition='outside'
            ))
            
            fig.update_layout(
                barmode='group',
                height=400,
                xaxis_title="Quarter",
                yaxis_title="Revenue ($M)",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with viz_col2:
            st.markdown("#### Variance Analysis")
            
            # Calculate variances
            variances = [f - b for f, b in zip(forecast_revenue, budget_revenue)]
            variance_pct = [(f - b) / b * 100 if b != 0 else 0 for f, b in zip(forecast_revenue, budget_revenue)]
            
            fig_var = go.Figure()
            
            # Color bars based on positive/negative
            colors = ['#2ca02c' if v >= 0 else '#d62728' for v in variances]
            
            fig_var.add_trace(go.Bar(
                x=quarters_simple,
                y=variances,
                marker_color=colors,
                text=[f'${v:+.1f}M<br>({p:+.1f}%)' for v, p in zip(variances, variance_pct)],
                textposition='outside',
                name='Variance'
            ))
            
            fig_var.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
            
            fig_var.update_layout(
                title="Forecast vs Budget Variance",
                height=400,
                xaxis_title="Quarter",
                yaxis_title="Variance ($M)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False
            )
            
            st.plotly_chart(fig_var, use_container_width=True)
        
        # Margin Trend
        st.markdown("### 📈 Margin Trend Analysis")
        
        margin_pct = [27.3, 27.9, 28.1, 28.7]
        
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=quarters_simple,
            y=margin_pct,
            mode='lines+markers',
            name='Contract Margin %',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10),
            text=[f"Q{i+1} ({list(quarter_info.values())[i]})" for i in range(4)],
            hovertemplate='%{text}<br>Margin: %{y:.1f}%<extra></extra>'
        ))
        
        fig2.update_layout(
            height=350,
            xaxis_title="Quarter",
            yaxis_title="Margin %",
            yaxis=dict(ticksuffix='%'),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # AI-Powered Insights
        st.markdown("---")
        st.markdown("### 🤖 AI-Powered Insights & Recommendations")
        
        # Generate insights
        insights_engine = FinancialInsightsEngine()
        insights = insights_engine.analyze_quarterly_data(forecast_df)
        variance_insights = insights_engine.analyze_variance(forecast_df, budget_df)
        
        # Display insights in tabs
        insight_tab1, insight_tab2, insight_tab3, insight_tab4 = st.tabs([
            "💡 Key Insights", "📊 Revenue Analysis", "💰 Margin Analysis", "⚠️ Recommendations"
        ])
        
        with insight_tab1:
            col_insight1, col_insight2 = st.columns(2)
            
            with col_insight1:
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
                    st.info("No significant revenue insights detected")
            
            with col_insight2:
                st.markdown("#### 📊 Trend Insights")
                if insights['trend_insights']:
                    for insight in insights['trend_insights']:
                        if insight['type'] == 'positive':
                            st.success(f"✅ {insight['message']}")
                        elif insight['type'] == 'warning':
                            st.warning(f"⚠️ {insight['message']}")
                        else:
                            st.info(f"ℹ️ {insight['message']}")
                else:
                    st.info("No significant trend insights detected")
        
        with insight_tab2:
            st.markdown("#### 📊 Quarterly Revenue Analysis")
            if insights['revenue_insights']:
                for insight in insights['revenue_insights']:
                    impact_color = "🔴" if insight['impact'] == 'high' else "🟡" if insight['impact'] == 'medium' else "🟢"
                    st.markdown(f"{impact_color} **Impact: {insight['impact'].upper()}**")
                    st.markdown(f"- {insight['message']}")
                    st.markdown("---")
            else:
                st.info("Revenue performance is within normal ranges")
        
        with insight_tab3:
            st.markdown("#### 💰 Margin Performance Analysis")
            if insights['margin_insights']:
                for insight in insights['margin_insights']:
                    impact_color = "🔴" if insight['impact'] == 'high' else "🟡" if insight['impact'] == 'medium' else "🟢"
                    st.markdown(f"{impact_color} **Impact: {insight['impact'].upper()}**")
                    st.markdown(f"- {insight['message']}")
                    st.markdown("---")
            else:
                st.info("Margin performance is within normal ranges")
        
        with insight_tab4:
            st.markdown("#### ⚠️ Actionable Recommendations")
            if insights['recommendations']:
                for idx, rec in enumerate(insights['recommendations'], 1):
                    priority_emoji = "🔴" if rec['priority'] == 'high' else "🟡"
                    with st.expander(f"{priority_emoji} {rec['category']}: {rec['action']}", expanded=(rec['priority']=='high')):
                        st.markdown(f"**Priority:** {rec['priority'].upper()}")
                        st.markdown(f"**Reason:** {rec['reason']}")
                        st.markdown(f"**Recommended Action:** {rec['action']}")
            else:
                st.success("✅ No critical actions required. Performance is on track!")
        
        # Export options
        st.markdown("---")
        st.markdown("### 💾 Export Options")
        
        export_col1, export_col2, export_col3, export_col4 = st.columns([2, 2, 2, 6])
        
        with export_col1:
            # Export all data to Excel
            excel_data = export_to_excel({
                'Current Forecast': forecast_df,
                'vs Prior Forecast': cfvpf_df,
                'Budget': budget_df,
                'Variance': variance_df
            })
            st.download_button(
                label="📥 Download Excel",
                data=excel_data,
                file_name=f"financial_dashboard_{fiscal_year}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with export_col2:
            # Export forecast to CSV
            csv_data = export_to_csv(forecast_df)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"forecast_{fiscal_year}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with export_col3:
            # Export variance analysis
            variance_csv = export_to_csv(variance_df)
            st.download_button(
                label="📊 Variance CSV",
                data=variance_csv,
                file_name=f"variance_{fiscal_year}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    elif st.session_state.data_loaded:
        # Display uploaded data
        df = st.session_state.uploaded_df
        
        st.markdown("---")
        
        # Show transformation summary if available
        if 'transformation_summary' in st.session_state:
            summary = st.session_state.transformation_summary
            st.success(f"✅ **Data Transformed Successfully!** {summary['records_processed']} transactions → Quarterly forecast")
            
            sum_col1, sum_col2, sum_col3, sum_col4, sum_col5 = st.columns(5)
            with sum_col1:
                st.metric("Q1 Total", f"${summary['q1_total']:,.0f}")
            with sum_col2:
                st.metric("Q2 Total", f"${summary['q2_total']:,.0f}")
            with sum_col3:
                st.metric("Q3 Total", f"${summary['q3_total']:,.0f}")
            with sum_col4:
                st.metric("Q4 Total", f"${summary['q4_total']:,.0f}")
            with sum_col5:
                st.metric("FY Total", f"${summary['fy_total']:,.0f}")
        
        # Show fiscal quarter info
        quarter_info = get_fiscal_quarter_info()
        st.info(f"📅 **Fiscal Year Calendar:** Q1: {quarter_info['Q1']} | Q2: {quarter_info['Q2']} | Q3: {quarter_info['Q3']} | Q4: {quarter_info['Q4']}")
        
        st.markdown("## 📊 Your Uploaded Data - Dashboard View")
        
        # Check if data has quarterly columns
        has_quarters = any(col in df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY'])
        
        if has_quarters:
            # Display in dashboard format
            st.success("✅ Quarterly data detected! Displaying in dashboard format.")
            
            # Main data table
            st.markdown("### 📋 Financial Data")
            st.dataframe(df, use_container_width=True, height=600)
            
            # Key Metrics if numeric columns exist
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if len(numeric_cols) >= 3:
                st.markdown("---")
                st.markdown("### 📈 Key Metrics")
                
                metric_cols = st.columns(5)
                
                # Try to find revenue and margin rows
                for idx, col in enumerate(numeric_cols[:5]):
                    if idx < 5:
                        with metric_cols[idx]:
                            if 'FY' in df.columns:
                                fy_value = df[df.columns[0]].iloc[idx] if len(df) > idx else "N/A"
                                fy_amount = df['FY'].iloc[idx] if len(df) > idx else 0
                                st.metric(str(fy_value)[:20], f"${fy_amount:,.1f}M" if pd.notna(fy_amount) else "N/A")
            
            # Quarterly visualization
            if all(q in df.columns for q in ['Q1', 'Q2', 'Q3', 'Q4']):
                st.markdown("---")
                st.markdown("### 📊 Quarterly Trend")
                
                # Find revenue row (first numeric row or row with 'revenue' in name)
                revenue_row_idx = 0
                for idx, row in df.iterrows():
                    if 'revenue' in str(row[df.columns[0]]).lower():
                        revenue_row_idx = idx
                        break
                
                if len(df) > revenue_row_idx:
                    quarters_simple = ['Q1', 'Q2', 'Q3', 'Q4']
                    values = [df['Q1'].iloc[revenue_row_idx], df['Q2'].iloc[revenue_row_idx], 
                             df['Q3'].iloc[revenue_row_idx], df['Q4'].iloc[revenue_row_idx]]
                    
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        x=quarters_simple,
                        y=values,
                        marker_color='#667eea',
                        text=[f'${v:,.1f}M' if pd.notna(v) else 'N/A' for v in values],
                        textposition='outside'
                    ))
                    
                    fig.update_layout(
                        title="Quarterly Performance",
                        height=400,
                        xaxis_title="Quarter (Fiscal Year: Apr-Mar)",
                        yaxis_title="Value ($M)",
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
        
        else:
            # Standard data view for non-quarterly data
            st.warning("⚠️ No quarterly columns (Q1, Q2, Q3, Q4) detected. Showing standard data view.")
            
            tab1, tab2, tab3 = st.tabs(["📋 Data View", "📈 Analysis", "📊 Summary"])
            
            with tab1:
                st.dataframe(df, use_container_width=True)
            
            with tab2:
                numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
                
                if len(numeric_cols) >= 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        x_col = st.selectbox("X-axis", df.columns)
                    with col2:
                        y_col = st.selectbox("Y-axis", numeric_cols)
                    
                    if st.button("Generate Chart"):
                        fig = go.Figure()
                        fig.add_trace(go.Bar(x=df[x_col].head(20), y=df[y_col].head(20)))
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                st.write("### Data Summary")
                st.write(f"**Rows:** {len(df)}")
                st.write(f"**Columns:** {len(df.columns)}")
                st.write("**Column Types:**")
                st.write(df.dtypes)
                
                st.markdown("---")
                st.info("""
                💡 **Tip:** For dashboard view, your data should have:
                - A column for Line Items (e.g., Revenue, Margins, etc.)
                - Columns named: Q1, Q2, Q3, Q4, FY
                - Numeric values in quarterly columns
                """)

else:
    # Welcome screen
    st.info("👆 Click **'Load Sample Data'** to see a demo dashboard, or upload your own data file")
    
    st.markdown("### 🎯 Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📊 Quarterly Analysis**
        - Q1, Q2, Q3, Q4, FY views
        - Multiple comparison modes
        - Variance calculations
        """)
    
    with col2:
        st.markdown("""
        **📈 Visual Analytics**
        - Revenue trends
        - Margin analysis
        - Interactive charts
        """)
    
    with col3:
        st.markdown("""
        **💾 Export Options**
        - Excel export
        - PDF reports
        - Custom formats
        """)

# Reset button in sidebar
with st.sidebar:
    st.markdown("## ⚙️ Options")
    
    if st.button("🔄 Reset Dashboard"):
        st.session_state.data_loaded = False
        st.session_state.sample_data_loaded = False
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📅 Fiscal Year Calendar")
    quarter_info = get_fiscal_quarter_info()
    st.markdown(f"""
    **Q1:** {quarter_info['Q1']} (Apr-Jun)  
    **Q2:** {quarter_info['Q2']} (Jul-Sep)  
    **Q3:** {quarter_info['Q3']} (Oct-Dec)  
    **Q4:** {quarter_info['Q4']} (Jan-Mar)  
    **FY:** April - March
    """)
    
    st.markdown("---")
    st.markdown("### 📊 Dashboard Info")
    st.markdown("""
    **Version:** 1.0  
    **Status:** ✅ Active  
    **Performance:** Fast Load
    """)
