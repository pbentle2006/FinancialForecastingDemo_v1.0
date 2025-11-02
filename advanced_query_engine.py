import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import re

class QueryCondition:
    """Represents a single query condition"""
    
    def __init__(self, field: str, operator: str, value: Any, logic: str = 'AND'):
        self.field = field
        self.operator = operator  # '=', '!=', '>', '<', '>=', '<=', 'contains', 'in', 'between'
        self.value = value
        self.logic = logic  # 'AND', 'OR'
    
    def apply(self, df: pd.DataFrame) -> pd.Series:
        """Apply condition to dataframe and return boolean mask"""
        
        if self.field not in df.columns:
            return pd.Series([True] * len(df), index=df.index)
        
        column = df[self.field]
        
        if self.operator == '=':
            return column == self.value
        elif self.operator == '!=':
            return column != self.value
        elif self.operator == '>':
            return column > self.value
        elif self.operator == '<':
            return column < self.value
        elif self.operator == '>=':
            return column >= self.value
        elif self.operator == '<=':
            return column <= self.value
        elif self.operator == 'contains':
            return column.astype(str).str.contains(str(self.value), case=False, na=False)
        elif self.operator == 'in':
            return column.isin(self.value if isinstance(self.value, list) else [self.value])
        elif self.operator == 'between':
            if isinstance(self.value, (list, tuple)) and len(self.value) == 2:
                return (column >= self.value[0]) & (column <= self.value[1])
        
        return pd.Series([True] * len(df), index=df.index)

class AdvancedQueryEngine:
    """Advanced query engine for data filtering and analysis"""
    
    def __init__(self):
        self.saved_queries = {}
        self.query_history = []
        
    def create_query(self, conditions: List[QueryCondition]) -> 'Query':
        """Create a new query with multiple conditions"""
        return Query(conditions, self)
    
    def save_query(self, name: str, query: 'Query'):
        """Save a query for reuse"""
        self.saved_queries[name] = query
        
    def load_query(self, name: str) -> Optional['Query']:
        """Load a saved query"""
        return self.saved_queries.get(name)
    
    def get_available_fields(self, df: pd.DataFrame) -> Dict[str, str]:
        """Get available fields and their types"""
        field_types = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            if 'int' in dtype or 'float' in dtype:
                field_types[col] = 'numeric'
            elif 'datetime' in dtype:
                field_types[col] = 'datetime'
            elif 'bool' in dtype:
                field_types[col] = 'boolean'
            else:
                field_types[col] = 'text'
        return field_types
    
    def suggest_filters(self, df: pd.DataFrame, target_field: str = 'revenue') -> List[Dict]:
        """Suggest useful filters based on data analysis"""
        suggestions = []
        
        # Revenue-based suggestions
        if target_field in df.columns:
            revenue_stats = df[target_field].describe()
            
            suggestions.append({
                'name': 'High Revenue Projects',
                'description': f'Projects with revenue > ${revenue_stats["75%"]:,.0f}',
                'conditions': [QueryCondition(target_field, '>', revenue_stats['75%'])]
            })
            
            suggestions.append({
                'name': 'Low Revenue Projects',
                'description': f'Projects with revenue < ${revenue_stats["25%"]:,.0f}',
                'conditions': [QueryCondition(target_field, '<', revenue_stats['25%'])]
            })
        
        # Time-based suggestions
        if 'year' in df.columns:
            current_year = datetime.now().year
            suggestions.append({
                'name': 'Current Year',
                'description': f'Data from {current_year}',
                'conditions': [QueryCondition('year', '=', current_year)]
            })
            
            suggestions.append({
                'name': 'Historical Data',
                'description': f'Data before {current_year}',
                'conditions': [QueryCondition('year', '<', current_year)]
            })
        
        # Business dimension suggestions
        for dim in ['offering', 'industry', 'sales_org']:
            if dim in df.columns:
                top_values = df[dim].value_counts().head(3).index.tolist()
                for value in top_values:
                    suggestions.append({
                        'name': f'Top {dim.title()}: {value}',
                        'description': f'Filter by {dim}: {value}',
                        'conditions': [QueryCondition(dim, '=', value)]
                    })
        
        return suggestions
    
    def create_dynamic_segments(self, df: pd.DataFrame, 
                              segment_field: str = 'revenue') -> Dict[str, List[QueryCondition]]:
        """Create dynamic segments based on data distribution"""
        
        if segment_field not in df.columns:
            return {}
        
        # Calculate quartiles
        quartiles = df[segment_field].quantile([0.25, 0.5, 0.75])
        
        segments = {
            'High Performers': [QueryCondition(segment_field, '>', quartiles[0.75])],
            'Medium Performers': [
                QueryCondition(segment_field, '>', quartiles[0.25]),
                QueryCondition(segment_field, '<=', quartiles[0.75], 'AND')
            ],
            'Low Performers': [QueryCondition(segment_field, '<=', quartiles[0.25])],
            'Top Quartile': [QueryCondition(segment_field, '>', quartiles[0.75])],
            'Bottom Quartile': [QueryCondition(segment_field, '<=', quartiles[0.25])]
        }
        
        return segments

