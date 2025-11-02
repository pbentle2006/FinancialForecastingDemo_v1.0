import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from advanced_analytics import AdvancedAnalytics

def show_advanced_analytics_tab():
    """Advanced Analytics Tab with ML Models and Insights"""
    st.markdown("## 🤖 Advanced Analytics & Machine Learning")
    
    projects_df = st.session_state.projects_df
    monthly_df = st.session_state.monthly_df
    scenarios = st.session_state.scenarios
    
    # Initialize analytics engine
    analytics_engine = AdvancedAnalytics()
    
    # Analytics Options
    st.markdown("### 🔧 Analytics Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        run_trend_analysis = st.checkbox("📈 Trend Analysis", value=True)
    with col2:
        run_ml_models = st.checkbox("🤖 ML Forecast Models", value=True)
    with col3:
        run_insights = st.checkbox("💡 Business Insights", value=True)
    
    if st.button("🚀 Run Advanced Analytics", type="primary"):
        with st.spinner("Running advanced analytics..."):
            
            # 1. Trend Analysis
            if run_trend_analysis:
                st.markdown("### 📈 Comprehensive Trend Analysis")
                
                trends = analytics_engine.calculate_trend_analysis(monthly_df, projects_df)
                
                # Revenue Growth Trends
                if 'monthly_revenue' in trends:
                    st.markdown("#### 📊 Revenue Growth Trends")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        avg_growth = trends.get('avg_growth_rate', 0)
                        st.metric("📈 Avg Monthly Growth", f"{avg_growth:.1f}%")
                    
                    with col2:
                        volatility = trends.get('growth_volatility', 0)
                        st.metric("📊 Growth Volatility", f"{volatility:.1f}%")
                    
                    with col3:
                        total_periods = len(trends['monthly_revenue'])
                        st.metric("📅 Analysis Periods", total_periods)
                    
                    # Revenue trend chart
                    monthly_trends = trends['monthly_revenue']
                    
                    fig = go.Figure()
                    
                    # Revenue line
                    fig.add_trace(go.Scatter(
                        x=monthly_trends['period'],
                        y=monthly_trends['revenue'],
                        mode='lines+markers',
                        name='Monthly Revenue',
                        line=dict(color='blue', width=3)
                    ))
                    
                    # 3-month moving average
                    fig.add_trace(go.Scatter(
                        x=monthly_trends['period'],
                        y=monthly_trends['revenue_ma3'],
                        mode='lines',
                        name='3-Month MA',
                        line=dict(color='red', width=2, dash='dash')
                    ))
                    
                    fig.update_layout(
                        title='Revenue Trends with Moving Average',
                        xaxis_title='Period',
                        yaxis_title='Revenue ($)',
                        height=400
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                # Business Dimension Trends
                if 'dimension_trends' in trends:
                    st.markdown("#### 🏷️ Business Dimension Performance")
                    
                    dim_tabs = st.tabs(["🎯 Offerings", "🏭 Industries", "👥 Sales Orgs", "📦 Products"])
                    
                    dimensions = ['offering', 'industry', 'sales_org', 'product_name']
                    
                    for i, (tab, dimension) in enumerate(zip(dim_tabs, dimensions)):
                        with tab:
                            if dimension in trends['dimension_trends']:
                                dim_data = trends['dimension_trends'][dimension]
                                
                                if 'performance' in dim_data and not dim_data['performance'].empty:
                                    # Performance table
                                    perf_df = dim_data['performance'].copy()
                                    perf_df['sum'] = perf_df['sum'].apply(lambda x: f"${x:,.0f}")
                                    perf_df['mean'] = perf_df['mean'].apply(lambda x: f"${x:,.0f}")
                                    
                                    st.dataframe(perf_df, use_container_width=True)
                                    
                                    # Top performer
                                    if dim_data['top_performer']:
                                        st.success(f"🏆 Top Performer: **{dim_data['top_performer']}**")
                                else:
                                    st.info(f"No data available for {dimension.replace('_', ' ').title()}")
                
                # Seasonality Analysis
                if 'seasonality' in trends and trends['seasonality']:
                    st.markdown("#### 📅 Seasonality Analysis")
                    
                    seasonality = trends['seasonality']
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("📈 Peak Month", seasonality.get('peak_month', 'N/A'))
                    with col2:
                        st.metric("📉 Low Month", seasonality.get('low_month', 'N/A'))
                    with col3:
                        strength = seasonality.get('seasonality_strength', 0)
                        if strength is not None:
                            st.metric("🌊 Seasonality Strength", f"{strength:.2f}")
                        else:
                            st.metric("🌊 Seasonality Strength", "N/A")
                    
                    # Seasonality chart
                    if 'monthly_patterns' in seasonality:
                        monthly_patterns = seasonality['monthly_patterns']
                        
                        fig = px.bar(
                            monthly_patterns,
                            x='month',
                            y='seasonality_index',
                            title='Seasonal Revenue Patterns (Index: 1.0 = Average)',
                            labels={'seasonality_index': 'Seasonality Index', 'month': 'Month'}
                        )
                        fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                                     annotation_text="Average")
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Portfolio Concentration
                if 'concentration' in trends:
                    st.markdown("#### ⚖️ Portfolio Concentration Analysis")
                    
                    conc = trends['concentration']
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("🔝 Top 5 Projects", f"{conc['top_5_projects_pct']:.1f}%")
                    with col2:
                        st.metric("🏢 Top Client", f"{conc['top_client_pct']:.1f}%")
                    with col3:
                        st.metric("👥 Total Clients", conc['client_count'])
                    with col4:
                        st.metric("📋 Total Projects", conc['project_count'])
                    
                    # Risk assessment
                    risk_level = "🔴 High" if conc['top_client_pct'] > 40 else "🟡 Medium" if conc['top_client_pct'] > 25 else "🟢 Low"
                    st.info(f"**Concentration Risk Level:** {risk_level}")
                    
                    # Top performers tables
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**🏆 Top Projects:**")
                        top_projects = conc['top_projects'][['project_id', 'client', 'revenue']].copy()
                        top_projects['revenue'] = top_projects['revenue'].apply(lambda x: f"${x:,.0f}")
                        st.dataframe(top_projects, use_container_width=True)
                    
                    with col2:
                        st.markdown("**🏢 Top Clients:**")
                        top_clients = conc['top_clients'].copy()
                        top_clients['revenue'] = top_clients['revenue'].apply(lambda x: f"${x:,.0f}")
                        st.dataframe(top_clients, use_container_width=True)
            
            # 2. Machine Learning Models
            if run_ml_models:
                st.markdown("### 🤖 Machine Learning Forecast Models")
                
                ml_models = analytics_engine.build_ml_forecast_models(monthly_df, projects_df)
                
                if 'error' in ml_models:
                    st.warning(f"⚠️ {ml_models['error']}")
                else:
                    # Model comparison
                    st.markdown("#### 📊 Model Performance Comparison")
                    
                    model_comparison = []
                    for model_name, model_data in ml_models.items():
                        if 'mae' in model_data:
                            model_comparison.append({
                                'Model': model_data['model_type'],
                                'MAE': f"${model_data['mae']:,.0f}",
                                'MSE': f"${model_data['mse']:,.0f}",
                                'R²': f"{model_data.get('r_squared', 0):.3f}"
                            })
                    
                    if model_comparison:
                        comparison_df = pd.DataFrame(model_comparison)
                        st.dataframe(comparison_df, use_container_width=True)
                        
                        # Best model
                        best_model_name = min(ml_models.keys(), 
                                            key=lambda x: ml_models[x].get('mae', float('inf')) 
                                            if 'mae' in ml_models[x] else float('inf'))
                        
                        if best_model_name and 'mae' in ml_models[best_model_name]:
                            best_model = ml_models[best_model_name]
                            st.success(f"🏆 **Best Model:** {best_model['model_type']} (MAE: ${best_model['mae']:,.0f})")
                    
                    # Individual model details
                    model_tabs = st.tabs([ml_models[k]['model_type'] for k in ml_models.keys() if 'model_type' in ml_models[k]])
                    
                    model_keys = [k for k in ml_models.keys() if 'model_type' in ml_models[k]]
                    
                    for tab, model_key in zip(model_tabs, model_keys):
                        with tab:
                            model_data = ml_models[model_key]
                            
                            # Model metrics
                            if 'mae' in model_data:
                                col1, col2, col3 = st.columns(3)
                                
                                with col1:
                                    st.metric("MAE", f"${model_data['mae']:,.0f}")
                                with col2:
                                    st.metric("R²", f"{model_data.get('r_squared', 0):.3f}")
                                with col3:
                                    if 'trend_slope' in model_data:
                                        slope = model_data['trend_slope']
                                        st.metric("Trend Slope", f"${slope:,.0f}/period")
                            
                            # Future forecast
                            if 'future_forecast' in model_data:
                                st.markdown("**📈 6-Month Forecast:**")
                                
                                future_data = []
                                for i, forecast in enumerate(model_data['future_forecast']):
                                    future_data.append({
                                        'Period': f"Month +{i+1}",
                                        'Forecast': f"${forecast:,.0f}"
                                    })
                                
                                forecast_df = pd.DataFrame(future_data)
                                st.dataframe(forecast_df, use_container_width=True)
                            
                            # Feature importance (for Random Forest)
                            if 'feature_importance' in model_data:
                                st.markdown("**🎯 Feature Importance:**")
                                
                                importance_data = []
                                for feature, importance in model_data['feature_importance'].items():
                                    importance_data.append({
                                        'Feature': feature.replace('_', ' ').title(),
                                        'Importance': f"{importance:.3f}"
                                    })
                                
                                importance_df = pd.DataFrame(importance_data)
                                importance_df = importance_df.sort_values('Importance', ascending=False)
                                st.dataframe(importance_df, use_container_width=True)
            
            # 3. Business Insights
            if run_insights:
                st.markdown("### 💡 AI-Generated Business Insights")
                
                # Generate insights
                try:
                    if run_trend_analysis and 'trends' in locals():
                        if run_ml_models and 'ml_models' in locals():
                            insights_data = analytics_engine.generate_insights_and_recommendations(
                                trends, ml_models, projects_df, monthly_df
                            )
                        else:
                            insights_data = analytics_engine.generate_insights_and_recommendations(
                                trends, {}, projects_df, monthly_df
                            )
                    else:
                        insights_data = {
                            'insights': ['📊 Enable Trend Analysis to generate insights'],
                            'recommendations': [],
                            'summary_score': 0,
                            'risk_score': 0
                        }
                except Exception as e:
                    st.error(f"❌ Error generating insights: {e}")
                    insights_data = {
                        'insights': ['⚠️ Unable to generate insights due to data processing error'],
                        'recommendations': [],
                        'summary_score': 0,
                        'risk_score': 0
                    }
                
                # Summary scores
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("📈 Positive Indicators", insights_data['summary_score'])
                with col2:
                    st.metric("⚠️ Risk Indicators", insights_data['risk_score'])
                with col3:
                    total_insights = len(insights_data['insights'])
                    st.metric("💡 Total Insights", total_insights)
                
                # Key Insights
                if insights_data['insights']:
                    st.markdown("#### 🔍 Key Business Insights")
                    
                    for insight in insights_data['insights']:
                        st.info(insight)
                
                # Recommendations
                if insights_data['recommendations']:
                    st.markdown("#### 🎯 Strategic Recommendations")
                    
                    for recommendation in insights_data['recommendations']:
                        st.success(recommendation)
                
                # Overall assessment
                if insights_data['summary_score'] > insights_data['risk_score']:
                    st.balloons()
                    st.success("🎉 **Overall Assessment:** Portfolio shows strong positive indicators!")
                elif insights_data['risk_score'] > insights_data['summary_score']:
                    st.warning("⚠️ **Overall Assessment:** Portfolio shows some risk factors that need attention.")
                else:
                    st.info("📊 **Overall Assessment:** Portfolio shows balanced risk and opportunity profile.")

# Add this function to the main app file
def add_advanced_analytics_to_main():
    """Function to integrate advanced analytics into main app"""
    return show_advanced_analytics_tab
