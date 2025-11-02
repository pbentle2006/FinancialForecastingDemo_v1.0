import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')

class AdvancedAnalytics:
    """Advanced analytics engine for forecasting platform"""
    
    def __init__(self):
        self.models = {}
        self.analytics_cache = {}
    
    def calculate_trend_analysis(self, monthly_df, projects_df):
        """Calculate comprehensive trend analysis"""
        
        trends = {}
        
        # 1. Revenue Growth Trends
        historical_data = monthly_df[monthly_df['is_historical']].copy()
        
        if not historical_data.empty:
            # Monthly revenue trends
            monthly_trends = historical_data.groupby(['year', 'month'])['revenue'].sum().reset_index()
            monthly_trends['period'] = pd.to_datetime(monthly_trends[['year', 'month']].assign(day=1))
            monthly_trends = monthly_trends.sort_values('period')
            
            # Calculate growth rates
            monthly_trends['revenue_growth'] = monthly_trends['revenue'].pct_change() * 100
            monthly_trends['revenue_ma3'] = monthly_trends['revenue'].rolling(window=3).mean()
            
            trends['monthly_revenue'] = monthly_trends
            trends['avg_growth_rate'] = monthly_trends['revenue_growth'].mean()
            trends['growth_volatility'] = monthly_trends['revenue_growth'].std()
        
        # 2. Business Dimension Trends
        dimension_trends = {}
        
        for dimension in ['offering', 'industry', 'sales_org', 'product_name']:
            if dimension in projects_df.columns:
                dim_analysis = self._analyze_dimension_trends(historical_data, projects_df, dimension)
                dimension_trends[dimension] = dim_analysis
        
        trends['dimension_trends'] = dimension_trends
        
        # 3. Seasonality Analysis
        seasonality = self._analyze_seasonality(historical_data)
        trends['seasonality'] = seasonality
        
        # 4. Portfolio Concentration Analysis
        concentration = self._analyze_portfolio_concentration(projects_df, monthly_df)
        trends['concentration'] = concentration
        
        return trends
    
    def _analyze_dimension_trends(self, monthly_df, projects_df, dimension):
        """Analyze trends for specific business dimension"""
        
        # Merge monthly data with project dimensions
        merged_df = monthly_df.merge(
            projects_df[['project_id', dimension]], 
            on='project_id', 
            how='left'
        )
        
        # Calculate dimension performance
        dim_performance = merged_df.groupby([dimension, 'year', 'month'])['revenue'].sum().reset_index()
        dim_totals = merged_df.groupby(dimension)['revenue'].agg(['sum', 'count', 'mean']).reset_index()
        
        # Calculate growth rates by dimension
        dim_growth = {}
        for dim_value in merged_df[dimension].unique():
            if pd.notna(dim_value):
                dim_data = dim_performance[dim_performance[dimension] == dim_value].copy()
                if len(dim_data) > 1:
                    dim_data = dim_data.sort_values(['year', 'month'])
                    dim_data['growth_rate'] = dim_data['revenue'].pct_change() * 100
                    dim_growth[dim_value] = {
                        'avg_growth': dim_data['growth_rate'].mean(),
                        'total_revenue': dim_data['revenue'].sum(),
                        'periods': len(dim_data)
                    }
        
        return {
            'performance': dim_totals,
            'growth_rates': dim_growth,
            'top_performer': dim_totals.loc[dim_totals['sum'].idxmax(), dimension] if not dim_totals.empty else None
        }
    
    def _analyze_seasonality(self, monthly_df):
        """Analyze seasonal patterns in revenue"""
        
        if monthly_df.empty:
            return {}
        
        try:
            # Group by month across years
            monthly_patterns = monthly_df.groupby('month')['revenue'].agg(['mean', 'std', 'count']).reset_index()
            
            # Handle division by zero for coefficient of variation
            monthly_patterns['cv'] = monthly_patterns.apply(
                lambda row: row['std'] / row['mean'] if row['mean'] != 0 else 0, axis=1
            )
            
            # Identify peak and low seasons
            if not monthly_patterns.empty:
                peak_month = monthly_patterns.loc[monthly_patterns['mean'].idxmax(), 'month']
                low_month = monthly_patterns.loc[monthly_patterns['mean'].idxmin(), 'month']
            else:
                peak_month = 1
                low_month = 1
            
            # Calculate seasonality index (month average / overall average)
            overall_avg = monthly_df['revenue'].mean()
            if overall_avg != 0:
                monthly_patterns['seasonality_index'] = monthly_patterns['mean'] / overall_avg
            else:
                monthly_patterns['seasonality_index'] = 1.0
            
            # Calculate seasonality strength (standard deviation of seasonality index)
            seasonality_strength = monthly_patterns['seasonality_index'].std() if len(monthly_patterns) > 1 else 0.0
            
            return {
                'monthly_patterns': monthly_patterns,
                'peak_month': peak_month,
                'low_month': low_month,
                'seasonality_strength': seasonality_strength
            }
        
        except Exception as e:
            # Return empty result if analysis fails
            return {
                'monthly_patterns': pd.DataFrame(),
                'peak_month': 1,
                'low_month': 1,
                'seasonality_strength': 0.0
            }
    
    def _analyze_portfolio_concentration(self, projects_df, monthly_df):
        """Analyze portfolio concentration and risk"""
        
        # Revenue concentration by project
        project_revenue = monthly_df.groupby('project_id')['revenue'].sum().reset_index()
        project_revenue = project_revenue.merge(projects_df[['project_id', 'client', 'offering']], on='project_id')
        
        total_revenue = project_revenue['revenue'].sum()
        
        # Top projects concentration
        project_revenue_sorted = project_revenue.sort_values('revenue', ascending=False)
        top_5_concentration = project_revenue_sorted.head(5)['revenue'].sum() / total_revenue * 100
        top_10_concentration = project_revenue_sorted.head(10)['revenue'].sum() / total_revenue * 100
        
        # Client concentration
        client_revenue = project_revenue.groupby('client')['revenue'].sum().reset_index()
        client_revenue_sorted = client_revenue.sort_values('revenue', ascending=False)
        top_client_concentration = client_revenue_sorted.head(1)['revenue'].sum() / total_revenue * 100
        top_3_clients_concentration = client_revenue_sorted.head(3)['revenue'].sum() / total_revenue * 100
        
        # Offering concentration
        offering_revenue = project_revenue.groupby('offering')['revenue'].sum().reset_index()
        offering_revenue_sorted = offering_revenue.sort_values('revenue', ascending=False)
        
        return {
            'top_5_projects_pct': top_5_concentration,
            'top_10_projects_pct': top_10_concentration,
            'top_client_pct': top_client_concentration,
            'top_3_clients_pct': top_3_clients_concentration,
            'project_count': len(project_revenue),
            'client_count': len(client_revenue),
            'offering_count': len(offering_revenue),
            'top_projects': project_revenue_sorted.head(5),
            'top_clients': client_revenue_sorted.head(3),
            'top_offerings': offering_revenue_sorted.head(3)
        }
    
    def build_ml_forecast_models(self, monthly_df, projects_df):
        """Build machine learning forecast models"""
        
        models_results = {}
        
        # Prepare data for ML models
        historical_data = monthly_df[monthly_df['is_historical']].copy()
        
        if len(historical_data) < 6:  # Need minimum data for ML
            return {"error": "Insufficient historical data for ML models (minimum 6 data points required)"}
        
        # 1. Time Series Linear Regression
        linear_model = self._build_linear_trend_model(historical_data)
        models_results['linear_trend'] = linear_model
        
        # 2. Random Forest with Features
        rf_model = self._build_random_forest_model(historical_data, projects_df)
        models_results['random_forest'] = rf_model
        
        # 3. Seasonal Decomposition Model
        seasonal_model = self._build_seasonal_model(historical_data)
        models_results['seasonal'] = seasonal_model
        
        return models_results
    
    def _build_linear_trend_model(self, historical_data):
        """Build linear trend model"""
        
        # Prepare time series data
        monthly_totals = historical_data.groupby(['year', 'month'])['revenue'].sum().reset_index()
        monthly_totals['period_num'] = range(len(monthly_totals))
        
        if len(monthly_totals) < 3:
            return {"error": "Insufficient data for linear model"}
        
        # Train model
        X = monthly_totals[['period_num']]
        y = monthly_totals['revenue']
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Generate predictions
        predictions = model.predict(X)
        
        # Calculate metrics
        mae = mean_absolute_error(y, predictions)
        mse = mean_squared_error(y, predictions)
        
        # Forecast next 6 periods
        future_periods = np.array([[len(monthly_totals) + i] for i in range(1, 7)])
        future_predictions = model.predict(future_periods)
        
        return {
            'model_type': 'Linear Trend',
            'mae': mae,
            'mse': mse,
            'r_squared': model.score(X, y),
            'trend_slope': model.coef_[0],
            'future_forecast': future_predictions.tolist(),
            'historical_fit': predictions.tolist()
        }
    
    def _build_random_forest_model(self, historical_data, projects_df):
        """Build Random Forest model with business features"""
        
        # Merge with project features
        merged_data = historical_data.merge(projects_df, on='project_id', how='left')
        
        # Create features
        features_df = pd.DataFrame()
        features_df['month'] = merged_data['month']
        features_df['year'] = merged_data['year']
        features_df['total_value'] = merged_data['total_value']
        
        # Encode categorical features
        for cat_col in ['offering', 'industry', 'sales_org']:
            if cat_col in merged_data.columns:
                # Simple frequency encoding
                freq_encoding = merged_data[cat_col].value_counts().to_dict()
                features_df[f'{cat_col}_freq'] = merged_data[cat_col].map(freq_encoding).fillna(0)
        
        # Remove rows with missing values
        features_df = features_df.fillna(0)
        y = merged_data['revenue']
        
        if len(features_df) < 5:
            return {"error": "Insufficient data for Random Forest model"}
        
        # Train model
        model = RandomForestRegressor(n_estimators=50, random_state=42)
        model.fit(features_df, y)
        
        # Generate predictions
        predictions = model.predict(features_df)
        
        # Calculate metrics
        mae = mean_absolute_error(y, predictions)
        mse = mean_squared_error(y, predictions)
        
        # Feature importance
        feature_importance = dict(zip(features_df.columns, model.feature_importances_))
        
        return {
            'model_type': 'Random Forest',
            'mae': mae,
            'mse': mse,
            'r_squared': model.score(features_df, y),
            'feature_importance': feature_importance,
            'historical_fit': predictions.tolist()
        }
    
    def _build_seasonal_model(self, historical_data):
        """Build seasonal decomposition model"""
        
        monthly_totals = historical_data.groupby(['year', 'month'])['revenue'].sum().reset_index()
        
        if len(monthly_totals) < 12:  # Need at least a year for seasonality
            return {"error": "Insufficient data for seasonal model (need 12+ months)"}
        
        # Simple seasonal model: average by month
        seasonal_averages = historical_data.groupby('month')['revenue'].mean().to_dict()
        
        # Calculate trend
        monthly_totals['period'] = range(len(monthly_totals))
        trend_model = LinearRegression()
        trend_model.fit(monthly_totals[['period']], monthly_totals['revenue'])
        
        # Generate seasonal forecast
        future_forecast = []
        for i in range(1, 7):  # Next 6 months
            last_period = len(monthly_totals)
            future_month = ((monthly_totals['month'].iloc[-1] + i - 1) % 12) + 1
            
            # Trend component
            trend_value = trend_model.predict([[last_period + i]])[0]
            
            # Seasonal component
            seasonal_factor = seasonal_averages.get(future_month, monthly_totals['revenue'].mean())
            overall_avg = monthly_totals['revenue'].mean()
            seasonal_multiplier = seasonal_factor / overall_avg
            
            # Combined forecast
            forecast_value = trend_value * seasonal_multiplier
            future_forecast.append(forecast_value)
        
        return {
            'model_type': 'Seasonal Decomposition',
            'seasonal_factors': seasonal_averages,
            'trend_slope': trend_model.coef_[0],
            'future_forecast': future_forecast
        }
    
    def calculate_forecast_accuracy_metrics(self, actual_data, predicted_data):
        """Calculate comprehensive forecast accuracy metrics"""
        
        if len(actual_data) != len(predicted_data) or len(actual_data) == 0:
            return {}
        
        actual = np.array(actual_data)
        predicted = np.array(predicted_data)
        
        # Basic metrics
        mae = mean_absolute_error(actual, predicted)
        mse = mean_squared_error(actual, predicted)
        rmse = np.sqrt(mse)
        
        # Percentage metrics
        mape = np.mean(np.abs((actual - predicted) / actual)) * 100
        
        # Bias metrics
        bias = np.mean(predicted - actual)
        bias_pct = (bias / np.mean(actual)) * 100
        
        # Directional accuracy
        actual_direction = np.diff(actual) > 0
        predicted_direction = np.diff(predicted) > 0
        directional_accuracy = np.mean(actual_direction == predicted_direction) * 100 if len(actual) > 1 else 0
        
        return {
            'mae': mae,
            'mse': mse,
            'rmse': rmse,
            'mape': mape,
            'bias': bias,
            'bias_percentage': bias_pct,
            'directional_accuracy': directional_accuracy,
            'accuracy_grade': self._get_accuracy_grade(mape)
        }
    
    def _get_accuracy_grade(self, mape):
        """Convert MAPE to accuracy grade"""
        if mape <= 10:
            return "A+ (Excellent)"
        elif mape <= 20:
            return "A (Very Good)"
        elif mape <= 30:
            return "B (Good)"
        elif mape <= 50:
            return "C (Fair)"
        else:
            return "D (Poor)"
    
    def generate_insights_and_recommendations(self, trends, ml_models, projects_df, monthly_df):
        """Generate business insights and recommendations"""
        
        insights = []
        recommendations = []
        
        # Revenue trend insights
        if 'avg_growth_rate' in trends:
            growth_rate = trends['avg_growth_rate']
            if growth_rate > 10:
                insights.append(f"📈 Strong revenue growth trend: {growth_rate:.1f}% average monthly growth")
                recommendations.append("🚀 Consider scaling successful offerings to capitalize on growth momentum")
            elif growth_rate < -5:
                insights.append(f"📉 Declining revenue trend: {growth_rate:.1f}% average monthly decline")
                recommendations.append("⚠️ Investigate causes of revenue decline and implement corrective measures")
        
        # Concentration risk insights
        if 'concentration' in trends:
            conc = trends['concentration']
            if conc['top_client_pct'] > 40:
                insights.append(f"⚠️ High client concentration risk: Top client represents {conc['top_client_pct']:.1f}% of revenue")
                recommendations.append("🎯 Diversify client base to reduce dependency on single large client")
            
            if conc['top_5_projects_pct'] > 60:
                insights.append(f"📊 Portfolio concentration: Top 5 projects represent {conc['top_5_projects_pct']:.1f}% of revenue")
                recommendations.append("📈 Develop more mid-size opportunities to balance portfolio risk")
        
        # Seasonality insights
        if 'seasonality' in trends and trends['seasonality']:
            seasonality_data = trends['seasonality']
            if 'seasonality_strength' in seasonality_data and seasonality_data['seasonality_strength'] > 0.3:
                peak_month = seasonality_data.get('peak_month', 'Unknown')
                low_month = seasonality_data.get('low_month', 'Unknown')
                insights.append(f"📅 Strong seasonal pattern: Peak in month {peak_month}, low in month {low_month}")
                recommendations.append("📋 Plan resource allocation and cash flow management around seasonal patterns")
        
        # ML model insights
        best_model = None
        best_accuracy = float('inf')
        
        for model_name, model_data in ml_models.items():
            if 'mae' in model_data and model_data['mae'] < best_accuracy:
                best_accuracy = model_data['mae']
                best_model = model_name
        
        if best_model:
            insights.append(f"🤖 Best performing forecast model: {ml_models[best_model]['model_type']}")
            if 'mape' in ml_models[best_model]:
                mape = ml_models[best_model].get('mape', 0)
                grade = self._get_accuracy_grade(mape)
                insights.append(f"📊 Forecast accuracy: {grade} (MAPE: {mape:.1f}%)")
        
        # Business dimension insights
        if 'dimension_trends' in trends:
            for dimension, dim_data in trends['dimension_trends'].items():
                if dim_data['top_performer']:
                    insights.append(f"🏆 Top performing {dimension}: {dim_data['top_performer']}")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'summary_score': len([i for i in insights if '📈' in i or '🏆' in i]),  # Positive indicators
            'risk_score': len([i for i in insights if '⚠️' in i or '📉' in i])  # Risk indicators
        }