class Query:
    """Represents a complex query with multiple conditions"""
    
    def __init__(self, conditions: List[QueryCondition], engine: AdvancedQueryEngine):
        self.conditions = conditions
        self.engine = engine
        self.name = None
        self.description = None
    
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Execute query on dataframe"""
        
        if not self.conditions:
            return df
        
        # Start with the first condition
        mask = self.conditions[0].apply(df)
        
        # Apply subsequent conditions with their logic operators
        for condition in self.conditions[1:]:
            condition_mask = condition.apply(df)
            
            if condition.logic == 'AND':
                mask = mask & condition_mask
            elif condition.logic == 'OR':
                mask = mask | condition_mask
        
        # Record query execution
        self.engine.query_history.append({
            'timestamp': datetime.now(),
            'conditions': len(self.conditions),
            'results': mask.sum()
        })
        
        return df[mask]
    
    def add_condition(self, condition: QueryCondition):
        """Add a condition to the query"""
        self.conditions.append(condition)
    
    def remove_condition(self, index: int):
        """Remove a condition by index"""
        if 0 <= index < len(self.conditions):
            self.conditions.pop(index)
    
    def get_summary(self) -> str:
        """Get human-readable summary of query"""
        if not self.conditions:
            return "No filters applied"
        
        summary_parts = []
        for i, condition in enumerate(self.conditions):
            if i > 0:
                summary_parts.append(f" {condition.logic} ")
            
            summary_parts.append(f"{condition.field} {condition.operator} {condition.value}")
        
        return "".join(summary_parts)

class DataAnalyzer:
    """Advanced data analysis capabilities"""
    
    def __init__(self):
        self.analysis_cache = {}
    
    def analyze_filtered_data(self, df: pd.DataFrame, 
                            comparison_df: pd.DataFrame = None) -> Dict:
        """Comprehensive analysis of filtered data"""
        
        analysis = {
            'summary_stats': self._calculate_summary_stats(df),
            'distribution_analysis': self._analyze_distribution(df),
            'trend_analysis': self._analyze_trends(df),
            'outlier_detection': self._detect_outliers(df)
        }
        
        # Comparative analysis if comparison data provided
        if comparison_df is not None:
            analysis['comparative_analysis'] = self._compare_datasets(df, comparison_df)
        
        return analysis
    
    def _calculate_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Calculate comprehensive summary statistics"""
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = {}
        
        for col in numeric_cols:
            col_stats = df[col].describe()
            stats[col] = {
                'count': col_stats['count'],
                'mean': col_stats['mean'],
                'median': col_stats['50%'],
                'std': col_stats['std'],
                'min': col_stats['min'],
                'max': col_stats['max'],
                'q1': col_stats['25%'],
                'q3': col_stats['75%'],
                'cv': col_stats['std'] / col_stats['mean'] if col_stats['mean'] != 0 else 0
            }
        
        return stats
    
    def _analyze_distribution(self, df: pd.DataFrame) -> Dict:
        """Analyze data distribution patterns"""
        
        distribution = {}
        
        # Categorical distributions
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            value_counts = df[col].value_counts()
            distribution[col] = {
                'unique_values': len(value_counts),
                'top_values': value_counts.head(5).to_dict(),
                'concentration': value_counts.iloc[0] / len(df) if len(value_counts) > 0 else 0
            }
        
        return distribution
    
    def _analyze_trends(self, df: pd.DataFrame) -> Dict:
        """Analyze temporal trends in data"""
        
        trends = {}
        
        # Time-based analysis
        if 'year' in df.columns and 'month' in df.columns:
            df_copy = df.copy()
            df_copy['period'] = pd.to_datetime(df_copy[['year', 'month']].assign(day=1))
            
            # Revenue trends
            if 'revenue' in df.columns:
                monthly_revenue = df_copy.groupby('period')['revenue'].sum()
                
                if len(monthly_revenue) > 1:
                    # Calculate growth rates
                    growth_rates = monthly_revenue.pct_change().dropna()
                    
                    trends['revenue'] = {
                        'total_periods': len(monthly_revenue),
                        'avg_growth_rate': growth_rates.mean(),
                        'growth_volatility': growth_rates.std(),
                        'trend_direction': 'increasing' if monthly_revenue.iloc[-1] > monthly_revenue.iloc[0] else 'decreasing'
                    }
        
        return trends
    
    def _detect_outliers(self, df: pd.DataFrame) -> Dict:
        """Detect outliers in numeric data"""
        
        outliers = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
            outlier_count = outlier_mask.sum()
            
            outliers[col] = {
                'count': outlier_count,
                'percentage': (outlier_count / len(df)) * 100,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_values': df[outlier_mask][col].tolist() if outlier_count > 0 else []
            }
        
        return outliers
    
    def _compare_datasets(self, df1: pd.DataFrame, df2: pd.DataFrame) -> Dict:
        """Compare two datasets"""
        
        comparison = {
            'size_comparison': {
                'filtered_count': len(df1),
                'total_count': len(df2),
                'percentage': (len(df1) / len(df2)) * 100 if len(df2) > 0 else 0
            }
        }
        
        # Compare numeric columns
        numeric_cols = df1.select_dtypes(include=[np.number]).columns
        numeric_comparison = {}
        
        for col in numeric_cols:
            if col in df2.columns:
                numeric_comparison[col] = {
                    'filtered_mean': df1[col].mean(),
                    'total_mean': df2[col].mean(),
                    'difference': df1[col].mean() - df2[col].mean(),
                    'percentage_change': ((df1[col].mean() - df2[col].mean()) / df2[col].mean()) * 100 if df2[col].mean() != 0 else 0
                }
        
        comparison['numeric_comparison'] = numeric_comparison
        
        return comparison
    
    def generate_insights(self, analysis: Dict) -> List[str]:
        """Generate business insights from analysis"""
        
        insights = []
        
        # Summary statistics insights
        if 'summary_stats' in analysis:
            for col, stats in analysis['summary_stats'].items():
                if stats['cv'] > 0.5:  # High coefficient of variation
                    insights.append(f"📊 High variability detected in {col} (CV: {stats['cv']:.2f})")
                
                if col == 'revenue' and stats['median'] > stats['mean']:
                    insights.append("💰 Revenue distribution is right-skewed - few high-value projects")
        
        # Trend insights
        if 'trend_analysis' in analysis and 'revenue' in analysis['trend_analysis']:
            trend = analysis['trend_analysis']['revenue']
            if trend['avg_growth_rate'] > 0.1:
                insights.append(f"📈 Strong revenue growth trend: {trend['avg_growth_rate']:.1%} average")
            elif trend['avg_growth_rate'] < -0.05:
                insights.append(f"📉 Declining revenue trend: {trend['avg_growth_rate']:.1%} average")
        
        # Outlier insights
        if 'outlier_detection' in analysis:
            for col, outlier_info in analysis['outlier_detection'].items():
                if outlier_info['percentage'] > 5:
                    insights.append(f"⚠️ {outlier_info['percentage']:.1f}% outliers detected in {col}")
        
        # Comparative insights
        if 'comparative_analysis' in analysis:
            comp = analysis['comparative_analysis']
            if comp['size_comparison']['percentage'] < 10:
                insights.append(f"🔍 Filter is highly selective: {comp['size_comparison']['percentage']:.1f}% of data")
        
        return insights
