"""
Accounting View - Standard P&L format with editable forecasts
"""

import streamlit as st
import pandas as pd
import numpy as np

class AccountingView:
    """Standard accounting view with P&L hierarchy and editable forecasts"""
    
    def __init__(self):
        self.pl_structure = {
            'REVENUE': {
                'children': ['Services Revenue', 'Product Revenue', 'Other Revenue'],
                'total': 'Total Revenue',
                'format': 'currency'
            },
            'COST OF REVENUE': {
                'children': ['Services COGS', 'Product COGS', 'Other COGS'],
                'total': 'Total COGS',
                'format': 'currency'
            },
            'GROSS MARGIN': {
                'calculation': 'Total Revenue - Total COGS',
                'format': 'currency'
            },
            'GROSS MARGIN %': {
                'calculation': '(Gross Margin / Total Revenue) * 100',
                'format': 'percentage'
            },
            'OPERATING EXPENSES': {
                'children': ['Sales & Marketing', 'R&D', 'G&A', 'Other OPEX'],
                'total': 'Total OPEX',
                'format': 'currency'
            },
            'EBITDA': {
                'calculation': 'Gross Margin - Total OPEX',
                'format': 'currency'
            },
            'EBITDA %': {
                'calculation': '(EBITDA / Total Revenue) * 100',
                'format': 'percentage'
            }
        }
    
    def create_pl_template(self, periods=['Q1', 'Q2', 'Q3', 'Q4', 'FY']):
        """Create a P&L template dataframe"""
        
        line_items = [
            # Revenue
            'Services Revenue',
            'Product Revenue', 
            'Other Revenue',
            'Total Revenue',
            '',  # Blank line
            # COGS
            'Services COGS',
            'Product COGS',
            'Other COGS',
            'Total COGS',
            '',  # Blank line
            # Margins
            'Gross Margin',
            'Gross Margin %',
            '',  # Blank line
            # OPEX
            'Sales & Marketing',
            'R&D',
            'G&A',
            'Other OPEX',
            'Total OPEX',
            '',  # Blank line
            # Bottom line
            'EBITDA',
            'EBITDA %'
        ]
        
        # Create dataframe with zeros
        data = {'Line Item': line_items}
        for period in periods:
            data[period] = [0.0] * len(line_items)
        
        df = pd.DataFrame(data)
        return df
    
    def transform_to_pl_format(self, df):
        """Transform uploaded data to P&L format"""
        
        # Check if data is already in P&L format
        if 'Line Item' in df.columns:
            return df
        
        # Otherwise, create template and try to map
        pl_df = self.create_pl_template()
        
        # Try to find revenue row
        if 'Revenue' in df.index or 'Total Revenue' in df.index:
            # Data might be in index
            df_reset = df.reset_index()
            if 'index' in df_reset.columns:
                df_reset = df_reset.rename(columns={'index': 'Line Item'})
            return df_reset
        
        return pl_df
    
    def calculate_totals(self, df):
        """Calculate totals and derived metrics"""
        
        df_calc = df.copy()
        periods = [col for col in df.columns if col != 'Line Item']
        
        for period in periods:
            # Skip if not numeric
            if not pd.api.types.is_numeric_dtype(df_calc[period]):
                continue
            
            # Revenue totals
            if 'Services Revenue' in df_calc['Line Item'].values:
                services_idx = df_calc[df_calc['Line Item'] == 'Services Revenue'].index[0]
                product_idx = df_calc[df_calc['Line Item'] == 'Product Revenue'].index[0]
                other_idx = df_calc[df_calc['Line Item'] == 'Other Revenue'].index[0]
                total_idx = df_calc[df_calc['Line Item'] == 'Total Revenue'].index[0]
                
                total_revenue = (
                    df_calc.loc[services_idx, period] +
                    df_calc.loc[product_idx, period] +
                    df_calc.loc[other_idx, period]
                )
                df_calc.loc[total_idx, period] = total_revenue
            
            # COGS totals
            if 'Services COGS' in df_calc['Line Item'].values:
                services_cogs_idx = df_calc[df_calc['Line Item'] == 'Services COGS'].index[0]
                product_cogs_idx = df_calc[df_calc['Line Item'] == 'Product COGS'].index[0]
                other_cogs_idx = df_calc[df_calc['Line Item'] == 'Other COGS'].index[0]
                total_cogs_idx = df_calc[df_calc['Line Item'] == 'Total COGS'].index[0]
                
                total_cogs = (
                    df_calc.loc[services_cogs_idx, period] +
                    df_calc.loc[product_cogs_idx, period] +
                    df_calc.loc[other_cogs_idx, period]
                )
                df_calc.loc[total_cogs_idx, period] = total_cogs
            
            # Gross Margin
            if all(item in df_calc['Line Item'].values for item in ['Total Revenue', 'Total COGS', 'Gross Margin']):
                revenue_idx = df_calc[df_calc['Line Item'] == 'Total Revenue'].index[0]
                cogs_idx = df_calc[df_calc['Line Item'] == 'Total COGS'].index[0]
                margin_idx = df_calc[df_calc['Line Item'] == 'Gross Margin'].index[0]
                
                gross_margin = df_calc.loc[revenue_idx, period] - df_calc.loc[cogs_idx, period]
                df_calc.loc[margin_idx, period] = gross_margin
                
                # Gross Margin %
                if 'Gross Margin %' in df_calc['Line Item'].values:
                    margin_pct_idx = df_calc[df_calc['Line Item'] == 'Gross Margin %'].index[0]
                    if df_calc.loc[revenue_idx, period] != 0:
                        margin_pct = (gross_margin / df_calc.loc[revenue_idx, period]) * 100
                        df_calc.loc[margin_pct_idx, period] = margin_pct
            
            # OPEX totals
            if 'Sales & Marketing' in df_calc['Line Item'].values:
                sm_idx = df_calc[df_calc['Line Item'] == 'Sales & Marketing'].index[0]
                rd_idx = df_calc[df_calc['Line Item'] == 'R&D'].index[0]
                ga_idx = df_calc[df_calc['Line Item'] == 'G&A'].index[0]
                other_opex_idx = df_calc[df_calc['Line Item'] == 'Other OPEX'].index[0]
                total_opex_idx = df_calc[df_calc['Line Item'] == 'Total OPEX'].index[0]
                
                total_opex = (
                    df_calc.loc[sm_idx, period] +
                    df_calc.loc[rd_idx, period] +
                    df_calc.loc[ga_idx, period] +
                    df_calc.loc[other_opex_idx, period]
                )
                df_calc.loc[total_opex_idx, period] = total_opex
            
            # EBITDA
            if all(item in df_calc['Line Item'].values for item in ['Gross Margin', 'Total OPEX', 'EBITDA']):
                margin_idx = df_calc[df_calc['Line Item'] == 'Gross Margin'].index[0]
                opex_idx = df_calc[df_calc['Line Item'] == 'Total OPEX'].index[0]
                ebitda_idx = df_calc[df_calc['Line Item'] == 'EBITDA'].index[0]
                
                ebitda = df_calc.loc[margin_idx, period] - df_calc.loc[opex_idx, period]
                df_calc.loc[ebitda_idx, period] = ebitda
                
                # EBITDA %
                if 'EBITDA %' in df_calc['Line Item'].values:
                    ebitda_pct_idx = df_calc[df_calc['Line Item'] == 'EBITDA %'].index[0]
                    revenue_idx = df_calc[df_calc['Line Item'] == 'Total Revenue'].index[0]
                    if df_calc.loc[revenue_idx, period] != 0:
                        ebitda_pct = (ebitda / df_calc.loc[revenue_idx, period]) * 100
                        df_calc.loc[ebitda_pct_idx, period] = ebitda_pct
        
        return df_calc
    
    def format_pl_dataframe(self, df):
        """Format P&L dataframe for display"""
        
        df_display = df.copy()
        
        # Format numbers
        for col in df_display.columns:
            if col == 'Line Item':
                continue
            
            if pd.api.types.is_numeric_dtype(df_display[col]):
                # Check if it's a percentage row
                line_items = df_display['Line Item'].values
                for idx, item in enumerate(line_items):
                    if '%' in str(item):
                        # Format as percentage
                        df_display.loc[idx, col] = f"{df_display.loc[idx, col]:.1f}%"
                    elif str(item).strip() == '':
                        # Blank line
                        df_display.loc[idx, col] = ''
                    else:
                        # Format as currency
                        val = df_display.loc[idx, col]
                        if pd.notna(val) and val != 0:
                            df_display.loc[idx, col] = f"${val:,.1f}M"
                        else:
                            df_display.loc[idx, col] = '-'
        
        return df_display
    
    def render_accounting_view(self, df, scenario_name, assumptions, editable=True):
        """Render the accounting view with proper data validation and transformation"""
        
        st.markdown("### 📊 Accounting View - P&L Format")
        
        # Check if data is in expected P&L format
        if 'Line Item' not in df.columns:
            st.error("❌ **Data Format Error**")
            st.markdown("""
            The Accounting View requires data in P&L (Profit & Loss) format with a 'Line Item' column.
            
            **Expected format:**
            - Column: 'Line Item' (containing accounting line items)
            - Columns: Period columns (Q1, Q2, Q3, Q4, FY, etc.)
            - Rows: Revenue, COGS, Expenses, etc.
            
            **Current data columns:** """ + ", ".join(df.columns.tolist()))
            
            st.markdown("---")
            st.markdown("**💡 Solution:** Use the Revenue Forecasting or Dynamic Reporting views first, or ensure your data is in proper P&L format.")
            
            # Offer to create a template
            if st.button("📄 Create P&L Template", type="primary"):
                template_df = self.create_pl_template()
                st.success("✅ P&L template created! You can now edit it below.")
                
                # Show the template
                st.markdown("### 📋 P&L Template")
                st.dataframe(template_df, use_container_width=True)
                
                # Allow download
                csv = template_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Template CSV",
                    data=csv,
                    file_name="pl_template.csv",
                    mime="text/csv",
                    key="download_template"
                )
                
                st.markdown("""
                **Instructions:**
                1. Download the template CSV
                2. Fill in your P&L data
                3. Upload it through the data foundation workflow
                4. Return to this Accounting View
                """)
            
            # Don't proceed if data format is wrong
            return None
        
        # Data is in correct format, proceed with rendering
        return self._render_accounting_view_internal(df, scenario_name, assumptions, editable)
    
    def _render_accounting_view_internal(self, df, scenario_name, assumptions, editable=True):
        """Render the accounting view interface"""
        
        st.markdown(f"### 📊 Accounting View - P&L Statement")
        st.markdown(f"**Scenario:** {scenario_name}")
        
        # Controls
        col1, col2, col3 = st.columns([2, 2, 8])
        
        with col1:
            units = st.selectbox("Units", ["$M", "$K", "$"], key=f"units_{scenario_name}")
        
        with col2:
            view_mode = st.radio("Mode", ["View", "Edit"], key=f"mode_{scenario_name}", horizontal=True)
        
        st.markdown("---")
        
        # Ensure calculations are up to date
        df_calc = self.calculate_totals(df)
        
        if view_mode == "Edit" and editable:
            # Editable mode
            st.markdown("**📝 Edit Mode** - Click cells to edit values. Totals will auto-calculate.")
            
            # Configure column types for st.data_editor
            column_config = {
                'Line Item': st.column_config.TextColumn(
                    'Line Item',
                    width='medium',
                    disabled=True
                )
            }
            
            # Add config for each period column
            periods = [col for col in df_calc.columns if col != 'Line Item']
            for period in periods:
                column_config[period] = st.column_config.NumberColumn(
                    period,
                    format="%.2f",
                    width='small'
                )
            
            # Editable data editor
            edited_df = st.data_editor(
                df_calc,
                column_config=column_config,
                hide_index=True,
                use_container_width=True,
                height=600,
                key=f"pl_editor_{scenario_name}"
            )
            
            # Recalculate after edits
            if st.button("🔄 Recalculate Totals", key=f"recalc_{scenario_name}"):
                edited_df = self.calculate_totals(edited_df)
                st.session_state[f'pl_data_{scenario_name}'] = edited_df
                st.success("✅ Totals recalculated!")
                st.rerun()
            
            # Store edited data
            st.session_state[f'pl_data_{scenario_name}'] = edited_df
            
        else:
            # View mode - formatted display
            df_display = self.format_pl_dataframe(df_calc)
            
            # Style the dataframe
            def highlight_totals(row):
                if any(keyword in str(row['Line Item']).lower() for keyword in ['total', 'ebitda', 'margin']):
                    return ['background-color: #f0f2f6; font-weight: bold'] * len(row)
                elif row['Line Item'] == '':
                    return ['background-color: white'] * len(row)
                else:
                    return [''] * len(row)
            
            styled_df = df_display.style.apply(highlight_totals, axis=1)
            
            st.dataframe(
                styled_df,
                hide_index=True,
                use_container_width=True,
                height=600
            )
        
        # Key metrics summary
        st.markdown("---")
        st.markdown("### 📈 Key Metrics")
        
        metrics_cols = st.columns(5)
        
        # Extract FY values if available
        if 'FY' in df_calc.columns:
            revenue_idx = df_calc[df_calc['Line Item'] == 'Total Revenue'].index
            margin_idx = df_calc[df_calc['Line Item'] == 'Gross Margin %'].index
            ebitda_idx = df_calc[df_calc['Line Item'] == 'EBITDA'].index
            ebitda_pct_idx = df_calc[df_calc['Line Item'] == 'EBITDA %'].index
            
            with metrics_cols[0]:
                if len(revenue_idx) > 0:
                    revenue = df_calc.loc[revenue_idx[0], 'FY']
                    st.metric("FY Revenue", f"${revenue:,.1f}M")
            
            with metrics_cols[1]:
                if len(margin_idx) > 0:
                    margin_pct = df_calc.loc[margin_idx[0], 'FY']
                    st.metric("Gross Margin %", f"{margin_pct:.1f}%")
            
            with metrics_cols[2]:
                if len(ebitda_idx) > 0:
                    ebitda = df_calc.loc[ebitda_idx[0], 'FY']
                    st.metric("EBITDA", f"${ebitda:,.1f}M")
            
            with metrics_cols[3]:
                if len(ebitda_pct_idx) > 0:
                    ebitda_pct = df_calc.loc[ebitda_pct_idx[0], 'FY']
                    st.metric("EBITDA %", f"{ebitda_pct:.1f}%")
            
            with metrics_cols[4]:
                # Calculate growth if Q4 and Q1 available
                if 'Q1' in df_calc.columns and 'Q4' in df_calc.columns and len(revenue_idx) > 0:
                    q1_rev = df_calc.loc[revenue_idx[0], 'Q1']
                    q4_rev = df_calc.loc[revenue_idx[0], 'Q4']
                    if q1_rev != 0:
                        growth = ((q4_rev - q1_rev) / q1_rev) * 100
                        st.metric("Q1-Q4 Growth", f"{growth:+.1f}%")
        
        return df_calc
    
    def get_pl_data(self, scenario_name='Base Case'):
        """Get P&L data for a scenario"""
        key = f'pl_data_{scenario_name}'
        if key in st.session_state:
            return st.session_state[key]
        return None
    
    def set_pl_data(self, df, scenario_name='Base Case'):
        """Set P&L data for a scenario"""
        key = f'pl_data_{scenario_name}'
        st.session_state[key] = df
