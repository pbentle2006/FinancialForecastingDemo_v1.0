import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go

# Page configuration
st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional look
st.markdown("""
<style>
    .main {
        padding: 0rem 1rem;
    }
    .stApp {
        max-width: 100%;
    }
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    /* Table styling */
    .dataframe {
        font-size: 11px !important;
    }
    .dataframe th {
        background-color: #667eea !important;
        color: white !important;
        font-weight: 600 !important;
        text-align: center !important;
        padding: 8px !important;
    }
    .dataframe td {
        text-align: right !important;
        padding: 6px !important;
    }
    /* Row colors */
    .row-header {
        background-color: #f0f2f6 !important;
        font-weight: 600 !important;
    }
    .row-total {
        background-color: #e8eaf6 !important;
        font-weight: 700 !important;
        border-top: 2px solid #667eea !important;
    }
    /* Negative values in red */
    .negative {
        color: #d32f2f !important;
    }
    /* Percentage styling */
    .percentage {
        font-style: italic;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)

def generate_sample_data():
    """Generate sample financial data similar to the image"""
    
    # Define quarters
    quarters = ['Q1', 'Q2', 'Q3', 'Q4', 'FY']
    
    # Current Forecast data
    forecast_data = {
        'Line Item': [
            'IYR Live', 'ABR Live*', 'TCV Live*', 'P2 Live*',
            'Revenue', 'Backlog', 'Sell and Bill', 'Services Revenue', 'Resale Revenue',
            'Contract Margin', 'Contract Margin%',
            'Services CM', 'Services CM%',
            'Resale CM', 'Resale CM%'
        ],
        'Q1': [254.4, 40.3, 70.4, 1.3, 548.3, 548.3, 71.5, 498.1, 50.2, 149.5, '27.3%', 144.5, '29.0%', 5.0, '9.9%'],
        'Q2': [256.0, 304.3, 495.1, 0.9, 559.9, 559.9, 71.5, 508.2, 51.8, 156.0, '27.9%', 151.0, '29.7%', 5.0, '9.7%'],
        'Q3': [285.3, 605.9, 59.6, 1.1, 566.0, 494.5, 71.5, 511.5, 54.5, 159.1, '28.1%', 154.6, '30.2%', 4.5, '8.3%'],
        'Q4': [140.8, 1,176, 203.3, 0.4, 552.9, 380.9, 172.0, 506.2, 46.7, 158.9, '28.7%', 154.4, '30.5%', 4.4, '9.5%'],
        'FY': [1014.5, 2489.3, 1998.4, 0.9, 2227.1, 1983.6, 243.5, 2024.0, 203.2, 623.4, '28.0%', 604.5, '29.9%', 18.9, '9.3%']
    }
    
    # CFvPF (Current Forecast vs Prior Forecast)
    cfvpf_data = {
        'Q1': [403, '', '', '', '(0.0)', '(0.0)', '', 0.0, '(0.0)', 0.0, '0.0%', '(0.0)', '(0.0%)', 0.0, '0.0%'],
        'Q2': [304.3, '', '', '', 0.0, 0.0, '', 0.0, 0.0, 0.0, '0.0%', 0.0, '0.0%', '(0.0)', '(0.0%)'],
        'Q3': [605.9, '', '', '', 0.0, 0.0, '', 0.0, '(0.0)', 0.0, '(0.0%)', '(0.0)', '(0.0%)', '(0.0)', '0.0%'],
        'Q4': [1176, '', '', '', 0.0, 0.0, '', 0.0, '(0.0)', 0.0, '(0.0%)', '(0.0)', '(0.0%)', '(0.0)', '0.0%'],
        'FY': [2489.3, '', '', '', 0.0, 0.0, '', 0.0, 0.0, 0.0, '(0.0%)', '(0.0)', '(0.0%)', 0.0, '(0.0%)']
    }
    
    # Budget data
    budget_data = {
        'Q1': [408.4, '', 657.7, '', 565.7, 472.8, 91.0, 513.4, 50.4, 156.3, '29.1%', 158.5, '30.9%', 5.8, '11.4%'],
        'Q2': [394.7, '', 675.6, '', 574.7, 382.8, 191.9, 523.6, 51.1, 167.1, '29.1%', 161.2, '30.8%', 5.9, '11.6%'],
        'Q3': [399.2, '', 636.4, '', 594.4, 330.2, 264.2, 532.4, 62.0, 184.7, '31.1%', 176.5, '33.2%', 8.1, '13.1%'],
        'Q4': [404.8, '', 664.5, '', 590.1, 283.5, 306.6, 539.0, 51.1, 181.2, '30.7%', 174.7, '32.4%', 6.5, '12.7%'],
        'FY': [1607.1, '', 2634.2, '', 2322.9, 1469.3, 853.6, 2108.4, 214.5, 697.2, '30.0%', 670.9, '31.8%', 26.3, '12.3%']
    }
    
    # CFvWB (Current Forecast vs Budget)
    cfvwb_data = {
        'Q1': ['(5.4)', '', 46.3, '', '(15.5)', 75.5, '(91.0)', '(15.3)', '(0.2)', '(14.8)', '(1.9%)', '(14.0)', '(1.9%)', '(0.8)', '(1.5%)'],
        'Q2': ['(90.4)', '', '(180.4)', '', '(14.7)', 177.2, '(191.9)', '(15.4)', 0.7, '(11.1)', '(1.2%)', '(10.2)', '(1.1%)', '(0.9)', '(2.0%)'],
        'Q3': [206.1, '', '(40.4)', '', '(28.4)', 164.3, '(192.7)', '(20.9)', '(7.5)', '(25.6)', '(3.0%)', '(21.9)', '(2.9%)', '(3.6)', '(4.8%)'],
        'Q4': ['', '', '', '', '', '', '', '', '', '', '', '', '', '', '']
    }
    
    return pd.DataFrame(forecast_data), cfvpf_data, budget_data, cfvwb_data

def format_value(val):
    """Format values with proper styling"""
    if pd.isna(val) or val == '':
        return ''
    
    val_str = str(val)
    
    # Check if negative
    if '(' in val_str or (isinstance(val, (int, float)) and val < 0):
        return f'<span class="negative">{val_str}</span>'
    
    # Check if percentage
    if '%' in val_str:
        return f'<span class="percentage">{val_str}</span>'
    
    return val_str

def create_financial_table(df, title, section_type="forecast"):
    """Create a styled financial table"""
    
    st.markdown(f"### {title}")
    
    # Create HTML table
    html = '<table style="width:100%; border-collapse: collapse; font-size: 11px;">'
    
    # Header
    html += '<thead><tr style="background-color: #667eea; color: white;">'
    for col in df.columns:
        html += f'<th style="padding: 8px; text-align: center; border: 1px solid #ddd;">{col}</th>'
    html += '</tr></thead>'
    
    # Body
    html += '<tbody>'
    for idx, row in df.iterrows():
        # Determine row class
        row_class = ''
        if row['Line Item'] in ['Revenue', 'Contract Margin', 'Services CM', 'Resale CM']:
            row_class = 'row-header'
        elif row['Line Item'] in ['Contract Margin%', 'Services CM%', 'Resale CM%']:
            row_class = 'row-total'
        
        html += f'<tr class="{row_class}">'
        for col_idx, val in enumerate(row):
            align = 'left' if col_idx == 0 else 'right'
            formatted_val = format_value(val)
            html += f'<td style="padding: 6px; text-align: {align}; border: 1px solid #ddd;">{formatted_val}</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    
    st.markdown(html, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="dashboard-header">
        <h1 style="margin: 0;">📊 Financial Forecast Dashboard</h1>
        <p style="margin: 0; opacity: 0.9;">FY2026 - Current Forecast vs Prior Forecast vs Budget</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filters in columns
    col1, col2, col3, col4 = st.columns([2, 2, 3, 5])
    
    with col1:
        version = st.selectbox("Version", ["Current Forecast", "Prior Forecast", "Budget"], key="version")
    
    with col2:
        fiscal_year = st.selectbox("Fiscal Year", ["FY2026", "FY2025", "FY2024"], key="fy")
    
    with col3:
        selection = st.selectbox("$M / $K / $ Selection", ["Millions", "Thousands", "Dollars"], key="units")
    
    # Generate sample data
    forecast_df, cfvpf_data, budget_data, cfvwb_data = generate_sample_data()
    
    # Create three-column layout for the main tables
    st.markdown("---")
    
    col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 2])
    
    with col_a:
        st.markdown("#### Current Forecast")
        st.dataframe(forecast_df, use_container_width=True, height=600)
    
    with col_b:
        st.markdown("#### vs Prior Forecast (CFvPF)")
        cfvpf_df = pd.DataFrame(cfvpf_data)
        cfvpf_df.insert(0, 'Line Item', forecast_df['Line Item'])
        st.dataframe(cfvpf_df, use_container_width=True, height=600)
    
    with col_c:
        st.markdown("#### Budget")
        budget_df = pd.DataFrame(budget_data)
        budget_df.insert(0, 'Line Item', forecast_df['Line Item'])
        st.dataframe(budget_df, use_container_width=True, height=600)
    
    with col_d:
        st.markdown("#### CFvWB")
        cfvwb_df = pd.DataFrame(cfvwb_data)
        cfvwb_df.insert(0, 'Line Item', forecast_df['Line Item'])
        st.dataframe(cfvwb_df, use_container_width=True, height=600)
    
    # Summary metrics at bottom
    st.markdown("---")
    st.markdown("### 📈 Key Metrics Summary")
    
    metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
    
    with metric_col1:
        st.metric("FY Revenue", "$2,227.1M", "0.0%")
    
    with metric_col2:
        st.metric("Contract Margin", "$623.4M", "0.0%")
    
    with metric_col3:
        st.metric("Margin %", "28.0%", "0.0%")
    
    with metric_col4:
        st.metric("Services CM", "$604.5M", "-0.0%")
    
    with metric_col5:
        st.metric("Services CM%", "29.9%", "-0.0%")
    
    # Quick visualization
    st.markdown("---")
    st.markdown("### 📊 Quarterly Revenue Trend")
    
    # Create simple bar chart
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    forecast_values = [548.3, 559.9, 566.0, 552.9]
    budget_values = [565.7, 574.7, 594.4, 590.1]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=quarters,
        y=forecast_values,
        name='Current Forecast',
        marker_color='#667eea',
        text=[f'${v}M' for v in forecast_values],
        textposition='outside'
    ))
    
    fig.add_trace(go.Bar(
        x=quarters,
        y=budget_values,
        name='Budget',
        marker_color='#764ba2',
        text=[f'${v}M' for v in budget_values],
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
    
    # Export options
    st.markdown("---")
    col_export1, col_export2, col_export3 = st.columns([1, 1, 8])
    
    with col_export1:
        if st.button("📥 Export to Excel", use_container_width=True):
            st.success("Export functionality ready to implement")
    
    with col_export2:
        if st.button("📊 Export to PDF", use_container_width=True):
            st.success("PDF export ready to implement")

if __name__ == "__main__":
    main()
