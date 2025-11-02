import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from master_assumptions import MasterAssumptionsEngine, RiskFactor, ForecastAssumptions
from advanced_query_engine import AdvancedQueryEngine, QueryCondition, DataAnalyzer
import json
from datetime import datetime

def show_master_assumptions_tab():
    """Master Assumptions & Configuration Tab"""
    st.markdown("## ⚙️ Master Assumptions & Risk Configuration")
    
    # Initialize engines
    if 'assumptions_engine' not in st.session_state:
        st.session_state.assumptions_engine = MasterAssumptionsEngine()
    
    if 'query_engine' not in st.session_state:
        st.session_state.query_engine = AdvancedQueryEngine()
    
    if 'data_analyzer' not in st.session_state:
        st.session_state.data_analyzer = DataAnalyzer()
    
    assumptions_engine = st.session_state.assumptions_engine
    query_engine = st.session_state.query_engine
    data_analyzer = st.session_state.data_analyzer
    
    # Get data
    projects_df = st.session_state.projects_df
    monthly_df = st.session_state.monthly_df
    
    # Main tabs for different configuration areas
    config_tab1, config_tab2, config_tab3, config_tab4 = st.tabs([
        "🎯 Forecast Assumptions", 
        "⚠️ Risk Factors", 
        "🔍 Advanced Queries", 
        "📊 Dual Perspective Forecasting"
    ])
    
    with config_tab1:
        show_forecast_assumptions_config(assumptions_engine)
    
    with config_tab2:
        show_risk_factors_config(assumptions_engine)
    
    with config_tab3:
        show_advanced_queries_config(query_engine, data_analyzer, projects_df, monthly_df)
    
    with config_tab4:
        show_dual_perspective_forecasting(assumptions_engine, projects_df, monthly_df)

