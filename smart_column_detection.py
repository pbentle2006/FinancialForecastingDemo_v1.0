import pandas as pd
import numpy as np
import re
from datetime import datetime
import streamlit as st

class SmartColumnDetector:
    """Intelligent column detection with confidence scoring"""
    
    def __init__(self):
        self.field_patterns = {
            'id': {
                'patterns': [r'id', r'identifier', r'proj', r'project.*id', r'opportunity.*id'],
                'data_checks': ['unique_ratio', 'alphanumeric'],
                'weight': 0.9
            },
            'name': {
                'patterns': [r'name', r'title', r'project.*name', r'opportunity.*name', r'description'],
                'data_checks': ['text_length', 'unique_ratio'],
                'weight': 0.8
            },
            'client': {
                'patterns': [r'client', r'customer', r'company', r'organization', r'account'],
                'data_checks': ['text_content', 'repeated_values'],
                'weight': 0.7
            },
            'total_value': {
                'patterns': [r'value', r'amount', r'total', r'contract.*value', r'tcv', r'revenue'],
                'data_checks': ['numeric', 'currency_format', 'positive_values'],
                'weight': 0.9
            },
            'status': {
                'patterns': [r'status', r'state', r'phase', r'stage'],
                'data_checks': ['categorical', 'limited_unique'],
                'weight': 0.8
            },
            'offering': {
                'patterns': [r'offering', r'service', r'solution', r'product.*type', r'category'],
                'data_checks': ['categorical', 'repeated_values'],
                'weight': 0.7
            },
            'industry': {
                'patterns': [r'industry', r'sector', r'vertical', r'market'],
                'data_checks': ['categorical', 'repeated_values'],
                'weight': 0.7
            },
            'sales_org': {
                'patterns': [r'sales.*org', r'region', r'territory', r'geo', r'area'],
                'data_checks': ['categorical', 'repeated_values'],
                'weight': 0.6
            }
        }
        
        self.monthly_patterns = [
            r'FY\d{4}-\d{2}',  # FY2025-04
            r'\d{4}-\d{2}',    # 2025-04
            r'Q[1-4].*\d{4}',  # Q1 2025
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec).*\d{4}',  # Jan 2025
        ]
    
    def detect_columns_with_confidence(self, df):
        """Detect column mappings with confidence scores"""
        
        results = {}
        
        for field, config in self.field_patterns.items():
            candidates = self._find_field_candidates(df, field, config)
            if candidates:
                results[field] = candidates
        
        # Detect monthly columns
        monthly_candidates = self._detect_monthly_columns(df)
        if monthly_candidates:
            results['monthly_columns'] = monthly_candidates
        
        return results
    
    def _find_field_candidates(self, df, field, config):
        """Find candidates for a specific field with confidence scoring"""
        
        candidates = []
        
        for col in df.columns:
            confidence_score = self._calculate_confidence_score(df, col, field, config)
            
            if confidence_score > 0.3:  # Minimum threshold
                candidates.append({
                    'column': col,
                    'confidence': confidence_score,
                    'reasons': self._get_confidence_reasons(df, col, field, config)
                })
        
        # Sort by confidence score
        candidates.sort(key=lambda x: x['confidence'], reverse=True)
        
        return candidates[:3]  # Return top 3 candidates
    
    def _calculate_confidence_score(self, df, column, field, config):
        """Calculate confidence score for column-field mapping"""
        
        score = 0.0
        col_name = str(column).lower()
        
        # 1. Pattern matching (40% weight)
        pattern_score = 0
        for pattern in config['patterns']:
            if re.search(pattern, col_name):
                pattern_score = max(pattern_score, 0.8)
                break
        
        score += pattern_score * 0.4
        
        # 2. Data content analysis (60% weight)
        data_score = self._analyze_data_content(df[column], config['data_checks'])
        score += data_score * 0.6
        
        return min(score, 1.0)
    
    def _analyze_data_content(self, series, checks):
        """Analyze data content for field type detection"""
        
        total_score = 0
        check_count = len(checks)
        
        for check in checks:
            check_score = self._run_data_check(series, check)
            total_score += check_score
        
        return total_score / check_count if check_count > 0 else 0
    
    def _run_data_check(self, series, check_type):
        """Run specific data content check"""
        
        non_null_series = series.dropna()
        if len(non_null_series) == 0:
            return 0
        
        if check_type == 'unique_ratio':
            unique_ratio = len(non_null_series.unique()) / len(non_null_series)
            return min(unique_ratio * 2, 1.0)  # Higher unique ratio = better for ID/name fields
        
        elif check_type == 'alphanumeric':
            alphanumeric_count = sum(1 for val in non_null_series if str(val).replace('-', '').replace('_', '').isalnum())
            return alphanumeric_count / len(non_null_series)
        
        elif check_type == 'text_length':
            avg_length = non_null_series.astype(str).str.len().mean()
            return min(avg_length / 50, 1.0)  # Normalize to 50 chars
        
        elif check_type == 'text_content':
            text_count = sum(1 for val in non_null_series if isinstance(val, str) and len(val) > 2)
            return text_count / len(non_null_series)
        
        elif check_type == 'numeric':
            try:
                numeric_series = pd.to_numeric(non_null_series, errors='coerce')
                numeric_count = numeric_series.notna().sum()
                return numeric_count / len(non_null_series)
            except:
                return 0
        
        elif check_type == 'currency_format':
            currency_patterns = [r'\$', r'USD', r'EUR', r'GBP', r'[0-9,]+\.[0-9]{2}']
            currency_count = 0
            for val in non_null_series.astype(str):
                if any(re.search(pattern, val) for pattern in currency_patterns):
                    currency_count += 1
            return currency_count / len(non_null_series)
        
        elif check_type == 'positive_values':
            try:
                numeric_series = pd.to_numeric(non_null_series, errors='coerce')
                positive_count = (numeric_series > 0).sum()
                return positive_count / len(numeric_series.dropna()) if len(numeric_series.dropna()) > 0 else 0
            except:
                return 0
        
        elif check_type == 'categorical':
            unique_ratio = len(non_null_series.unique()) / len(non_null_series)
            return 1.0 - unique_ratio  # Lower unique ratio = more categorical
        
        elif check_type == 'limited_unique':
            unique_count = len(non_null_series.unique())
            return 1.0 if unique_count <= 20 else max(0, 1.0 - (unique_count - 20) / 100)
        
        elif check_type == 'repeated_values':
            value_counts = non_null_series.value_counts()
            max_frequency = value_counts.iloc[0] if len(value_counts) > 0 else 0
            return min(max_frequency / len(non_null_series), 1.0)
        
        return 0
    
    def _get_confidence_reasons(self, df, column, field, config):
        """Get human-readable reasons for confidence score"""
        
        reasons = []
        col_name = str(column).lower()
        
        # Pattern matching reasons
        for pattern in config['patterns']:
            if re.search(pattern, col_name):
                reasons.append(f"Column name matches '{pattern}' pattern")
                break
        
        # Data content reasons
        series = df[column].dropna()
        if len(series) > 0:
            
            if 'numeric' in config['data_checks']:
                try:
                    numeric_ratio = pd.to_numeric(series, errors='coerce').notna().sum() / len(series)
                    if numeric_ratio > 0.8:
                        reasons.append(f"{numeric_ratio:.0%} numeric values")
                except:
                    pass
            
            if 'unique_ratio' in config['data_checks']:
                unique_ratio = len(series.unique()) / len(series)
                if unique_ratio > 0.8:
                    reasons.append(f"{unique_ratio:.0%} unique values")
                elif unique_ratio < 0.2:
                    reasons.append(f"Low diversity ({unique_ratio:.0%} unique)")
            
            if 'categorical' in config['data_checks']:
                unique_count = len(series.unique())
                if unique_count <= 10:
                    reasons.append(f"Only {unique_count} unique values (categorical)")
        
        return reasons
    
    def _detect_monthly_columns(self, df):
        """Detect monthly/period columns with confidence scoring"""
        
        monthly_candidates = []
        
        for col in df.columns:
            col_str = str(col)
            confidence = 0
            reasons = []
            
            # Pattern matching
            for pattern in self.monthly_patterns:
                if re.search(pattern, col_str):
                    confidence += 0.6
                    reasons.append(f"Matches date pattern: {pattern}")
                    break
            
            # Data content analysis
            try:
                numeric_count = pd.to_numeric(df[col], errors='coerce').notna().sum()
                if numeric_count > 0:
                    confidence += 0.4
                    reasons.append(f"{numeric_count} numeric values")
            except:
                pass
            
            # Year detection
            current_year = datetime.now().year
            year_match = re.search(r'(202[0-9]|203[0-9])', col_str)
            if year_match:
                year = int(year_match.group(1))
                is_future = year > current_year
                reasons.append(f"Year {year} ({'future' if is_future else 'historical'})")
            
            if confidence > 0.5:
                monthly_candidates.append({
                    'column': col,
                    'confidence': confidence,
                    'reasons': reasons,
                    'is_future': year > current_year if year_match else False
                })
        
        monthly_candidates.sort(key=lambda x: x['confidence'], reverse=True)
        return monthly_candidates

