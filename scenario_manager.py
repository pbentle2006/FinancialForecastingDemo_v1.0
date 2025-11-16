"""
Scenario Manager - Create and compare multiple forecast scenarios
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

class ScenarioManager:
    """Manage multiple forecast scenarios with comparison capabilities"""
    
    def __init__(self):
        self.default_scenarios = ['Base Case', 'Optimistic', 'Conservative']
        
        # Initialize session state
        if 'scenarios' not in st.session_state:
            st.session_state.scenarios = {
                'Base Case': {
                    'created': datetime.now(),
                    'description': 'Base case revenue forecast',
                    'assumptions': {
                        'growth_rate': 5.0,        # Quarterly growth %
                        'seasonal_adjustment': 0.0, # Seasonal variation
                        'market_share': 0.0,       # Market share changes
                        'new_customer_growth': 0.0, # New customer acquisition
                        'existing_customer_growth': 0.0  # Existing customer expansion
                    }
                },
                'Optimistic': {
                    'created': datetime.now(),
                    'description': 'Aggressive growth scenario',
                    'assumptions': {
                        'growth_rate': 12.0,
                        'seasonal_adjustment': 2.0,
                        'market_share': 3.0,
                        'new_customer_growth': 15.0,
                        'existing_customer_growth': 8.0
                    }
                },
                'Conservative': {
                    'created': datetime.now(),
                    'description': 'Conservative growth scenario',
                    'assumptions': {
                        'growth_rate': 1.0,
                        'seasonal_adjustment': -1.0,
                        'market_share': -1.0,
                        'new_customer_growth': -5.0,
                        'existing_customer_growth': -2.0
                    }
                }
            }
        
        if 'active_scenario' not in st.session_state:
            st.session_state.active_scenario = 'Base Case'
    
    def create_scenario(self, name, description='', base_scenario='Base Case', adjustments=None):
        """Create a new scenario"""
        
        if name in st.session_state.scenarios:
            return False, f"Scenario '{name}' already exists"
        
        # Copy base scenario assumptions
        base_assumptions = st.session_state.scenarios[base_scenario]['assumptions'].copy()
        
        # Apply adjustments if provided
        if adjustments:
            for key, value in adjustments.items():
                base_assumptions[key] = value
        
        st.session_state.scenarios[name] = {
            'created': datetime.now(),
            'description': description,
            'assumptions': base_assumptions,
            'base_scenario': base_scenario
        }
        
        return True, f"Scenario '{name}' created successfully"
    
    def delete_scenario(self, name):
        """Delete a scenario"""
        
        if name == 'Base Case':
            return False, "Cannot delete Base Case scenario"
        
        if name not in st.session_state.scenarios:
            return False, f"Scenario '{name}' does not exist"
        
        del st.session_state.scenarios[name]
        
        # Switch to Base Case if deleted scenario was active
        if st.session_state.active_scenario == name:
            st.session_state.active_scenario = 'Base Case'
        
        return True, f"Scenario '{name}' deleted"
    
    def get_scenario_list(self):
        """Get list of all scenarios"""
        return list(st.session_state.scenarios.keys())
    
    def get_active_scenario(self):
        """Get the currently active scenario"""
        return st.session_state.active_scenario
    
    def set_active_scenario(self, name):
        """Set the active scenario"""
        if name in st.session_state.scenarios:
            st.session_state.active_scenario = name
            return True
        return False
    
    def get_scenario_assumptions(self, name):
        """Get assumptions for a scenario"""
        if name in st.session_state.scenarios:
            return st.session_state.scenarios[name]['assumptions']
        return {}
    
    def update_scenario_assumptions(self, name, assumptions):
        """Update assumptions for a scenario"""
        if name in st.session_state.scenarios:
            st.session_state.scenarios[name]['assumptions'].update(assumptions)
            return True
        return False
    
    def compare_scenarios(self, scenario_names, metric_name='Total Revenue'):
        """Compare metrics across scenarios"""
        
        comparison_data = []
        
        for scenario in scenario_names:
            if scenario in st.session_state.scenarios:
                # Get P&L data for this scenario
                pl_key = f'pl_data_{scenario}'
                if pl_key in st.session_state:
                    pl_df = st.session_state[pl_key]
                    
                    # Extract metric
                    metric_rows = pl_df[pl_df['Line Item'] == metric_name]
                    if len(metric_rows) > 0:
                        row_data = {'Scenario': scenario}
                        for col in pl_df.columns:
                            if col != 'Line Item':
                                row_data[col] = metric_rows.iloc[0][col]
                        comparison_data.append(row_data)
        
        if comparison_data:
            return pd.DataFrame(comparison_data)
        return None
    
    def render_scenario_selector(self):
        """Render scenario selector widget"""
        
        scenarios = self.get_scenario_list()
        active = self.get_active_scenario()
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            selected = st.selectbox(
                "Active Scenario",
                scenarios,
                index=scenarios.index(active) if active in scenarios else 0,
                key="scenario_selector"
            )
            
            if selected != active:
                self.set_active_scenario(selected)
                st.rerun()
        
        with col2:
            if st.button("➕ New", key="new_scenario_btn"):
                st.session_state.show_new_scenario_dialog = True
        
        with col3:
            if st.button("📊 Compare", key="compare_scenarios_btn"):
                st.session_state.show_comparison_dialog = True
        
        return selected
    
    def render_new_scenario_dialog(self):
        """Render dialog for creating new scenario"""
        
        if not st.session_state.get('show_new_scenario_dialog', False):
            return
        
        st.markdown("---")
        st.markdown("### ➕ Create New Scenario")
        
        col1, col2 = st.columns(2)
        
        with col1:
            new_name = st.text_input("Scenario Name", key="new_scenario_name")
            base_scenario = st.selectbox(
                "Base Scenario",
                self.get_scenario_list(),
                key="new_scenario_base"
            )
        
        with col2:
            description = st.text_area("Description", key="new_scenario_desc")
        
        st.markdown("**Adjustments:**")
        
        adj_col1, adj_col2, adj_col3 = st.columns(3)
        
        with adj_col1:
            revenue_adj = st.number_input(
                "Revenue Growth (%)",
                value=5.0,
                step=1.0,
                key="new_scenario_revenue"
            )
        
        with adj_col2:
            margin_adj = st.number_input(
                "Margin Target (%)",
                value=28.0,
                step=1.0,
                key="new_scenario_margin"
            )
        
        with adj_col3:
            win_rate_adj = st.number_input(
                "Win Rate (%)",
                value=40.0,
                step=5.0,
                key="new_scenario_winrate"
            )
        
        button_col1, button_col2, button_col3 = st.columns([1, 1, 4])
        
        with button_col1:
            if st.button("✓ Create", type="primary"):
                if new_name:
                    adjustments = {
                        'revenue_growth': revenue_adj,
                        'margin_target': margin_adj,
                        'win_rate': win_rate_adj
                    }
                    success, message = self.create_scenario(
                        new_name,
                        description,
                        base_scenario,
                        adjustments
                    )
                    if success:
                        st.success(message)
                        st.session_state.show_new_scenario_dialog = False
                        st.session_state.active_scenario = new_name
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter a scenario name")
        
        with button_col2:
            if st.button("✗ Cancel"):
                st.session_state.show_new_scenario_dialog = False
                st.rerun()
    
    def render_comparison_view(self):
        """Render scenario comparison view"""
        
        if not st.session_state.get('show_comparison_dialog', False):
            return
        
        st.markdown("---")
        st.markdown("### 📊 Scenario Comparison")
        
        # Select scenarios to compare
        scenarios = self.get_scenario_list()
        selected_scenarios = st.multiselect(
            "Select Scenarios to Compare",
            scenarios,
            default=scenarios[:min(3, len(scenarios))],
            key="comparison_scenarios"
        )
        
        if len(selected_scenarios) < 2:
            st.warning("Please select at least 2 scenarios to compare")
            if st.button("✗ Close"):
                st.session_state.show_comparison_dialog = False
                st.rerun()
            return
        
        # Select metric to compare
        metrics = [
            'Total Revenue',
            'Gross Margin',
            'Gross Margin %',
            'EBITDA',
            'EBITDA %'
        ]
        
        selected_metric = st.selectbox(
            "Metric to Compare",
            metrics,
            key="comparison_metric"
        )
        
        # Get comparison data
        comparison_df = self.compare_scenarios(selected_scenarios, selected_metric)
        
        if comparison_df is not None and len(comparison_df) > 0:
            # Display comparison table
            st.markdown(f"**{selected_metric} Comparison:**")
            st.dataframe(comparison_df, hide_index=True, use_container_width=True)
            
            # Create comparison chart
            st.markdown("---")
            st.markdown("**Visual Comparison:**")
            
            # Prepare data for chart
            periods = [col for col in comparison_df.columns if col != 'Scenario']
            
            fig = go.Figure()
            
            for _, row in comparison_df.iterrows():
                scenario_name = row['Scenario']
                values = [row[period] for period in periods]
                
                fig.add_trace(go.Bar(
                    name=scenario_name,
                    x=periods,
                    y=values,
                    text=[f'${v:,.1f}M' if not isinstance(v, str) else v for v in values],
                    textposition='outside'
                ))
            
            fig.update_layout(
                barmode='group',
                height=400,
                xaxis_title="Period",
                yaxis_title=selected_metric,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Variance analysis
            st.markdown("---")
            st.markdown("**Variance Analysis:**")
            
            if len(selected_scenarios) >= 2:
                base_scenario = selected_scenarios[0]
                
                for scenario in selected_scenarios[1:]:
                    base_row = comparison_df[comparison_df['Scenario'] == base_scenario].iloc[0]
                    comp_row = comparison_df[comparison_df['Scenario'] == scenario].iloc[0]
                    
                    st.markdown(f"**{scenario} vs {base_scenario}:**")
                    
                    var_cols = st.columns(len(periods))
                    for i, period in enumerate(periods):
                        with var_cols[i]:
                            base_val = base_row[period]
                            comp_val = comp_row[period]
                            
                            if isinstance(base_val, (int, float)) and isinstance(comp_val, (int, float)):
                                diff = comp_val - base_val
                                diff_pct = (diff / base_val * 100) if base_val != 0 else 0
                                
                                st.metric(
                                    period,
                                    f"${comp_val:,.1f}M",
                                    delta=f"{diff:+,.1f}M ({diff_pct:+.1f}%)"
                                )
        else:
            st.info("No data available for comparison. Please ensure scenarios have P&L data.")
        
        if st.button("✗ Close Comparison"):
            st.session_state.show_comparison_dialog = False
            st.rerun()
    
    def show_compact_assumptions(self, scenario_name):
        """Show a compact view of revenue assumptions at the top of the page"""
        assumptions = self.get_scenario_assumptions(scenario_name)
        if not assumptions:
            return
            
        # Create a container with a light background
        with st.container():
            st.markdown("### 📊 Revenue Assumptions")
            
            # Display assumptions in columns
            col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
            
            with col1:
                st.metric(
                    "Growth Rate",
                    f"{assumptions.get('growth_rate', 0.0):.1f}%"
                )
            
            with col2:
                st.metric(
                    "Seasonal Adj",
                    f"{assumptions.get('seasonal_adjustment', 0.0):.1f}%"
                )
            
            with col3:
                st.metric(
                    "Market Share",
                    f"{assumptions.get('market_share', 0.0):.1f}%"
                )
            
            with col4:
                st.markdown("""
                <div style='margin-top: 1.5rem;'>
                    <a href='#scenario-assumptions' class='css-1a7z2to' style='text-decoration: none;'>
                        <button style='background-color: #f0f2f6; border: 1px solid #d6d6d6; border-radius: 4px; padding: 0.5rem 1rem; cursor: pointer;'>
                            ⚙️ Edit Assumptions
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
            
            # Show additional assumptions in a compact format
            st.markdown("**Additional Factors:**")
            add_col1, add_col2 = st.columns(2)
            with add_col1:
                st.caption(f"New Customers: {assumptions.get('new_customer_growth', 0.0):.1f}%")
            with add_col2:
                st.caption(f"Existing Growth: {assumptions.get('existing_customer_growth', 0.0):.1f}%")
        
        st.markdown("---")
    
    def render_assumptions_editor(self, scenario_name):
        """Render revenue assumptions editor for a scenario"""
        
        st.markdown(f"<a id='scenario-assumptions'></a>", unsafe_allow_html=True)
        st.markdown(f"### ⚙️ Edit Revenue Assumptions - {scenario_name}")
        
        assumptions = self.get_scenario_assumptions(scenario_name)
        
        if not assumptions:
            st.info("No assumptions defined for this scenario")
            return
        
        # Revenue Growth Assumptions
        st.markdown("#### 📈 Revenue Growth Assumptions")
        st.markdown("Adjust the key drivers of revenue growth:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            growth_rate = st.slider(
                "Quarterly Growth Rate (%)",
                min_value=-10.0,
                max_value=20.0,
                value=assumptions.get('growth_rate', 5.0),
                step=0.5,
                key=f"growth_rate_{scenario_name}",
                help="Expected quarter-over-quarter revenue growth percentage"
            )
            
            seasonal_adjustment = st.slider(
                "Seasonal Adjustment (%)",
                min_value=-15.0,
                max_value=15.0,
                value=assumptions.get('seasonal_adjustment', 0.0),
                step=1.0,
                key=f"seasonal_adj_{scenario_name}",
                help="Seasonal variation in revenue (Q4 typically higher, Q1 typically lower)"
            )
        
        with col2:
            market_share = st.slider(
                "Market Share Change (%)",
                min_value=-5.0,
                max_value=10.0,
                value=assumptions.get('market_share', 0.0),
                step=0.5,
                key=f"market_share_{scenario_name}",
                help="Change in market share percentage (gaining/losing share)"
            )
            
            new_customer_growth = st.slider(
                "New Customer Growth (%)",
                min_value=-20.0,
                max_value=50.0,
                value=assumptions.get('new_customer_growth', 0.0),
                step=5.0,
                key=f"new_customer_{scenario_name}",
                help="Growth rate from new customer acquisition"
            )
        
        # Customer Expansion
        st.markdown("#### 👥 Customer Expansion")
        existing_customer_growth = st.slider(
            "Existing Customer Growth (%)",
            min_value=-15.0,
            max_value=25.0,
            value=assumptions.get('existing_customer_growth', 0.0),
            step=1.0,
            key=f"existing_customer_{scenario_name}",
            help="Growth from existing customer expansion and upsells"
        )
        
        # Save button
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("💾 Save Assumptions", key=f"save_assumptions_{scenario_name}", type="primary"):
                updated_assumptions = {
                    'growth_rate': growth_rate,
                    'seasonal_adjustment': seasonal_adjustment,
                    'market_share': market_share,
                    'new_customer_growth': new_customer_growth,
                    'existing_customer_growth': existing_customer_growth
                }
                self.update_scenario_assumptions(scenario_name, updated_assumptions)
                st.success("✅ Assumptions updated!")
                st.rerun()
        
        with col2:
            if st.button("🔄 Reset to Default", key=f"reset_assumptions_{scenario_name}"):
                # Reset to Base Case defaults
                default_assumptions = {
                    'growth_rate': 5.0,
                    'seasonal_adjustment': 0.0,
                    'market_share': 0.0,
                    'new_customer_growth': 0.0,
                    'existing_customer_growth': 0.0
                }
                self.update_scenario_assumptions(scenario_name, default_assumptions)
                st.success("🔄 Assumptions reset to defaults!")
                st.rerun()
        
        # Show scenario info
        with st.expander("📋 Scenario Details"):
            scenario_info = st.session_state.scenarios[scenario_name]
            st.markdown(f"**Created:** {scenario_info['created'].strftime('%Y-%m-%d %H:%M')}")
            st.markdown(f"**Description:** {scenario_info.get('description', 'No description')}")
            if 'base_scenario' in scenario_info:
                st.markdown(f"**Based on:** {scenario_info['base_scenario']}")