def show_forecast_assumptions_config(assumptions_engine):
    """Forecast assumptions configuration"""
    st.markdown("### 🎯 Core Forecast Assumptions")
    
    assumptions = assumptions_engine.assumptions
    
    # Core Growth Parameters
    st.markdown("#### 📈 Growth Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        base_growth = st.slider(
            "Base Growth Rate (Monthly)", 
            min_value=-0.10, 
            max_value=0.20, 
            value=assumptions.base_growth_rate,
            step=0.01,
            format="%.2f%%",
            help="Base monthly growth rate assumption"
        )
    
    with col2:
        market_risk = st.slider(
            "Market Risk Factor", 
            min_value=0.0, 
            max_value=0.30, 
            value=assumptions.market_risk,
            step=0.01,
            format="%.2f%%"
        )
    
    with col3:
        execution_risk = st.slider(
            "Execution Risk Factor", 
            min_value=0.0, 
            max_value=0.20, 
            value=assumptions.execution_risk,
            step=0.01,
            format="%.2f%%"
        )
    
    # Finance vs Sales Perspective Settings
    st.markdown("#### 🏦 Finance Perspective Settings")
    fin_col1, fin_col2, fin_col3 = st.columns(3)
    
    with fin_col1:
        finance_conservatism = st.slider(
            "Finance Conservatism Factor", 
            min_value=0.60, 
            max_value=1.00, 
            value=assumptions.finance_conservatism,
            step=0.05,
            help="Finance applies this multiplier for conservative estimates"
        )
    
    with fin_col2:
        finance_threshold = st.slider(
            "Finance Confidence Threshold", 
            min_value=0.50, 
            max_value=0.95, 
            value=assumptions.finance_probability_threshold,
            step=0.05,
            help="Minimum confidence level for finance inclusion"
        )
    
    with fin_col3:
        finance_buffer = st.slider(
            "Finance Risk Buffer", 
            min_value=0.00, 
            max_value=0.25, 
            value=assumptions.finance_risk_buffer,
            step=0.01,
            help="Additional risk buffer applied by finance"
        )
    
    st.markdown("#### 💼 Sales Perspective Settings")
    sales_col1, sales_col2, sales_col3 = st.columns(3)
    
    with sales_col1:
        sales_optimism = st.slider(
            "Sales Optimism Factor", 
            min_value=1.00, 
            max_value=1.50, 
            value=assumptions.sales_optimism,
            step=0.05,
            help="Sales applies this multiplier for optimistic estimates"
        )
    
    with sales_col2:
        sales_confidence = st.slider(
            "Sales Pipeline Confidence", 
            min_value=0.70, 
            max_value=1.00, 
            value=assumptions.sales_pipeline_confidence,
            step=0.05,
            help="Sales confidence in pipeline conversion"
        )
    
    with sales_col3:
        sales_acceleration = st.slider(
            "Sales Acceleration Factor", 
            min_value=1.00, 
            max_value=1.20, 
            value=assumptions.sales_acceleration_factor,
            step=0.01,
            help="Expected acceleration in sales execution"
        )
    
    # Reconciliation Settings
    st.markdown("#### 🤝 Reconciliation Settings")
    recon_col1, recon_col2 = st.columns(2)
    
    with recon_col1:
        reconciliation_method = st.selectbox(
            "Reconciliation Method",
            ['weighted_average', 'finance_priority', 'sales_priority'],
            index=['weighted_average', 'finance_priority', 'sales_priority'].index(assumptions.reconciliation_method),
            help="How to reconcile differences between finance and sales forecasts"
        )
    
    with recon_col2:
        if reconciliation_method == 'weighted_average':
            finance_weight = st.slider(
                "Finance Weight in Reconciliation", 
                min_value=0.0, 
                max_value=1.0, 
                value=assumptions.finance_weight,
                step=0.1,
                help="Weight given to finance perspective in reconciliation"
            )
        else:
            finance_weight = assumptions.finance_weight
    
    # Update assumptions
    if st.button("💾 Update Assumptions", type="primary"):
        assumptions_engine.update_assumptions(
            base_growth_rate=base_growth,
            market_risk=market_risk,
            execution_risk=execution_risk,
            finance_conservatism=finance_conservatism,
            finance_probability_threshold=finance_threshold,
            finance_risk_buffer=finance_buffer,
            sales_optimism=sales_optimism,
            sales_pipeline_confidence=sales_confidence,
            sales_acceleration_factor=sales_acceleration,
            reconciliation_method=reconciliation_method,
            finance_weight=finance_weight
        )
        st.success("✅ Assumptions updated successfully!")
        st.rerun()
    
    # Show current assumptions summary
    with st.expander("📋 Current Assumptions Summary"):
        assumptions_dict = assumptions_engine.export_assumptions()['forecast_assumptions']
        
        summary_data = []
        for key, value in assumptions_dict.items():
            summary_data.append({
                'Parameter': key.replace('_', ' ').title(),
                'Value': f"{value:.2%}" if isinstance(value, float) and abs(value) <= 2 else str(value)
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

def show_risk_factors_config(assumptions_engine):
    """Risk factors configuration"""
    st.markdown("### ⚠️ Risk Factors Management")
    
    # Display existing risk factors
    st.markdown("#### 📊 Current Risk Factors")
    
    risk_factors_data = []
    for i, rf in enumerate(assumptions_engine.risk_factors):
        risk_factors_data.append({
            'Index': i,
            'Name': rf.name,
            'Category': rf.category,
            'Impact Type': rf.impact_type,
            'Base Value': rf.base_value,
            'Min Value': rf.min_value,
            'Max Value': rf.max_value,
            'Applies To': ', '.join(rf.applies_to)
        })
    
    risk_df = pd.DataFrame(risk_factors_data)
    st.dataframe(risk_df, use_container_width=True)
    
    # Risk factor categories analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # Risk factors by category
        category_counts = pd.Series([rf.category for rf in assumptions_engine.risk_factors]).value_counts()
        
        fig_cat = px.pie(
            values=category_counts.values,
            names=category_counts.index,
            title="Risk Factors by Category"
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col2:
        # Risk impact visualization
        impact_data = []
        for rf in assumptions_engine.risk_factors:
            impact_data.append({
                'Risk Factor': rf.name,
                'Optimistic Impact': rf.min_value if rf.impact_type == 'multiplier' else rf.max_value,
                'Pessimistic Impact': rf.max_value if rf.impact_type == 'multiplier' else rf.min_value,
                'Category': rf.category
            })
        
        impact_df = pd.DataFrame(impact_data)
        
        fig_impact = px.scatter(
            impact_df,
            x='Optimistic Impact',
            y='Pessimistic Impact',
            color='Category',
            hover_name='Risk Factor',
            title="Risk Factor Impact Range"
        )
        st.plotly_chart(fig_impact, use_container_width=True)
    
    # Edit existing risk factor
    st.markdown("#### ✏️ Edit Risk Factor")
    
    if risk_factors_data:
        selected_risk_index = st.selectbox(
            "Select Risk Factor to Edit",
            range(len(assumptions_engine.risk_factors)),
            format_func=lambda x: assumptions_engine.risk_factors[x].name
        )
        
        selected_rf = assumptions_engine.risk_factors[selected_risk_index]
        
        edit_col1, edit_col2, edit_col3 = st.columns(3)
        
        with edit_col1:
            new_base_value = st.number_input(
                "Base Value",
                value=selected_rf.base_value,
                step=0.01,
                key=f"edit_base_value_{selected_risk_index}"
            )
        
        with edit_col2:
            new_min_value = st.number_input(
                "Min Value",
                value=selected_rf.min_value,
                step=0.01,
                key=f"edit_min_value_{selected_risk_index}"
            )
        
        with edit_col3:
            new_max_value = st.number_input(
                "Max Value",
                value=selected_rf.max_value,
                step=0.01,
                key=f"edit_max_value_{selected_risk_index}"
            )
        
        if st.button("💾 Update Risk Factor"):
            assumptions_engine.update_risk_factor(
                selected_rf.name,
                base_value=new_base_value,
                min_value=new_min_value,
                max_value=new_max_value
            )
            st.success(f"✅ Updated {selected_rf.name}")
            st.rerun()
    
    # Add new risk factor
    st.markdown("#### ➕ Add New Risk Factor")
    
    with st.expander("Create New Risk Factor"):
        new_col1, new_col2 = st.columns(2)
        
        with new_col1:
            new_name = st.text_input("Risk Factor Name", key="new_risk_name")
            new_category = st.selectbox(
                "Category",
                ['market', 'operational', 'financial', 'competitive'],
                key="new_risk_category"
            )
            new_impact_type = st.selectbox(
                "Impact Type",
                ['multiplier', 'additive', 'probability'],
                key="new_risk_impact_type"
            )
        
        with new_col2:
            new_base = st.number_input("Base Value", value=1.0, step=0.01, key="new_risk_base_value")
            new_min = st.number_input("Min Value", value=0.8, step=0.01, key="new_risk_min_value")
            new_max = st.number_input("Max Value", value=1.2, step=0.01, key="new_risk_max_value")
        
        new_description = st.text_area("Description", key="new_risk_description")
        new_applies_to = st.multiselect(
            "Applies To",
            ['all', 'offering', 'industry', 'sales_org', 'product_name'],
            default=['all'],
            key="new_risk_applies_to"
        )
        
        if st.button("➕ Add Risk Factor") and new_name:
            new_risk_factor = RiskFactor(
                name=new_name,
                category=new_category,
                impact_type=new_impact_type,
                base_value=new_base,
                min_value=new_min,
                max_value=new_max,
                description=new_description,
                applies_to=new_applies_to
            )
            
            assumptions_engine.add_custom_risk_factor(new_risk_factor)
            st.success(f"✅ Added new risk factor: {new_name}")
            st.rerun()

def show_advanced_queries_config(query_engine, data_analyzer, projects_df, monthly_df):
    """Advanced queries and filtering configuration"""
    st.markdown("### 🔍 Advanced Data Queries & Analysis")
    
    # Query builder
    st.markdown("#### 🛠️ Query Builder")
    
    # Available fields
    available_fields = query_engine.get_available_fields(monthly_df)
    
    # Build query conditions
    if 'query_conditions' not in st.session_state:
        st.session_state.query_conditions = []
    
    # Add condition interface
    with st.expander("➕ Add Query Condition"):
        cond_col1, cond_col2, cond_col3, cond_col4 = st.columns(4)
        
        with cond_col1:
            field = st.selectbox("Field", list(available_fields.keys()), key="new_field")
        
        with cond_col2:
            field_type = available_fields[field]
            if field_type == 'numeric':
                operators = ['=', '!=', '>', '<', '>=', '<=', 'between']
            else:
                operators = ['=', '!=', 'contains', 'in']
            
            operator = st.selectbox("Operator", operators, key="new_operator")
        
        with cond_col3:
            if operator == 'between':
                value1 = st.number_input("Min Value", key="query_min_value")
                value2 = st.number_input("Max Value", key="query_max_value")
                value = [value1, value2]
            elif operator == 'in':
                value_text = st.text_input("Values (comma-separated)", key="query_value_text")
                value = [v.strip() for v in value_text.split(',') if v.strip()]
            elif field_type == 'numeric':
                value = st.number_input("Value", key="query_numeric_value")
            else:
                value = st.text_input("Value", key="query_text_value")
        
        with cond_col4:
            logic = st.selectbox("Logic", ['AND', 'OR'], key="new_logic")
        
        if st.button("➕ Add Condition"):
            new_condition = QueryCondition(field, operator, value, logic)
            st.session_state.query_conditions.append(new_condition)
            st.rerun()
    
    # Display current conditions
    if st.session_state.query_conditions:
        st.markdown("#### 📋 Current Query Conditions")
        
        conditions_data = []
        for i, cond in enumerate(st.session_state.query_conditions):
            conditions_data.append({
                'Index': i,
                'Field': cond.field,
                'Operator': cond.operator,
                'Value': str(cond.value),
                'Logic': cond.logic if i > 0 else 'N/A'
            })
        
        conditions_df = pd.DataFrame(conditions_data)
        st.dataframe(conditions_df, use_container_width=True)
        
        # Query actions
        query_col1, query_col2, query_col3 = st.columns(3)
        
        with query_col1:
            if st.button("🚀 Execute Query"):
                query = query_engine.create_query(st.session_state.query_conditions)
                filtered_data = query.execute(monthly_df)
                
                st.session_state.filtered_data = filtered_data
                st.session_state.query_summary = query.get_summary()
                
                st.success(f"✅ Query executed: {len(filtered_data)} results")
        
        with query_col2:
            query_name = st.text_input("Query Name", key="save_query_name")
            if st.button("💾 Save Query") and query_name:
                query = query_engine.create_query(st.session_state.query_conditions)
                query.name = query_name
                query_engine.save_query(query_name, query)
                st.success(f"✅ Saved query: {query_name}")
        
        with query_col3:
            if st.button("🗑️ Clear Conditions"):
                st.session_state.query_conditions = []
                st.rerun()
    
    # Suggested queries
    st.markdown("#### 💡 Suggested Queries")
    
    suggestions = query_engine.suggest_filters(monthly_df)
    
    if suggestions:
        suggestion_names = [s['name'] for s in suggestions]
        selected_suggestion = st.selectbox("Select Suggested Query", [''] + suggestion_names)
        
        if selected_suggestion:
            suggestion = next(s for s in suggestions if s['name'] == selected_suggestion)
            st.info(f"**{suggestion['name']}**: {suggestion['description']}")
            
            if st.button("🎯 Apply Suggested Query"):
                st.session_state.query_conditions = suggestion['conditions']
                st.rerun()
    
    # Query results analysis
    if hasattr(st.session_state, 'filtered_data') and not st.session_state.filtered_data.empty:
        st.markdown("#### 📊 Query Results Analysis")
        
        filtered_data = st.session_state.filtered_data
        
        # Basic stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Filtered Records", len(filtered_data))
        with col2:
            st.metric("Total Revenue", f"${filtered_data['revenue'].sum():,.0f}")
        with col3:
            st.metric("Avg Revenue", f"${filtered_data['revenue'].mean():,.0f}")
        with col4:
            filter_pct = (len(filtered_data) / len(monthly_df)) * 100
            st.metric("% of Total Data", f"{filter_pct:.1f}%")
        
        # Detailed analysis
        analysis = data_analyzer.analyze_filtered_data(filtered_data, monthly_df)
        
        # Show insights
        insights = data_analyzer.generate_insights(analysis)
        if insights:
            st.markdown("**🔍 Key Insights:**")
            for insight in insights:
                st.info(insight)
        
        # Visualization
        if len(filtered_data) > 0:
            viz_col1, viz_col2 = st.columns(2)
            
            with viz_col1:
                # Revenue by period
                if 'year' in filtered_data.columns and 'month' in filtered_data.columns:
                    period_revenue = filtered_data.groupby(['year', 'month'])['revenue'].sum().reset_index()
                    period_revenue['period'] = period_revenue['year'].astype(str) + '-' + period_revenue['month'].astype(str).str.zfill(2)
                    
                    fig_period = px.line(
                        period_revenue,
                        x='period',
                        y='revenue',
                        title='Filtered Revenue by Period'
                    )
                    st.plotly_chart(fig_period, use_container_width=True)
            
            with viz_col2:
                # Revenue distribution
                fig_dist = px.histogram(
                    filtered_data,
                    x='revenue',
                    title='Revenue Distribution (Filtered)'
                )
                st.plotly_chart(fig_dist, use_container_width=True)

def show_dual_perspective_forecasting(assumptions_engine, projects_df, monthly_df):
    """Dual perspective forecasting and reconciliation"""
    st.markdown("### 📊 Finance vs Sales Perspective Forecasting")
    
    if st.button("🚀 Generate Dual Perspective Forecasts", type="primary"):
        with st.spinner("Generating finance and sales perspective forecasts..."):
            
            # Generate both perspectives
            finance_forecast = assumptions_engine.generate_finance_perspective_forecast(monthly_df, projects_df)
            sales_forecast = assumptions_engine.generate_sales_perspective_forecast(monthly_df, projects_df)
            
            # Reconcile forecasts
            reconciliation_results = assumptions_engine.reconcile_forecasts(finance_forecast, sales_forecast)
            
            # Store results
            st.session_state.finance_forecast = finance_forecast
            st.session_state.sales_forecast = sales_forecast
            st.session_state.reconciliation_results = reconciliation_results
            
            st.success("✅ Dual perspective forecasts generated!")
    
    # Display results if available
    if hasattr(st.session_state, 'reconciliation_results'):
        reconciliation = st.session_state.reconciliation_results
        
        # Check if reconciliation has data
        if reconciliation['reconciliation'].empty:
            st.warning("⚠️ No reconciliation data available. This may be due to:")
            st.write("• No overlapping time periods between finance and sales forecasts")
            st.write("• Empty forecast data")
            st.write("• Missing required columns (year, month, revenue)")
            return
        
        # Summary metrics
        st.markdown("#### 📊 Forecast Comparison Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Finance Total", f"${reconciliation['finance_total']:,.0f}")
        with col2:
            st.metric("Sales Total", f"${reconciliation['sales_total']:,.0f}")
        with col3:
            st.metric("Reconciled Total", f"${reconciliation['reconciled_total']:,.0f}")
        with col4:
            variance = reconciliation['sales_total'] - reconciliation['finance_total']
            variance_pct = (variance / reconciliation['finance_total']) * 100
            st.metric("Variance", f"${variance:,.0f}", f"{variance_pct:+.1f}%")
        
        # Variance analysis
        st.markdown("#### 📈 Variance Analysis")
        
        variance_analysis = reconciliation['variance_analysis']
        
        var_col1, var_col2, var_col3 = st.columns(3)
        
        with var_col1:
            st.metric("Avg Variance %", f"{variance_analysis['avg_variance_pct']:.1f}%")
        with var_col2:
            st.metric("High Variance Months", variance_analysis['high_variance_months'])
        with var_col3:
            st.metric("Variance Trend", variance_analysis['variance_trend'].title())
        
        # Reconciliation chart
        st.markdown("#### 📊 Forecast Reconciliation Visualization")
        
        recon_data = reconciliation['reconciliation']
        
        fig = go.Figure()
        
        # Finance forecast
        fig.add_trace(go.Scatter(
            x=recon_data['year'].astype(str) + '-' + recon_data['month'].astype(str).str.zfill(2),
            y=recon_data['revenue_finance'],
            mode='lines+markers',
            name='Finance Perspective',
            line=dict(color='blue', width=3)
        ))
        
        # Sales forecast
        fig.add_trace(go.Scatter(
            x=recon_data['year'].astype(str) + '-' + recon_data['month'].astype(str).str.zfill(2),
            y=recon_data['revenue_sales'],
            mode='lines+markers',
            name='Sales Perspective',
            line=dict(color='green', width=3)
        ))
        
        # Reconciled forecast
        fig.add_trace(go.Scatter(
            x=recon_data['year'].astype(str) + '-' + recon_data['month'].astype(str).str.zfill(2),
            y=recon_data['reconciled_revenue'],
            mode='lines+markers',
            name='Reconciled Forecast',
            line=dict(color='red', width=3, dash='dash')
        ))
        
        fig.update_layout(
            title='Finance vs Sales Perspective Reconciliation',
            xaxis_title='Period',
            yaxis_title='Revenue ($)',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed reconciliation table
        st.markdown("#### 📋 Detailed Reconciliation")
        
        display_recon = recon_data.copy()
        display_recon['Period'] = display_recon['year'].astype(str) + '-' + display_recon['month'].astype(str).str.zfill(2)
        display_recon['Finance Revenue'] = display_recon['revenue_finance'].apply(lambda x: f"${x:,.0f}")
        display_recon['Sales Revenue'] = display_recon['revenue_sales'].apply(lambda x: f"${x:,.0f}")
        display_recon['Reconciled Revenue'] = display_recon['reconciled_revenue'].apply(lambda x: f"${x:,.0f}")
        display_recon['Variance $'] = display_recon['variance_abs'].apply(lambda x: f"${x:,.0f}")
        display_recon['Variance %'] = display_recon['variance_pct'].apply(lambda x: f"{x:+.1f}%")
        
        st.dataframe(
            display_recon[['Period', 'Finance Revenue', 'Sales Revenue', 'Reconciled Revenue', 'Variance $', 'Variance %']],
            use_container_width=True
        )
        
        # Recommendations
        st.markdown("#### 💡 Reconciliation Recommendations")
        
        if variance_analysis['avg_variance_pct'] > 20:
            st.warning("⚠️ **High variance detected** between finance and sales perspectives. Consider:")
            st.write("• Review assumptions alignment between teams")
            st.write("• Increase collaboration on pipeline assessment")
            st.write("• Implement regular reconciliation meetings")
        elif variance_analysis['avg_variance_pct'] > 10:
            st.info("ℹ️ **Moderate variance** - within acceptable range but monitor trends")
        else:
            st.success("✅ **Low variance** - good alignment between perspectives")
        
        if variance_analysis['high_variance_months'] > 3:
            st.warning("⚠️ Multiple months with high variance - investigate seasonal factors or systematic differences")
        
        # Export reconciliation
        if st.button("💾 Export Reconciliation Results"):
            # Create export data
            export_data = {
                'summary': {
                    'finance_total': reconciliation['finance_total'],
                    'sales_total': reconciliation['sales_total'],
                    'reconciled_total': reconciliation['reconciled_total'],
                    'variance_analysis': variance_analysis
                },
                'detailed_reconciliation': recon_data.to_dict('records')
            }
            
            # Convert to JSON for download
            json_str = json.dumps(export_data, indent=2, default=str)
            
            st.download_button(
                label="⬇️ Download Reconciliation JSON",
                data=json_str,
                file_name=f"forecast_reconciliation_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

# Integration function
def add_master_assumptions_to_main():
    """Function to integrate master assumptions into main app"""
    return show_master_assumptions_tab