def show_smart_mapping_interface(df):
    """Enhanced mapping interface with smart suggestions"""
    
    st.markdown("### 🧠 Smart Column Detection")
    
    detector = SmartColumnDetector()
    
    with st.spinner("Analyzing columns..."):
        detection_results = detector.detect_columns_with_confidence(df)
    
    if not detection_results:
        st.warning("No suitable columns detected. Please map manually.")
        return {}
    
    st.success(f"✅ Detected {len(detection_results)} field types with confidence scores")
    
    mapping = {}
    
    # Show field mappings with confidence
    for field, candidates in detection_results.items():
        if field == 'monthly_columns':
            continue
            
        st.markdown(f"#### {field.replace('_', ' ').title()}")
        
        if candidates:
            # Show top candidate with confidence
            top_candidate = candidates[0]
            
            col1, col2 = st.columns([3, 1])
            with col1:
                selected = st.selectbox(
                    f"Select column for {field}:",
                    options=['[Skip]'] + [c['column'] for c in candidates] + ['[Other...]'],
                    index=1,  # Default to top candidate
                    key=f"mapping_{field}"
                )
            
            with col2:
                if selected != '[Skip]' and selected != '[Other...]':
                    candidate = next((c for c in candidates if c['column'] == selected), None)
                    if candidate:
                        confidence_pct = int(candidate['confidence'] * 100)
                        st.metric("Confidence", f"{confidence_pct}%")
            
            # Show confidence reasons
            if selected != '[Skip]' and selected != '[Other...]':
                candidate = next((c for c in candidates if c['column'] == selected), None)
                if candidate and candidate['reasons']:
                    with st.expander("Why this suggestion?"):
                        for reason in candidate['reasons']:
                            st.write(f"• {reason}")
            
            # Handle manual selection
            if selected == '[Other...]':
                manual_selection = st.selectbox(
                    "Choose manually:",
                    options=['[Skip]'] + list(df.columns),
                    key=f"manual_{field}"
                )
                if manual_selection != '[Skip]':
                    mapping[field] = manual_selection
            elif selected != '[Skip]':
                mapping[field] = selected
    
    # Show monthly columns detection
    if 'monthly_columns' in detection_results:
        st.markdown("#### 📅 Monthly/Period Columns")
        monthly_candidates = detection_results['monthly_columns']
        
        st.info(f"Detected {len(monthly_candidates)} potential monthly columns")
        
        # Show top monthly candidates
        for i, candidate in enumerate(monthly_candidates[:5]):  # Show top 5
            col1, col2, col3 = st.columns([2, 1, 2])
            
            with col1:
                st.write(f"**{candidate['column']}**")
            
            with col2:
                confidence_pct = int(candidate['confidence'] * 100)
                st.write(f"{confidence_pct}% confidence")
            
            with col3:
                period_type = "🔮 Future" if candidate.get('is_future', False) else "📊 Historical"
                st.write(period_type)
    
    return mapping
