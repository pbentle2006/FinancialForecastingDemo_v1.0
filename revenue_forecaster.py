"""
Revenue Forecasting Engine - Interactive revenue forecasting with scenario analysis
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class RevenueForecaster:
    """Interactive revenue forecasting engine with real-time updates"""

    def __init__(self, historical_data=None):
        """
        Initialize the revenue forecaster

        Args:
            historical_data: DataFrame with historical revenue data or validated dataframe
        """
        if historical_data is not None and len(historical_data) > 0:
            self.historical_data = self._extract_historical_revenue(historical_data)
        else:
            self.historical_data = self._create_sample_data()

    def _extract_historical_revenue(self, df):
        """
        Extract historical revenue data from validated dataframe
        
        Args:
            df: Validated dataframe from upload
            
        Returns:
            DataFrame with historical revenue data in standard format
        """
        try:
            # Look for revenue columns in order of preference
            revenue_columns = []
            
            # Check for TCV columns
            tcv_cols = [col for col in df.columns if 'tcv' in col.lower() and 'usd' in col.lower()]
            if tcv_cols:
                revenue_columns.extend(tcv_cols)
            
            # Check for IYR columns  
            iyr_cols = [col for col in df.columns if 'iyr' in col.lower()]
            if iyr_cols:
                revenue_columns.extend(iyr_cols)
                
            # Check for margin columns
            margin_cols = [col for col in df.columns if 'margin' in col.lower() and 'usd' in col.lower()]
            if margin_cols:
                revenue_columns.extend(margin_cols)
            
            if not revenue_columns:
                st.warning("⚠️ No revenue columns found in data. Using sample data for forecasting.")
                return self._create_sample_data()
            
            # Use the first available revenue column
            revenue_col = revenue_columns[0]
            st.info(f"📊 Using '{revenue_col}' for historical revenue data")
            
            # Aggregate revenue by month/quarter if possible
            # For now, create a simple time series from the data
            historical_revenues = []
            
            # Group by close_date or reporting_period if available
            date_columns = [col for col in df.columns if any(term in col.lower() for term in ['date', 'period', 'month'])]
            
            if date_columns:
                # Try to group by date
                date_col = date_columns[0]
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                
                # Group by month and sum revenue
                monthly_revenue = df.groupby(df[date_col].dt.to_period('M'))[revenue_col].sum().reset_index()
                monthly_revenue.columns = ['period', 'revenue']
                monthly_revenue['period'] = monthly_revenue['period'].astype(str)
                
                # Convert to standard format
                for idx, row in monthly_revenue.iterrows():
                    try:
                        # Parse period string like '2023-01' 
                        year, month = map(int, row['period'].split('-'))
                        date = pd.Timestamp(year=year, month=month, day=1)
                        
                        historical_revenues.append({
                            'date': date,
                            'period': f"{year}Q{((month-1)//3)+1}",
                            'revenue': float(row['revenue']),
                            'quarter': ((month-1)//3)+1,
                            'year': year
                        })
                    except:
                        continue
            else:
                # No date column - create aggregate historical data
                total_revenue = df[revenue_col].sum()
                avg_monthly = total_revenue / 24  # Assume 2 years of data
                
                # Generate monthly data
                base_date = pd.Timestamp.now() - pd.DateOffset(months=23)
                for i in range(24):
                    date = base_date + pd.DateOffset(months=i)
                    quarter = ((date.month-1)//3)+1
                    
                    historical_revenues.append({
                        'date': date,
                        'period': f"{date.year}Q{quarter}",
                        'revenue': float(avg_monthly),
                        'quarter': quarter,
                        'year': date.year
                    })
            
            if historical_revenues:
                result_df = pd.DataFrame(historical_revenues)
                st.success(f"✅ Extracted {len(result_df)} historical revenue data points")
                return result_df
            else:
                st.warning("⚠️ Could not extract historical revenue data. Using sample data.")
                return self._create_sample_data()
                
        except Exception as e:
            st.error(f"❌ Error extracting historical revenue data: {str(e)}")
            return self._create_sample_data()

    def _create_sample_data(self):
        """Create sample historical revenue data for demonstration"""
        # Generate 24 months of historical data (2 years)
        dates = pd.date_range(start='2022-01-01', periods=24, freq='M')

        # Create realistic revenue pattern with growth and seasonality
        base_revenue = 10.0  # $10M base
        revenues = []

        for i, date in enumerate(dates):
            # Base growth trend (3% quarterly growth)
            growth_factor = (1 + 0.03) ** (i // 3)

            # Seasonal pattern (Q4 highest, Q1 lowest)
            quarter = ((date.month - 1) // 3) + 1
            seasonal_factor = 1 + (0.15 * (quarter == 4)) - (0.1 * (quarter == 1))

            # Add some random variation
            random_factor = np.random.normal(1.0, 0.05)

            revenue = base_revenue * growth_factor * seasonal_factor * random_factor

            revenues.append({
                'date': date,
                'period': f"{date.year}Q{quarter}",
                'revenue': revenue,
                'quarter': quarter,
                'year': date.year
            })

        return pd.DataFrame(revenues)

    def forecast_revenue(self, assumptions, periods=8, scenario_name='Base Case'):
        """
        Generate revenue forecast based on assumptions

        Args:
            assumptions: Dict of revenue assumptions
            periods: Number of periods to forecast
            scenario_name: Name of the scenario

        Returns:
            DataFrame with forecast data
        """
        if self.historical_data is None or len(self.historical_data) == 0:
            return self._create_empty_forecast(periods)

        # Get the last historical revenue value
        last_revenue = self.historical_data['revenue'].iloc[-1]

        # Generate forecast periods (assuming quarterly)
        forecast_data = []

        for i in range(1, periods + 1):
            # Calculate quarter for seasonality
            last_date = self.historical_data['date'].iloc[-1]
            forecast_date = last_date + pd.DateOffset(months=3*i)
            quarter = ((forecast_date.month - 1) // 3) + 1

            # Apply assumptions
            revenue = self._calculate_revenue_for_period(
                last_revenue, assumptions, quarter, i
            )

            forecast_data.append({
                'date': forecast_date,
                'period': f"{forecast_date.year}Q{quarter}",
                'revenue': revenue,
                'quarter': quarter,
                'year': forecast_date.year,
                'scenario': scenario_name,
                'is_forecast': True
            })

            # Update last_revenue for next period
            last_revenue = revenue

        return pd.DataFrame(forecast_data)

    def _calculate_revenue_for_period(self, previous_revenue, assumptions, quarter, period_index):
        """Calculate revenue for a specific forecast period"""

        # Base growth rate
        growth_factor = 1 + (assumptions.get('growth_rate', 5.0) / 100)

        # Seasonal adjustment
        seasonal_base = assumptions.get('seasonal_adjustment', 0.0) / 100

        # Seasonal pattern: Q4 +seasonal_adjustment, Q1 -seasonal_adjustment
        if quarter == 4:
            seasonal_factor = 1 + seasonal_base
        elif quarter == 1:
            seasonal_factor = 1 - seasonal_base
        else:
            seasonal_factor = 1 + (seasonal_base * 0.3)  # Mild effect for Q2/Q3

        # Market share change
        market_factor = 1 + (assumptions.get('market_share', 0.0) / 100)

        # New customer growth (decaying effect over time)
        new_customer_decay = max(0.3, 1 - (period_index * 0.1))  # Decays over time
        new_customer_factor = 1 + (assumptions.get('new_customer_growth', 0.0) / 100 * new_customer_decay)

        # Existing customer growth (sustained effect)
        existing_customer_factor = 1 + (assumptions.get('existing_customer_growth', 0.0) / 100)

        # Calculate final revenue
        revenue = (previous_revenue *
                  growth_factor *
                  seasonal_factor *
                  market_factor *
                  new_customer_factor *
                  existing_customer_factor)

        return max(revenue, 0)  # Ensure non-negative revenue

    def _create_empty_forecast(self, periods):
        """Create empty forecast DataFrame"""
        dates = pd.date_range(start=datetime.now(), periods=periods, freq='Q')
        forecast_data = []

        for i, date in enumerate(dates):
            quarter = ((date.month - 1) // 3) + 1
            forecast_data.append({
                'date': date,
                'period': f"{date.year}Q{quarter}",
                'revenue': 0.0,
                'quarter': quarter,
                'year': date.year,
                'scenario': 'Empty',
                'is_forecast': True
            })

        return pd.DataFrame(forecast_data)

    def combine_historical_and_forecast(self, forecast_df, scenario_name='Base Case'):
        """Combine historical and forecast data"""
        if self.historical_data is None:
            return forecast_df

        # Mark historical data
        historical = self.historical_data.copy()
        historical['scenario'] = scenario_name
        historical['is_forecast'] = False

        # Combine datasets
        combined = pd.concat([historical, forecast_df], ignore_index=True)
        combined = combined.sort_values('date')

        return combined

    def calculate_growth_metrics(self, forecast_df):
        """Calculate growth metrics from forecast data"""
        if len(forecast_df) < 2:
            return {}

        revenues = forecast_df['revenue'].values

        # Calculate quarter-over-quarter growth rates
        growth_rates = []
        for i in range(1, len(revenues)):
            if revenues[i-1] != 0:
                growth = ((revenues[i] - revenues[i-1]) / revenues[i-1]) * 100
                growth_rates.append(growth)

        metrics = {
            'avg_growth_rate': np.mean(growth_rates) if growth_rates else 0,
            'max_growth_rate': max(growth_rates) if growth_rates else 0,
            'min_growth_rate': min(growth_rates) if growth_rates else 0,
            'volatility': np.std(growth_rates) if growth_rates else 0,
            'final_revenue': revenues[-1] if len(revenues) > 0 else 0,
            'total_growth': ((revenues[-1] - revenues[0]) / revenues[0] * 100) if len(revenues) > 1 and revenues[0] != 0 else 0
        }

        return metrics
