"""
Revenue Forecasting Dashboard - Interactive scenario comparison and visualization
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from revenue_forecaster import RevenueForecaster
from export_utilities import ExportUtilities

class RevenueForecastingDashboard:
    """Interactive dashboard for revenue forecasting with scenario comparison"""

    def __init__(self, historical_data=None):
        self.forecaster = RevenueForecaster(historical_data)
        self.historical_data = historical_data

    def update_data(self, new_data):
        """Update the historical data used for forecasting"""
        self.historical_data = new_data
        self.forecaster = RevenueForecaster(new_data)

    def render_scenario_comparison(self, scenarios_data):
        """
        Render side-by-side scenario comparison

        Args:
            scenarios_data: Dict of scenario_name -> forecast_df
        """
        st.markdown("### 📊 Scenario Comparison")

        if not scenarios_data:
            st.info("No scenario data available. Please generate forecasts first.")
            return

        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs(["📈 Forecast Chart", "📋 Comparison Table", "📊 Growth Analysis"])

        with tab1:
            self._render_forecast_chart(scenarios_data)

        with tab2:
            self._render_comparison_table(scenarios_data)

        with tab3:
            self._render_growth_analysis(scenarios_data)

    def _render_forecast_chart(self, scenarios_data):
        """Render the main forecast comparison chart"""
        fig = go.Figure()

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

        for i, (scenario_name, data) in enumerate(scenarios_data.items()):
            if data is not None and len(data) > 0:
                # Separate historical and forecast data
                historical = data[~data.get('is_forecast', False)] if 'is_forecast' in data.columns else pd.DataFrame()
                forecast = data[data.get('is_forecast', True)] if 'is_forecast' in data.columns else data

                color = colors[i % len(colors)]

                # Plot historical data (solid line)
                if not historical.empty:
                    fig.add_trace(go.Scatter(
                        x=historical['date'] if 'date' in historical.columns else historical['period'],
                        y=historical['revenue'],
                        mode='lines+markers',
                        name=f"{scenario_name} (Historical)",
                        line=dict(color=color, width=2),
                        marker=dict(size=6),
                        showlegend=True
                    ))

                # Plot forecast data (dashed line)
                if not forecast.empty:
                    fig.add_trace(go.Scatter(
                        x=forecast['date'] if 'date' in forecast.columns else forecast['period'],
                        y=forecast['revenue'],
                        mode='lines+markers',
                        name=f"{scenario_name} (Forecast)",
                        line=dict(color=color, width=3, dash='dash'),
                        marker=dict(size=8, symbol='diamond'),
                        showlegend=True
                    ))

        fig.update_layout(
            title="Revenue Forecast Scenarios",
            xaxis_title="Period",
            yaxis_title="Revenue ($M)",
            hovermode='x unified',
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        # Format y-axis as millions
        fig.update_yaxes(tickformat=",.0f", ticksuffix="M")

        st.plotly_chart(fig, use_container_width=True)

        # Show key metrics comparison
        self._render_key_metrics_comparison(scenarios_data)

    def _render_key_metrics_comparison(self, scenarios_data):
        """Render key metrics comparison table"""
        st.markdown("#### 📋 Key Metrics Comparison")

        metrics_data = []
        for scenario_name, data in scenarios_data.items():
            if data is not None and len(data) > 0:
                # Calculate metrics for forecast period only
                forecast_data = data[data.get('is_forecast', True)] if 'is_forecast' in data.columns else data

                if not forecast_data.empty:
                    metrics = self.forecaster.calculate_growth_metrics(forecast_data)

                    metrics_data.append({
                        'Scenario': scenario_name,
                        'Final Revenue': f"${metrics.get('final_revenue', 0):,.1f}M",
                        'Avg Growth': f"{metrics.get('avg_growth_rate', 0):.1f}%",
                        'Total Growth': f"{metrics.get('total_growth', 0):.1f}%",
                        'Volatility': f"{metrics.get('volatility', 0):.1f}%"
                    })

        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)
            st.dataframe(metrics_df, hide_index=True, use_container_width=True)

    def _render_comparison_table(self, scenarios_data):
        """Render detailed comparison table"""
        st.markdown("#### 📋 Detailed Forecast Comparison")

        if not scenarios_data:
            return

        # Get all unique periods
        all_periods = set()
        for data in scenarios_data.values():
            if data is not None and len(data) > 0:
                period_col = 'period' if 'period' in data.columns else 'date'
                all_periods.update(data[period_col].astype(str))

        all_periods = sorted(list(all_periods))

        # Create comparison table
        comparison_data = []
        for period in all_periods:
            row = {'Period': period}

            for scenario_name, data in scenarios_data.items():
                if data is not None and len(data) > 0:
                    period_col = 'period' if 'period' in data.columns else 'date'
                    period_data = data[data[period_col].astype(str) == period]

                    if not period_data.empty:
                        revenue = period_data['revenue'].iloc[0]
                        row[f"{scenario_name} ($M)"] = f"{revenue:,.1f}"
                    else:
                        row[f"{scenario_name} ($M)"] = "-"

            comparison_data.append(row)

        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)

            # Add download button
            csv = comparison_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Comparison CSV",
                data=csv,
                file_name="scenario_comparison.csv",
                mime="text/csv",
                use_container_width=False
            )

    def _render_growth_analysis(self, scenarios_data):
        """Render growth rate analysis across scenarios"""
        st.markdown("#### 📈 Growth Rate Analysis")

        if not scenarios_data:
            return

        # Calculate growth rates for each scenario
        growth_data = []

        for scenario_name, data in scenarios_data.items():
            if data is not None and len(data) > 1:
                forecast_data = data[data.get('is_forecast', True)] if 'is_forecast' in data.columns else data

                if len(forecast_data) > 1:
                    revenues = forecast_data['revenue'].values
                    periods = forecast_data['period'].values if 'period' in forecast_data.columns else range(len(revenues))

                    for i in range(1, len(revenues)):
                        if revenues[i-1] != 0:
                            growth_rate = ((revenues[i] - revenues[i-1]) / revenues[i-1]) * 100

                            growth_data.append({
                                'Scenario': scenario_name,
                                'Period': periods[i],
                                'Growth Rate': growth_rate
                            })

        if growth_data:
            growth_df = pd.DataFrame(growth_data)

            # Create growth rate chart
            fig = px.bar(
                growth_df,
                x='Period',
                y='Growth Rate',
                color='Scenario',
                barmode='group',
                title="Quarter-over-Quarter Growth Rates by Scenario"
            )

            fig.update_layout(
                yaxis_title="Growth Rate (%)",
                height=400
            )

            st.plotly_chart(fig, use_container_width=True)

            # Growth rate statistics
            st.markdown("**Growth Rate Statistics:**")
            stats_data = []

            for scenario_name in growth_df['Scenario'].unique():
                scenario_growth = growth_df[growth_df['Scenario'] == scenario_name]['Growth Rate']

                stats_data.append({
                    'Scenario': scenario_name,
                    'Average': f"{scenario_growth.mean():.1f}%",
                    'Maximum': f"{scenario_growth.max():.1f}%",
                    'Minimum': f"{scenario_growth.min():.1f}%",
                    'Volatility': f"{scenario_growth.std():.1f}%"
                })

            stats_df = pd.DataFrame(stats_data)
            st.dataframe(stats_df, hide_index=True, use_container_width=True)

    def render_revenue_forecast_section(self, scenario_name, assumptions):
        """Render the revenue forecast section for a specific scenario"""
        st.markdown(f"### 📈 Revenue Forecast - {scenario_name}")

        # Generate forecast
        with st.spinner("Generating revenue forecast..."):
            forecast_df = self.forecaster.forecast_revenue(assumptions, periods=8, scenario_name=scenario_name)
            combined_df = self.forecaster.combine_historical_and_forecast(forecast_df, scenario_name)

        # Display forecast chart
        fig = go.Figure()

        # Historical data
        historical = combined_df[~combined_df.get('is_forecast', False)]
        if not historical.empty:
            fig.add_trace(go.Scatter(
                x=historical['date'] if 'date' in historical.columns else historical['period'],
                y=historical['revenue'],
                mode='lines+markers',
                name='Historical',
                line=dict(color='#1f77b4', width=2),
                marker=dict(size=6)
            ))

        # Forecast data
        forecast = combined_df[combined_df.get('is_forecast', True)]
        if not forecast.empty:
            fig.add_trace(go.Scatter(
                x=forecast['date'] if 'date' in forecast.columns else forecast['period'],
                y=forecast['revenue'],
                mode='lines+markers',
                name='Forecast',
                line=dict(color='#ff7f0e', width=3, dash='dash'),
                marker=dict(size=8, symbol='diamond')
            ))

        fig.update_layout(
            title=f"Revenue Forecast - {scenario_name}",
            xaxis_title="Period",
            yaxis_title="Revenue ($M)",
            hovermode='x unified',
            height=400
        )

        fig.update_yaxes(tickformat=",.0f", ticksuffix="M")

        st.plotly_chart(fig, use_container_width=True)

        # Forecast metrics
        if not forecast.empty:
            metrics = self.forecaster.calculate_growth_metrics(forecast)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Final Revenue", f"${metrics.get('final_revenue', 0):,.1f}M")

            with col2:
                st.metric("Avg Growth", f"{metrics.get('avg_growth_rate', 0):.1f}%")

            with col3:
                st.metric("Total Growth", f"{metrics.get('total_growth', 0):.1f}%")

            with col4:
                st.metric("Volatility", f"{metrics.get('volatility', 0):.1f}%")

        # Add export functionality
        st.markdown("---")
        export_utils = ExportUtilities()

        # Prepare data for export
        export_data = export_utils.prepare_forecast_export_data(
            forecast_df, metrics, scenario_name
        )

        # Quick export button
        export_utils.add_export_button(
            export_data,
            button_text="📤 Export Forecast Results",
            scenario_name=scenario_name
        )

        return combined_df
