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
        """Render the forecast trend view"""
        
        st.markdown(f"### 📈 Forecast Trend Analysis - {scenario_name}")
        st.markdown("Aggregate monthly forecast data into fiscal quarters to show revenue phasing trend.")
        
        # Identify forecast columns
        forecast_cols = self.identify_forecast_columns(df)
        
        if not forecast_cols:
            st.error("❌ No monthly forecast columns found. Expected format: YYYY-MM (e.g., 2025-04, 2025-05)")
            st.info("💡 Forecast columns should start from column BR onwards with format: 2025-04, 2025-05, etc.")
            return None
        
        st.success(f"✓ Found {len(forecast_cols)} monthly forecast columns: {forecast_cols[0]} to {forecast_cols[-1]}")
        
        st.markdown("---")
        
        # Control panel
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Group By:**")
            
            # Detect available dimensions
            available_dimensions = {'none': '📊 Total Only (No Grouping)'}
            if 'account_name' in df.columns or 'Account Name' in df.columns:
                available_dimensions['account_name'] = '🏢 By Account'
            if 'industry_vertical' in df.columns or 'Industry Vertical' in df.columns:
                available_dimensions['industry_vertical'] = '🏭 By Industry Vertical'
            if 'product_name' in df.columns or 'Product Name' in df.columns:
                available_dimensions['product_name'] = '📦 By Product Name'
            if 'sales_stage' in df.columns or 'Sales Stage' in df.columns:
                available_dimensions['sales_stage'] = '🎯 By Sales Stage'
            
            selected_dimension = st.radio(
                "Select grouping",
                options=list(available_dimensions.keys()),
                format_func=lambda x: available_dimensions[x],
                key=f"forecast_dimension_{scenario_name}",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**💰 Include Total TCV:**")
            include_tcv = st.checkbox(
                "Show Total TCV column",
                value=True,
                key=f"include_tcv_{scenario_name}",
                help="Display the Total Contract Value alongside forecast trend"
            )
        
        st.markdown("---")
        
        # Normalize column names
        df_norm = df.copy()
        col_mapping = {}
        for col in df.columns:
            normalized = col.lower().replace(' ', '_')
            col_mapping[col] = normalized
        df_norm.columns = [col_mapping[col] for col in df.columns]
        
        # Get grouping column
        group_by = None if selected_dimension == 'none' else selected_dimension
        
        # Aggregate to fiscal quarters
        result_df, sorted_quarters = self.aggregate_to_fiscal_quarters(df_norm, forecast_cols, group_by)
        
        # Add Total TCV if requested
        if include_tcv:
            # Try to find TCV column with various names
            tcv_col = None
            for possible_name in ['revenue_tcv_usd', 'tcv_usd', 'tcv']:
                if possible_name in df_norm.columns:
                    tcv_col = possible_name
                    break
            
            if tcv_col:
                
                if group_by:
                    # Sum TCV by group
                    df_norm[tcv_col] = pd.to_numeric(df_norm[tcv_col], errors='coerce').fillna(0)
                    tcv_data = df_norm.groupby(group_by)[tcv_col].sum()
                    result_df = result_df.merge(
                        tcv_data.rename('Total_TCV'),
                        left_on=group_by,
                        right_index=True,
                        how='left'
                    )
                else:
                    # Total TCV
                    df_norm[tcv_col] = pd.to_numeric(df_norm[tcv_col], errors='coerce').fillna(0)
                    result_df['Total_TCV'] = df_norm[tcv_col].sum()
        
        # Display summary metrics
        st.markdown("**📈 Summary Metrics:**")
        
        summary_cols = st.columns(4)
        
        with summary_cols[0]:
            if include_tcv and 'Total_TCV' in result_df.columns:
                total_tcv = result_df['Total_TCV'].sum()
                st.metric("Total TCV", self.format_number_millions(total_tcv))
        
        with summary_cols[1]:
            total_forecast = result_df['Total_Forecast'].sum()
            st.metric("Total Forecast", self.format_number_millions(total_forecast))
        
        with summary_cols[2]:
            st.metric("Forecast Periods", len(sorted_quarters))
        
        with summary_cols[3]:
            if group_by:
                st.metric(f"Number of {group_by.replace('_', ' ').title()}", len(result_df))
            else:
                st.metric("Monthly Columns", len(forecast_cols))
        
        st.markdown("---")
        
        # Format display dataframe
        display_df = result_df.copy()
        
        # Reorder columns
        if group_by:
            cols_order = [group_by]
        else:
            cols_order = ['Metric']
        
        if include_tcv and 'Total_TCV' in display_df.columns:
            cols_order.append('Total_TCV')
        
        cols_order.extend(sorted_quarters)
        cols_order.append('Total_Forecast')
        
        display_df = display_df[cols_order]
        
        # Format numbers in millions
        for col in display_df.columns:
            if col not in [group_by, 'Metric']:
                display_df[col] = display_df[col].apply(self.format_number_millions)
        
        # Rename columns for display
        display_df.columns = [col.replace('_', ' ').title() if col not in sorted_quarters + ['Total_TCV', 'Total_Forecast'] else col for col in display_df.columns]
        
        # Display the report
        st.markdown("**📋 Forecast Trend Report:**")
        st.info("💡 Tip: Values are displayed in millions (e.g., 3.10m = $3,100,000)")
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Add download button
        st.markdown("---")
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Forecast Trend Report",
            data=csv,
            file_name=f"forecast_trend_{scenario_name.lower().replace(' ', '_')}.csv",
            mime="text/csv"
        )
        
        return display_df
