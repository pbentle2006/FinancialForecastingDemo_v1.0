"""
Dynamic Reporting View - Flexible reporting by Account, Industry, or Product
"""

import streamlit as st
import pandas as pd
import numpy as np

class DynamicReportingView:
    """Dynamic reporting view that groups by different dimensions"""
    
    def __init__(self):
        self.grouping_options = {
            'account_name': '🏢 By Account',
            'industry_vertical': '🏭 By Industry Vertical',
            'product_name': '📦 By Product Name',
            'sales_stage': '🎯 By Sales Stage'
        }
        
        self.metric_columns = {
            'revenue_tcv_usd': 'Revenue TCV USD',
            'iyr_usd': 'IYR USD',
            'margin_usd': 'Margin USD'
        }
    
    def detect_available_dimensions(self, df):
        """Detect which grouping dimensions are available in the data"""
        available = {}
        
        # Check for account name
        if 'account_name' in df.columns or 'Account Name' in df.columns:
            available['account_name'] = '🏢 By Account'
        
        # Check for industry vertical
        if 'industry_vertical' in df.columns or 'Industry Vertical' in df.columns:
            available['industry_vertical'] = '🏭 By Industry Vertical'
        
        # Check for product name
        if 'product_name' in df.columns or 'Product Name' in df.columns:
            available['product_name'] = '📦 By Product Name'
        
        # Check for sales stage
        if 'sales_stage' in df.columns or 'Sales Stage' in df.columns:
            available['sales_stage'] = '🎯 By Sales Stage'
        
        return available
    
    def detect_available_metrics(self, df):
        """Detect which metrics are available in the data"""
        available = {}
        
        # Check for revenue - try multiple variations
        if ('revenue_tcv_usd' in df.columns or 'Revenue TCV USD' in df.columns or 
            'tcv_usd' in df.columns or 'TCV USD' in df.columns or
            'tcv' in df.columns or 'TCV' in df.columns):
            available['revenue_tcv_usd'] = 'Revenue TCV USD'
        
        # Check for IYR
        if 'iyr_usd' in df.columns or 'IYR USD' in df.columns or 'iyr' in df.columns or 'IYR' in df.columns:
            available['iyr_usd'] = 'IYR USD'
        
        # Check for margin
        if 'margin_usd' in df.columns or 'Margin USD' in df.columns or 'margin' in df.columns or 'Margin' in df.columns:
            available['margin_usd'] = 'Margin USD'
        
        return available
    
    def normalize_column_names(self, df):
        """Normalize column names to lowercase with underscores"""
        df_normalized = df.copy()
        
        # Create mapping of original to normalized names
        column_mapping = {}
        for col in df.columns:
            normalized = col.lower().replace(' ', '_')
            
            # Special handling for TCV variations - map to revenue_tcv_usd
            if normalized in ['tcv_usd', 'tcv']:
                normalized = 'revenue_tcv_usd'
            # Special handling for IYR variations
            elif normalized == 'iyr':
                normalized = 'iyr_usd'
            # Special handling for Margin variations
            elif normalized == 'margin':
                normalized = 'margin_usd'
            
            column_mapping[col] = normalized
        
        df_normalized.columns = [column_mapping[col] for col in df.columns]
        
        return df_normalized, column_mapping
    
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
    
    def create_dynamic_report(self, df, group_by, metrics, periods=None):
        """
        Create a dynamic report grouped by specified dimension
        
        Args:
            df: Source dataframe
            group_by: Column to group by (account_name, industry_vertical, product_name)
            metrics: List of metrics to aggregate (revenue_tcv_usd, iyr_usd, margin_usd)
            periods: Optional list of periods to include
        
        Returns:
            DataFrame with grouped data
        """
        
        # Normalize column names
        df_norm, col_map = self.normalize_column_names(df)
        
        # Check if close_date exists and calculate fiscal periods
        has_periods = 'close_date' in df_norm.columns
        
        if has_periods:
            # Convert close_date to datetime
            df_norm['close_date'] = pd.to_datetime(df_norm['close_date'], errors='coerce')
            
            # Calculate fiscal period from close_date
            df_norm['fiscal_period'] = df_norm['close_date'].apply(self.get_fiscal_quarter)
            
            # Convert metric columns to numeric first
            for metric in metrics:
                if metric in df_norm.columns:
                    df_norm[metric] = pd.to_numeric(df_norm[metric], errors='coerce').fillna(0)
            
            # Group by dimension and period
            group_cols = [group_by, 'fiscal_period']
            
            # Aggregate metrics
            agg_dict = {metric: 'sum' for metric in metrics}
            
            report_df = df_norm.groupby(group_cols).agg(agg_dict).reset_index()
            
            # Get unique periods and sort them
            unique_periods = sorted([p for p in report_df['fiscal_period'].unique() if p is not None])
            
            # Create a result dataframe with the grouping column
            result_df = report_df[[group_by]].drop_duplicates().reset_index(drop=True)
            
            # For each metric, create columns for each period
            for metric in metrics:
                # Pivot this metric
                pivot = report_df.pivot(index=group_by, columns='fiscal_period', values=metric)
                
                # Ensure columns are in sorted order and rename with metric name
                for period in unique_periods:
                    if period in pivot.columns:
                        col_name = f"{period}_{metric}"
                        result_df = result_df.merge(
                            pivot[[period]].rename(columns={period: col_name}),
                            left_on=group_by,
                            right_index=True,
                            how='left'
                        )
                
                # Calculate total for this metric
                metric_cols = [f"{period}_{metric}" for period in unique_periods if f"{period}_{metric}" in result_df.columns]
                if metric_cols:
                    # Ensure all metric columns are numeric
                    for col in metric_cols:
                        result_df[col] = pd.to_numeric(result_df[col], errors='coerce').fillna(0)
                    result_df[f'Total_{metric}'] = result_df[metric_cols].sum(axis=1)
            
            # Fill NaN with 0
            result_df = result_df.fillna(0)
            
        else:
            # Simple grouping without periods
            # Convert metric columns to numeric first
            for metric in metrics:
                if metric in df_norm.columns:
                    df_norm[metric] = pd.to_numeric(df_norm[metric], errors='coerce').fillna(0)
            
            agg_dict = {metric: 'sum' for metric in metrics}
            result_df = df_norm.groupby(group_by).agg(agg_dict).reset_index()
        
        return result_df
    
    def calculate_margin_percentage(self, df, revenue_col, margin_col):
        """Calculate margin percentage"""
        df_calc = df.copy()
        
        # Find revenue and margin columns
        revenue_cols = [col for col in df.columns if revenue_col in col]
        margin_cols = [col for col in df.columns if margin_col in col]
        
        # Calculate percentage for each period
        for rev_col, mar_col in zip(revenue_cols, margin_cols):
            pct_col = mar_col.replace(margin_col, f'{margin_col}_pct')
            df_calc[pct_col] = (df_calc[mar_col] / df_calc[rev_col] * 100).round(1)
        
        return df_calc
    
    def get_fiscal_quarter(self, date):
        """
        Convert a date to fiscal quarter based on April-March fiscal year
        Q1: April - June
        Q2: July - September
        Q3: October - December
        Q4: January - March
        """
        if pd.isna(date):
            return None
        
        month = date.month
        year = date.year
        
        # Determine fiscal year and quarter
        if month >= 4:  # April onwards
            fiscal_year = year + 1  # FY starts in April, so FY26 starts April 2025
            if 4 <= month <= 6:
                quarter = 'Q1'
            elif 7 <= month <= 9:
                quarter = 'Q2'
            else:  # 10-12
                quarter = 'Q3'
        else:  # January-March
            fiscal_year = year  # Still in previous FY
            quarter = 'Q4'
        
        return f"FY{str(fiscal_year)[-2:]}-{quarter}"
    
    def get_available_periods(self, df):
        """Get list of available periods from the data based on Close Date"""
        df_norm, _ = self.normalize_column_names(df)
        
        # Use close_date to calculate fiscal periods
        if 'close_date' in df_norm.columns:
            # Convert to datetime
            df_norm['close_date'] = pd.to_datetime(df_norm['close_date'], errors='coerce')
            
            # Calculate fiscal period for each row
            df_norm['fiscal_period'] = df_norm['close_date'].apply(self.get_fiscal_quarter)
            
            # Get unique periods and sort
            periods = sorted([p for p in df_norm['fiscal_period'].unique() if p is not None])
            return periods
        
        return []
    
    def parse_period(self, period_str):
        """Parse period string to extract year and quarter (e.g., 'FY26-Q2' -> ('FY26', 'Q2'))"""
        if '-' in period_str:
            parts = period_str.split('-')
            return parts[0], parts[1] if len(parts) > 1 else ''
        return period_str, ''
    
    def render_dynamic_report(self, df, scenario_name='Base Case', editable=True):
        """Render the dynamic reporting interface"""
        
        st.markdown(f"### 📊 Dynamic Reporting - {scenario_name}")
        
        # Detect available dimensions and metrics
        available_dimensions = self.detect_available_dimensions(df)
        available_metrics = self.detect_available_metrics(df)
        
        if not available_dimensions:
            st.error("❌ No grouping dimensions found. Please ensure your data has Account Name, Industry Vertical, or Product Name.")
            return None
        
        if not available_metrics:
            st.error("❌ No metrics found. Please ensure your data has Revenue TCV USD, IYR USD, or Margin USD.")
            return None
        
        # Get available periods
        available_periods = self.get_available_periods(df)
        
        # Selection controls
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**📊 Group By:**")
            selected_dimension = st.radio(
                "Select grouping dimension",
                options=list(available_dimensions.keys()),
                format_func=lambda x: available_dimensions[x],
                key=f"dimension_{scenario_name}",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**💰 Metrics to Display:**")
            selected_metrics = []
            for metric_key, metric_label in available_metrics.items():
                if st.checkbox(metric_label, value=True, key=f"metric_{metric_key}_{scenario_name}"):
                    selected_metrics.append(metric_key)
        
        with col3:
            st.markdown("**📅 Define Period:**")
            
            if available_periods:
                # From period
                from_period = st.selectbox(
                    "From:",
                    options=available_periods,
                    index=0,
                    key=f"from_period_{scenario_name}"
                )
                
                # To period
                to_period = st.selectbox(
                    "To:",
                    options=available_periods,
                    index=len(available_periods) - 1,
                    key=f"to_period_{scenario_name}"
                )
                
                # Get index positions
                from_idx = available_periods.index(from_period)
                to_idx = available_periods.index(to_period)
                
                # Ensure from is before or equal to to
                if from_idx <= to_idx:
                    filtered_periods = available_periods[from_idx:to_idx + 1]
                else:
                    st.warning("⚠️ 'From' period must be before or equal to 'To' period")
                    filtered_periods = [from_period]
            else:
                filtered_periods = []
                st.info("No period data available")
        
        if not selected_metrics:
            st.warning("⚠️ Please select at least one metric to display.")
            return None
        
        st.markdown("---")
        
        # Filter dataframe by selected periods
        if filtered_periods:
            df_filtered = df.copy()
            df_norm, _ = self.normalize_column_names(df_filtered)
            
            # Debug info in collapsible expander
            with st.expander("🔍 Debug Information", expanded=False):
                st.info(f"**Columns:** Found {len(df_norm.columns)} columns. TCV-related: {[c for c in df_norm.columns if 'tcv' in c.lower() or 'revenue' in c.lower()]}")
                
                # Debug: Check TCV column values
                if 'revenue_tcv_usd' in df_norm.columns:
                    tcv_col = df_norm['revenue_tcv_usd']
                    tcv_numeric = pd.to_numeric(tcv_col, errors='coerce')
                    st.info(f"**TCV Column:** Non-null: {tcv_col.notna().sum()}, Type: {tcv_col.dtype}, Sum: ${tcv_numeric.sum():,.0f}")
                    st.caption(f"Sample values: {tcv_col.head(5).tolist()}")
            
            if 'close_date' in df_norm.columns:
                # Convert close_date to datetime
                df_norm['close_date'] = pd.to_datetime(df_norm['close_date'], errors='coerce')
                
                # Calculate fiscal period from close_date
                df_norm['fiscal_period'] = df_norm['close_date'].apply(self.get_fiscal_quarter)
                
                # Debug: Show period distribution in expander
                with st.expander("🔍 Debug Information", expanded=False):
                    period_counts = df_norm['fiscal_period'].value_counts().sort_index()
                    st.info(f"**Data Periods:** {period_counts.to_dict()}")
                    st.info(f"**Selected Periods:** {filtered_periods}")
                    st.info(f"**Filtering:** {len(df)} rows → {len(df[df_norm['fiscal_period'].isin(filtered_periods)])} rows")
                
                # Filter to only include selected periods
                mask = df_norm['fiscal_period'].isin(filtered_periods)
                df_filtered = df[mask]
                
                if len(df_filtered) == 0:
                    st.warning("⚠️ No data available for selected periods.")
                    st.info("💡 Try selecting a wider period range or check your Close Date values")
                    return None
            else:
                st.warning("⚠️ Close Date column not found. Cannot filter by period.")
                return None
        else:
            st.warning("⚠️ Please select at least one period.")
            return None
        
        # Create report with filtered data
        report_df = self.create_dynamic_report(df_filtered, selected_dimension, selected_metrics)
        
        # Calculate margin percentages if both revenue and margin are selected
        if 'revenue_tcv_usd' in selected_metrics and 'margin_usd' in selected_metrics:
            report_df = self.calculate_margin_percentage(report_df, 'revenue_tcv_usd', 'margin_usd')
        
        # Display summary metrics
        st.markdown("**📈 Summary Metrics:**")
        
        summary_cols = st.columns(len(selected_metrics) + 1)
        
        with summary_cols[0]:
            dimension_label = available_dimensions[selected_dimension].replace('By ', '')
            st.metric(
                dimension_label,
                f"{len(report_df):,}",
                help=f"Number of unique {dimension_label.lower()}"
            )
        
        for idx, metric in enumerate(selected_metrics, 1):
            with summary_cols[idx]:
                total_col = f'Total_{metric}' if f'Total_{metric}' in report_df.columns else metric
                total_value = report_df[total_col].sum()
                st.metric(
                    available_metrics[metric],
                    f"${total_value:,.0f}",
                    help=f"Total {available_metrics[metric]}"
                )
        
        st.markdown("---")
        
        # Display editable table
        st.markdown("**📋 Detailed Report:**")
        
        # Format numbers in millions for display
        display_df = report_df.copy()
        
        # Apply millions formatting to numeric columns (except the grouping column)
        for col in display_df.columns:
            if col != selected_dimension and display_df[col].dtype in ['float64', 'int64']:
                # Check if it's a percentage column
                if 'pct' in col.lower() or '%' in col:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "0.00%")
                else:
                    # Format as millions
                    display_df[col] = display_df[col].apply(self.format_number_millions)
        
        # Format column names for display
        display_df.columns = [col.replace('_', ' ').title() for col in display_df.columns]
        
        if editable:
            # Note: Editing with formatted strings - will need to convert back
            st.info("💡 Tip: Values are displayed in millions (e.g., 3.10m = $3,100,000)")
            
            edited_df = st.data_editor(
                display_df,
                use_container_width=True,
                hide_index=True,
                num_rows="dynamic",
                key=f"dynamic_report_{scenario_name}_{selected_dimension}",
                disabled=[col.replace('_', ' ').title() for col in report_df.columns if col != selected_dimension]
            )
            
            # Convert back to original column names
            edited_df.columns = report_df.columns
            return edited_df
        else:
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            return report_df
    
    def get_report_data(self, scenario_name, dimension):
        """Get saved report data for a scenario and dimension"""
        key = f'dynamic_report_data_{scenario_name}_{dimension}'
        return st.session_state.get(key, None)
    
    def set_report_data(self, df, scenario_name, dimension):
        """Save report data for a scenario and dimension"""
        key = f'dynamic_report_data_{scenario_name}_{dimension}'
        st.session_state[key] = df
    
    def export_to_excel(self, df, filename='dynamic_report.xlsx'):
        """Export report to Excel"""
        import io
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Report', index=False)
            
            # Get workbook and worksheet
            workbook = writer.book
            worksheet = writer.sheets['Report']
            
            # Format currency columns
            currency_format = workbook.add_format({'num_format': '$#,##0'})
            percentage_format = workbook.add_format({'num_format': '0.0%'})
            
            for idx, col in enumerate(df.columns):
                if 'usd' in col.lower() or 'revenue' in col.lower() or 'margin' in col.lower():
                    if 'pct' not in col.lower():
                        worksheet.set_column(idx, idx, 15, currency_format)
                    else:
                        worksheet.set_column(idx, idx, 12, percentage_format)
        
        return output.getvalue()
