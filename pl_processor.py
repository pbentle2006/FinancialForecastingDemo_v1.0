import pandas as pd
import numpy as np
from datetime import datetime
import re

class PLDataProcessor:
    """Process and analyze Profit & Loss data"""
    
    def __init__(self):
        self.pl_categories = {
            'revenue': ['revenue', 'sales', 'income', 'turnover', 'receipts'],
            'cogs': ['cogs', 'cost of goods', 'cost of sales', 'direct costs'],
            'gross_profit': ['gross profit', 'gross margin', 'gp'],
            'operating_expenses': ['opex', 'operating expense', 'overhead', 'sga'],
            'ebitda': ['ebitda', 'operating income', 'operating profit'],
            'depreciation': ['depreciation', 'amortization', 'd&a', 'da'],
            'ebit': ['ebit', 'earnings before interest'],
            'interest': ['interest', 'finance cost', 'interest expense'],
            'tax': ['tax', 'income tax', 'taxation'],
            'net_income': ['net income', 'net profit', 'net earnings', 'bottom line', 'profit after tax']
        }
    
    def find_pl_columns(self, df):
        """Detect P&L line items and monthly columns"""
        
        # Find the line item column (usually first text column)
        line_item_col = None
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check if it contains P&L keywords
                sample_values = df[col].dropna().astype(str).str.lower()
                if any(keyword in ' '.join(sample_values.values) for keywords in self.pl_categories.values() for keyword in keywords):
                    line_item_col = col
                    break
        
        # Find monthly/period columns
        monthly_cols = self._find_monthly_columns(df)
        
        # Categorize line items
        categorized_items = self._categorize_line_items(df, line_item_col) if line_item_col else {}
        
        return {
            'line_item_column': line_item_col,
            'monthly_columns': monthly_cols,
            'categorized_items': categorized_items
        }
    
    def _find_monthly_columns(self, df):
        """Find monthly/period columns in P&L data"""
        monthly_patterns = [
            r'FY\d{4}-\d{2}',  # FY2025-04
            r'\d{4}-\d{2}',    # 2025-04
            r'Q[1-4].*\d{4}',  # Q1 2025
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*\d{4}',  # Jan 2025
            r'(January|February|March|April|May|June|July|August|September|October|November|December).*\d{4}'
        ]
        
        monthly_cols = []
        current_year = datetime.now().year
        
        for col in df.columns:
            col_str = str(col)
            
            # Check if column name matches date patterns
            if any(re.search(pattern, col_str, re.IGNORECASE) for pattern in monthly_patterns):
                try:
                    # Check if column contains numeric data
                    numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                    if numeric_count > 0:
                        year = self._extract_year_from_column(col_str)
                        monthly_cols.append({
                            'name': col,
                            'year': year,
                            'is_future': year > current_year,
                            'is_historical': year <= current_year
                        })
                except:
                    continue
        
        return monthly_cols
    
    def _extract_year_from_column(self, col_str):
        """Extract year from column name"""
        year_match = re.search(r'(202[0-9]|203[0-9])', col_str)
        if year_match:
            return int(year_match.group(1))
        return datetime.now().year
    
    def _categorize_line_items(self, df, line_item_col):
        """Categorize P&L line items"""
        if not line_item_col or line_item_col not in df.columns:
            return {}
        
        categorized = {}
        
        for idx, row in df.iterrows():
            line_item = str(row[line_item_col]).lower().strip()
            
            for category, keywords in self.pl_categories.items():
                if any(keyword in line_item for keyword in keywords):
                    if category not in categorized:
                        categorized[category] = []
                    categorized[category].append({
                        'row_index': idx,
                        'line_item': row[line_item_col],
                        'original_text': line_item
                    })
                    break
        
        return categorized
    
    def create_pl_mapping_interface(self, df, detection_results):
        """Create mapping interface for P&L data"""
        import streamlit as st
        
        st.markdown("### 💰 P&L Data Column Mapping")
        
        col_options = ["[Skip this field]"] + list(df.columns)
        
        # Line item column
        st.markdown("**📋 Core P&L Fields:**")
        col1, col2 = st.columns(2)
        
        with col1:
            line_item_default = detection_results.get('line_item_column', '[Skip this field]')
            if line_item_default and line_item_default in col_options:
                default_idx = col_options.index(line_item_default)
            else:
                default_idx = 0
            
            line_item_col = st.selectbox(
                "📝 Line Item / Account Name",
                col_options,
                index=default_idx,
                key="pl_line_item",
                help="Column containing P&L line item names (Revenue, COGS, etc.)"
            )
        
        with col2:
            entity_col = st.selectbox(
                "🏢 Entity / Department",
                col_options,
                key="pl_entity",
                help="Optional: Column for entity or department breakdown"
            )
        
        # Show detected categories
        if detection_results.get('categorized_items'):
            with st.expander("🔍 Detected P&L Line Items"):
                for category, items in detection_results['categorized_items'].items():
                    st.markdown(f"**{category.replace('_', ' ').title()}:**")
                    for item in items[:3]:  # Show first 3 items per category
                        st.write(f"  • {item['line_item']}")
        
        # Monthly columns info
        monthly_cols = detection_results.get('monthly_columns', [])
        if monthly_cols:
            historical_cols = [col for col in monthly_cols if col['is_historical']]
            future_cols = [col for col in monthly_cols if col['is_future']]
            
            st.success(f"✅ **{len(monthly_cols)} monthly columns detected in P&L data**")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"📊 **Historical periods**: {len(historical_cols)} columns")
            with col2:
                st.info(f"🔮 **Future periods**: {len(future_cols)} columns")
        
        # Create mapping
        mapping = {
            'line_item': line_item_col if line_item_col != "[Skip this field]" else None,
            'entity': entity_col if entity_col != "[Skip this field]" else None
        }
        
        return mapping, monthly_cols
    
    def process_pl_data(self, df, mapping, monthly_cols):
        """Process P&L data into structured format"""
        
        if not mapping.get('line_item'):
            raise ValueError("Line item column must be mapped")
        
        line_item_col = mapping['line_item']
        entity_col = mapping.get('entity')
        
        # Process P&L data
        pl_data = []
        
        for idx, row in df.iterrows():
            line_item = row[line_item_col]
            entity = row[entity_col] if entity_col else "Default"
            
            # Skip empty line items
            if pd.isna(line_item) or str(line_item).strip() == '':
                continue
            
            # Categorize the line item
            category = self._get_line_item_category(str(line_item))
            
            # Extract monthly values
            for col_info in monthly_cols:
                col = col_info['name']
                value = row[col]
                
                if pd.notna(value):
                    try:
                        amount = float(value)
                        year, month = self._parse_date_from_column(col)
                        
                        pl_data.append({
                            'entity': entity,
                            'line_item': line_item,
                            'category': category,
                            'year': year,
                            'month': month,
                            'period': f"{year}-{month:02d}",
                            'amount': amount,
                            'is_historical': col_info['is_historical'],
                            'is_future': col_info['is_future']
                        })
                    except:
                        continue
        
        pl_df = pd.DataFrame(pl_data)
        
        # Calculate derived metrics
        summary_df = self._calculate_pl_summary(pl_df)
        
        return pl_df, summary_df
    
    def _get_line_item_category(self, line_item):
        """Categorize a line item"""
        line_item_lower = line_item.lower()
        
        for category, keywords in self.pl_categories.items():
            if any(keyword in line_item_lower for keyword in keywords):
                return category
        
        return 'other'
    
    def _parse_date_from_column(self, col_name):
        """Parse year and month from column name"""
        col_str = str(col_name)
        
        # Try FY format
        if 'FY' in col_str and '-' in col_str:
            try:
                parts = col_str.split('-')
                year = int(parts[0].replace('FY', ''))
                month = int(parts[1])
                return year, month
            except:
                pass
        
        # Try YYYY-MM format
        if '-' in col_str:
            try:
                parts = col_str.split('-')
                if len(parts) >= 2:
                    year = int(parts[0])
                    month = int(parts[1])
                    return year, month
            except:
                pass
        
        return datetime.now().year, 1
    
    def _calculate_pl_summary(self, pl_df):
        """Calculate P&L summary metrics by period"""
        
        if pl_df.empty:
            return pd.DataFrame()
        
        # Group by period and category
        summary = pl_df.groupby(['period', 'category']).agg({
            'amount': 'sum'
        }).reset_index()
        
        # Pivot to get categories as columns
        summary_pivot = summary.pivot(index='period', columns='category', values='amount').fillna(0)
        
        # Calculate derived metrics
        if 'revenue' in summary_pivot.columns and 'cogs' in summary_pivot.columns:
            summary_pivot['calculated_gross_profit'] = summary_pivot['revenue'] - summary_pivot['cogs']
            summary_pivot['gross_margin_%'] = (summary_pivot['calculated_gross_profit'] / summary_pivot['revenue'] * 100).round(2)
        
        if 'revenue' in summary_pivot.columns and 'net_income' in summary_pivot.columns:
            summary_pivot['net_margin_%'] = (summary_pivot['net_income'] / summary_pivot['revenue'] * 100).round(2)
        
        summary_pivot = summary_pivot.reset_index()
        
        return summary_pivot
    
    def aggregate_forecast_and_pl(self, forecast_df, pl_df):
        """Aggregate forecast revenue data with P&L data"""
        
        # Aggregate forecast revenue by period
        forecast_summary = forecast_df.groupby('period').agg({
            'revenue': 'sum',
            'project_id': 'nunique'
        }).reset_index()
        forecast_summary.columns = ['period', 'forecast_revenue', 'project_count']
        
        # Get P&L revenue by period
        pl_revenue = pl_df[pl_df['category'] == 'revenue'].groupby('period').agg({
            'amount': 'sum'
        }).reset_index()
        pl_revenue.columns = ['period', 'pl_revenue']
        
        # Merge datasets
        combined = forecast_summary.merge(pl_revenue, on='period', how='outer').fillna(0)
        
        # Calculate variance
        combined['variance'] = combined['forecast_revenue'] - combined['pl_revenue']
        combined['variance_%'] = ((combined['variance'] / combined['pl_revenue']) * 100).round(2)
        combined['variance_%'] = combined['variance_%'].replace([np.inf, -np.inf], 0)
        
        return combined
    
    def generate_integrated_insights(self, forecast_df, pl_df, pl_summary_df):
        """Generate insights from combined forecast and P&L data"""
        
        insights = {
            'summary_metrics': {},
            'variance_analysis': {},
            'profitability_analysis': {},
            'recommendations': []
        }
        
        # Summary metrics
        total_forecast_revenue = forecast_df['revenue'].sum()
        total_pl_revenue = pl_df[pl_df['category'] == 'revenue']['amount'].sum()
        
        insights['summary_metrics'] = {
            'total_forecast_revenue': total_forecast_revenue,
            'total_pl_revenue': total_pl_revenue,
            'revenue_variance': total_forecast_revenue - total_pl_revenue,
            'revenue_variance_%': ((total_forecast_revenue - total_pl_revenue) / total_pl_revenue * 100) if total_pl_revenue > 0 else 0
        }
        
        # Profitability analysis
        if not pl_summary_df.empty:
            avg_gross_margin = pl_summary_df.get('gross_margin_%', pd.Series([0])).mean()
            avg_net_margin = pl_summary_df.get('net_margin_%', pd.Series([0])).mean()
            
            insights['profitability_analysis'] = {
                'avg_gross_margin_%': avg_gross_margin,
                'avg_net_margin_%': avg_net_margin,
                'profitability_trend': 'improving' if avg_net_margin > 10 else 'needs_attention'
            }
        
        # Generate recommendations
        if insights['summary_metrics']['revenue_variance_%'] > 10:
            insights['recommendations'].append({
                'type': 'warning',
                'message': 'Forecast revenue significantly exceeds P&L actuals',
                'action': 'Review forecast assumptions and pipeline probability'
            })
        
        if insights['profitability_analysis'].get('avg_net_margin_%', 0) < 5:
            insights['recommendations'].append({
                'type': 'alert',
                'message': 'Low net profit margin detected',
                'action': 'Focus on cost optimization and pricing strategy'
            })
        
        return insights
