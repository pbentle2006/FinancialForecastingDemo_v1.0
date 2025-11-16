import streamlit as st
import pandas as pd
from datetime import datetime
import time

def show_progress_indicator(current_step, total_steps, step_names=None):
    """Enhanced progress indicator with step names and status"""
    
    if step_names is None:
        step_names = [f"Step {i+1}" for i in range(total_steps)]
    
    # Progress bar
    progress = current_step / total_steps
    st.progress(progress, text=f"Progress: {current_step}/{total_steps} steps completed")
    
    # Step indicators
    cols = st.columns(total_steps)
    for i, (col, step_name) in enumerate(zip(cols, step_names)):
        with col:
            if i < current_step:
                st.success(f"✅ {step_name}")
            elif i == current_step:
                st.info(f"🔄 {step_name}")
            else:
                st.write(f"⏳ {step_name}")

def show_status_badge(status, label="Status"):
    """Display status badges with consistent styling"""
    
    status_config = {
        'complete': {'color': 'green', 'icon': '✅', 'text': 'Complete'},
        'in_progress': {'color': 'blue', 'icon': '🔄', 'text': 'In Progress'},
        'pending': {'color': 'orange', 'icon': '⏳', 'text': 'Pending'},
        'error': {'color': 'red', 'icon': '❌', 'text': 'Error'},
        'warning': {'color': 'orange', 'icon': '⚠️', 'text': 'Warning'},
        'info': {'color': 'blue', 'icon': 'ℹ️', 'text': 'Info'}
    }
    
    config = status_config.get(status.lower(), status_config['info'])
    
    st.markdown(f"""
    <div style="
        display: inline-block;
        padding: 4px 8px;
        border-radius: 12px;
        background-color: {config['color']}20;
        border: 1px solid {config['color']}40;
        color: {config['color']};
        font-size: 12px;
        font-weight: 500;
        margin: 2px;
    ">
        {config['icon']} {config['text']}
    </div>
    """, unsafe_allow_html=True)

def show_help_tooltip(text, help_text):
    """Display text with contextual help tooltip"""
    
    st.markdown(f"""
    <div style="display: inline-block;">
        <span>{text}</span>
        <span style="
            margin-left: 5px;
            color: #666;
            cursor: help;
            font-size: 12px;
        " title="{help_text}">ℹ️</span>
    </div>
    """, unsafe_allow_html=True)

def enhanced_file_uploader(label, help_text=None, accepted_types=None):
    """Enhanced file uploader with preview and validation"""
    
    if accepted_types is None:
        accepted_types = ['csv', 'xlsx', 'xls']
    
    # File uploader with enhanced styling
    st.markdown(f"### {label}")
    if help_text:
        st.markdown(f"*{help_text}*")
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=accepted_types,
        help=f"Supported formats: {', '.join(accepted_types).upper()}"
    )
    
    if uploaded_file is not None:
        # File info display
        file_size = len(uploaded_file.getvalue())
        file_size_mb = file_size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📄 File Name", uploaded_file.name)
        with col2:
            st.metric("📊 File Size", f"{file_size_mb:.2f} MB")
        with col3:
            st.metric("📅 Upload Time", datetime.now().strftime("%H:%M:%S"))
        
        # File validation
        if file_size_mb > 50:
            st.warning("⚠️ Large file detected. Processing may take longer.")
        elif file_size_mb > 100:
            st.error("❌ File too large. Please use files under 100MB.")
            return None
        else:
            st.success("✅ File uploaded successfully!")
    
    return uploaded_file

