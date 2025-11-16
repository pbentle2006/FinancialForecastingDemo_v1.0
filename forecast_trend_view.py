"""
Forecast Trend View - Aggregate monthly forecast columns into fiscal quarters
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class ForecastTrendView:
    """View for aggregating monthly forecast data into fiscal quarters"""
    
    def __init__(self):
        self.grouping_options = {
            'account_name': '🏢 By Account',
            'industry_vertical': '🏭 By Industry Vertical',
            'product_name': '📦 By Product Name',
            'sales_stage': '🎯 By Sales Stage'
        }
    
    def get_fiscal_quarter_from_month(self, year_month_str):
        """
        Convert year-month string to fiscal quarter
        Format: '2025-04' → 'FY26-Q1'
        
        Fiscal Year: April to March
        Q1: April - June
        Q2: July - September
        Q3: October - December
        Q4: January - March
        """
        try:
            # Parse year-month
            year, month = map(int, year_month_str.split('-'))
            
            # Determine fiscal year and quarter
            if month >= 4:  # April onwards
                fiscal_year = year + 1
                if 4 <= month <= 6:
                    quarter = 'Q1'
                elif 7 <= month <= 9:
                    quarter = 'Q2'
                else:  # 10-12
                    quarter = 'Q3'
            else:  # January-March
                fiscal_year = year
                quarter = 'Q4'
            
            return f"FY{str(fiscal_year)[-2:]}-{quarter}"
        except:
            return None
    
    def identify_forecast_columns(self, df):
        """
        Identify columns that contain monthly forecast data
        Format: YYYY-MM (e.g., 2025-04, 2025-05)
        """
        forecast_cols = []
        
        for col in df.columns:
            col_str = str(col)
            # Check if column name matches YYYY-MM format
            if '-' in col_str and len(col_str.split('-')) == 2:
                try:
                    parts = col_str.split('-')
                    year = int(parts[0])
                    month = int(parts[1])
                    if 2020 <= year <= 2030 and 1 <= month <= 12:
                        forecast_cols.append(col)
                except:
                    continue
        
        return sorted(forecast_cols)
    
    def aggregate_to_fiscal_quarters(self, df, forecast_cols, group_by=None):
        """
        Aggregate monthly forecast columns into fiscal quarters
        
        Args:
            df: Source dataframe
            forecast_cols: List of monthly forecast column names
            group_by: Optional grouping dimension
        
        Returns:
            DataFrame with fiscal quarter columns
        """
        
        # Create a mapping of fiscal quarters to month columns
        quarter_mapping = {}
        for col in forecast_cols:
            fiscal_quarter = self.get_fiscal_quarter_from_month(col)
            if fiscal_quarter:
                if fiscal_quarter not in quarter_mapping:
                    quarter_mapping[fiscal_quarter] = []
                quarter_mapping[fiscal_quarter].append(col)
        
        # Sort quarters chronologically
        sorted_quarters = sorted(quarter_mapping.keys())
        
        # Prepare result dataframe
        if group_by and group_by in df.columns:
            # Group by dimension
            result_df = df[[group_by]].drop_duplicates().reset_index(drop=True)
            
            # For each fiscal quarter, sum the monthly columns
            for quarter in sorted_quarters:
                month_cols = quarter_mapping[quarter]
                
                # Convert columns to numeric
                for col in month_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                # Sum by group
                quarter_data = df.groupby(group_by)[month_cols].sum().sum(axis=1)
                result_df = result_df.merge(
                    quarter_data.rename(quarter),
                    left_on=group_by,
                    right_index=True,
                    how='left'
                )
            
            # Calculate total across all quarters
            result_df['Total_Forecast'] = result_df[sorted_quarters].sum(axis=1)
            
        else:
            # No grouping - aggregate all data
            result_df = pd.DataFrame({'Metric': ['Total']})
            
            for quarter in sorted_quarters:
                month_cols = quarter_mapping[quarter]
                
                # Convert to numeric and sum
                total = 0
                for col in month_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    total += df[col].sum()
                
                result_df[quarter] = total
            
            # Calculate total
            result_df['Total_Forecast'] = result_df[sorted_quarters].sum(axis=1)
        
        return result_df, sorted_quarters
    
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
    
    def render_forecast_trend(self, df, scenario_name='Base Case'):
        """Render Forecast Trend view with fiscal quarter aggregation"""
        
        st.markdown(f"### 📈 Forecast Trend - {scenario_name}")
        st.markdown("Aggregate monthly forecast data into fiscal quarters")
        
        if df is None or len(df) == 0:
            st.error("❌ No data available for forecast trend analysis")
            return
        
        # Detect forecast columns (columns that look like dates/periods)
        forecast_cols = []
        for col in df.columns:
            # Look for columns that contain year-month patterns like '2025-04', 'fy2025-01', etc.
            if any(pattern in col.lower() for pattern in ['fy', '202', '203']):
                forecast_cols.append(col)
            # Also check for columns with numeric patterns that might be periods
            elif any(char.isdigit() for char in col) and ('-' in col or len(col) >= 6):
                forecast_cols.append(col)
        
        if not forecast_cols:
            st.warning("⚠️ No forecast columns detected. Looking for columns with year/month patterns.")
            st.info("💡 Expected format: '2025-04', 'FY25-Q1', 'fy2025-01', etc.")
            
            # Show sample columns for debugging
            sample_cols = list(df.columns)[:10]
            st.write(f"**Available columns:** {sample_cols}")
            return
        
        st.success(f"✅ Found {len(forecast_cols)} forecast columns")
        
        # Dimension selection
        available_dimensions = {'none': '📊 Total Only (No Grouping)'}
        if 'account_name' in df.columns:
            available_dimensions['account_name'] = '🏢 By Account'
        if 'industry_vertical' in df.columns:
            available_dimensions['industry_vertical'] = '🏭 By Industry Vertical'
        if 'product_name' in df.columns:
            available_dimensions['product_name'] = '📦 By Product Name'
        if 'sales_stage' in df.columns:
            available_dimensions['sales_stage'] = '🎯 By Sales Stage'
        
        selected_dimension = st.radio(
            "Group by:",
            options=list(available_dimensions.keys()),
            format_func=lambda x: available_dimensions[x],
            key=f"forecast_dimension_{scenario_name}",
            horizontal=True
        )
        df_norm = df.copy()
        
        # Data validation
        with st.expander("🔍 Data Validation", expanded=False):
            st.write(f"**DataFrame shape:** {df.shape}")
            st.write(f"**Columns:** {list(df.columns)}")
            st.write(f"**Forecast columns found:** {forecast_cols}")
        
        # Convert 'none' to None for processing
        if selected_dimension == 'none':
            selected_dimension = None
        
        try:
            aggregated_df, sorted_quarters = self.aggregate_to_fiscal_quarters(df_norm, forecast_cols, selected_dimension)
            
            if aggregated_df is None or len(aggregated_df) == 0:
                st.error("❌ Failed to aggregate forecast data")
                return
            
            st.success(f"✅ Successfully aggregated data into {len(aggregated_df)} groups")
            
            # Display results
            self._display_forecast_results(aggregated_df, forecast_cols, selected_dimension)
            
        except Exception as e:
            st.error(f"❌ Error processing forecast data: {str(e)}")
            st.info("💡 This might be due to data format issues or missing columns")

    def format_number_millions(self, value):
        """Format number in millions (e.g., 12,853m or 2.6m)"""
        if pd.isna(value) or value == 0:
            return "0m"
        
        millions = value / 1_000_000
        
        # If >= 1000m, show without decimals (e.g., 12,853m)
        if millions >= 1000:
            return f"{millions:,.0f}m"
        # If >= 10m, show 1 decimal (e.g., 123.5m)
            return
        
        # Show summary metrics
        st.markdown("**📈 Summary Metrics:**")
        summary_cols = st.columns(4)
        
        with summary_cols[0]:
            if 'Total_Forecast' in df.columns:
                total_forecast = df['Total_Forecast'].sum()
                st.metric("Total Forecast", self.format_number_millions(total_forecast))
            else:
                st.metric("Groups", len(df))
        
        with summary_cols[1]:
            quarters = [col for col in df.columns if 'FY' in str(col)]
            st.metric("Forecast Quarters", len(quarters))
        
        with summary_cols[2]:
            if group_by:
                st.metric(f"Number of {group_by.replace('_', ' ').title()}", len(df))
            else:
                st.metric("Data Points", len(df))
        
        with summary_cols[3]:
            avg_quarterly = df.select_dtypes(include=[np.number]).mean().mean()
            st.metric("Avg Quarterly", self.format_number_millions(avg_quarterly))
        
        st.markdown("---")
        
        # Display data table
        st.markdown("**📋 Forecast Data:**")
        
        # Format numeric columns for display
        display_df = df.copy()
        numeric_cols = display_df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            display_df[col] = display_df[col].apply(self.format_number_millions)
        
        st.dataframe(display_df, use_container_width=True)
        
        # Add download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast Trend Report",
            data=csv,
            file_name="forecast_trend_report.csv",
            mime="text/csv",
            use_container_width=False
        )
