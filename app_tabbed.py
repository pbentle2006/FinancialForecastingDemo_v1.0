import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from validation_engine import ForecastValidationEngine
from advanced_analytics import AdvancedAnalytics
from advanced_analytics_tab import show_advanced_analytics_tab
from master_assumptions_tab import show_master_assumptions_tab

# Page configuration
st.set_page_config(
    page_title="Tabbed Forecasting Platform",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Financial Forecasting Platform")
st.markdown("**Organized Tabbed Interface for Professional Forecasting**")

def create_autocomplete_selectbox(label, options, key, help_text=None, default_value=None):
    """Create an integrated autocomplete selectbox"""
    
    # Initialize session state for this component
    if f"{key}_value" not in st.session_state:
        st.session_state[f"{key}_value"] = default_value or options[0] if options else ""
    if f"{key}_input" not in st.session_state:
        st.session_state[f"{key}_input"] = ""
    
    # Create container for the autocomplete
    container = st.container()
    
    with container:
        # Text input that acts as both search and display
        current_input = st.text_input(
            label,
            value=st.session_state[f"{key}_input"],
            placeholder=f"Type to search or select {label.lower()}...",
            key=f"{key}_text_input",
            help=help_text
        )
        
        # Update input state
        st.session_state[f"{key}_input"] = current_input
        
        # Filter options based on current input
        if current_input:
            search_lower = current_input.lower()
            
            # Smart matching with priority
            exact_matches = [opt for opt in options if search_lower == opt.lower()]
            starts_with = [opt for opt in options if opt.lower().startswith(search_lower) and opt not in exact_matches]
            contains = [opt for opt in options if search_lower in opt.lower() and opt not in exact_matches and opt not in starts_with]
            
            filtered_options = exact_matches + starts_with + contains
            
            # Limit results for performance
            if len(filtered_options) > 10:
                filtered_options = filtered_options[:10]
        else:
            # Show top options when no input
            filtered_options = options[:10] if len(options) > 10 else options
        
        # Show filtered options as buttons for selection
        if filtered_options and current_input:
            st.markdown("**Suggestions:**")
            
            # Create columns for suggestions (max 2 per row)
            cols_per_row = 2
            for i in range(0, len(filtered_options), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for j, option in enumerate(filtered_options[i:i+cols_per_row]):
                    with cols[j]:
                        if st.button(
                            f"✓ {option}", 
                            key=f"{key}_option_{i+j}",
                            use_container_width=True,
                            type="secondary"
                        ):
                            st.session_state[f"{key}_value"] = option
                            st.session_state[f"{key}_input"] = option
                            st.rerun()
        
        # Show current selection
        if st.session_state[f"{key}_value"] and st.session_state[f"{key}_value"] != st.session_state[f"{key}_input"]:
            st.success(f"Selected: **{st.session_state[f'{key}_value']}**")
            
            if st.button(f"Clear selection", key=f"{key}_clear"):
                st.session_state[f"{key}_value"] = ""
                st.session_state[f"{key}_input"] = ""
                st.rerun()
        
        # Auto-select if exact match
        if current_input in options:
            st.session_state[f"{key}_value"] = current_input
    
    return st.session_state[f"{key}_value"]

def read_file_smart(file):
    """Smart file reader with enhanced error handling"""
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = None
            for header_row in [0, 1, 2]:
                try:
                    test_df = pd.read_excel(file, header=header_row)
                    unnamed_count = sum(1 for col in test_df.columns if 'Unnamed' in str(col))
                    
                    if unnamed_count < len(test_df.columns) * 0.3:
                        df = test_df
                        st.info(f"✅ Using header row {header_row + 1}")
                        break
                except:
                    continue
            
            if df is None:
                df = pd.read_excel(file, header=0)
                st.warning("⚠️ Using default headers")
        
        return df
    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
        return None

def find_monthly_columns(df):
    """Enhanced monthly column detection with future period awareness"""
    monthly_patterns = [
        'FY202', 'FY203',  # FY2025-04, FY2030-12, etc.
        '2024-', '2025-', '2026-', '2027-', '2028-', '2029-', '2030-',
        'Q1 ', 'Q2 ', 'Q3 ', 'Q4 ',
    ]
    
    monthly_cols = []
    current_year = datetime.now().year
    
    for col in df.columns:
        col_str = str(col)
        if any(pattern in col_str for pattern in monthly_patterns):
            try:
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0:
                    # Categorize as historical vs future
                    year = extract_year_from_column(col)
                    col_info = {
                        'name': col,
                        'year': year,
                        'is_future': year > current_year,
                        'is_historical': year <= current_year
                    }
                    monthly_cols.append(col_info)
            except:
                continue
    
    return monthly_cols

def extract_year_from_column(col_name):
    """Extract year from column name"""
    col_str = str(col_name)
    import re
    year_match = re.search(r'(202[0-9]|203[0-9])', col_str)
    if year_match:
        return int(year_match.group(1))
    return datetime.now().year

def create_enhanced_mapping_interface(df, monthly_cols):
    """Enhanced mapping interface with business dimensions"""
    st.markdown("### 🔧 Column Mapping")
    
    col_options = ["[Skip this field]"] + list(df.columns)
    
    # Core Fields
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**📋 Core Fields:**")
        id_col = create_autocomplete_selectbox("🆔 Project ID", col_options, "id_mapping")
        name_col = create_autocomplete_selectbox("📝 Project Name", col_options, "name_mapping")
        client_col = create_autocomplete_selectbox("🏢 Client Name", col_options, "client_mapping")
    
    with col2:
        st.markdown("**💰 Financial Fields:**")
        value_col = create_autocomplete_selectbox("💵 Total Value", col_options, "value_mapping")
        status_col = create_autocomplete_selectbox("📊 Status", col_options, "status_mapping")
        date_col = create_autocomplete_selectbox("📅 Key Date", col_options, "date_mapping")
    
    with col3:
        st.markdown("**🏷️ Business Dimensions:**")
        offering_col = create_autocomplete_selectbox("🎯 Offering", col_options, "offering_mapping", "Service offering or solution type")
        product_col = create_autocomplete_selectbox("📦 Product Name", col_options, "product_mapping", "Specific product or service")
        industry_col = create_autocomplete_selectbox("🏭 Industry", col_options, "industry_mapping", "Client industry or vertical")
        sales_org_col = create_autocomplete_selectbox("👥 Sales Org", col_options, "sales_org_mapping", "Sales organization or region")
    
    # Monthly columns analysis
    if monthly_cols:
        historical_cols = [col for col in monthly_cols if col['is_historical']]
        future_cols = [col for col in monthly_cols if col['is_future']]
        
        st.success(f"✅ **{len(monthly_cols)} monthly columns detected**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📊 **Historical periods**: {len(historical_cols)} columns")
        with col2:
            st.info(f"🔮 **Future periods**: {len(future_cols)} columns")
    
    # Create mapping including business dimensions
    mapping = {}
    field_mappings = [
        ('id', id_col), ('name', name_col), ('client', client_col),
        ('total_value', value_col), ('status', status_col), ('date', date_col),
        ('offering', offering_col), ('product_name', product_col), 
        ('industry', industry_col), ('sales_org', sales_org_col)
    ]
    
    for field, col in field_mappings:
        if col != "[Skip this field]":
            mapping[field] = col
    
    # Show mapping summary
    if len(mapping) > 3:  # Show if we have more than just basic fields
        with st.expander("📋 Mapping Summary"):
            core_fields = ['id', 'name', 'client', 'total_value', 'status', 'date']
            business_fields = ['offering', 'product_name', 'industry', 'sales_org']
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Core Fields Mapped:**")
                for field in core_fields:
                    if field in mapping:
                        st.write(f"✅ {field.replace('_', ' ').title()}: `{mapping[field]}`")
            
            with col2:
                st.markdown("**Business Dimensions Mapped:**")
                for field in business_fields:
                    if field in mapping:
                        st.write(f"✅ {field.replace('_', ' ').title()}: `{mapping[field]}`")
                    else:
                        st.write(f"⚪ {field.replace('_', ' ').title()}: Not mapped")
    
    return mapping

def process_enhanced_data(df, mapping, monthly_cols):
    """Enhanced data processing"""
    
    # Create projects dataframe with business dimensions
    projects = []
    for idx, row in df.iterrows():
        project = {
            'project_id': row.get(mapping.get('id', ''), f"PROJ_{idx+1}"),
            'name': row.get(mapping.get('name', ''), f"Project {idx+1}"),
            'client': row.get(mapping.get('client', ''), "Unknown"),
            'status': row.get(mapping.get('status', ''), "Active"),
            'offering': row.get(mapping.get('offering', ''), "Not Specified"),
            'product_name': row.get(mapping.get('product_name', ''), "Not Specified"),
            'industry': row.get(mapping.get('industry', ''), "Not Specified"),
            'sales_org': row.get(mapping.get('sales_org', ''), "Not Specified"),
        }
        
        total_value = row.get(mapping.get('total_value', ''), 0)
        try:
            project['total_value'] = float(total_value) if pd.notna(total_value) else 0
        except:
            project['total_value'] = 0
            
        projects.append(project)
    
    projects_df = pd.DataFrame(projects)
    
    # Process monthly data
    monthly_data = []
    for idx, row in df.iterrows():
        project_id = row.get(mapping.get('id', ''), f"PROJ_{idx+1}")
        
        for col_info in monthly_cols:
            col = col_info['name']
            value = row[col]
            if pd.notna(value) and value != 0:
                try:
                    revenue = float(value)
                    if revenue > 0:
                        year, month = parse_date_from_column(col)
                        
                        monthly_data.append({
                            'project_id': project_id,
                            'year': year,
                            'month': month,
                            'column': col,
                            'revenue': revenue,
                            'period': f"{year}-{month:02d}",
                            'is_historical': col_info['is_historical'],
                            'is_future': col_info['is_future']
                        })
                except:
                    continue
    
    monthly_df = pd.DataFrame(monthly_data)
    
    return projects_df, monthly_df

def parse_date_from_column(col_name):
    """Parse year and month from column name"""
    col_str = str(col_name)
    
    if 'FY' in col_str and '-' in col_str:
        try:
            parts = col_str.split('-')
            year = int(parts[0].replace('FY', ''))
            month = int(parts[1])
            return year, month
        except:
            pass
    
    if '-' in col_str:
        try:
            parts = col_str.split('-')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
                return year, month
        except:
            pass
    
    return datetime.now().year, 1

def generate_enhanced_scenarios(monthly_df):
    """Generate scenarios with enhanced analytics"""
    scenarios = {}
    
    base_scenarios = {
        'Conservative': 0.85,
        'Most Likely': 1.00,
        'Optimistic': 1.15
    }
    
    for scenario_name, multiplier in base_scenarios.items():
        scenario_data = monthly_df.copy()
        scenario_data['revenue_adjusted'] = scenario_data['revenue'] * multiplier
        
        monthly_totals = scenario_data.groupby(['year', 'month']).agg({
            'revenue_adjusted': 'sum',
            'project_id': 'nunique'
        }).reset_index()
        monthly_totals['period'] = monthly_totals['year'].astype(str) + '-' + monthly_totals['month'].astype(str).str.zfill(2)
        
        scenarios[scenario_name] = {
            'data': scenario_data,
            'multiplier': multiplier,
            'total_revenue': scenario_data['revenue_adjusted'].sum(),
            'monthly_totals': monthly_totals,
            'avg_monthly': scenario_data['revenue_adjusted'].sum() / len(monthly_totals) if len(monthly_totals) > 0 else 0
        }
    
    return scenarios

# Enhanced Validation Engine with Future Period Logic
class EnhancedValidationEngine(ForecastValidationEngine):
    """Enhanced validation engine with future period awareness"""
    
    def validate_data_quality(self, df, monthly_cols, mapping):
        """Enhanced validation with future period logic"""
        
        quality_issues = []
        quality_warnings = []
        quality_info = []
        
        total_rows = len(df)
        current_year = datetime.now().year
        
        # Separate historical and future columns
        historical_cols = [col for col in monthly_cols if col['is_historical']]
        future_cols = [col for col in monthly_cols if col['is_future']]
        
        # 1. Validate mapped columns
        for field, column in mapping.items():
            if column in df.columns:
                null_count = df[column].isnull().sum()
                null_percentage = (null_count / total_rows) * 100
                
                if null_percentage > 50:
                    quality_issues.append(f"❌ {field.title()}: {null_percentage:.1f}% missing data")
                elif null_percentage > 20:
                    quality_warnings.append(f"⚠️ {field.title()}: {null_percentage:.1f}% missing data")
        
        # 2. Validate historical data (stricter validation)
        if historical_cols:
            historical_data_issues = self._validate_historical_data(df, historical_cols)
            quality_issues.extend(historical_data_issues['issues'])
            quality_warnings.extend(historical_data_issues['warnings'])
            quality_info.extend(historical_data_issues['info'])
        
        # 3. Validate future data (more lenient - zeros are expected)
        if future_cols:
            future_data_info = self._validate_future_data(df, future_cols)
            quality_info.extend(future_data_info['info'])
        
        return {
            'issues': quality_issues,
            'warnings': quality_warnings,
            'info': quality_info,
            'overall_score': self._calculate_enhanced_quality_score(quality_issues, quality_warnings, quality_info, historical_cols, future_cols),
            'historical_columns': len(historical_cols),
            'future_columns': len(future_cols)
        }
    
    def _validate_historical_data(self, df, historical_cols):
        """Strict validation for historical data"""
        issues = []
        warnings = []
        info = []
        
        for col_info in historical_cols:
            col = col_info['name']
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                non_null_count = numeric_data.notna().sum()
                zero_count = (numeric_data == 0).sum()
                
                if non_null_count == 0:
                    warnings.append(f"⚠️ Historical column '{col}': No valid data")
                elif zero_count > len(df) * 0.7:
                    warnings.append(f"⚠️ Historical column '{col}': {zero_count/len(df)*100:.1f}% zero values")
                else:
                    info.append(f"ℹ️ Historical column '{col}': {non_null_count} valid entries")
                    
            except Exception:
                issues.append(f"❌ Historical column '{col}': Cannot process as numeric")
        
        return {'issues': issues, 'warnings': warnings, 'info': info}
    
    def _validate_future_data(self, df, future_cols):
        """Lenient validation for future data - zeros are expected"""
        info = []
        
        non_zero_future_cols = 0
        for col_info in future_cols:
            col = col_info['name']
            try:
                numeric_data = pd.to_numeric(df[col], errors='coerce')
                non_zero_count = (numeric_data > 0).sum()
                
                if non_zero_count > 0:
                    non_zero_future_cols += 1
                    info.append(f"ℹ️ Future column '{col}': {non_zero_count} planned entries")
                    
            except Exception:
                continue
        
        if non_zero_future_cols > 0:
            info.append(f"ℹ️ Found planned revenue in {non_zero_future_cols} future periods")
        else:
            info.append("ℹ️ No future revenue planned (normal for current forecasts)")
        
        return {'info': info}
    
    def _calculate_enhanced_quality_score(self, issues, warnings, info, historical_cols, future_cols):
        """Enhanced quality score that considers historical vs future data"""
        
        base_score = 100
        
        # Heavier penalty for issues in historical data
        base_score -= len(issues) * 25
        base_score -= len(warnings) * 15
        
        # Bonus for having good historical data coverage
        if len(historical_cols) > 12:  # More than a year of history
            base_score += 10
        elif len(historical_cols) > 6:  # More than 6 months
            base_score += 5
        
        # Small bonus for having future planning data
        if len(future_cols) > 0:
            base_score += 5
        
        return max(0, min(100, base_score))

# Main Application with Tabbed Interface
def main():
    # Sidebar configuration
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        conservative_mult = st.slider("Conservative Multiplier", 0.5, 1.0, 0.85, 0.05)
        optimistic_mult = st.slider("Optimistic Multiplier", 1.0, 2.0, 1.15, 0.05)
    
    # File upload
    uploaded_file = st.file_uploader(
        "📤 Upload Revenue Phasing File",
        type=['xlsx', 'xls', 'csv'],
        help="Upload your file with monthly revenue columns"
    )
    
    if uploaded_file:
        df = read_file_smart(uploaded_file)
        
        if df is not None:
            st.success(f"📊 Loaded: {len(df)} rows, {len(df.columns)} columns")
            
            # Find monthly columns with future awareness
            monthly_cols = find_monthly_columns(df)
            
            if monthly_cols:
                # Enhanced mapping interface
                mapping = create_enhanced_mapping_interface(df, monthly_cols)
                
                if st.button("🚀 Process Data", type="primary"):
                    with st.spinner("Processing data..."):
                        try:
                            # Process data
                            projects_df, monthly_df = process_enhanced_data(df, mapping, monthly_cols)
                            
                            if not monthly_df.empty:
                                # Generate scenarios
                                scenarios = generate_enhanced_scenarios(monthly_df)
                                
                                # Store in session state
                                st.session_state.projects_df = projects_df
                                st.session_state.monthly_df = monthly_df
                                st.session_state.scenarios = scenarios
                                st.session_state.mapping = mapping
                                st.session_state.monthly_cols = monthly_cols
                                st.session_state.original_df = df
                                st.session_state.data_processed = True
                                
                                st.success("✅ Data processed successfully!")
                                st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ Processing failed: {e}")
            else:
                st.warning("⚠️ No monthly columns detected")
    
    # Tabbed Interface (only show if data is processed)
    if hasattr(st.session_state, 'data_processed') and st.session_state.data_processed:
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Data Integrity", "📊 Forecast Dashboard", "🤖 Advanced Analytics", "⚙️ Master Assumptions", "💾 Export & Reports"])
        
        with tab1:
            show_data_integrity_tab()
        
        with tab2:
            show_forecast_dashboard_tab()
        
        with tab3:
            show_advanced_analytics_tab()
        
        with tab4:
            show_master_assumptions_tab()
        
        with tab5:
            show_export_tab()

def show_data_integrity_tab():
    """Data Integrity and Validation Tab"""
    st.markdown("## 🔍 Data Integrity & Quality Assessment")
    
    # Initialize enhanced validation engine
    validation_engine = EnhancedValidationEngine()
    
    # Run validation
    quality_results = validation_engine.validate_data_quality(
        st.session_state.original_df, 
        st.session_state.monthly_cols, 
        st.session_state.mapping
    )
    
    confidence_metrics = validation_engine.calculate_forecast_confidence(
        st.session_state.monthly_df, 
        st.session_state.scenarios
    )
    
    anomalies = validation_engine.detect_forecast_anomalies(
        st.session_state.monthly_df, 
        st.session_state.scenarios
    )
    
    # Quality Score Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        quality_score = quality_results['overall_score']
        st.metric("📊 Data Quality Score", f"{quality_score}/100")
    
    with col2:
        avg_confidence = np.mean([m['overall_score'] for m in confidence_metrics.values()])
        st.metric("🎯 Avg Confidence", f"{avg_confidence:.1f}/100")
    
    with col3:
        st.metric("📊 Historical Periods", quality_results['historical_columns'])
    
    with col4:
        st.metric("🔮 Future Periods", quality_results['future_columns'])
    
    # Issues and Warnings
    if quality_results['issues'] or quality_results['warnings']:
        st.markdown("### 🔍 Data Quality Issues")
        
        if quality_results['issues']:
            st.error("**Critical Issues:**")
            for issue in quality_results['issues']:
                st.write(f"• {issue}")
        
        if quality_results['warnings']:
            st.warning("**Warnings:**")
            for warning in quality_results['warnings']:
                st.write(f"• {warning}")
    
    # Confidence Analysis
    st.markdown("### 🎯 Forecast Confidence Analysis")
    
    confidence_data = []
    for scenario, metrics in confidence_metrics.items():
        confidence_data.append({
            'Scenario': scenario,
            'Confidence Score': metrics['overall_score'],
            'Grade': metrics['grade'],
            'Data Coverage': f"{metrics['factors']['data_coverage']:.1f}%",
            'Consistency': f"{metrics['factors']['data_consistency']:.1f}%"
        })
    
    confidence_df = pd.DataFrame(confidence_data)
    st.dataframe(confidence_df, use_container_width=True)
    
    # Anomaly Detection
    if anomalies:
        st.markdown("### 🚨 Detected Anomalies")
        
        anomaly_data = []
        for anomaly in anomalies:
            anomaly_data.append({
                'Type': anomaly['type'],
                'Scenario': anomaly['scenario'],
                'Period': anomaly['period'],
                'Severity': anomaly['severity']
            })
        
        anomaly_df = pd.DataFrame(anomaly_data)
        st.dataframe(anomaly_df, use_container_width=True)

def show_forecast_dashboard_tab():
    """Forecast Dashboard Tab with Business Dimension Filtering"""
    st.markdown("## 📊 Forecast Dashboard & Analytics")
    
    projects_df = st.session_state.projects_df
    monthly_df = st.session_state.monthly_df
    scenarios = st.session_state.scenarios
    
    # Business Dimension Filters
    st.markdown("### 🔍 Business Dimension Filters")
    
    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
    
    with filter_col1:
        offerings = ["All"] + sorted(projects_df['offering'].unique().tolist())
        selected_offering = create_autocomplete_selectbox("🎯 Filter by Offering", offerings, "filter_offering")
    
    with filter_col2:
        products = ["All"] + sorted(projects_df['product_name'].unique().tolist())
        selected_product = create_autocomplete_selectbox("📦 Filter by Product", products, "filter_product")
    
    with filter_col3:
        industries = ["All"] + sorted(projects_df['industry'].unique().tolist())
        selected_industry = create_autocomplete_selectbox("🏭 Filter by Industry", industries, "filter_industry")
    
    with filter_col4:
        sales_orgs = ["All"] + sorted(projects_df['sales_org'].unique().tolist())
        selected_sales_org = create_autocomplete_selectbox("👥 Filter by Sales Org", sales_orgs, "filter_sales_org")
    
    # Apply filters
    filtered_projects = projects_df.copy()
    
    if selected_offering != "All":
        filtered_projects = filtered_projects[filtered_projects['offering'] == selected_offering]
    if selected_product != "All":
        filtered_projects = filtered_projects[filtered_projects['product_name'] == selected_product]
    if selected_industry != "All":
        filtered_projects = filtered_projects[filtered_projects['industry'] == selected_industry]
    if selected_sales_org != "All":
        filtered_projects = filtered_projects[filtered_projects['sales_org'] == selected_sales_org]
    
    # Filter monthly data based on project selection
    filtered_project_ids = filtered_projects['project_id'].tolist()
    filtered_monthly = monthly_df[monthly_df['project_id'].isin(filtered_project_ids)]
    
    # Key Metrics (Filtered)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Filtered Projects", len(filtered_projects))
    
    with col2:
        st.metric("📅 Time Periods", filtered_monthly['period'].nunique() if not filtered_monthly.empty else 0)
    
    with col3:
        historical_revenue = filtered_monthly[filtered_monthly['is_historical']]['revenue'].sum() if not filtered_monthly.empty else 0
        st.metric("📊 Historical Revenue", f"${historical_revenue:,.0f}")
    
    with col4:
        future_revenue = filtered_monthly[filtered_monthly['is_future']]['revenue'].sum() if not filtered_monthly.empty else 0
        st.metric("🔮 Planned Revenue", f"${future_revenue:,.0f}")
    
    # Business Dimension Summaries
    if not filtered_projects.empty:
        st.markdown("### 📊 Business Dimension Summaries")
        
        summary_tab1, summary_tab2, summary_tab3, summary_tab4 = st.tabs(["🎯 By Offering", "📦 By Product", "🏭 By Industry", "👥 By Sales Org"])
        
        with summary_tab1:
            offering_summary = create_dimension_summary(filtered_projects, filtered_monthly, 'offering', scenarios)
            st.dataframe(offering_summary, use_container_width=True)
        
        with summary_tab2:
            product_summary = create_dimension_summary(filtered_projects, filtered_monthly, 'product_name', scenarios)
            st.dataframe(product_summary, use_container_width=True)
        
        with summary_tab3:
            industry_summary = create_dimension_summary(filtered_projects, filtered_monthly, 'industry', scenarios)
            st.dataframe(industry_summary, use_container_width=True)
        
        with summary_tab4:
            sales_org_summary = create_dimension_summary(filtered_projects, filtered_monthly, 'sales_org', scenarios)
            st.dataframe(sales_org_summary, use_container_width=True)
    
    # Scenario Analysis (Filtered)
    if not filtered_monthly.empty:
        st.markdown("### 🎯 Scenario Analysis (Filtered Data)")
        
        # Calculate filtered scenarios
        filtered_scenarios = {}
        base_revenue = filtered_monthly['revenue'].sum()
        
        for scenario_name, scenario in scenarios.items():
            filtered_scenarios[scenario_name] = {
                'multiplier': scenario['multiplier'],
                'total_revenue': base_revenue * scenario['multiplier']
            }
        
        scenario_cols = st.columns(len(filtered_scenarios))
        for i, (name, data) in enumerate(filtered_scenarios.items()):
            with scenario_cols[i]:
                st.markdown(f"**{name}**")
                st.markdown(f"*{data['multiplier']:.0%} multiplier*")
                st.metric("Filtered Revenue", f"${data['total_revenue']:,.0f}")
    
    # Visualizations
    if not filtered_monthly.empty:
        st.markdown("### 📈 Revenue Trends (Filtered)")
        
        # Create filtered trend chart
        filtered_chart_data = []
        base_monthly_totals = filtered_monthly.groupby(['year', 'month'])['revenue'].sum().reset_index()
        base_monthly_totals['period'] = base_monthly_totals['year'].astype(str) + '-' + base_monthly_totals['month'].astype(str).str.zfill(2)
        
        for scenario_name, scenario in scenarios.items():
            for _, row in base_monthly_totals.iterrows():
                filtered_chart_data.append({
                    'Scenario': scenario_name,
                    'Period': row['period'],
                    'Revenue': row['revenue'] * scenario['multiplier']
                })
        
        filtered_chart_df = pd.DataFrame(filtered_chart_data)
        
        if not filtered_chart_df.empty:
            fig = px.line(
                filtered_chart_df, 
                x='Period', 
                y='Revenue', 
                color='Scenario',
                title='Filtered Revenue Forecast Trends by Scenario'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
    
    # Data Tables
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📋 Filtered Projects Overview")
        if not filtered_projects.empty:
            st.dataframe(filtered_projects, use_container_width=True)
        else:
            st.info("No projects match the selected filters")
    
    with col2:
        st.markdown("### 📊 Filtered Monthly Data Sample")
        if not filtered_monthly.empty:
            st.dataframe(filtered_monthly.head(10), use_container_width=True)
        else:
            st.info("No monthly data for selected filters")

def create_dimension_summary(projects_df, monthly_df, dimension_col, scenarios):
    """Create summary by business dimension"""
    
    summary_data = []
    
    for dimension_value in projects_df[dimension_col].unique():
        # Filter projects for this dimension value
        dim_projects = projects_df[projects_df[dimension_col] == dimension_value]
        dim_project_ids = dim_projects['project_id'].tolist()
        dim_monthly = monthly_df[monthly_df['project_id'].isin(dim_project_ids)]
        
        if not dim_monthly.empty:
            base_revenue = dim_monthly['revenue'].sum()
            historical_revenue = dim_monthly[dim_monthly['is_historical']]['revenue'].sum()
            future_revenue = dim_monthly[dim_monthly['is_future']]['revenue'].sum()
            
            summary_row = {
                dimension_col.replace('_', ' ').title(): dimension_value,
                'Projects': len(dim_projects),
                'Total Value': dim_projects['total_value'].sum(),
                'Historical Revenue': historical_revenue,
                'Future Revenue': future_revenue,
                'Conservative Forecast': base_revenue * 0.85,
                'Most Likely Forecast': base_revenue * 1.00,
                'Optimistic Forecast': base_revenue * 1.15
            }
            
            summary_data.append(summary_row)
    
    summary_df = pd.DataFrame(summary_data)
    
    # Format currency columns
    currency_cols = ['Total Value', 'Historical Revenue', 'Future Revenue', 
                    'Conservative Forecast', 'Most Likely Forecast', 'Optimistic Forecast']
    
    for col in currency_cols:
        if col in summary_df.columns:
            summary_df[col] = summary_df[col].apply(lambda x: f"${x:,.0f}")
    
    return summary_df

def show_export_tab():
    """Export and Reports Tab with Business Dimension Summaries"""
    st.markdown("## 💾 Export & Reports")
    
    scenarios = st.session_state.scenarios
    projects_df = st.session_state.projects_df
    monthly_df = st.session_state.monthly_df
    
    # Export Options
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Enhanced Excel Export")
        
        if st.button("📊 Generate Comprehensive Excel Report", type="primary"):
            # Create comprehensive Excel export
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # Scenario Summary sheet
                summary_data = []
                for name, data in scenarios.items():
                    summary_data.append({
                        'Scenario': name,
                        'Multiplier': data['multiplier'],
                        'Total Revenue': data['total_revenue']
                    })
                
                summary_df = pd.DataFrame(summary_data)
                summary_df.to_excel(writer, sheet_name='Scenario Summary', index=False)
                
                # Projects sheet with business dimensions
                projects_df.to_excel(writer, sheet_name='Projects', index=False)
                
                # Monthly data sheet
                monthly_df.to_excel(writer, sheet_name='Monthly Data', index=False)
                
                # Business dimension summaries
                offering_summary = create_dimension_summary(projects_df, monthly_df, 'offering', scenarios)
                offering_summary.to_excel(writer, sheet_name='By Offering', index=False)
                
                product_summary = create_dimension_summary(projects_df, monthly_df, 'product_name', scenarios)
                product_summary.to_excel(writer, sheet_name='By Product', index=False)
                
                industry_summary = create_dimension_summary(projects_df, monthly_df, 'industry', scenarios)
                industry_summary.to_excel(writer, sheet_name='By Industry', index=False)
                
                sales_org_summary = create_dimension_summary(projects_df, monthly_df, 'sales_org', scenarios)
                sales_org_summary.to_excel(writer, sheet_name='By Sales Org', index=False)
                
                # Executive summary sheet
                exec_summary = create_executive_summary(projects_df, monthly_df, scenarios)
                exec_summary.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            output.seek(0)
            
            st.download_button(
                label="⬇️ Download Comprehensive Excel Report",
                data=output,
                file_name=f"comprehensive_forecast_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    
    with col2:
        st.markdown("### 📋 Executive Summary Report")
        
        total_revenue = monthly_df['revenue'].sum()
        historical_revenue = monthly_df[monthly_df['is_historical']]['revenue'].sum()
        future_revenue = monthly_df[monthly_df['is_future']]['revenue'].sum()
        
        # Business dimension insights
        top_offering = projects_df.groupby('offering')['total_value'].sum().idxmax() if 'offering' in projects_df.columns else "N/A"
        top_industry = projects_df.groupby('industry')['total_value'].sum().idxmax() if 'industry' in projects_df.columns else "N/A"
        top_sales_org = projects_df.groupby('sales_org')['total_value'].sum().idxmax() if 'sales_org' in projects_df.columns else "N/A"
        
        summary_text = f"""
**Executive Forecast Summary Report**
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

**Portfolio Overview:**
- Total Projects: {len(projects_df)}
- Time Periods: {monthly_df['period'].nunique()}
- Historical Revenue: ${historical_revenue:,.0f}
- Planned Future Revenue: ${future_revenue:,.0f}

**Business Dimensions:**
- Top Offering: {top_offering}
- Top Industry: {top_industry}
- Top Sales Org: {top_sales_org}
- Unique Offerings: {projects_df['offering'].nunique()}
- Unique Industries: {projects_df['industry'].nunique()}
- Unique Sales Orgs: {projects_df['sales_org'].nunique()}

**Scenario Forecasts:**
- Conservative (85%): ${total_revenue * 0.85:,.0f}
- Most Likely (100%): ${total_revenue:,.0f}
- Optimistic (115%): ${total_revenue * 1.15:,.0f}

**Risk Analysis:**
- Downside Risk: ${total_revenue * 0.15:,.0f}
- Upside Potential: ${total_revenue * 0.15:,.0f}
- Risk/Reward Ratio: 1.0

**Key Insights:**
- Portfolio spans {projects_df['industry'].nunique()} industries
- {projects_df['offering'].nunique()} different offerings in pipeline
- {len(projects_df[projects_df['status'] == 'Active'])} active projects
        """
        
        st.code(summary_text)
        
        if st.button("📋 Copy Executive Summary"):
            st.success("Executive summary copied to clipboard!")
    
    # Business Dimension Export Options
    st.markdown("### 🏷️ Business Dimension Reports")
    
    export_col1, export_col2, export_col3, export_col4 = st.columns(4)
    
    with export_col1:
        if st.button("🎯 Export Offering Summary"):
            offering_summary = create_dimension_summary(projects_df, monthly_df, 'offering', scenarios)
            csv = offering_summary.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Offering CSV",
                data=csv,
                file_name=f"offering_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with export_col2:
        if st.button("📦 Export Product Summary"):
            product_summary = create_dimension_summary(projects_df, monthly_df, 'product_name', scenarios)
            csv = product_summary.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Product CSV",
                data=csv,
                file_name=f"product_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with export_col3:
        if st.button("🏭 Export Industry Summary"):
            industry_summary = create_dimension_summary(projects_df, monthly_df, 'industry', scenarios)
            csv = industry_summary.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Industry CSV",
                data=csv,
                file_name=f"industry_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with export_col4:
        if st.button("👥 Export Sales Org Summary"):
            sales_org_summary = create_dimension_summary(projects_df, monthly_df, 'sales_org', scenarios)
            csv = sales_org_summary.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Sales Org CSV",
                data=csv,
                file_name=f"sales_org_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

def create_executive_summary(projects_df, monthly_df, scenarios):
    """Create executive summary for Excel export"""
    
    total_revenue = monthly_df['revenue'].sum()
    historical_revenue = monthly_df[monthly_df['is_historical']]['revenue'].sum()
    future_revenue = monthly_df[monthly_df['is_future']]['revenue'].sum()
    
    summary_data = [
        {'Metric': 'Total Projects', 'Value': len(projects_df)},
        {'Metric': 'Time Periods', 'Value': monthly_df['period'].nunique()},
        {'Metric': 'Historical Revenue', 'Value': f"${historical_revenue:,.0f}"},
        {'Metric': 'Future Revenue', 'Value': f"${future_revenue:,.0f}"},
        {'Metric': 'Conservative Forecast', 'Value': f"${total_revenue * 0.85:,.0f}"},
        {'Metric': 'Most Likely Forecast', 'Value': f"${total_revenue:,.0f}"},
        {'Metric': 'Optimistic Forecast', 'Value': f"${total_revenue * 1.15:,.0f}"},
        {'Metric': 'Unique Offerings', 'Value': projects_df['offering'].nunique()},
        {'Metric': 'Unique Industries', 'Value': projects_df['industry'].nunique()},
        {'Metric': 'Unique Sales Orgs', 'Value': projects_df['sales_org'].nunique()},
    ]
    
    return pd.DataFrame(summary_data)

if __name__ == "__main__":
    main()
