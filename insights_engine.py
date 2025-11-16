"""
Financial Insights Engine
Analyzes financial data and generates actionable insights
"""

import pandas as pd
import numpy as np

class FinancialInsightsEngine:
    """Generate insights from financial forecast data"""
    
    def __init__(self):
        self.insights = []
        self.warnings = []
        self.opportunities = []
    
    def analyze_quarterly_data(self, df):
        """Analyze quarterly performance data"""
        insights = {
            'revenue_insights': [],
            'margin_insights': [],
            'variance_insights': [],
            'trend_insights': [],
            'recommendations': []
        }
        
        # Check if quarterly columns exist
        if not all(col in df.columns for col in ['Q1', 'Q2', 'Q3', 'Q4', 'FY']):
            return insights
        
        # Find revenue row
        revenue_row = None
        for idx, row in df.iterrows():
            if 'revenue' in str(row[df.columns[0]]).lower():
                revenue_row = idx
                break
        
        if revenue_row is not None:
            q1 = df['Q1'].iloc[revenue_row]
            q2 = df['Q2'].iloc[revenue_row]
            q3 = df['Q3'].iloc[revenue_row]
            q4 = df['Q4'].iloc[revenue_row]
            fy = df['FY'].iloc[revenue_row]
            
            # Revenue growth analysis
            if pd.notna(q1) and pd.notna(q2):
                q1_to_q2_growth = ((q2 - q1) / q1) * 100 if q1 != 0 else 0
                if q1_to_q2_growth > 5:
                    insights['revenue_insights'].append({
                        'type': 'positive',
                        'message': f'Strong Q1 to Q2 growth of {q1_to_q2_growth:.1f}%',
                        'impact': 'high'
                    })
                elif q1_to_q2_growth < -5:
                    insights['revenue_insights'].append({
                        'type': 'warning',
                        'message': f'Revenue declined {abs(q1_to_q2_growth):.1f}% from Q1 to Q2',
                        'impact': 'high'
                    })
            
            # Q4 performance check
            if pd.notna(q4) and pd.notna(fy):
                q4_contribution = (q4 / fy) * 100 if fy != 0 else 0
                if q4_contribution < 20:
                    insights['trend_insights'].append({
                        'type': 'warning',
                        'message': f'Q4 contributes only {q4_contribution:.1f}% of FY revenue',
                        'impact': 'medium'
                    })
                elif q4_contribution > 30:
                    insights['trend_insights'].append({
                        'type': 'info',
                        'message': f'Q4 is strong contributor at {q4_contribution:.1f}% of FY revenue',
                        'impact': 'medium'
                    })
            
            # Consistency check
            if all(pd.notna(x) for x in [q1, q2, q3, q4]):
                avg_quarter = (q1 + q2 + q3 + q4) / 4
                std_dev = np.std([q1, q2, q3, q4])
                cv = (std_dev / avg_quarter) * 100 if avg_quarter != 0 else 0
                
                if cv < 10:
                    insights['trend_insights'].append({
                        'type': 'positive',
                        'message': f'Consistent quarterly performance (CV: {cv:.1f}%)',
                        'impact': 'low'
                    })
                elif cv > 25:
                    insights['trend_insights'].append({
                        'type': 'warning',
                        'message': f'High quarterly volatility (CV: {cv:.1f}%)',
                        'impact': 'high'
                    })
        
        # Margin analysis
        margin_row = None
        for idx, row in df.iterrows():
            if 'contract margin%' in str(row[df.columns[0]]).lower():
                margin_row = idx
                break
        
        if margin_row is not None:
            margins = []
            for col in ['Q1', 'Q2', 'Q3', 'Q4']:
                val = df[col].iloc[margin_row]
                if pd.notna(val):
                    margins.append(val)
            
            if margins:
                avg_margin = np.mean(margins)
                if avg_margin < 20:
                    insights['margin_insights'].append({
                        'type': 'warning',
                        'message': f'Average margin of {avg_margin:.1f}% is below 20% threshold',
                        'impact': 'high'
                    })
                elif avg_margin > 30:
                    insights['margin_insights'].append({
                        'type': 'positive',
                        'message': f'Strong average margin of {avg_margin:.1f}%',
                        'impact': 'high'
                    })
                
                # Margin trend
                if len(margins) >= 2:
                    if margins[-1] > margins[0]:
                        trend = ((margins[-1] - margins[0]) / margins[0]) * 100
                        insights['margin_insights'].append({
                            'type': 'positive',
                            'message': f'Margin improving by {trend:.1f}% over the year',
                            'impact': 'medium'
                        })
                    elif margins[-1] < margins[0]:
                        trend = ((margins[0] - margins[-1]) / margins[0]) * 100
                        insights['margin_insights'].append({
                            'type': 'warning',
                            'message': f'Margin declining by {trend:.1f}% over the year',
                            'impact': 'medium'
                        })
        
        # Generate recommendations
        insights['recommendations'] = self._generate_recommendations(insights)
        
        return insights
    
    def analyze_variance(self, forecast_df, budget_df):
        """Analyze variance between forecast and budget"""
        variance_insights = []
        
        if 'FY' not in forecast_df.columns or 'FY' not in budget_df.columns:
            return variance_insights
        
        # Revenue variance
        for idx in range(min(len(forecast_df), len(budget_df))):
            line_item = forecast_df[forecast_df.columns[0]].iloc[idx]
            
            if 'revenue' in str(line_item).lower():
                forecast_fy = forecast_df['FY'].iloc[idx]
                budget_fy = budget_df['FY'].iloc[idx]
                
                if pd.notna(forecast_fy) and pd.notna(budget_fy) and budget_fy != 0:
                    variance = forecast_fy - budget_fy
                    variance_pct = (variance / budget_fy) * 100
                    
                    if abs(variance_pct) > 10:
                        variance_insights.append({
                            'type': 'warning' if variance < 0 else 'info',
                            'message': f'{line_item}: {variance_pct:+.1f}% variance vs budget',
                            'value': variance,
                            'percentage': variance_pct
                        })
        
        return variance_insights
    
    def _generate_recommendations(self, insights):
        """Generate actionable recommendations based on insights"""
        recommendations = []
        
        # Revenue recommendations
        if insights['revenue_insights']:
            for insight in insights['revenue_insights']:
                if insight['type'] == 'warning' and 'declined' in insight['message']:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'Revenue',
                        'action': 'Review sales pipeline and accelerate deal closures',
                        'reason': insight['message']
                    })
        
        # Margin recommendations
        if insights['margin_insights']:
            for insight in insights['margin_insights']:
                if insight['type'] == 'warning' and 'below' in insight['message']:
                    recommendations.append({
                        'priority': 'high',
                        'category': 'Margin',
                        'action': 'Analyze cost structure and identify efficiency opportunities',
                        'reason': insight['message']
                    })
                elif 'declining' in insight['message']:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'Margin',
                        'action': 'Investigate margin erosion causes and implement corrective measures',
                        'reason': insight['message']
                    })
        
        # Volatility recommendations
        if insights['trend_insights']:
            for insight in insights['trend_insights']:
                if 'volatility' in insight['message']:
                    recommendations.append({
                        'priority': 'medium',
                        'category': 'Planning',
                        'action': 'Improve revenue predictability through better pipeline management',
                        'reason': insight['message']
                    })
        
        return recommendations
    
    def get_summary_stats(self, df):
        """Calculate summary statistics"""
        stats = {}
        
        if 'FY' in df.columns:
            # Total revenue
            for idx, row in df.iterrows():
                line_item = str(row[df.columns[0]]).lower()
                if 'revenue' in line_item and 'resale' not in line_item and 'services' not in line_item:
                    stats['total_revenue'] = row['FY']
                    break
            
            # Total margin
            for idx, row in df.iterrows():
                line_item = str(row[df.columns[0]]).lower()
                if 'contract margin' in line_item and '%' not in line_item:
                    stats['total_margin'] = row['FY']
                    break
            
            # Margin percentage
            for idx, row in df.iterrows():
                line_item = str(row[df.columns[0]]).lower()
                if 'contract margin%' in line_item:
                    stats['margin_pct'] = row['FY']
                    break
        
        return stats
