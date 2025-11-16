"""
Management Information View - Tables with visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

class ManagementInformationView:
    """Management Information view with tables and charts"""
    
    def __init__(self):
        self.grouping_options = {
            'account_name': '🏢 By Account',
            'industry_vertical': '🏭 By Industry Vertical',
            'product_name': '📦 By Product Name',
            'sales_stage': '🎯 By Sales Stage'
        }
    
    def get_fiscal_quarter(self, date):
        """Convert date to fiscal quarter (April-March fiscal year)"""
        if pd.isna(date):
            return None
        
        try:
            if isinstance(date, str):
                date = pd.to_datetime(date)
            
            month = date.month
            year = date.year
            
            if month >= 4:
                fiscal_year = year + 1
                if 4 <= month <= 6:
                    quarter = 'Q1'
                elif 7 <= month <= 9:
                    quarter = 'Q2'
                else:
                    quarter = 'Q3'
            else:
                fiscal_year = year
                quarter = 'Q4'
            
            return f"FY{str(fiscal_year)[-2:]}-{quarter}"
        except:
            return None
    
    def normalize_column_names(self, df):
        """Normalize column names"""
        df_norm = df.copy()
        column_mapping = {}
        
        for col in df.columns:
            normalized = col.lower().replace(' ', '_')
            
            if normalized in ['tcv_usd', 'tcv']:
                normalized = 'revenue_tcv_usd'
            elif normalized == 'iyr':
                normalized = 'iyr_usd'
            elif normalized == 'margin':
                normalized = 'margin_usd'
            
            column_mapping[col] = normalized
        
        df_norm.columns = [column_mapping[col] for col in df.columns]
        return df_norm, column_mapping
    
    def format_number_millions(self, value):
        """Format number in millions (e.g., 12,853m or 2.6m)"""
        if pd.isna(value) or value == 0:
            return "0m"
        
        millions = value / 1_000_000
        
        # If >= 1000m, show without decimals (e.g., 12,853m)
        if millions >= 1000:
            return f"{millions:,.0f}m"
        # If >= 10m, show 1 decimal (e.g., 123.5m)
        elif millions >= 10:
            return f"{millions:.1f}m"
        # If < 10m, show 1 decimal (e.g., 2.6m)
        else:
            return f"{millions:.1f}m"
    
    def create_bar_chart(self, df, group_by, metric, title):
        """Create bar chart for grouped data"""
        
        # Aggregate data
        grouped = df.groupby(group_by)[metric].sum().sort_values(ascending=False).head(10)
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=grouped.index,
                y=grouped.values,
                marker_color='rgb(55, 83, 109)',
                text=[self.format_number_millions(v) for v in grouped.values],
                textposition='auto',
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=group_by.replace('_', ' ').title(),
            yaxis_title=f'{metric.replace("_", " ").title()} ($)',
            height=400,
            showlegend=False,
            hovermode='x'
        )
        
        return fig
    
    def create_trend_line(self, df, group_by, metric, title):
        """Create line chart for quarterly trends"""
        
        # Get fiscal quarters
        df_copy = df.copy()
        if 'close_date' in df_copy.columns:
            df_copy['close_date'] = pd.to_datetime(df_copy['close_date'], errors='coerce')
            df_copy['fiscal_period'] = df_copy['close_date'].apply(self.get_fiscal_quarter)
            
            # Aggregate by period
            trend_data = df_copy.groupby('fiscal_period')[metric].sum().sort_index()
            
            # Create line chart
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=trend_data.index,
                y=trend_data.values,
                mode='lines+markers',
                name=metric.replace('_', ' ').title(),
                line=dict(color='rgb(55, 83, 109)', width=3),
                marker=dict(size=8),
                text=[self.format_number_millions(v) for v in trend_data.values],
                hovertemplate='%{x}<br>%{text}<extra></extra>'
            ))
            
            fig.update_layout(
                title=title,
                xaxis_title='Fiscal Quarter',
                yaxis_title=f'{metric.replace("_", " ").title()} ($)',
                height=400,
                showlegend=False,
                hovermode='x'
            )
            
            return fig
        
        return None
    
    def create_pie_chart(self, df, group_by, metric, title):
        """Create pie chart for proportions"""
        
        # Aggregate data - top 10 + Others
        grouped = df.groupby(group_by)[metric].sum().sort_values(ascending=False)
        
        if len(grouped) > 10:
            top_10 = grouped.head(10)
            others = pd.Series({'Others': grouped.iloc[10:].sum()})
            grouped = pd.concat([top_10, others])
        
        # Create pie chart
        fig = go.Figure(data=[
            go.Pie(
                labels=grouped.index,
                values=grouped.values,
                hole=0.3,
                textinfo='label+percent',
                hovertemplate='%{label}<br>%{value:,.0f}<br>%{percent}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            height=400,
            showlegend=True
        )
        
        return fig
    
    def render_mi_view(self, df, scenario_name='Base Case'):
        """Render Management Information view"""
        
        st.markdown(f"### 📊 Management Information - {scenario_name}")
        st.markdown("Analyze your data with interactive tables and visualizations")
        
        # Normalize columns
        df_norm, _ = self.normalize_column_names(df)
        
        # Detect available dimensions
        available_dimensions = {}
        if 'account_name' in df_norm.columns:
            available_dimensions['account_name'] = '🏢 By Account'
        if 'industry_vertical' in df_norm.columns:
            available_dimensions['industry_vertical'] = '🏭 By Industry Vertical'
        if 'product_name' in df_norm.columns:
            available_dimensions['product_name'] = '📦 By Product Name'
        if 'sales_stage' in df_norm.columns:
            available_dimensions['sales_stage'] = '🎯 By Sales Stage'
        
        # Detect available metrics
        available_metrics = []
        if 'revenue_tcv_usd' in df_norm.columns:
            available_metrics.append('revenue_tcv_usd')
        if 'iyr_usd' in df_norm.columns:
            available_metrics.append('iyr_usd')
        if 'margin_usd' in df_norm.columns:
            available_metrics.append('margin_usd')
        
        if not available_dimensions or not available_metrics:
            st.error("❌ Required columns not found. Please ensure data is properly mapped.")
            return
        
        st.markdown("---")
        
        # Control panel
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Group By:**")
            selected_dimension = st.radio(
                "Select dimension",
                options=list(available_dimensions.keys()),
                format_func=lambda x: available_dimensions[x],
                key=f"mi_dimension_{scenario_name}",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**💰 Metric:**")
            metric_labels = {
                'revenue_tcv_usd': 'Revenue TCV USD',
                'iyr_usd': 'IYR USD',
                'margin_usd': 'Margin USD'
            }
            selected_metric = st.radio(
                "Select metric",
                options=available_metrics,
                format_func=lambda x: metric_labels.get(x, x),
                key=f"mi_metric_{scenario_name}",
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        # Convert metric to numeric
        df_norm[selected_metric] = pd.to_numeric(df_norm[selected_metric], errors='coerce').fillna(0)
        
        # Summary metrics
        st.markdown("**📈 Summary Metrics:**")
        summary_cols = st.columns(4)
        
        with summary_cols[0]:
            total = df_norm[selected_metric].sum()
            st.metric("Total", self.format_number_millions(total))
        
        with summary_cols[1]:
            avg = df_norm[selected_metric].mean()
            st.metric("Average", self.format_number_millions(avg))
        
        with summary_cols[2]:
            count = len(df_norm[df_norm[selected_metric] > 0])
            st.metric("Count", f"{count:,}")
        
        with summary_cols[3]:
            unique_groups = df_norm[selected_dimension].nunique()
            st.metric(f"Unique {selected_dimension.replace('_', ' ').title()}", f"{unique_groups:,}")
        
        st.markdown("---")
        
        # Create visualizations
        st.markdown("**📊 Visualizations:**")
        
        # Bar Chart
        with st.container():
            st.markdown(f"#### Top 10 by {selected_dimension.replace('_', ' ').title()}")
            bar_chart = self.create_bar_chart(
                df_norm,
                selected_dimension,
                selected_metric,
                f"Top 10 {selected_dimension.replace('_', ' ').title()} by {metric_labels[selected_metric]}"
            )
            st.plotly_chart(bar_chart, use_container_width=True)
        
        st.markdown("---")
        
        # Line Chart (Trend)
        with st.container():
            st.markdown("#### Quarterly Trend")
            trend_chart = self.create_trend_line(
                df_norm,
                selected_dimension,
                selected_metric,
                f"{metric_labels[selected_metric]} Trend Over Time"
            )
            if trend_chart:
                st.plotly_chart(trend_chart, use_container_width=True)
            else:
                st.info("💡 Close Date column required for trend analysis")
        
        st.markdown("---")
        
        # Pie Chart
        col_pie, col_table = st.columns([1, 1])
        
        with col_pie:
            st.markdown("#### Proportion by Group")
            pie_chart = self.create_pie_chart(
                df_norm,
                selected_dimension,
                selected_metric,
                f"{metric_labels[selected_metric]} Distribution"
            )
            st.plotly_chart(pie_chart, use_container_width=True)
        
        with col_table:
            st.markdown("#### Top 10 Details")
            # Create summary table
            summary_table = df_norm.groupby(selected_dimension)[selected_metric].agg([
                ('Total', 'sum'),
                ('Count', 'count'),
                ('Average', 'mean')
            ]).sort_values('Total', ascending=False).head(10)
            
            # Format numbers
            summary_table['Total'] = summary_table['Total'].apply(lambda x: self.format_number_millions(x))
            summary_table['Average'] = summary_table['Average'].apply(lambda x: self.format_number_millions(x))
            
            st.dataframe(summary_table, use_container_width=True)
        
        st.markdown("---")
        
        # Detailed table
        st.markdown("**📋 Detailed Report:**")
        
        # Group data
        grouped_data = df_norm.groupby(selected_dimension)[selected_metric].sum().sort_values(ascending=False)
        
        # Format for display
        display_df = pd.DataFrame({
            selected_dimension.replace('_', ' ').title(): grouped_data.index,
            metric_labels[selected_metric]: grouped_data.values
        })
        
        display_df[metric_labels[selected_metric]] = display_df[metric_labels[selected_metric]].apply(
            lambda x: self.format_number_millions(x)
        )
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Download button
        st.markdown("---")
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Report",
            data=csv,
            file_name=f"mi_report_{scenario_name.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
