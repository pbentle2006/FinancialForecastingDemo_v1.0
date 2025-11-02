import pandas as pd
import numpy as np
from datetime import datetime
import streamlit as st

class ForecastValidationEngine:
    """Automatic validation, error detection, and confidence scoring for forecasts"""
    
    def __init__(self):
        self.validation_results = {}
        self.confidence_scores = {}
        self.data_quality_metrics = {}
    
    def validate_data_quality(self, df, monthly_cols, mapping):
        """Comprehensive data quality validation"""
        
        quality_issues = []
        quality_warnings = []
        quality_info = []
        
        # 1. Data Completeness Validation
        total_rows = len(df)
        
        # Check mapped columns
        for field, column in mapping.items():
            if column in df.columns:
                null_count = df[column].isnull().sum()
                null_percentage = (null_count / total_rows) * 100
                
                if null_percentage > 50:
                    quality_issues.append(f"❌ {field.title()}: {null_percentage:.1f}% missing data (critical)")
                elif null_percentage > 20:
                    quality_warnings.append(f"⚠️ {field.title()}: {null_percentage:.1f}% missing data")
                elif null_percentage > 0:
                    quality_info.append(f"ℹ️ {field.title()}: {null_percentage:.1f}% missing data")
        
        # 2. Monthly Data Validation
        monthly_data_quality = self._validate_monthly_data(df, monthly_cols)
        quality_issues.extend(monthly_data_quality['issues'])
        quality_warnings.extend(monthly_data_quality['warnings'])
        quality_info.extend(monthly_data_quality['info'])
        
        # 3. Data Consistency Validation
        consistency_results = self._validate_data_consistency(df, monthly_cols, mapping)
        quality_issues.extend(consistency_results['issues'])
        quality_warnings.extend(consistency_results['warnings'])
        
        return {
            'issues': quality_issues,
            'warnings': quality_warnings,
            'info': quality_info,
            'overall_score': self._calculate_quality_score(quality_issues, quality_warnings, quality_info)
        }
    
    def _validate_monthly_data(self, df, monthly_cols):
        """Validate monthly revenue data quality"""
        
        issues = []
        warnings = []
        info = []
        
        if not monthly_cols:
            issues.append("❌ No monthly revenue columns detected")
            return {'issues': issues, 'warnings': warnings, 'info': info}
        
        # Check for numeric data in monthly columns
        numeric_cols = 0
        zero_cols = 0
        negative_cols = 0
        
        for col in monthly_cols:
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                non_null_count = numeric_data.notna().sum()
                
                if non_null_count == 0:
                    warnings.append(f"⚠️ Column '{col}': No valid numeric data")
                else:
                    numeric_cols += 1
                    
                    # Check for zeros and negatives
                    zero_count = (numeric_data == 0).sum()
                    negative_count = (numeric_data < 0).sum()
                    
                    if zero_count > len(df) * 0.8:
                        zero_cols += 1
                        warnings.append(f"⚠️ Column '{col}': {zero_count/len(df)*100:.1f}% zero values")
                    
                    if negative_count > 0:
                        negative_cols += 1
                        warnings.append(f"⚠️ Column '{col}': {negative_count} negative values")
                        
            except Exception:
                issues.append(f"❌ Column '{col}': Cannot process as numeric data")
        
        # Summary assessment
        if numeric_cols < len(monthly_cols) * 0.5:
            issues.append(f"❌ Only {numeric_cols}/{len(monthly_cols)} monthly columns have valid data")
        elif numeric_cols < len(monthly_cols) * 0.8:
            warnings.append(f"⚠️ Only {numeric_cols}/{len(monthly_cols)} monthly columns have valid data")
        else:
            info.append(f"ℹ️ {numeric_cols}/{len(monthly_cols)} monthly columns validated successfully")
        
        return {'issues': issues, 'warnings': warnings, 'info': info}
    
    def _validate_data_consistency(self, df, monthly_cols, mapping):
        """Validate data consistency and logical relationships"""
        
        issues = []
        warnings = []
        
        # Check ID uniqueness
        if 'id' in mapping and mapping['id'] in df.columns:
            id_col = mapping['id']
            duplicate_count = df[id_col].duplicated().sum()
            if duplicate_count > 0:
                warnings.append(f"⚠️ {duplicate_count} duplicate IDs found in {id_col}")
        
        # Check total value vs monthly sum consistency
        if 'total_value' in mapping and mapping['total_value'] in df.columns and monthly_cols:
            total_col = mapping['total_value']
            
            inconsistent_count = 0
            for idx, row in df.iterrows():
                try:
                    total_value = float(row[total_col]) if pd.notna(row[total_col]) else 0
                    monthly_sum = sum(float(row[col]) for col in monthly_cols 
                                    if pd.notna(row[col]) and col in df.columns)
                    
                    if total_value > 0 and monthly_sum > 0:
                        ratio = abs(total_value - monthly_sum) / total_value
                        if ratio > 0.2:  # More than 20% difference
                            inconsistent_count += 1
                            
                except Exception:
                    continue
            
            if inconsistent_count > len(df) * 0.1:
                warnings.append(f"⚠️ {inconsistent_count} projects have inconsistent total vs monthly values")
        
        return {'issues': issues, 'warnings': warnings}
    
    def calculate_forecast_confidence(self, monthly_df, scenarios):
        """Calculate confidence levels for forecast scenarios"""
        
        confidence_metrics = {}
        
        for scenario_name, scenario_data in scenarios.items():
            confidence_score = self._calculate_scenario_confidence(monthly_df, scenario_data)
            confidence_metrics[scenario_name] = confidence_score
        
        return confidence_metrics
    
    def _calculate_scenario_confidence(self, monthly_df, scenario_data):
        """Calculate confidence score for individual scenario"""
        
        confidence_factors = {}
        
        # 1. Data Coverage Score (0-100)
        total_possible_periods = monthly_df['period'].nunique()
        periods_with_data = len(scenario_data['monthly_totals'])
        coverage_score = (periods_with_data / max(total_possible_periods, 1)) * 100
        confidence_factors['data_coverage'] = min(coverage_score, 100)
        
        # 2. Data Consistency Score (0-100)
        revenue_values = monthly_df['revenue'].values
        non_zero_values = revenue_values[revenue_values > 0]
        
        if len(non_zero_values) > 1:
            cv = np.std(non_zero_values) / np.mean(non_zero_values)  # Coefficient of variation
            consistency_score = max(0, 100 - (cv * 50))  # Lower CV = higher consistency
        else:
            consistency_score = 50  # Neutral score for insufficient data
        
        confidence_factors['data_consistency'] = consistency_score
        
        # 3. Temporal Distribution Score (0-100)
        if len(scenario_data['monthly_totals']) > 1:
            monthly_revenues = scenario_data['monthly_totals']['revenue_adjusted'].values
            # Check for reasonable distribution (not all in one period)
            max_concentration = max(monthly_revenues) / sum(monthly_revenues)
            distribution_score = max(0, 100 - (max_concentration * 100))
        else:
            distribution_score = 30  # Low score for single period
        
        confidence_factors['temporal_distribution'] = distribution_score
        
        # 4. Project Diversity Score (0-100)
        unique_projects = monthly_df['project_id'].nunique()
        total_records = len(monthly_df)
        
        if total_records > 0:
            diversity_ratio = unique_projects / total_records
            diversity_score = min(diversity_ratio * 200, 100)  # Scale to 0-100
        else:
            diversity_score = 0
        
        confidence_factors['project_diversity'] = diversity_score
        
        # 5. Scenario Reasonableness Score (0-100)
        multiplier = scenario_data['multiplier']
        if 0.5 <= multiplier <= 2.0:  # Reasonable range
            reasonableness_score = 100 - abs(1.0 - multiplier) * 50
        else:
            reasonableness_score = max(0, 50 - abs(1.0 - multiplier) * 25)
        
        confidence_factors['scenario_reasonableness'] = reasonableness_score
        
        # Calculate weighted overall confidence
        weights = {
            'data_coverage': 0.25,
            'data_consistency': 0.25,
            'temporal_distribution': 0.20,
            'project_diversity': 0.15,
            'scenario_reasonableness': 0.15
        }
        
        overall_confidence = sum(
            confidence_factors[factor] * weight 
            for factor, weight in weights.items()
        )
        
        return {
            'overall_score': round(overall_confidence, 1),
            'factors': confidence_factors,
            'grade': self._get_confidence_grade(overall_confidence)
        }
    
    def _get_confidence_grade(self, score):
        """Convert confidence score to letter grade"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very High)"
        elif score >= 70:
            return "B (High)"
        elif score >= 60:
            return "C (Moderate)"
        elif score >= 50:
            return "D (Low)"
        else:
            return "F (Very Low)"
    
    def _calculate_quality_score(self, issues, warnings, info):
        """Calculate overall data quality score"""
        
        base_score = 100
        
        # Deduct points for issues and warnings
        base_score -= len(issues) * 20  # Major deduction for critical issues
        base_score -= len(warnings) * 10  # Moderate deduction for warnings
        base_score -= len(info) * 2  # Minor deduction for info items
        
        return max(0, base_score)
    
    def detect_forecast_anomalies(self, monthly_df, scenarios):
        """Detect anomalies and outliers in forecast data"""
        
        anomalies = []
        
        # 1. Extreme Revenue Spikes
        for scenario_name, scenario in scenarios.items():
            monthly_totals = scenario['monthly_totals']
            if len(monthly_totals) > 1:
                revenues = monthly_totals['revenue_adjusted'].values
                mean_revenue = np.mean(revenues)
                std_revenue = np.std(revenues)
                
                for idx, revenue in enumerate(revenues):
                    if abs(revenue - mean_revenue) > 3 * std_revenue:
                        period = monthly_totals.iloc[idx]['period']
                        anomalies.append({
                            'type': 'Revenue Spike',
                            'scenario': scenario_name,
                            'period': period,
                            'value': revenue,
                            'severity': 'High' if abs(revenue - mean_revenue) > 4 * std_revenue else 'Medium'
                        })
        
        # 2. Zero Revenue Periods
        for scenario_name, scenario in scenarios.items():
            monthly_totals = scenario['monthly_totals']
            zero_periods = monthly_totals[monthly_totals['revenue_adjusted'] == 0]
            
            if len(zero_periods) > 0:
                for _, period_row in zero_periods.iterrows():
                    anomalies.append({
                        'type': 'Zero Revenue',
                        'scenario': scenario_name,
                        'period': period_row['period'],
                        'value': 0,
                        'severity': 'Medium'
                    })
        
        # 3. Unrealistic Growth Rates
        for scenario_name, scenario in scenarios.items():
            monthly_totals = scenario['monthly_totals'].sort_values('period')
            if len(monthly_totals) > 1:
                revenues = monthly_totals['revenue_adjusted'].values
                
                for i in range(1, len(revenues)):
                    if revenues[i-1] > 0:
                        growth_rate = (revenues[i] - revenues[i-1]) / revenues[i-1]
                        
                        if abs(growth_rate) > 2.0:  # More than 200% change
                            period = monthly_totals.iloc[i]['period']
                            anomalies.append({
                                'type': 'Extreme Growth',
                                'scenario': scenario_name,
                                'period': period,
                                'value': growth_rate * 100,
                                'severity': 'High' if abs(growth_rate) > 5.0 else 'Medium'
                            })
        
        return anomalies
    
    def generate_validation_report(self, quality_results, confidence_metrics, anomalies):
        """Generate comprehensive validation report"""
        
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_quality': quality_results,
            'confidence_scores': confidence_metrics,
            'anomalies': anomalies,
            'recommendations': self._generate_recommendations(quality_results, confidence_metrics, anomalies)
        }
        
        return report
    
    def _generate_recommendations(self, quality_results, confidence_metrics, anomalies):
        """Generate actionable recommendations based on validation results"""
        
        recommendations = []
        
        # Data quality recommendations
        if quality_results['overall_score'] < 70:
            recommendations.append("🔧 Improve data quality by addressing missing values and inconsistencies")
        
        if len(quality_results['issues']) > 0:
            recommendations.append("❌ Resolve critical data issues before using forecasts for decision-making")
        
        # Confidence recommendations
        low_confidence_scenarios = [
            name for name, metrics in confidence_metrics.items() 
            if metrics['overall_score'] < 60
        ]
        
        if low_confidence_scenarios:
            recommendations.append(f"⚠️ Review scenarios with low confidence: {', '.join(low_confidence_scenarios)}")
        
        # Anomaly recommendations
        high_severity_anomalies = [a for a in anomalies if a['severity'] == 'High']
        
        if high_severity_anomalies:
            recommendations.append("🚨 Investigate high-severity anomalies in forecast data")
        
        if len(anomalies) > 10:
            recommendations.append("📊 Consider data smoothing or outlier removal for more stable forecasts")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ Data quality and forecasts look good - proceed with confidence")
        
        return recommendations
