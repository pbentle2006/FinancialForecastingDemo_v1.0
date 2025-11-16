"""
Data Validation Engine - Comprehensive validation and reconciliation
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

class DataValidationEngine:
    """Comprehensive data validation and reconciliation engine"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.auto_fixes = []
    
    def apply_fix(self, df, issue):
        """
        Apply automatic fix to the dataframe based on the issue
        
        Args:
            df: DataFrame to fix
            issue: Issue dict with column, message, and fix information
        
        Returns:
            bool: True if fix was applied successfully
        """
        try:
            # Extract column name from the issue
            if 'column' not in issue:
                return False
            
            column = issue['column']
            message = issue['message'].lower()
            
            # Fix 1: Convert to numeric
            if 'should be numeric' in message or 'is object' in message:
                df[column] = pd.to_numeric(df[column], errors='coerce')
                # Fill NaN with 0 for numeric columns
                df[column] = df[column].fillna(0)
                
                # Update session state with fixed dataframe
                if 'mapped_df' in st.session_state:
                    st.session_state.mapped_df = df
                
                return True
            
            # Fix 2: Convert percentage to decimal
            elif 'outside 0-100% range' in message or 'decimal format' in message:
                # Check if values are in percentage format (0-100)
                max_val = df[column].max()
                if max_val > 1:
                    # Convert from percentage to decimal
                    df[column] = df[column] / 100
                    
                    # Update session state
                    if 'mapped_df' in st.session_state:
                        st.session_state.mapped_df = df
                    
                    return True
            
            # Fix 3: Remove outliers (cap at reasonable values)
            elif 'outliers detected' in message:
                # Calculate IQR and cap outliers
                Q1 = df[column].quantile(0.25)
                Q3 = df[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 3 * IQR
                upper_bound = Q3 + 3 * IQR
                
                # Cap values at bounds
                df[column] = df[column].clip(lower=lower_bound, upper=upper_bound)
                
                # Update session state
                if 'mapped_df' in st.session_state:
                    st.session_state.mapped_df = df
                
                return True
            
            # Fix 4: Fill missing values
            elif 'missing values' in message:
                # Fill with 0 for numeric columns
                if pd.api.types.is_numeric_dtype(df[column]):
                    df[column] = df[column].fillna(0)
                else:
                    df[column] = df[column].fillna('Unknown')
                
                # Update session state
                if 'mapped_df' in st.session_state:
                    st.session_state.mapped_df = df
                
                return True
            
            return False
            
        except Exception as e:
            st.error(f"Error applying fix: {str(e)}")
            return False
    
    def validate_data(self, df, data_type='quarterly'):
        """
        Run comprehensive validation checks
        
        Args:
            df: DataFrame to validate
            data_type: 'quarterly' or 'transaction'
        
        Returns:
            dict with validation results
        """
        
        self.errors = []
        self.warnings = []
        self.passed = []
        self.auto_fixes = []
        
        # Data quality checks
        self._check_missing_values(df)
        self._check_data_types(df)
        self._check_value_ranges(df)
        self._check_duplicates(df)
        
        # Type-specific checks
        if data_type == 'quarterly':
            self._check_quarterly_reconciliation(df)
            self._check_quarterly_calculations(df)
        else:
            self._check_transaction_consistency(df)
        
        # Calculate quality score
        total_checks = len(self.errors) + len(self.warnings) + len(self.passed)
        score = (len(self.passed) / total_checks * 100) if total_checks > 0 else 0
        
        return {
            'score': score,
            'errors': self.errors,
            'warnings': self.warnings,
            'passed': self.passed,
            'auto_fixes': self.auto_fixes,
            'total_checks': total_checks
        }
    
    def _check_missing_values(self, df):
        """Check for missing values in all columns"""
        for col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100
            
            if missing_count > 0:
                if missing_pct > 20:
                    self.errors.append({
                        'type': 'missing_values',
                        'severity': 'error',
                        'column': col,
                        'message': f"Column '{col}': {missing_pct:.1f}% missing values ({missing_count} rows)",
                        'fix': f"Remove rows or fill with average/median"
                    })
                elif missing_pct > 5:
                    self.warnings.append({
                        'type': 'missing_values',
                        'severity': 'warning',
                        'column': col,
                        'message': f"Column '{col}': {missing_pct:.1f}% missing values ({missing_count} rows)",
                        'fix': f"Consider filling missing values"
                    })
                else:
                    self.passed.append(f"Column '{col}': Acceptable missing rate ({missing_pct:.1f}%)")
            else:
                self.passed.append(f"Column '{col}': No missing values ✓")
    
    def _check_data_types(self, df):
        """Check if data types are appropriate"""
        for col in df.columns:
            col_lower = col.lower()
            
            # Check numeric columns
            if any(keyword in col_lower for keyword in ['amount', 'revenue', 'value', 'q1', 'q2', 'q3', 'q4', 'fy']):
                if not pd.api.types.is_numeric_dtype(df[col]):
                    self.errors.append({
                        'type': 'data_type',
                        'severity': 'error',
                        'column': col,
                        'message': f"Column '{col}' should be numeric but is {df[col].dtype}",
                        'fix': f"Convert to numeric using pd.to_numeric()"
                    })
                else:
                    self.passed.append(f"Column '{col}': Correct numeric type ✓")
            
            # Check date columns
            elif any(keyword in col_lower for keyword in ['date', 'period']):
                if not pd.api.types.is_datetime64_any_dtype(df[col]) and df[col].dtype != 'object':
                    self.warnings.append({
                        'type': 'data_type',
                        'severity': 'warning',
                        'column': col,
                        'message': f"Column '{col}' may need date conversion (currently {df[col].dtype})",
                        'fix': f"Convert to datetime using pd.to_datetime()"
                    })
    
    def _check_value_ranges(self, df):
        """Check if values are within reasonable ranges"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_lower = col.lower()
            
            # Check for negative values in revenue/amount columns
            if any(keyword in col_lower for keyword in ['revenue', 'amount', 'value']):
                negative_count = (df[col] < 0).sum()
                if negative_count > 0:
                    self.warnings.append({
                        'type': 'value_range',
                        'severity': 'warning',
                        'column': col,
                        'message': f"Column '{col}': {negative_count} negative values found",
                        'fix': f"Review negative values - may indicate returns or adjustments"
                    })
                else:
                    self.passed.append(f"Column '{col}': All values positive ✓")
            
            # Check for percentage columns
            if '%' in col or 'percent' in col_lower or 'margin' in col_lower:
                out_of_range = ((df[col] < 0) | (df[col] > 100)).sum()
                if out_of_range > 0:
                    self.warnings.append({
                        'type': 'value_range',
                        'severity': 'warning',
                        'column': col,
                        'message': f"Column '{col}': {out_of_range} values outside 0-100% range",
                        'fix': f"Check if values are in decimal format (0-1) vs percentage (0-100)"
                    })
            
            # Check for outliers
            if len(df) > 10:
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                outliers = ((df[col] < (q1 - 3 * iqr)) | (df[col] > (q3 + 3 * iqr))).sum()
                
                if outliers > 0:
                    self.warnings.append({
                        'type': 'outliers',
                        'severity': 'warning',
                        'column': col,
                        'message': f"Column '{col}': {outliers} potential outliers detected",
                        'fix': f"Review extreme values for data entry errors"
                    })
    
    def _check_duplicates(self, df):
        """Check for duplicate rows"""
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count > 0:
            self.warnings.append({
                'type': 'duplicates',
                'severity': 'warning',
                'message': f"{duplicate_count} duplicate rows found",
                'fix': f"Remove duplicates using df.drop_duplicates()"
            })
        else:
            self.passed.append(f"No duplicate rows ✓")
    
    def _check_quarterly_reconciliation(self, df):
        """Check if quarterly totals match FY totals"""
        if all(col in df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY']):
            for idx, row in df.iterrows():
                try:
                    q1 = float(row['Q1']) if pd.notna(row['Q1']) else 0
                    q2 = float(row['Q2']) if pd.notna(row['Q2']) else 0
                    q3 = float(row['Q3']) if pd.notna(row['Q3']) else 0
                    q4 = float(row['Q4']) if pd.notna(row['Q4']) else 0
                    fy = float(row['FY']) if pd.notna(row['FY']) else 0
                    
                    calculated_fy = q1 + q2 + q3 + q4
                    diff = abs(calculated_fy - fy)
                    
                    # Allow 0.1% tolerance for rounding
                    tolerance = abs(fy * 0.001) if fy != 0 else 0.01
                    
                    if diff > tolerance:
                        line_item = row.get('Line Item', f'Row {idx}')
                        self.errors.append({
                            'type': 'reconciliation',
                            'severity': 'error',
                            'row': idx,
                            'message': f"{line_item}: Q1+Q2+Q3+Q4 ({calculated_fy:.2f}) ≠ FY ({fy:.2f}), Diff: {diff:.2f}",
                            'fix': f"Recalculate FY as sum of quarters"
                        })
                        
                        # Suggest auto-fix
                        self.auto_fixes.append({
                            'row': idx,
                            'column': 'FY',
                            'current_value': fy,
                            'suggested_value': calculated_fy,
                            'reason': 'Reconcile quarterly totals'
                        })
                    else:
                        line_item = row.get('Line Item', f'Row {idx}')
                        self.passed.append(f"{line_item}: Quarterly totals reconcile ✓")
                
                except (ValueError, TypeError) as e:
                    self.warnings.append({
                        'type': 'reconciliation',
                        'severity': 'warning',
                        'row': idx,
                        'message': f"Row {idx}: Cannot validate reconciliation - {str(e)}",
                        'fix': f"Check data types in quarterly columns"
                    })
        else:
            self.warnings.append({
                'type': 'reconciliation',
                'severity': 'warning',
                'message': "Quarterly columns (Q1, Q2, Q3, Q4, FY) not all present",
                'fix': "Ensure all quarterly columns exist for reconciliation"
            })
    
    def _check_quarterly_calculations(self, df):
        """Check calculated fields like margins"""
        # Check margin calculations
        if all(col in df.columns for col in ['Revenue', 'Margin', 'Margin%']):
            for idx, row in df.iterrows():
                try:
                    revenue = float(row['Revenue']) if pd.notna(row['Revenue']) else 0
                    margin = float(row['Margin']) if pd.notna(row['Margin']) else 0
                    margin_pct = float(row['Margin%']) if pd.notna(row['Margin%']) else 0
                    
                    if revenue > 0:
                        calculated_margin_pct = (margin / revenue) * 100
                        diff = abs(calculated_margin_pct - margin_pct)
                        
                        if diff > 0.5:  # Allow 0.5% tolerance
                            line_item = row.get('Line Item', f'Row {idx}')
                            self.warnings.append({
                                'type': 'calculation',
                                'severity': 'warning',
                                'row': idx,
                                'message': f"{line_item}: Margin% calculation off by {diff:.2f}%",
                                'fix': f"Recalculate as (Margin / Revenue) * 100"
                            })
                        else:
                            line_item = row.get('Line Item', f'Row {idx}')
                            self.passed.append(f"{line_item}: Margin% calculation correct ✓")
                
                except (ValueError, TypeError, ZeroDivisionError):
                    pass
    
    def _check_transaction_consistency(self, df):
        """Check consistency in transaction-level data"""
        # Check date ranges
        if 'date_period' in df.columns:
            try:
                dates = pd.to_datetime(df['date_period'], errors='coerce')
                valid_dates = dates.notna().sum()
                invalid_dates = dates.isna().sum()
                
                if invalid_dates > 0:
                    self.warnings.append({
                        'type': 'date_consistency',
                        'severity': 'warning',
                        'message': f"{invalid_dates} rows with invalid dates",
                        'fix': "Review and correct date formats"
                    })
                else:
                    self.passed.append(f"All dates are valid ✓")
                
                # Check date range
                if valid_dates > 0:
                    min_date = dates.min()
                    max_date = dates.max()
                    date_range = (max_date - min_date).days
                    
                    if date_range > 1825:  # More than 5 years
                        self.warnings.append({
                            'type': 'date_consistency',
                            'severity': 'warning',
                            'message': f"Date range spans {date_range} days ({date_range/365:.1f} years)",
                            'fix': "Verify date range is correct"
                        })
            
            except Exception as e:
                self.warnings.append({
                    'type': 'date_consistency',
                    'severity': 'warning',
                    'message': f"Cannot validate dates: {str(e)}",
                    'fix': "Check date column format"
                })
    
    def render_validation_results(self, results, df=None):
        """Render validation results in Streamlit"""
        
        st.markdown("### ⚙️ Validation Results")
        
        # Score display
        score = results['score']
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if score >= 90:
                st.metric("Quality Score", f"{score:.0f}/100", delta="Excellent", delta_color="normal")
            elif score >= 70:
                st.metric("Quality Score", f"{score:.0f}/100", delta="Good", delta_color="normal")
            elif score >= 50:
                st.metric("Quality Score", f"{score:.0f}/100", delta="Fair", delta_color="inverse")
            else:
                st.metric("Quality Score", f"{score:.0f}/100", delta="Poor", delta_color="inverse")
        
        with col2:
            st.metric("Errors", len(results['errors']), delta=None)
        
        with col3:
            st.metric("Warnings", len(results['warnings']), delta=None)
        
        with col4:
            st.metric("Passed", len(results['passed']), delta=None)
        
        st.markdown("---")
        
        # Errors with action buttons
        if results['errors']:
            with st.expander(f"🔴 ERRORS ({len(results['errors'])}) - Must Fix", expanded=True):
                # Fix All button at the top
                if df is not None:
                    col_btn, col_info = st.columns([1, 3])
                    with col_btn:
                        if st.button("🔧 Fix All Errors", key="fix_all_errors", type="primary", use_container_width=True):
                            fixed_count = 0
                            for error in results['errors']:
                                if self.apply_fix(df, error):
                                    fixed_count += 1
                            
                            if fixed_count > 0:
                                st.success(f"✓ Applied {fixed_count} fixes!")
                                st.session_state.fix_applied = True
                                st.rerun()
                            else:
                                st.warning("No fixes could be applied automatically")
                    
                    with col_info:
                        st.info(f"💡 Click to automatically fix all {len(results['errors'])} errors at once")
                    
                    st.markdown("---")
                
                for i, error in enumerate(results['errors'], 1):
                    col_msg, col_btn1, col_btn2 = st.columns([3, 1, 1])
                    
                    with col_msg:
                        st.error(f"**{i}.** {error['message']}")
                        st.caption(f"💡 Suggested Action: {error['fix']}")
                    
                    with col_btn1:
                        if st.button("🔧 Fix", key=f"fix_error_{i}", type="primary"):
                            # Apply the fix
                            if self.apply_fix(df, error):
                                st.success("✓ Fix applied!")
                                st.session_state.fix_applied = True
                                st.rerun()
                            else:
                                st.error("Could not apply fix automatically")
                    
                    with col_btn2:
                        if st.button("🔍 Review", key=f"review_error_{i}"):
                            st.session_state[f'reviewing_error_{i}'] = True
                    
                    # Show review details if clicked
                    if st.session_state.get(f'reviewing_error_{i}', False):
                        with st.container():
                            st.info(f"**Investigation Required:**\n\n{error['fix']}")
                            if 'column' in error:
                                st.markdown(f"**Affected Column:** `{error['column']}`")
                            if 'row' in error:
                                st.markdown(f"**Affected Row:** {error['row']}")
                            if st.button("✓ Mark as Reviewed", key=f"mark_error_{i}"):
                                st.session_state[f'reviewing_error_{i}'] = False
                                st.rerun()
                    
                    if i < len(results['errors']):
                        st.markdown("---")
        
        # Warnings with action buttons
        if results['warnings']:
            with st.expander(f"🟡 WARNINGS ({len(results['warnings'])}) - Review Recommended", expanded=False):
                # Fix All button at the top
                if df is not None:
                    col_btn, col_info = st.columns([1, 3])
                    with col_btn:
                        if st.button("🔧 Fix All Warnings", key="fix_all_warnings", type="secondary", use_container_width=True):
                            fixed_count = 0
                            for warning in results['warnings']:
                                if self.apply_fix(df, warning):
                                    fixed_count += 1
                            
                            if fixed_count > 0:
                                st.success(f"✓ Applied {fixed_count} fixes!")
                                st.session_state.fix_applied = True
                                st.rerun()
                            else:
                                st.warning("No fixes could be applied automatically")
                    
                    with col_info:
                        st.info(f"💡 Click to automatically fix all {len(results['warnings'])} warnings at once")
                    
                    st.markdown("---")
                
                for i, warning in enumerate(results['warnings'], 1):
                    col_msg, col_btn1, col_btn2 = st.columns([3, 1, 1])
                    
                    with col_msg:
                        st.warning(f"**{i}.** {warning['message']}")
                        st.caption(f"💡 Suggested Action: {warning['fix']}")
                    
                    with col_btn1:
                        if st.button("🔧 Fix", key=f"fix_warning_{i}", type="primary"):
                            # Apply the fix
                            if self.apply_fix(df, warning):
                                st.success("✓ Fix applied!")
                                st.session_state.fix_applied = True
                                st.rerun()
                            else:
                                st.error("Could not apply fix automatically")
                    
                    with col_btn2:
                        if st.button("🔍 Review", key=f"review_warning_{i}"):
                            st.session_state[f'reviewing_warning_{i}'] = True
                    
                    # Show review details if clicked
                    if st.session_state.get(f'reviewing_warning_{i}', False):
                        with st.container():
                            st.info(f"**Investigation Recommended:**\n\n{warning['fix']}")
                            if 'column' in warning:
                                st.markdown(f"**Affected Column:** `{warning['column']}`")
                            if 'row' in warning:
                                st.markdown(f"**Affected Row:** {warning['row']}")
                            if st.button("✓ Mark as Reviewed", key=f"mark_warning_{i}"):
                                st.session_state[f'reviewing_warning_{i}'] = False
                                st.rerun()
                    
                    if i < len(results['warnings']):
                        st.markdown("---")
        
        # Auto-fixes
        if results['auto_fixes']:
            with st.expander(f"🔧 AUTO-FIX SUGGESTIONS ({len(results['auto_fixes'])})", expanded=False):
                st.info("Click 'Apply Auto-Fixes' to automatically correct these issues")
                for fix in results['auto_fixes']:
                    st.markdown(f"**Row {fix['row']}**, Column `{fix['column']}`")
                    st.markdown(f"- Current: `{fix['current_value']}`")
                    st.markdown(f"- Suggested: `{fix['suggested_value']}`")
                    st.caption(f"Reason: {fix['reason']}")
                    st.markdown("---")
        
        # Passed checks
        with st.expander(f"🟢 PASSED ({len(results['passed'])} checks)", expanded=False):
            # Show first 20
            for passed in results['passed'][:20]:
                st.success(passed)
            if len(results['passed']) > 20:
                st.info(f"... and {len(results['passed']) - 20} more passed checks")
        
        return results
    
    def apply_auto_fixes(self, df, auto_fixes):
        """Apply suggested auto-fixes to dataframe"""
        df_fixed = df.copy()
        
        for fix in auto_fixes:
            row = fix['row']
            col = fix['column']
            new_value = fix['suggested_value']
            
            df_fixed.at[row, col] = new_value
        
        return df_fixed
    
    def calculate_data_summary(self, df):
        """Calculate summary statistics for the data"""
        summary = {}
        
        # Total Revenue (TCV)
        if 'revenue_tcv_usd' in df.columns:
            summary['total_revenue'] = pd.to_numeric(df['revenue_tcv_usd'], errors='coerce').fillna(0).sum()
        elif 'Revenue TCV USD' in df.columns:
            summary['total_revenue'] = pd.to_numeric(df['Revenue TCV USD'], errors='coerce').fillna(0).sum()
        else:
            # Try to find any revenue column
            revenue_cols = [col for col in df.columns if 'revenue' in col.lower() or 'tcv' in col.lower()]
            if revenue_cols:
                summary['total_revenue'] = pd.to_numeric(df[revenue_cols[0]], errors='coerce').fillna(0).sum()
            else:
                summary['total_revenue'] = 0
        
        # Number of Clients (unique account names)
        if 'account_name' in df.columns:
            summary['num_clients'] = df['account_name'].nunique()
        elif 'Account Name' in df.columns:
            summary['num_clients'] = df['Account Name'].nunique()
        else:
            # Try to find account column
            account_cols = [col for col in df.columns if 'account' in col.lower() or 'client' in col.lower() or 'customer' in col.lower()]
            if account_cols:
                summary['num_clients'] = df[account_cols[0]].nunique()
            else:
                summary['num_clients'] = 0
        
        # Number of Industry Verticals
        if 'industry_vertical' in df.columns:
            summary['num_industries'] = df['industry_vertical'].nunique()
        elif 'Industry Vertical' in df.columns:
            summary['num_industries'] = df['Industry Vertical'].nunique()
        else:
            # Try to find industry column
            industry_cols = [col for col in df.columns if 'industry' in col.lower() or 'vertical' in col.lower() or 'sector' in col.lower()]
            if industry_cols:
                summary['num_industries'] = df[industry_cols[0]].nunique()
            else:
                summary['num_industries'] = 0
        
        # Number of Products
        if 'product_name' in df.columns:
            summary['num_products'] = df['product_name'].nunique()
        elif 'Product Name' in df.columns:
            summary['num_products'] = df['Product Name'].nunique()
        else:
            # Try to find product column
            product_cols = [col for col in df.columns if 'product' in col.lower()]
            if product_cols:
                summary['num_products'] = df[product_cols[0]].nunique()
            else:
                summary['num_products'] = 0
        
        # Number of Sales Stages
        if 'sales_stage' in df.columns:
            summary['num_stages'] = df['sales_stage'].nunique()
        elif 'Sales Stage' in df.columns:
            summary['num_stages'] = df['Sales Stage'].nunique()
        else:
            # Try to find stage column
            stage_cols = [col for col in df.columns if 'stage' in col.lower() or 'status' in col.lower()]
            if stage_cols:
                summary['num_stages'] = df[stage_cols[0]].nunique()
            else:
                summary['num_stages'] = 0
        
        # Total number of records
        summary['total_records'] = len(df)
        
        return summary
    
    def render_data_summary(self, df):
        """Render data summary section"""
        st.markdown("### 📊 Data Summary")
        
        summary = self.calculate_data_summary(df)
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric(
                "Total Revenue (TCV)",
                f"${summary['total_revenue']:,.0f}",
                help="Sum of all Revenue TCV USD values"
            )
        
        with col2:
            st.metric(
                "Number of Clients",
                f"{summary['num_clients']:,}",
                help="Count of unique Account Names"
            )
        
        with col3:
            st.metric(
                "Industry Verticals",
                f"{summary['num_industries']:,}",
                help="Count of unique Industry Verticals"
            )
        
        with col4:
            st.metric(
                "Products",
                f"{summary['num_products']:,}",
                help="Count of unique Product Names"
            )
        
        with col5:
            st.metric(
                "Sales Stages",
                f"{summary['num_stages']:,}",
                help="Count of unique Sales Stages"
            )
        
        with col6:
            st.metric(
                "Total Records",
                f"{summary['total_records']:,}",
                help="Total number of rows in dataset"
            )
        
        # Additional breakdown
        with st.expander("📋 Detailed Breakdown", expanded=False):
            breakdown_col1, breakdown_col2 = st.columns(2)
            
            with breakdown_col1:
                # Top clients by revenue
                if 'account_name' in df.columns or 'Account Name' in df.columns:
                    account_col = 'account_name' if 'account_name' in df.columns else 'Account Name'
                    revenue_col = 'revenue_tcv_usd' if 'revenue_tcv_usd' in df.columns else 'Revenue TCV USD'
                    
                    if revenue_col in df.columns:
                        st.markdown("**Top 5 Clients by Revenue:**")
                        # Convert to numeric before grouping
                        df_numeric = df.copy()
                        df_numeric[revenue_col] = pd.to_numeric(df_numeric[revenue_col], errors='coerce').fillna(0)
                        top_clients = df_numeric.groupby(account_col)[revenue_col].sum().sort_values(ascending=False).head(5)
                        for client, revenue in top_clients.items():
                            st.markdown(f"- {client}: ${revenue:,.0f}")
            
            with breakdown_col2:
                # Revenue by industry
                if 'industry_vertical' in df.columns or 'Industry Vertical' in df.columns:
                    industry_col = 'industry_vertical' if 'industry_vertical' in df.columns else 'Industry Vertical'
                    revenue_col = 'revenue_tcv_usd' if 'revenue_tcv_usd' in df.columns else 'Revenue TCV USD'
                    
                    if revenue_col in df.columns:
                        st.markdown("**Revenue by Industry:**")
                        # Convert to numeric before grouping
                        df_numeric = df.copy()
                        df_numeric[revenue_col] = pd.to_numeric(df_numeric[revenue_col], errors='coerce').fillna(0)
                        industry_revenue = df_numeric.groupby(industry_col)[revenue_col].sum().sort_values(ascending=False)
                        for industry, revenue in industry_revenue.items():
                            st.markdown(f"- {industry}: ${revenue:,.0f}")
