"""
Data Transformer - Converts transaction-level data to quarterly forecast format
Handles: Opportunity Created, Master Period, Reporting Period, Reporting Month, Close Date
"""

import pandas as pd
import numpy as np
from datetime import datetime

class DataTransformer:
    """Transform transaction-level data into quarterly forecast format"""
    
    def __init__(self):
        self.fiscal_quarters = {
            'Q1': [4, 5, 6],    # Apr, May, Jun
            'Q2': [7, 8, 9],    # Jul, Aug, Sep
            'Q3': [10, 11, 12], # Oct, Nov, Dec
            'Q4': [1, 2, 3]     # Jan, Feb, Mar
        }
    
    def detect_date_columns(self, df):
        """Detect date-related columns in the dataframe"""
        date_columns = []
        potential_names = [
            'opportunity created', 'master period', 'reporting period', 
            'reporting month', 'close date', 'created date', 'date',
            'period', 'month', 'quarter'
        ]
        
        for col in df.columns:
            col_lower = str(col).lower()
            if any(name in col_lower for name in potential_names):
                date_columns.append(col)
        
        return date_columns
    
    def detect_value_columns(self, df):
        """Detect numeric value columns (revenue, amount, etc.)"""
        value_columns = []
        potential_names = [
            'revenue', 'amount', 'value', 'forecast', 'budget',
            'sales', 'total', 'price', 'cost'
        ]
        
        # First, check for explicitly named columns
        for col in df.columns:
            col_lower = str(col).lower()
            if any(name in col_lower for name in potential_names):
                if pd.api.types.is_numeric_dtype(df[col]):
                    value_columns.append(col)
        
        # If no named columns found, use all numeric columns
        if not value_columns:
            value_columns = df.select_dtypes(include=['number']).columns.tolist()
        
        return value_columns
    
    def parse_period_to_date(self, period_str):
        """Convert period strings like 'FY26-Q2' to datetime"""
        try:
            if pd.isna(period_str):
                return None
            
            period_str = str(period_str).upper()
            
            # Handle FY26-Q2 format
            if 'FY' in period_str and 'Q' in period_str:
                parts = period_str.split('-')
                fy_part = parts[0].replace('FY', '20')  # FY26 -> 2026
                q_part = parts[1].replace('Q', '')      # Q2 -> 2
                
                year = int(fy_part)
                quarter = int(q_part)
                
                # Map quarter to month (using fiscal year Apr-Mar)
                quarter_start_months = {1: 4, 2: 7, 3: 10, 4: 1}
                month = quarter_start_months[quarter]
                
                # Adjust year for Q4 (Jan-Mar is next calendar year)
                if quarter == 4:
                    year += 1
                
                return pd.Timestamp(year=year, month=month, day=1)
            
            # Try parsing as regular date
            return pd.to_datetime(period_str, errors='coerce')
            
        except:
            return None
    
    def get_fiscal_quarter(self, date):
        """Get fiscal quarter (Q1-Q4) from a date"""
        if pd.isna(date):
            return None
        
        month = date.month
        
        for quarter, months in self.fiscal_quarters.items():
            if month in months:
                return quarter
        
        return None
    
    def get_fiscal_year(self, date):
        """Get fiscal year from a date (Apr-Mar)"""
        if pd.isna(date):
            return None
        
        # If month is Jan-Mar, it's part of previous fiscal year
        if date.month <= 3:
            return date.year - 1
        else:
            return date.year
    
    def transform_to_quarterly(self, df, date_column=None, value_column=None):
        """
        Transform transaction-level data to quarterly forecast format
        
        Args:
            df: Input dataframe with transaction-level data
            date_column: Column to use for date (auto-detected if None)
            value_column: Column to use for values (auto-detected if None)
        
        Returns:
            DataFrame in quarterly format with Line Item, Q1, Q2, Q3, Q4, FY columns
        """
        
        # Auto-detect columns if not provided
        if date_column is None:
            date_columns = self.detect_date_columns(df)
            if not date_columns:
                raise ValueError("No date columns detected. Please specify date_column parameter.")
            date_column = date_columns[0]  # Use first detected
        
        if value_column is None:
            value_columns = self.detect_value_columns(df)
            if not value_columns:
                raise ValueError("No numeric value columns detected. Please specify value_column parameter.")
            value_column = value_columns[0]  # Use first detected
        
        # Create working copy
        work_df = df.copy()
        
        # Parse dates
        if date_column in work_df.columns:
            # Try parsing as period first (FY26-Q2), then as regular date
            work_df['parsed_date'] = work_df[date_column].apply(self.parse_period_to_date)
            
            # If still no dates, try standard date parsing
            if work_df['parsed_date'].isna().all():
                work_df['parsed_date'] = pd.to_datetime(work_df[date_column], errors='coerce')
        
        # Remove rows with invalid dates
        work_df = work_df[work_df['parsed_date'].notna()]
        
        if len(work_df) == 0:
            raise ValueError(f"No valid dates found in column '{date_column}'")
        
        # Extract fiscal quarter and year
        work_df['fiscal_quarter'] = work_df['parsed_date'].apply(self.get_fiscal_quarter)
        work_df['fiscal_year'] = work_df['parsed_date'].apply(self.get_fiscal_year)
        
        # Aggregate by quarter
        quarterly_data = work_df.groupby('fiscal_quarter')[value_column].sum()
        
        # Create output dataframe
        output_data = {
            'Line Item': ['Revenue', 'Forecast Total'],
            'Q1': [
                quarterly_data.get('Q1', 0),
                quarterly_data.get('Q1', 0)
            ],
            'Q2': [
                quarterly_data.get('Q2', 0),
                quarterly_data.get('Q2', 0)
            ],
            'Q3': [
                quarterly_data.get('Q3', 0),
                quarterly_data.get('Q3', 0)
            ],
            'Q4': [
                quarterly_data.get('Q4', 0),
                quarterly_data.get('Q4', 0)
            ]
        }
        
        # Calculate FY total
        fy_total = sum(quarterly_data.values())
        output_data['FY'] = [fy_total, fy_total]
        
        result_df = pd.DataFrame(output_data)
        
        # Add metadata
        result_df.attrs['source_column'] = date_column
        result_df.attrs['value_column'] = value_column
        result_df.attrs['record_count'] = len(work_df)
        result_df.attrs['date_range'] = f"{work_df['parsed_date'].min()} to {work_df['parsed_date'].max()}"
        
        return result_df
    
    def get_transformation_summary(self, df, result_df):
        """Get summary of the transformation"""
        summary = {
            'input_rows': len(df),
            'output_rows': len(result_df),
            'date_column': result_df.attrs.get('source_column', 'Unknown'),
            'value_column': result_df.attrs.get('value_column', 'Unknown'),
            'records_processed': result_df.attrs.get('record_count', 0),
            'date_range': result_df.attrs.get('date_range', 'Unknown'),
            'q1_total': result_df['Q1'].iloc[0] if len(result_df) > 0 else 0,
            'q2_total': result_df['Q2'].iloc[0] if len(result_df) > 0 else 0,
            'q3_total': result_df['Q3'].iloc[0] if len(result_df) > 0 else 0,
            'q4_total': result_df['Q4'].iloc[0] if len(result_df) > 0 else 0,
            'fy_total': result_df['FY'].iloc[0] if len(result_df) > 0 else 0
        }
        return summary
    
    def create_detailed_quarterly_view(self, df, date_column=None, group_by_column=None):
        """
        Create detailed quarterly view with multiple line items
        
        Args:
            df: Input dataframe
            date_column: Column to use for dates
            group_by_column: Column to group by (e.g., 'Industry Segment', 'Sales Stage')
        
        Returns:
            DataFrame with multiple line items grouped by specified column
        """
        
        # Auto-detect columns
        if date_column is None:
            date_columns = self.detect_date_columns(df)
            date_column = date_columns[0] if date_columns else None
        
        if group_by_column is None:
            # Try to find a categorical column
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            if categorical_cols:
                group_by_column = categorical_cols[0]
        
        value_columns = self.detect_value_columns(df)
        value_column = value_columns[0] if value_columns else None
        
        if not all([date_column, value_column]):
            raise ValueError("Could not detect required columns")
        
        # Parse dates
        work_df = df.copy()
        work_df['parsed_date'] = work_df[date_column].apply(self.parse_period_to_date)
        if work_df['parsed_date'].isna().all():
            work_df['parsed_date'] = pd.to_datetime(work_df[date_column], errors='coerce')
        
        work_df = work_df[work_df['parsed_date'].notna()]
        work_df['fiscal_quarter'] = work_df['parsed_date'].apply(self.get_fiscal_quarter)
        
        # Group by category and quarter
        if group_by_column and group_by_column in work_df.columns:
            grouped = work_df.groupby([group_by_column, 'fiscal_quarter'])[value_column].sum().unstack(fill_value=0)
        else:
            # Just aggregate by quarter
            grouped = work_df.groupby('fiscal_quarter')[value_column].sum()
            grouped = pd.DataFrame({'Total': grouped}).T
        
        # Ensure all quarters exist
        for q in ['Q1', 'Q2', 'Q3', 'Q4']:
            if q not in grouped.columns:
                grouped[q] = 0
        
        # Calculate FY total
        grouped['FY'] = grouped[['Q1', 'Q2', 'Q3', 'Q4']].sum(axis=1)
        
        # Reset index to make group column a regular column
        grouped = grouped.reset_index()
        grouped.columns.name = None
        
        # Rename first column to 'Line Item'
        grouped.rename(columns={grouped.columns[0]: 'Line Item'}, inplace=True)
        
        # Reorder columns
        column_order = ['Line Item', 'Q1', 'Q2', 'Q3', 'Q4', 'FY']
        grouped = grouped[column_order]
        
        return grouped
