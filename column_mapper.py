"""
Column Mapper - Visual interface for mapping uploaded data columns
"""

import streamlit as st
import pandas as pd
import json

class ColumnMapper:
    """Visual column mapping interface with auto-detection and validation"""
    
    def __init__(self):
        # Define target fields and their common variations
        self.target_fields = {
            'account_name': {
                'label': '🏢 Account Name',
                'keywords': ['account name', 'accountname', 'account_name', 'account', 'customer name', 'customer', 'client name', 'client', 'company name', 'company'],
                'exact_matches': ['Account Name', 'account name', 'Account_Name', 'account_name', 'ACCOUNT NAME'],
                'required': False
            },
            'opportunity_id': {
                'label': '🔑 Opportunity ID',
                'keywords': ['opportunity id', 'opportunityid', 'opportunity_id', 'opp id', 'oppid', 'opp_id', 'deal id', 'dealid', 'deal_id', 'opportunity number', 'opp number'],
                'exact_matches': ['Opportunity ID', 'opportunity id', 'Opportunity_ID', 'opportunity_id', 'OPPORTUNITY ID', 'Opp ID', 'OppID'],
                'required': False
            },
            'opportunity_name': {
                'label': '📋 Opportunity Name',
                'keywords': ['opportunity name', 'opportunityname', 'opportunity_name', 'opp name', 'oppname', 'opp_name', 'deal name', 'dealname', 'deal_name', 'opportunity'],
                'exact_matches': ['Opportunity Name', 'opportunity name', 'Opportunity_Name', 'opportunity_name', 'OPPORTUNITY NAME', 'Opp Name'],
                'required': False
            },
            'master_period': {
                'label': '📅 Master Period',
                'keywords': ['master period', 'masterperiod', 'master_period', 'period', 'fiscal period', 'fiscalperiod', 'fiscal_period', 'reporting period', 'quarter', 'fiscal quarter'],
                'exact_matches': ['Master Period', 'master period', 'Master_Period', 'master_period', 'MASTER PERIOD', 'Period', 'Fiscal Period'],
                'required': True
            },
            'close_date': {
                'label': '📆 Close Date',
                'keywords': ['close date', 'closedate', 'close_date', 'closing date', 'closingdate', 'closing_date', 'expected close', 'expected close date', 'date'],
                'exact_matches': ['Close Date', 'close date', 'Close_Date', 'close_date', 'CLOSE DATE', 'Closing Date', 'Expected Close Date'],
                'required': False
            },
            'industry_vertical': {
                'label': '🏭 Industry Vertical',
                'keywords': ['industry vertical', 'industryvertical', 'industry_vertical', 'industry', 'vertical', 'sector', 'industry segment', 'business segment'],
                'exact_matches': ['Industry Vertical', 'industry vertical', 'Industry_Vertical', 'industry_vertical', 'INDUSTRY VERTICAL', 'Industry', 'Vertical'],
                'required': False
            },
            'product_name': {
                'label': '📦 Product Name',
                'keywords': ['product name', 'productname', 'product_name', 'product', 'solution name', 'solution', 'service name', 'service'],
                'exact_matches': ['Product Name', 'product name', 'Product_Name', 'product_name', 'PRODUCT NAME', 'Product'],
                'required': False
            },
            'revenue_tcv_usd': {
                'label': '💰 Revenue TCV USD',
                'keywords': ['revenue tcv usd', 'revenuetcvusd', 'revenue_tcv_usd', 'tcv usd', 'tcvusd', 'tcv_usd', 'tcv', 'total contract value', 'revenue', 'contract value'],
                'exact_matches': ['Revenue TCV USD', 'revenue tcv usd', 'Revenue_TCV_USD', 'revenue_tcv_usd', 'REVENUE TCV USD', 'TCV USD', 'tcv usd', 'Tcv Usd', 'TCV', 'tcv', 'Revenue TCV'],
                'required': True
            },
            'iyr_usd': {
                'label': '💵 IYR USD',
                'keywords': ['iyr usd', 'iyrusd', 'iyr_usd', 'iyr', 'in year revenue', 'inyearrevenue', 'in_year_revenue', 'first year revenue', 'year 1 revenue'],
                'exact_matches': ['IYR USD', 'iyr usd', 'IYR_USD', 'iyr_usd', 'IYR', 'In Year Revenue', 'First Year Revenue'],
                'required': False
            },
            'margin_usd': {
                'label': '📊 Margin USD',
                'keywords': ['margin usd', 'marginusd', 'margin_usd', 'margin', 'gross margin', 'grossmargin', 'gross_margin', 'profit', 'gm'],
                'exact_matches': ['Margin USD', 'margin usd', 'Margin_USD', 'margin_usd', 'MARGIN USD', 'Margin', 'Gross Margin'],
                'required': False
            },
            'sales_stage': {
                'label': '🎯 Sales Stage',
                'keywords': ['sales stage', 'salesstage', 'sales_stage', 'stage', 'opportunity stage', 'opportunitystage', 'opportunity_stage', 'deal stage', 'dealstage', 'deal_stage', 'pipeline stage', 'status'],
                'exact_matches': ['Sales Stage', 'sales stage', 'Sales_Stage', 'sales_stage', 'SALES STAGE', 'Stage', 'Opportunity Stage', 'Deal Stage', 'Pipeline Stage'],
                'required': False
            }
        }
    
    def auto_detect_mapping(self, df):
        """
        Auto-detect column mappings with confidence scores
        Prioritizes exact matches, then close matches
        
        Returns:
            mapping: dict of {source_column: target_field}
            confidence: dict of {source_column: confidence_score}
        """
        
        mapping = {}
        confidence = {}
        used_targets = set()  # Track which targets have been mapped
        
        for col in df.columns:
            col_lower = col.lower().strip()
            col_normalized = col.replace(' ', '').replace('_', '').lower()
            best_match = None
            best_score = 0
            
            for target_field, config in self.target_fields.items():
                # Skip if this target is already mapped
                if target_field in used_targets:
                    continue
                
                score = 0
                
                # Priority 1: Check for exact matches (case-insensitive)
                if 'exact_matches' in config:
                    for exact in config['exact_matches']:
                        if col == exact or col_lower == exact.lower():
                            score = 1.0
                            break
                
                # Priority 2: Check normalized exact match (no spaces/underscores)
                if score < 1.0:
                    for keyword in config['keywords']:
                        keyword_normalized = keyword.replace(' ', '').replace('_', '').lower()
                        
                        # Exact normalized match
                        if col_normalized == keyword_normalized:
                            score = max(score, 0.95)
                            break
                        # Starts with keyword (full word)
                        elif col_lower.startswith(keyword.lower() + ' ') or col_lower.startswith(keyword.lower() + '_'):
                            score = max(score, 0.9)
                        # Ends with keyword (full word)
                        elif col_lower.endswith(' ' + keyword.lower()) or col_lower.endswith('_' + keyword.lower()):
                            score = max(score, 0.85)
                        # Contains keyword as whole word
                        elif f' {keyword.lower()} ' in f' {col_lower} ' or f'_{keyword.lower()}_' in f'_{col_lower}_':
                            score = max(score, 0.8)
                        # Contains keyword (partial)
                        elif keyword.lower() in col_lower:
                            score = max(score, 0.7)
                
                if score > best_score:
                    best_score = score
                    best_match = target_field
            
            # Only map if confidence is high enough
            if best_match and best_score >= 0.7:
                mapping[col] = best_match
                confidence[col] = best_score
                used_targets.add(best_match)  # Mark this target as used
        
        return mapping, confidence
    
    def validate_mapping(self, mapping):
        """
        Validate that required fields are mapped
        
        Returns:
            is_valid: bool
            missing_fields: list of missing required fields
        """
        mapped_targets = set(mapping.values())
        required_fields = [
            field for field, config in self.target_fields.items() 
            if config['required']
        ]
        
        missing_fields = [
            self.target_fields[field]['label'] 
            for field in required_fields 
            if field not in mapped_targets
        ]
        
        return len(missing_fields) == 0, missing_fields
    
    def save_mapping_template(self, mapping, template_name):
        """Save mapping template to session state"""
        if 'mapping_templates' not in st.session_state:
            st.session_state.mapping_templates = {}
        
        st.session_state.mapping_templates[template_name] = mapping
    
    def load_mapping_template(self, template_name):
        """Load mapping template from session state"""
        if 'mapping_templates' in st.session_state:
            return st.session_state.mapping_templates.get(template_name)
        return None
    
    def render_mapping_interface(self, df):
        """
        Render the visual column mapping interface - 10 target fields with dropdown to select source
        
        Returns:
            validated: bool - True if user clicked validate and mapping is valid
        """
        
        st.markdown("### 🔗 Column Mapping")
        st.markdown("Map your source columns to the 11 target fields. Auto-suggestions have been applied.")
        
        # Auto-detect if not already done
        if 'column_mapping' not in st.session_state:
            auto_mapping, confidence = self.auto_detect_mapping(df)
            st.session_state.column_mapping = auto_mapping
            st.session_state.mapping_confidence = confidence
        
        # Reverse mapping: target → source
        if 'reverse_mapping' not in st.session_state:
            # Create reverse mapping from column_mapping
            reverse_map = {}
            for src, tgt in st.session_state.column_mapping.items():
                reverse_map[tgt] = src
            st.session_state.reverse_mapping = reverse_map
        
        # Create mapping interface
        st.markdown("---")
        
        # Header row
        header_cols = st.columns([3, 1, 3, 1])
        with header_cols[0]:
            st.markdown("**Target Field**")
        with header_cols[2]:
            st.markdown("**Source Column**")
        with header_cols[3]:
            st.markdown("**Confidence**")
        
        # Source column options (add "None" option)
        source_options = ["(None)"] + list(df.columns)
        
        # Mapping rows - one row per target field
        for target_key, config in self.target_fields.items():
            cols = st.columns([3, 1, 3, 1])
            
            with cols[0]:
                # Show target field with required indicator
                label = config['label']
                if config['required']:
                    st.markdown(f"**{label}** ⭐")
                    st.caption("Required")
                else:
                    st.markdown(f"{label}")
                    st.caption("Optional")
            
            with cols[1]:
                st.markdown("←")
            
            with cols[2]:
                # Dropdown to select source column
                current_source = st.session_state.reverse_mapping.get(target_key, "(None)")
                
                # Find index
                if current_source in source_options:
                    default_idx = source_options.index(current_source)
                else:
                    default_idx = 0
                
                selected_source = st.selectbox(
                    f"source_{target_key}",
                    source_options,
                    index=default_idx,
                    key=f"mapping_{target_key}",
                    label_visibility="collapsed"
                )
                
                # Update reverse mapping
                if selected_source != "(None)":
                    st.session_state.reverse_mapping[target_key] = selected_source
                elif target_key in st.session_state.reverse_mapping:
                    del st.session_state.reverse_mapping[target_key]
            
            with cols[3]:
                # Show confidence indicator for current mapping
                if selected_source != "(None)":
                    # Check if this was auto-detected
                    conf = 0
                    if target_key in st.session_state.column_mapping.values():
                        for src, tgt in st.session_state.column_mapping.items():
                            if tgt == target_key and src == selected_source:
                                conf = st.session_state.mapping_confidence.get(src, 0)
                                break
                    
                    if conf >= 0.9:
                        st.success("✓ High")
                    elif conf >= 0.7:
                        st.warning("~ Medium")
                    elif conf > 0:
                        st.info("? Low")
                    else:
                        st.info("Manual")
                else:
                    st.markdown("-")
        
        # Update column_mapping from reverse_mapping
        st.session_state.column_mapping = {
            src: tgt for tgt, src in st.session_state.reverse_mapping.items()
        }
        
        # Preview mapped data
        st.markdown("---")
        st.markdown("**📋 Preview (First 5 rows):**")
        
        # Show only mapped columns
        mapped_cols = list(st.session_state.column_mapping.keys())
        if mapped_cols:
            preview_df = df[mapped_cols].head(5)
            # Rename columns to show target fields
            rename_dict = {
                col: f"{col} → {self.target_fields[st.session_state.column_mapping[col]]['label']}"
                for col in mapped_cols
            }
            preview_df = preview_df.rename(columns=rename_dict)
            st.dataframe(preview_df, use_container_width=True)
        else:
            st.info("No columns mapped yet. Please map at least the required fields.")
        
        # Validation and continue
        st.markdown("---")
        
        # Check if mapping is valid
        is_valid, missing_fields = self.validate_mapping(st.session_state.column_mapping)
        
        if not is_valid:
            st.error(f"⚠️ Missing required fields: {', '.join(missing_fields)}")
            st.info("The system could not auto-detect all required fields. Please ensure your data contains: Master Period and Revenue TCV USD columns.")
        else:
            st.success("✅ All required fields detected!")
        
        # Validate button
        if st.button("✓ Validate & Continue", type="primary", disabled=not is_valid, use_container_width=True):
            st.session_state.mapping_validated = True
            return True
        
        return False
    
    def get_mapped_dataframe(self, df):
        """
        Return dataframe with columns renamed to target fields
        
        Returns:
            mapped_df: DataFrame with renamed columns
            mapping_info: dict with mapping details
        """
        if 'column_mapping' not in st.session_state:
            return None, None
        
        mapping = st.session_state.column_mapping
        
        # Create rename dictionary
        rename_dict = {
            source: target 
            for source, target in mapping.items()
        }
        
        # IMPORTANT: Keep ALL columns, not just mapped ones
        # This preserves forecast columns (FY26 Q1, FY26 Q2, etc.)
        mapped_df = df.copy()
        
        # Rename only the mapped columns
        mapped_df = mapped_df.rename(columns=rename_dict)
        
        # Mapping info
        mapping_info = {
            'source_columns': list(rename_dict.keys()),
            'target_fields': list(rename_dict.values()),
            'total_columns': len(df.columns),
            'mapped_columns': len(rename_dict),
            'unmapped_columns': len(df.columns) - len(rename_dict)
        }
        
        return mapped_df, mapping_info
