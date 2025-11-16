"""
Data Diagnostic View - Analyze data quality and structure
"""

import streamlit as st
import pandas as pd
import numpy as np

class DataDiagnosticView:
    """Diagnostic view to analyze data quality and identify issues"""
    
    def __init__(self):
        pass
    
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
    
    def render_diagnostic(self, df):
        """Render comprehensive data diagnostic"""
        
        st.markdown("### 🔍 Data Diagnostic Report")
        st.markdown("Analyze data quality, completeness, and structure")
        
        st.markdown("---")
        
        # Section 1: Column Detection
        st.markdown("#### 📋 Column Detection")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Key Columns Found:**")
            key_cols = {
                'TCV USD': self._find_column(df, ['tcv usd', 'tcv_usd', 'revenue tcv usd', 'revenue_tcv_usd', 'tcv']),
                'IYR USD': self._find_column(df, ['iyr usd', 'iyr_usd', 'iyr', 'in year revenue']),
                'Margin USD': self._find_column(df, ['margin usd', 'margin_usd', 'margin']),
                'Close Date': self._find_column(df, ['close date', 'close_date', 'closedate']),
                'Account Name': self._find_column(df, ['account name', 'account_name', 'accountname', 'account'])
            }
            
            for key, col in key_cols.items():
                if col:
                    st.success(f"✓ {key}: `{col}`")
                else:
                    st.error(f"✗ {key}: Not found")
        
        with col2:
            st.markdown("**Monthly Forecast Columns:**")
            forecast_cols = self._find_forecast_columns(df)
            if forecast_cols:
                st.success(f"✓ Found {len(forecast_cols)} forecast columns")
                st.caption(f"Range: {forecast_cols[0]} to {forecast_cols[-1]}")
            else:
                st.error("✗ No forecast columns found")
        
        st.markdown("---")
        
        # Section 2: Data Quality Metrics
        st.markdown("#### 📊 Data Quality Metrics")
        
        metrics_cols = st.columns(4)
        
        with metrics_cols[0]:
            st.metric("Total Rows", f"{len(df):,}")
        
        with metrics_cols[1]:
            st.metric("Total Columns", f"{len(df.columns):,}")
        
        with metrics_cols[2]:
            missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100)
            st.metric("Missing Values", f"{missing_pct:.1f}%")
        
        with metrics_cols[3]:
            duplicate_rows = df.duplicated().sum()
            st.metric("Duplicate Rows", f"{duplicate_rows:,}")
        
        st.markdown("---")
        
        # Section 3: TCV Analysis
        st.markdown("#### 💰 TCV USD Analysis")
        
        tcv_col = key_cols['TCV USD']
        if tcv_col:
            self._analyze_column(df, tcv_col, "TCV USD")
        else:
            st.error("❌ TCV USD column not found. Please check column mapping.")
            st.info("💡 Expected column names: 'TCV USD', 'tcv usd', 'Revenue TCV USD', 'revenue_tcv_usd'")
        
        st.markdown("---")
        
        # Section 4: IYR Analysis
        st.markdown("#### 💵 IYR USD Analysis")
        
        iyr_col = key_cols['IYR USD']
        if iyr_col:
            self._analyze_column(df, iyr_col, "IYR USD")
        else:
            st.warning("⚠️ IYR USD column not found")
        
        st.markdown("---")
        
        # Section 5: Forecast Columns Analysis
        st.markdown("#### 📈 Forecast Columns Analysis")
        
        if forecast_cols:
            self._analyze_forecast_columns(df, forecast_cols)
        else:
            st.error("❌ No forecast columns found")
            st.info("💡 Expected format: YYYY-MM (e.g., 2025-04, 2025-05)")
        
        st.markdown("---")
        
        # Section 6: Relationship Validation
        st.markdown("#### 🔗 Data Relationship Validation")
        
        if tcv_col and iyr_col:
            self._validate_relationships(df, tcv_col, iyr_col, forecast_cols)
        else:
            st.warning("⚠️ Cannot validate relationships - missing key columns")
        
        st.markdown("---")
        
        # Section 7: Sample Data
        st.markdown("#### 📋 Sample Data Preview")
        
        with st.expander("View First 10 Rows", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
        
        with st.expander("View Column List", expanded=False):
            col_df = pd.DataFrame({
                'Column Name': df.columns,
                'Data Type': df.dtypes.astype(str),
                'Non-Null Count': df.count(),
                'Null Count': df.isnull().sum(),
                'Null %': (df.isnull().sum() / len(df) * 100).round(2)
            })
            st.dataframe(col_df, use_container_width=True)
    
    def _find_column(self, df, possible_names):
        """Find column by checking multiple possible names"""
        for col in df.columns:
            col_lower = col.lower().replace(' ', '_')
            for name in possible_names:
                if name.lower().replace(' ', '_') == col_lower:
                    return col
        return None
    
    def _find_forecast_columns(self, df):
        """Find columns that match YYYY-MM format"""
        forecast_cols = []
        for col in df.columns:
            col_str = str(col)
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
    
    def _analyze_column(self, df, col_name, display_name):
        """Analyze a specific column"""
        
        col_data = df[col_name]
        
        analysis_cols = st.columns(4)
        
        with analysis_cols[0]:
            non_null = col_data.notna().sum()
            st.metric("Non-Null Values", f"{non_null:,}")
        
        with analysis_cols[1]:
            null_count = col_data.isnull().sum()
            st.metric("Null Values", f"{null_count:,}")
        
        with analysis_cols[2]:
            data_type = col_data.dtype
            st.metric("Data Type", str(data_type))
        
        with analysis_cols[3]:
            unique_count = col_data.nunique()
            st.metric("Unique Values", f"{unique_count:,}")
        
        # Try to convert to numeric and analyze
        try:
            numeric_data = pd.to_numeric(col_data, errors='coerce')
            
            if numeric_data.notna().sum() > 0:
                st.markdown("**Numeric Statistics:**")
                stats_cols = st.columns(5)
                
                with stats_cols[0]:
                    st.metric("Sum", self.format_number_millions(numeric_data.sum()))
                
                with stats_cols[1]:
                    st.metric("Mean", self.format_number_millions(numeric_data.mean()))
                
                with stats_cols[2]:
                    st.metric("Median", self.format_number_millions(numeric_data.median()))
                
                with stats_cols[3]:
                    st.metric("Min", self.format_number_millions(numeric_data.min()))
                
                with stats_cols[4]:
                    st.metric("Max", self.format_number_millions(numeric_data.max()))
            else:
                st.warning(f"⚠️ No numeric values found in {display_name}")
                st.info("💡 Values might be text. Click '🔧 Fix' on validation page to convert.")
        
        except Exception as e:
            st.error(f"❌ Error analyzing {display_name}: {str(e)}")
        
        # Show sample values
        with st.expander(f"Sample {display_name} Values", expanded=False):
            sample_df = pd.DataFrame({
                'Value': col_data.head(20),
                'Type': col_data.head(20).apply(lambda x: type(x).__name__)
            })
            st.dataframe(sample_df, use_container_width=True)
    
    def _analyze_forecast_columns(self, df, forecast_cols):
        """Analyze forecast columns"""
        
        st.markdown(f"**Found {len(forecast_cols)} forecast columns**")
        
        # Calculate total across all forecast columns
        total_forecast = 0
        numeric_cols = 0
        
        for col in forecast_cols:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce').fillna(0)
                total_forecast += numeric_data.sum()
                numeric_cols += 1
            except:
                continue
        
        metrics_cols = st.columns(4)
        
        with metrics_cols[0]:
            st.metric("Forecast Columns", f"{len(forecast_cols):,}")
        
        with metrics_cols[1]:
            st.metric("Numeric Columns", f"{numeric_cols:,}")
        
        with metrics_cols[2]:
            st.metric("Total Forecast", f"${total_forecast:,.0f}")
        
        with metrics_cols[3]:
            if len(forecast_cols) > 0:
                avg_per_col = total_forecast / len(forecast_cols)
                st.metric("Avg per Column", f"${avg_per_col:,.0f}")
        
        # Show date range
        if forecast_cols:
            st.info(f"📅 Forecast Range: {forecast_cols[0]} to {forecast_cols[-1]}")
    
    def _validate_relationships(self, df, tcv_col, iyr_col, forecast_cols):
        """Validate logical relationships between columns"""
        
        # Convert to numeric
        tcv_data = pd.to_numeric(df[tcv_col], errors='coerce').fillna(0)
        iyr_data = pd.to_numeric(df[iyr_col], errors='coerce').fillna(0)
        
        # Calculate forecast total
        forecast_total = pd.Series([0] * len(df))
        if forecast_cols:
            for col in forecast_cols:
                try:
                    forecast_total += pd.to_numeric(df[col], errors='coerce').fillna(0)
                except:
                    continue
        
        # Validation checks
        checks = []
        
        # Check 1: IYR <= TCV
        iyr_exceeds_tcv = (iyr_data > tcv_data) & (tcv_data > 0)
        checks.append({
            'Check': 'IYR ≤ TCV',
            'Passed': (~iyr_exceeds_tcv).sum(),
            'Failed': iyr_exceeds_tcv.sum(),
            'Status': '✓' if iyr_exceeds_tcv.sum() == 0 else '✗'
        })
        
        # Check 2: Forecast Total ≈ TCV (within 10%)
        if forecast_cols:
            forecast_variance = abs(forecast_total - tcv_data) / tcv_data.replace(0, 1)
            forecast_matches = (forecast_variance <= 0.1) | (tcv_data == 0)
            checks.append({
                'Check': 'Forecast ≈ TCV (±10%)',
                'Passed': forecast_matches.sum(),
                'Failed': (~forecast_matches).sum(),
                'Status': '✓' if (~forecast_matches).sum() < len(df) * 0.1 else '⚠️'
            })
        
        # Check 3: No negative values
        negative_tcv = (tcv_data < 0).sum()
        negative_iyr = (iyr_data < 0).sum()
        checks.append({
            'Check': 'No Negative Values',
            'Passed': len(df) - negative_tcv - negative_iyr,
            'Failed': negative_tcv + negative_iyr,
            'Status': '✓' if (negative_tcv + negative_iyr) == 0 else '✗'
        })
        
        # Display checks
        check_df = pd.DataFrame(checks)
        st.dataframe(check_df, use_container_width=True, hide_index=True)
        
        # Summary metrics
        st.markdown("**Relationship Summary:**")
        summary_cols = st.columns(3)
        
        with summary_cols[0]:
            total_tcv = tcv_data.sum()
            st.metric("Total TCV", f"${total_tcv:,.0f}")
        
        with summary_cols[1]:
            total_iyr = iyr_data.sum()
            st.metric("Total IYR", f"${total_iyr:,.0f}")
            if total_tcv > 0:
                iyr_pct = (total_iyr / total_tcv * 100)
                st.caption(f"{iyr_pct:.1f}% of TCV")
        
        with summary_cols[2]:
            if forecast_cols:
                total_forecast_sum = forecast_total.sum()
                st.metric("Total Forecast", f"${total_forecast_sum:,.0f}")
                if total_tcv > 0:
                    forecast_pct = (total_forecast_sum / total_tcv * 100)
                    st.caption(f"{forecast_pct:.1f}% of TCV")