def show_data_preview(df, max_rows=10):
    """Enhanced data preview with statistics"""
    
    if df is None or df.empty:
        st.warning("No data to preview")
        return
    
    st.markdown("### 👀 Data Preview")
    
    # Data statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📊 Rows", f"{len(df):,}")
    with col2:
        st.metric("📋 Columns", len(df.columns))
    with col3:
        st.metric("💾 Memory", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
    with col4:
        null_percentage = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        st.metric("❓ Missing Data", f"{null_percentage:.1f}%")
    
    # Data preview table
    st.markdown("**First 10 rows:**")
    preview_df = df.head(max_rows)
    st.dataframe(preview_df, use_container_width=True)
    
    # Column information
    with st.expander("📋 Column Information"):
        col_info = []
        for col in df.columns:
            col_type = str(df[col].dtype)
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            unique_count = df[col].nunique()
            
            col_info.append({
                'Column': col,
                'Type': col_type,
                'Null Count': null_count,
                'Null %': f"{null_pct:.1f}%",
                'Unique Values': unique_count
            })
        
        col_info_df = pd.DataFrame(col_info)
        st.dataframe(col_info_df, use_container_width=True)

def show_processing_status(steps_completed, total_steps, current_task="Processing..."):
    """Show processing status with animated progress"""
    
    progress_container = st.empty()
    status_container = st.empty()
    
    with progress_container.container():
        progress = steps_completed / total_steps
        st.progress(progress, text=f"{current_task} ({steps_completed}/{total_steps})")
    
    with status_container.container():
        if steps_completed == total_steps:
            st.success("✅ Processing completed successfully!")
        else:
            st.info(f"🔄 {current_task}")

def enhanced_error_display(error_type, error_message, suggestions=None):
    """Enhanced error display with actionable suggestions"""
    
    error_configs = {
        'file_error': {
            'icon': '📄',
            'title': 'File Processing Error',
            'color': 'red'
        },
        'data_error': {
            'icon': '📊',
            'title': 'Data Validation Error',
            'color': 'orange'
        },
        'calculation_error': {
            'icon': '🧮',
            'title': 'Calculation Error',
            'color': 'red'
        },
        'mapping_error': {
            'icon': '🔗',
            'title': 'Column Mapping Error',
            'color': 'orange'
        }
    }
    
    config = error_configs.get(error_type, error_configs['data_error'])
    
    st.error(f"{config['icon']} **{config['title']}**")
    st.write(f"**Error Details:** {error_message}")
    
    if suggestions:
        st.markdown("**💡 Suggested Solutions:**")
        for i, suggestion in enumerate(suggestions, 1):
            st.write(f"{i}. {suggestion}")

def auto_save_session_state(key_prefix="autosave"):
    """Auto-save session state with timestamp"""
    
    if 'last_autosave' not in st.session_state:
        st.session_state.last_autosave = datetime.now()
    
    # Auto-save every 30 seconds
    current_time = datetime.now()
    time_diff = (current_time - st.session_state.last_autosave).seconds
    
    if time_diff > 30:  # 30 seconds
        # Save current session state
        save_data = {}
        for key, value in st.session_state.items():
            if not key.startswith('_') and key != 'last_autosave':
                try:
                    # Only save serializable data
                    if isinstance(value, (str, int, float, bool, list, dict)):
                        save_data[key] = value
                    elif hasattr(value, 'to_dict'):  # DataFrames
                        save_data[f"{key}_df"] = value.to_dict()
                except:
                    continue
        
        st.session_state[f"{key_prefix}_backup"] = save_data
        st.session_state.last_autosave = current_time
        
        # Show auto-save indicator
        st.sidebar.success("💾 Auto-saved")

def show_workflow_sidebar():
    """Enhanced sidebar with workflow status"""
    
    st.sidebar.markdown("## 🎯 Workflow Status")
    
    # Workflow steps
    workflow_steps = [
        ("Upload Data", "data_uploaded"),
        ("Map Columns", "columns_mapped"), 
        ("Process Data", "data_processed"),
        ("Run Analysis", "analysis_complete"),
        ("Generate Reports", "reports_ready")
    ]
    
    for step_name, session_key in workflow_steps:
        if hasattr(st.session_state, session_key) and getattr(st.session_state, session_key):
            show_status_badge('complete')
            st.sidebar.write(f"✅ {step_name}")
        else:
            show_status_badge('pending')
            st.sidebar.write(f"⏳ {step_name}")
    
    st.sidebar.markdown("---")
    
    # Quick actions
    st.sidebar.markdown("## ⚡ Quick Actions")
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    if st.sidebar.button("💾 Save Progress"):
        auto_save_session_state()
        st.sidebar.success("Progress saved!")
    
    if st.sidebar.button("🗑️ Clear All Data"):
        for key in list(st.session_state.keys()):
            if not key.startswith('_'):
                del st.session_state[key]
        st.sidebar.success("Data cleared!")
        st.rerun()
