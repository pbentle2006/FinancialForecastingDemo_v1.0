"""
Sales View - Pipeline-based forecasting with deal tracking
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

class SalesView:
    """Sales pipeline view with deal-level forecasting"""
    
    def __init__(self):
        # Default sales stages - will be overridden by scenario assumptions
        self.default_sales_stages = {
            'Closed Won': {'probability': 100, 'color': '#2ca02c'},
            'Negotiation': {'probability': 75, 'color': '#1f77b4'},
            'Proposal': {'probability': 50, 'color': '#ff7f0e'},
            'Discovery': {'probability': 10, 'color': '#d62728'},
            'Qualification': {'probability': 25, 'color': '#9467bd'}
        }
    
    def get_sales_stages(self, scenario_name='Base Case'):
        """Get sales stages with probabilities from scenario assumptions"""
        from scenario_manager import ScenarioManager
        
        scenario_mgr = ScenarioManager()
        assumptions = scenario_mgr.get_scenario_assumptions(scenario_name)
        
        if assumptions and 'win_rates' in assumptions:
            win_rates = assumptions['win_rates']
            # Create stages dictionary from win rates
            stages = {}
            for stage, probability in win_rates.items():
                # Assign colors based on probability
                if probability >= 90:
                    color = '#2ca02c'  # Green for high probability
                elif probability >= 70:
                    color = '#1f77b4'  # Blue for medium-high
                elif probability >= 40:
                    color = '#ff7f0e'  # Orange for medium
                elif probability >= 20:
                    color = '#d62728'  # Red for low-medium
                else:
                    color = '#9467bd'  # Purple for low
                    
                stages[stage] = {'probability': probability, 'color': color}
            
            return stages
        else:
            # Fall back to defaults
            return self.default_sales_stages
    
    def create_pipeline_template(self):
        """Create a pipeline template dataframe"""
        
        data = {
            'Deal Name': [],
            'Stage': [],
            'Amount': [],
            'Probability %': [],
            'Weighted Amount': [],
            'Close Date': [],
            'Owner': [],
            'Category': []
        }
        
        return pd.DataFrame(data)
    
    def transform_to_pipeline_format(self, df):
        """Transform uploaded data to pipeline format"""
        
        # Check if already in pipeline format
        required_cols = ['stage', 'amount']
        if all(col in [c.lower() for c in df.columns] for col in required_cols):
            # Rename columns to standard format
            col_mapping = {}
            for col in df.columns:
                col_lower = col.lower()
                if 'stage' in col_lower or 'status' in col_lower:
                    col_mapping[col] = 'Stage'
                elif 'amount' in col_lower or 'value' in col_lower or 'revenue' in col_lower:
                    col_mapping[col] = 'Amount'
                elif 'prob' in col_lower or 'confidence' in col_lower:
                    col_mapping[col] = 'Probability %'
                elif 'owner' in col_lower or 'rep' in col_lower:
                    col_mapping[col] = 'Owner'
                elif 'category' in col_lower or 'industry' in col_lower:
                    col_mapping[col] = 'Category'
                elif 'date' in col_lower or 'close' in col_lower:
                    col_mapping[col] = 'Close Date'
            
            df_renamed = df.rename(columns=col_mapping)
            
            # Add missing columns
            if 'Deal Name' not in df_renamed.columns:
                df_renamed.insert(0, 'Deal Name', [f'Deal {i+1}' for i in range(len(df_renamed))])
            
            if 'Probability %' not in df_renamed.columns and 'Stage' in df_renamed.columns:
                # Assign probabilities based on stage
                df_renamed['Probability %'] = df_renamed['Stage'].map(
                    lambda x: self.sales_stages.get(x, {}).get('probability', 50)
                )
            
            if 'Weighted Amount' not in df_renamed.columns:
                df_renamed['Weighted Amount'] = (
                    df_renamed['Amount'] * df_renamed['Probability %'] / 100
                )
            
            return df_renamed
        
        return self.create_pipeline_template()
    
    def calculate_pipeline_metrics(self, df, scenario_name='Base Case'):
        """Calculate pipeline metrics"""
        
        if len(df) == 0:
            return {}
        
        metrics = {
            'total_deals': len(df),
            'total_value': df['Amount'].sum() if 'Amount' in df.columns else 0,
            'weighted_value': df['Weighted Amount'].sum() if 'Weighted Amount' in df.columns else 0,
            'avg_deal_size': df['Amount'].mean() if 'Amount' in df.columns and len(df) > 0 else 0,
            'win_rate': 0
        }
        
        # Calculate win rate if we have stages
        if 'Stage' in df.columns:
            closed_won = len(df[df['Stage'] == 'Closed Won'])
            total_closed = len(df[df['Stage'].isin(['Closed Won', 'Closed Lost'])])
            if total_closed > 0:
                metrics['win_rate'] = (closed_won / total_closed) * 100
        
        # By stage breakdown
        if 'Stage' in df.columns:
            stage_metrics = {}
            sales_stages = self.get_sales_stages(scenario_name)
            for stage in sales_stages.keys():
                stage_df = df[df['Stage'] == stage]
                stage_metrics[stage] = {
                    'count': len(stage_df),
                    'value': stage_df['Amount'].sum() if len(stage_df) > 0 else 0,
                    'weighted': stage_df['Weighted Amount'].sum() if len(stage_df) > 0 else 0
                }
            metrics['by_stage'] = stage_metrics
        
        return metrics
    
    def create_quarterly_forecast(self, df):
        """Create quarterly forecast from pipeline"""
        
        if 'Close Date' not in df.columns:
            return None
        
        # Convert close dates to datetime
        df['Close Date'] = pd.to_datetime(df['Close Date'], errors='coerce')
        
        # Extract quarter
        df['Quarter'] = df['Close Date'].dt.quarter
        df['Quarter'] = df['Quarter'].apply(lambda x: f'Q{x}' if pd.notna(x) else 'Unknown')
        
        # Group by quarter
        quarterly = df.groupby('Quarter').agg({
            'Amount': 'sum',
            'Weighted Amount': 'sum',
            'Deal Name': 'count'
        }).reset_index()
        
        quarterly.columns = ['Quarter', 'Pipeline', 'Weighted Forecast', 'Deal Count']
        
        return quarterly
    
    def render_sales_view(self, df, scenario_name='Base Case', editable=True):
        """Render the sales pipeline view"""
        
        st.markdown(f"### 💼 Sales View - Pipeline Forecast")
        st.markdown(f"**Scenario:** {scenario_name}")
        
        # Controls
        col1, col2, col3 = st.columns([2, 2, 8])
        
        with col1:
            units = st.selectbox("Units", ["$M", "$K", "$"], key=f"sales_units_{scenario_name}")
        
        with col2:
            view_mode = st.radio("Mode", ["Summary", "Deals"], key=f"sales_mode_{scenario_name}", horizontal=True)
        
        st.markdown("---")
        
        if len(df) == 0:
            st.info("No pipeline data available. Upload deal data or add deals manually.")
            
            if st.button("➕ Add Sample Deals"):
                # Create sample data
                sample_data = {
                    'Deal Name': ['Enterprise Corp', 'Tech Startup', 'Global Inc', 'Local Business', 'Mid-Market Co'],
                    'Stage': ['Commit', 'Best Case', 'Pipeline', 'Closed Won', 'Prospect'],
                    'Amount': [2.5, 1.2, 3.0, 0.8, 1.5],
                    'Probability %': [90, 70, 40, 100, 15],
                    'Owner': ['John', 'Sarah', 'Mike', 'John', 'Sarah'],
                    'Category': ['Enterprise', 'SMB', 'Enterprise', 'SMB', 'Mid-Market']
                }
                df = pd.DataFrame(sample_data)
                df['Weighted Amount'] = df['Amount'] * df['Probability %'] / 100
                df['Close Date'] = pd.date_range(start='2026-01-01', periods=5, freq='M')
                
                st.session_state[f'pipeline_data_{scenario_name}'] = df
                st.rerun()
            
            return df
        
        # Calculate metrics
        metrics = self.calculate_pipeline_metrics(df, scenario_name)
        
        if view_mode == "Summary":
            # Pipeline summary view
            st.markdown("### 📊 Pipeline Summary")
            
            # Get sales stages for this scenario
            sales_stages = self.get_sales_stages(scenario_name)
            
            # Top metrics
            metric_cols = st.columns(5)
            
            with metric_cols[0]:
                st.metric("Total Deals", f"{metrics['total_deals']:,}")
            
            with metric_cols[1]:
                st.metric("Pipeline Value", self.format_number_millions(metrics['total_value']))
            
            with metric_cols[2]:
                st.metric("Weighted Forecast", self.format_number_millions(metrics['weighted_value']))
            
            with metric_cols[3]:
                st.metric("Avg Deal Size", self.format_number_millions(metrics['avg_deal_size']))
            
            with metric_cols[4]:
                if metrics['win_rate'] > 0:
                    st.metric("Win Rate", f"{metrics['win_rate']:.1f}%")
                else:
                    st.metric("Win Rate", "N/A")
            
            st.markdown("---")
            
            # By stage breakdown
            st.markdown("### 🎯 Pipeline by Stage")
            
            if 'by_stage' in metrics:
                stage_data = []
                for stage, data in metrics['by_stage'].items():
                    if data['count'] > 0:
                        stage_data.append({
                            'Stage': stage,
                            'Deals': data['count'],
                            'Value': self.format_number_millions(data['value']),
                            'Probability': sales_stages[stage]['probability'],
                            'Weighted': self.format_number_millions(data['weighted'])
                        })
                
                stage_df = pd.DataFrame(stage_data)
                
                # Display table
                st.dataframe(
                    stage_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        'Stage': st.column_config.TextColumn('Stage', width='medium'),
                        'Deals': st.column_config.NumberColumn('Deals', format='%d'),
                        'Value': st.column_config.TextColumn('Value', width='medium'),
                        'Probability': st.column_config.NumberColumn('Prob %', format='%d%%'),
                        'Weighted': st.column_config.TextColumn('Weighted', width='medium')
                    }
                )
                
                # Funnel chart
                st.markdown("---")
                st.markdown("### 📈 Pipeline Funnel")
                
                fig = go.Figure(go.Funnel(
                    y=[row['Stage'] for _, row in stage_df.iterrows()],
                    x=[metrics['by_stage'][row['Stage']]['weighted'] for _, row in stage_df.iterrows()],
                    textinfo="value+percent initial",
                    marker=dict(
                        color=[sales_stages[stage]['color'] for stage in stage_df['Stage']]
                    )
                ))
                
                fig.update_layout(
                    height=400,
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Quarterly forecast
            st.markdown("---")
            st.markdown("### 📅 Quarterly Forecast")
            
            quarterly = self.create_quarterly_forecast(df)
            if quarterly is not None and len(quarterly) > 0:
                # Format values in millions
                display_quarterly = quarterly.copy()
                display_quarterly['Pipeline'] = display_quarterly['Pipeline'].apply(self.format_number_millions)
                display_quarterly['Weighted Forecast'] = display_quarterly['Weighted Forecast'].apply(self.format_number_millions)
                
                st.dataframe(
                    display_quarterly,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        'Quarter': st.column_config.TextColumn('Quarter'),
                        'Pipeline': st.column_config.TextColumn('Pipeline', width='medium'),
                        'Weighted Forecast': st.column_config.TextColumn('Forecast', width='medium'),
                        'Deal Count': st.column_config.NumberColumn('Deals', format='%d')
                    }
                )
            else:
                st.info("Add close dates to deals to see quarterly forecast")
        
        else:
            # Deal-level view
            st.markdown("### 📋 Deal Pipeline")
            
            if editable:
                # Editable mode
                sales_stages = self.get_sales_stages(scenario_name)
                column_config = {
                    'Deal Name': st.column_config.TextColumn('Deal Name', width='medium'),
                    'Stage': st.column_config.SelectboxColumn(
                        'Stage',
                        options=list(sales_stages.keys()),
                        width='small'
                    ),
                    'Amount': st.column_config.NumberColumn('Amount ($M)', format='%.2f'),
                    'Probability %': st.column_config.NumberColumn('Prob %', format='%d%%'),
                    'Weighted Amount': st.column_config.NumberColumn('Weighted ($M)', format='%.2f'),
                    'Close Date': st.column_config.DateColumn('Close Date'),
                    'Owner': st.column_config.TextColumn('Owner', width='small'),
                    'Category': st.column_config.TextColumn('Category', width='small')
                }
                
                edited_df = st.data_editor(
                    df,
                    column_config=column_config,
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic",
                    height=500,
                    key=f"pipeline_editor_{scenario_name}"
                )
                
                # Recalculate weighted amounts
                if 'Amount' in edited_df.columns and 'Probability %' in edited_df.columns:
                    edited_df['Weighted Amount'] = (
                        edited_df['Amount'] * edited_df['Probability %'] / 100
                    )
                
                # Update probabilities based on stage
                if 'Stage' in edited_df.columns:
                    for idx, row in edited_df.iterrows():
                        stage = row['Stage']
                        if stage in self.sales_stages:
                            edited_df.at[idx, 'Probability %'] = self.sales_stages[stage]['probability']
                
                st.session_state[f'pipeline_data_{scenario_name}'] = edited_df
                
            else:
                # View only
                st.dataframe(
                    df,
                    hide_index=True,
                    use_container_width=True,
                    height=500
                )
        
        return df
    
    def get_pipeline_data(self, scenario_name='Base Case'):
        """Get pipeline data for a scenario"""
        key = f'pipeline_data_{scenario_name}'
        if key in st.session_state:
            return st.session_state[key]
        return self.create_pipeline_template()
    
    def set_pipeline_data(self, df, scenario_name='Base Case'):
        """Set pipeline data for a scenario"""
        key = f'pipeline_data_{scenario_name}'
        st.session_state[key] = df
