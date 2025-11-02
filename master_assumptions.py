import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import json

@dataclass
class RiskFactor:
    """Risk factor configuration"""
    name: str
    category: str  # 'market', 'operational', 'financial', 'competitive'
    impact_type: str  # 'multiplier', 'additive', 'probability'
    base_value: float
    min_value: float
    max_value: float
    description: str
    applies_to: List[str]  # ['offering', 'industry', 'sales_org', 'all']

@dataclass
class ForecastAssumptions:
    """Master forecast assumptions"""
    # Growth assumptions
    base_growth_rate: float = 0.05  # 5% monthly
    seasonal_factors: Dict[int, float] = None  # Month -> multiplier
    
    # Risk factors
    market_risk: float = 0.1  # 10% volatility
    execution_risk: float = 0.05  # 5% execution risk
    competitive_risk: float = 0.08  # 8% competitive pressure
    
    # Finance perspective assumptions
    finance_conservatism: float = 0.85  # 15% haircut
    finance_probability_threshold: float = 0.75  # 75% confidence
    finance_risk_buffer: float = 0.10  # 10% buffer
    
    # Sales perspective assumptions
    sales_optimism: float = 1.15  # 15% uplift
    sales_pipeline_confidence: float = 0.90  # 90% pipeline confidence
    sales_acceleration_factor: float = 1.05  # 5% acceleration
    
    # Reconciliation rules
    reconciliation_method: str = 'weighted_average'  # 'finance_priority', 'sales_priority', 'weighted_average'
    finance_weight: float = 0.6  # 60% finance, 40% sales in weighted average

class MasterAssumptionsEngine:
    """Master assumptions and configuration engine"""
    
    def __init__(self):
        self.assumptions = ForecastAssumptions()
        self.risk_factors = self._initialize_default_risk_factors()
        self.custom_rules = {}
        
    def _initialize_default_risk_factors(self) -> List[RiskFactor]:
        """Initialize default risk factors"""
        return [
            RiskFactor(
                name="Market Volatility",
                category="market",
                impact_type="multiplier",
                base_value=1.0,
                min_value=0.7,
                max_value=1.3,
                description="General market conditions affecting revenue",
                applies_to=["all"]
            ),
            RiskFactor(
                name="Competitive Pressure",
                category="competitive",
                impact_type="multiplier",
                base_value=1.0,
                min_value=0.8,
                max_value=1.1,
                description="Impact of competitive dynamics on pricing and win rates",
                applies_to=["offering"]
            ),
            RiskFactor(
                name="Economic Downturn",
                category="market",
                impact_type="probability",
                base_value=0.15,
                min_value=0.05,
                max_value=0.40,
                description="Probability of economic downturn affecting demand",
                applies_to=["industry"]
            ),
            RiskFactor(
                name="Execution Risk",
                category="operational",
                impact_type="multiplier",
                base_value=0.95,
                min_value=0.80,
                max_value=1.0,
                description="Risk of not delivering projects on time/budget",
                applies_to=["sales_org"]
            ),
            RiskFactor(
                name="Currency Fluctuation",
                category="financial",
                impact_type="multiplier",
                base_value=1.0,
                min_value=0.85,
                max_value=1.15,
                description="Impact of currency exchange rate changes",
                applies_to=["all"]
            ),
            RiskFactor(
                name="Technology Disruption",
                category="market",
                impact_type="additive",
                base_value=0.0,
                min_value=-0.20,
                max_value=0.10,
                description="Impact of new technology on market demand",
                applies_to=["offering"]
            )
        ]
    
    def update_assumptions(self, **kwargs):
        """Update forecast assumptions"""
        for key, value in kwargs.items():
            if hasattr(self.assumptions, key):
                setattr(self.assumptions, key, value)
    
    def add_custom_risk_factor(self, risk_factor: RiskFactor):
        """Add custom risk factor"""
        self.risk_factors.append(risk_factor)
    
    def update_risk_factor(self, name: str, **kwargs):
        """Update existing risk factor"""
        for rf in self.risk_factors:
            if rf.name == name:
                for key, value in kwargs.items():
                    if hasattr(rf, key):
                        setattr(rf, key, value)
                break
    
    def get_risk_factors_by_category(self, category: str) -> List[RiskFactor]:
        """Get risk factors by category"""
        return [rf for rf in self.risk_factors if rf.category == category]
    
    def get_applicable_risk_factors(self, dimension: str, value: str) -> List[RiskFactor]:
        """Get risk factors applicable to specific dimension/value"""
        applicable = []
        for rf in self.risk_factors:
            if 'all' in rf.applies_to or dimension in rf.applies_to:
                applicable.append(rf)
        return applicable
    
    def calculate_risk_adjusted_forecast(self, base_forecast: pd.DataFrame, 
                                       dimension_filters: Dict[str, str] = None) -> Dict[str, pd.DataFrame]:
        """Calculate risk-adjusted forecasts"""
        
        # Get applicable risk factors
        applicable_risks = []
        if dimension_filters:
            for dimension, value in dimension_filters.items():
                applicable_risks.extend(self.get_applicable_risk_factors(dimension, value))
        else:
            applicable_risks = [rf for rf in self.risk_factors if 'all' in rf.applies_to]
        
        # Calculate different risk scenarios
        scenarios = {
            'base': base_forecast.copy(),
            'optimistic': self._apply_risk_scenario(base_forecast, applicable_risks, 'optimistic'),
            'pessimistic': self._apply_risk_scenario(base_forecast, applicable_risks, 'pessimistic'),
            'most_likely': self._apply_risk_scenario(base_forecast, applicable_risks, 'most_likely')
        }
        
        return scenarios
    
    def _apply_risk_scenario(self, forecast: pd.DataFrame, risk_factors: List[RiskFactor], 
                           scenario_type: str) -> pd.DataFrame:
        """Apply risk factors to create scenario"""
        
        adjusted_forecast = forecast.copy()
        
        for rf in risk_factors:
            if scenario_type == 'optimistic':
                risk_value = rf.min_value if rf.impact_type == 'multiplier' else rf.max_value
            elif scenario_type == 'pessimistic':
                risk_value = rf.max_value if rf.impact_type == 'multiplier' and rf.max_value < 1 else rf.min_value
            else:  # most_likely
                risk_value = rf.base_value
            
            # Apply risk factor
            if rf.impact_type == 'multiplier':
                adjusted_forecast['revenue'] *= risk_value
            elif rf.impact_type == 'additive':
                adjusted_forecast['revenue'] *= (1 + risk_value)
            elif rf.impact_type == 'probability':
                # Apply probability-based adjustment
                adjusted_forecast['revenue'] *= (1 - risk_value * 0.5)  # Simplified probability impact
        
        return adjusted_forecast
    
    def generate_finance_perspective_forecast(self, base_data: pd.DataFrame, 
                                            projects_df: pd.DataFrame) -> pd.DataFrame:
        """Generate finance-perspective forecast"""
        
        finance_forecast = base_data.copy()
        
        # Apply finance conservatism
        finance_forecast['revenue'] *= self.assumptions.finance_conservatism
        
        # Apply risk buffer
        finance_forecast['revenue'] *= (1 - self.assumptions.finance_risk_buffer)
        
        # Apply probability threshold (only include high-confidence revenue)
        # Simulate confidence scoring based on project characteristics
        confidence_scores = self._calculate_project_confidence(projects_df)
        
        # Filter based on confidence threshold
        high_confidence_projects = [pid for pid, score in confidence_scores.items() 
                                  if score >= self.assumptions.finance_probability_threshold]
        
        finance_forecast = finance_forecast[
            finance_forecast['project_id'].isin(high_confidence_projects)
        ]
        
        # Add finance-specific adjustments
        finance_forecast['perspective'] = 'Finance'
        finance_forecast['confidence_level'] = 'High'
        finance_forecast['risk_adjustment'] = 'Conservative'
        
        return finance_forecast
    
    def generate_sales_perspective_forecast(self, base_data: pd.DataFrame, 
                                          projects_df: pd.DataFrame) -> pd.DataFrame:
        """Generate sales-perspective forecast"""
        
        sales_forecast = base_data.copy()
        
        # Apply sales optimism
        sales_forecast['revenue'] *= self.assumptions.sales_optimism
        
        # Apply pipeline confidence
        sales_forecast['revenue'] *= self.assumptions.sales_pipeline_confidence
        
        # Apply acceleration factor (sales expects faster ramp-up)
        sales_forecast['revenue'] *= self.assumptions.sales_acceleration_factor
        
        # Include more speculative revenue (lower confidence threshold)
        confidence_scores = self._calculate_project_confidence(projects_df)
        
        # Include medium and high confidence projects
        included_projects = [pid for pid, score in confidence_scores.items() 
                           if score >= 0.5]  # Lower threshold for sales
        
        sales_forecast = sales_forecast[
            sales_forecast['project_id'].isin(included_projects)
        ]
        
        # Add sales-specific adjustments
        sales_forecast['perspective'] = 'Sales'
        sales_forecast['confidence_level'] = 'Medium-High'
        sales_forecast['risk_adjustment'] = 'Optimistic'
        
        return sales_forecast
    
    def _calculate_project_confidence(self, projects_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate confidence scores for projects"""
        
        confidence_scores = {}
        
        for _, project in projects_df.iterrows():
            score = 0.7  # Base confidence
            
            # Adjust based on project characteristics
            if project.get('status') == 'Active':
                score += 0.2
            elif project.get('status') == 'Pipeline':
                score -= 0.1
            
            # Adjust based on client relationship
            if 'existing' in str(project.get('client', '')).lower():
                score += 0.15
            
            # Adjust based on offering maturity
            if project.get('offering') in ['Core Services', 'Established Products']:
                score += 0.1
            
            # Ensure score is between 0 and 1
            confidence_scores[project['project_id']] = max(0, min(1, score))
        
        return confidence_scores
    
    def _empty_reconciliation_result(self) -> Dict:
        """Return empty reconciliation result structure"""
        return {
            'reconciliation': pd.DataFrame(),
            'variance_analysis': {
                'total_variance': 0,
                'avg_variance_pct': 0,
                'max_variance_month': {'period': 'N/A', 'variance': 0, 'variance_pct': 0},
                'high_variance_months': 0,
                'medium_variance_months': 0,
                'variance_trend': 'stable'
            },
            'finance_total': 0,
            'sales_total': 0,
            'reconciled_total': 0
        }
    
    def reconcile_forecasts(self, finance_forecast: pd.DataFrame, 
                          sales_forecast: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Reconcile finance and sales forecasts"""
        
        # Handle empty forecasts
        if finance_forecast.empty or sales_forecast.empty:
            return {
                'reconciliation': pd.DataFrame(),
                'variance_analysis': {
                    'total_variance': 0,
                    'avg_variance_pct': 0,
                    'max_variance_month': {'period': 'N/A', 'variance': 0, 'variance_pct': 0},
                    'high_variance_months': 0,
                    'medium_variance_months': 0,
                    'variance_trend': 'stable'
                },
                'finance_total': 0,
                'sales_total': 0,
                'reconciled_total': 0
            }
        
        # Check if required columns exist
        required_cols = ['year', 'month', 'revenue']
        if not all(col in finance_forecast.columns for col in required_cols):
            return self._empty_reconciliation_result()
        if not all(col in sales_forecast.columns for col in required_cols):
            return self._empty_reconciliation_result()
        
        # Merge forecasts on common dimensions
        finance_agg = finance_forecast.groupby(['year', 'month'])['revenue'].sum().reset_index()
        sales_agg = sales_forecast.groupby(['year', 'month'])['revenue'].sum().reset_index()
        
        # Handle empty aggregations
        if finance_agg.empty or sales_agg.empty:
            return self._empty_reconciliation_result()
        
        finance_agg['perspective'] = 'Finance'
        sales_agg['perspective'] = 'Sales'
        
        # Create reconciliation
        reconciliation = finance_agg.merge(
            sales_agg, on=['year', 'month'], suffixes=('_finance', '_sales')
        )
        
        # Handle empty reconciliation
        if reconciliation.empty:
            return self._empty_reconciliation_result()
        
        # Calculate variance
        reconciliation['variance_abs'] = reconciliation['revenue_sales'] - reconciliation['revenue_finance']
        reconciliation['variance_pct'] = (reconciliation['variance_abs'] / reconciliation['revenue_finance']) * 100
        
        # Calculate reconciled forecast based on method
        if self.assumptions.reconciliation_method == 'finance_priority':
            reconciliation['reconciled_revenue'] = reconciliation['revenue_finance']
        elif self.assumptions.reconciliation_method == 'sales_priority':
            reconciliation['reconciled_revenue'] = reconciliation['revenue_sales']
        else:  # weighted_average
            reconciliation['reconciled_revenue'] = (
                reconciliation['revenue_finance'] * self.assumptions.finance_weight +
                reconciliation['revenue_sales'] * (1 - self.assumptions.finance_weight)
            )
        
        # Create variance analysis
        variance_analysis = self._analyze_forecast_variance(reconciliation)
        
        return {
            'reconciliation': reconciliation,
            'variance_analysis': variance_analysis,
            'finance_total': finance_agg['revenue'].sum(),
            'sales_total': sales_agg['revenue'].sum(),
            'reconciled_total': reconciliation['reconciled_revenue'].sum()
        }
    
    def _analyze_forecast_variance(self, reconciliation: pd.DataFrame) -> Dict:
        """Analyze variance between finance and sales forecasts"""
        
        # Handle empty reconciliation data
        if reconciliation.empty:
            return {
                'total_variance': 0,
                'avg_variance_pct': 0,
                'max_variance_month': {
                    'period': 'N/A',
                    'variance': 0,
                    'variance_pct': 0
                },
                'high_variance_months': 0,
                'medium_variance_months': 0,
                'variance_trend': 'stable'
            }
        
        total_variance = reconciliation['variance_abs'].sum()
        avg_variance_pct = reconciliation['variance_pct'].mean()
        
        # Safe max variance calculation
        if len(reconciliation) > 0 and not reconciliation['variance_abs'].isna().all():
            max_variance_idx = reconciliation['variance_abs'].abs().idxmax()
            max_variance_month = reconciliation.loc[max_variance_idx]
            max_variance_info = {
                'period': f"{max_variance_month['year']}-{max_variance_month['month']:02d}",
                'variance': max_variance_month['variance_abs'],
                'variance_pct': max_variance_month['variance_pct']
            }
        else:
            max_variance_info = {
                'period': 'N/A',
                'variance': 0,
                'variance_pct': 0
            }
        
        # Categorize variance levels
        high_variance_months = len(reconciliation[reconciliation['variance_pct'].abs() > 20])
        medium_variance_months = len(reconciliation[
            (reconciliation['variance_pct'].abs() > 10) & 
            (reconciliation['variance_pct'].abs() <= 20)
        ])
        
        # Safe variance trend calculation
        if len(reconciliation) > 1:
            variance_trend = 'increasing' if reconciliation['variance_pct'].iloc[-1] > reconciliation['variance_pct'].iloc[0] else 'decreasing'
        else:
            variance_trend = 'stable'
        
        return {
            'total_variance': total_variance,
            'avg_variance_pct': avg_variance_pct,
            'max_variance_month': max_variance_info,
            'high_variance_months': high_variance_months,
            'medium_variance_months': medium_variance_months,
            'variance_trend': variance_trend
        }
    
    def export_assumptions(self) -> Dict:
        """Export current assumptions configuration"""
        return {
            'forecast_assumptions': {
                'base_growth_rate': self.assumptions.base_growth_rate,
                'finance_conservatism': self.assumptions.finance_conservatism,
                'sales_optimism': self.assumptions.sales_optimism,
                'reconciliation_method': self.assumptions.reconciliation_method,
                'finance_weight': self.assumptions.finance_weight
            },
            'risk_factors': [
                {
                    'name': rf.name,
                    'category': rf.category,
                    'impact_type': rf.impact_type,
                    'base_value': rf.base_value,
                    'min_value': rf.min_value,
                    'max_value': rf.max_value,
                    'description': rf.description,
                    'applies_to': rf.applies_to
                }
                for rf in self.risk_factors
            ]
        }
    
    def import_assumptions(self, config: Dict):
        """Import assumptions configuration"""
        if 'forecast_assumptions' in config:
            for key, value in config['forecast_assumptions'].items():
                if hasattr(self.assumptions, key):
                    setattr(self.assumptions, key, value)
        
        if 'risk_factors' in config:
            self.risk_factors = [
                RiskFactor(**rf_config) for rf_config in config['risk_factors']
            ]
