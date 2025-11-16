"""
Export Utilities - Generate reports and exports from financial data
Supports PDF, Excel, and CSV export formats
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
import base64
from typing import Dict, Any, Tuple

class ExportUtilities:
    """Utilities for exporting financial reports and data"""

    def __init__(self):
        self.formats = {
            'pdf': self._export_pdf,
            'excel': self._export_excel,
            'csv': self._export_csv
        }

    def render_export_panel(self, data_dict: Dict[str, Any], scenario_name: str = "Base Case"):
        """
        Render export panel with format options

        Args:
            data_dict: Dictionary containing data to export (forecasts, metrics, etc.)
            scenario_name: Name of the current scenario
        """

        st.markdown("### 📤 Export Reports")
        st.markdown("Download your financial analysis in various formats")

        # Export format selection
        export_format = st.selectbox(
            "Select export format:",
            options=["PDF Report", "Excel Workbook", "CSV Data"],
            key="export_format"
        )

        # Export options
        with st.expander("⚙️ Export Options", expanded=False):
            include_charts = st.checkbox("Include charts in PDF", value=True)
            include_summary = st.checkbox("Include executive summary", value=True)
            include_raw_data = st.checkbox("Include raw data tables", value=True)

        # Generate and download button
        if st.button("🚀 Generate & Download", type="primary", use_container_width=True):
            try:
                with st.spinner("Generating export..."):
                    if export_format == "PDF Report":
                        file_data, filename = self._export_pdf(data_dict, scenario_name, include_charts, include_summary)
                        mime_type = "application/pdf"
                        file_label = "PDF Report"

                    elif export_format == "Excel Workbook":
                        file_data, filename = self._export_excel(data_dict, scenario_name, include_raw_data)
                        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        file_label = "Excel Workbook"

                    else:  # CSV Data
                        file_data, filename = self._export_csv(data_dict, scenario_name)
                        mime_type = "text/csv"
                        file_label = "CSV Data"

                # Create download link
                b64 = base64.b64encode(file_data).decode()
                href = f'data:{mime_type};base64,{b64}'

                st.success(f"✅ {file_label} generated successfully!")
                st.markdown(
                    f'<a href="{href}" download="{filename}" style="display: inline-block; padding: 12px 20px; background-color: #4CAF50; color: white; text-decoration: none; border-radius: 4px; margin: 10px 0;">📥 Download {file_label}</a>',
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")

    def _export_pdf(self, data_dict: Dict[str, Any], scenario_name: str,
                   include_charts: bool = True, include_summary: bool = True) -> Tuple[bytes, str]:
        """
        Generate PDF report

        Note: This is a simplified implementation. In production, you'd use libraries like
        reportlab, fpdf, or weasyprint for proper PDF generation.
        """

        # Create a simple text-based "PDF" for demonstration
        # In a real implementation, you'd use proper PDF libraries

        pdf_content = []
        pdf_content.append(f"Financial Forecasting Report - {scenario_name}")
        pdf_content.append("=" * 50)
        pdf_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        pdf_content.append("")

        if include_summary and 'summary' in data_dict:
            pdf_content.append("EXECUTIVE SUMMARY")
            pdf_content.append("-" * 20)
            for item in data_dict['summary']:
                pdf_content.append(f"• {item}")
            pdf_content.append("")

        if 'forecast_data' in data_dict:
            pdf_content.append("FORECAST DATA")
            pdf_content.append("-" * 15)
            forecast_df = data_dict['forecast_data']
            # Convert to simple text representation
            pdf_content.append(forecast_df.to_string())
            pdf_content.append("")

        if 'metrics' in data_dict:
            pdf_content.append("KEY METRICS")
            pdf_content.append("-" * 12)
            for key, value in data_dict['metrics'].items():
                pdf_content.append(f"{key}: {value}")
            pdf_content.append("")

        # Join all content
        full_content = "\n".join(pdf_content)

        # Convert to bytes (simplified - in reality you'd create proper PDF)
        pdf_bytes = full_content.encode('utf-8')

        filename = f"financial_report_{scenario_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        return pdf_bytes, filename

    def _export_excel(self, data_dict: Dict[str, Any], scenario_name: str,
                     include_raw_data: bool = True) -> Tuple[bytes, str]:
        """
        Generate Excel workbook with multiple sheets
        """

        # Create Excel file in memory
        output = BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook = writer.book

            # Summary sheet
            if 'summary' in data_dict:
                summary_df = pd.DataFrame({'Summary Points': data_dict['summary']})
                summary_df.to_excel(writer, sheet_name='Summary', index=False)

            # Forecast data sheet
            if 'forecast_data' in data_dict:
                data_dict['forecast_data'].to_excel(writer, sheet_name='Forecast Data', index=False)

            # Metrics sheet
            if 'metrics' in data_dict:
                metrics_df = pd.DataFrame(list(data_dict['metrics'].items()),
                                        columns=['Metric', 'Value'])
                metrics_df.to_excel(writer, sheet_name='Key Metrics', index=False)

            # Raw data sheets (if requested)
            if include_raw_data and 'raw_data' in data_dict:
                for sheet_name, df in data_dict['raw_data'].items():
                    # Limit sheet name length
                    safe_sheet_name = sheet_name[:31]  # Excel limit
                    df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

        output.seek(0)
        excel_bytes = output.getvalue()

        filename = f"financial_analysis_{scenario_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        return excel_bytes, filename

    def _export_csv(self, data_dict: Dict[str, Any], scenario_name: str) -> Tuple[bytes, str]:
        """
        Generate CSV export (primary data only)
        """

        if 'forecast_data' in data_dict:
            csv_data = data_dict['forecast_data'].to_csv(index=False)
        elif 'metrics' in data_dict:
            # Convert metrics dict to DataFrame for CSV export
            metrics_df = pd.DataFrame(list(data_dict['metrics'].items()),
                                    columns=['Metric', 'Value'])
            csv_data = metrics_df.to_csv(index=False)
        else:
            # Fallback - create a simple CSV with summary
            summary_data = data_dict.get('summary', ['No data available'])
            summary_df = pd.DataFrame({'Summary': summary_data})
            csv_data = summary_df.to_csv(index=False)

        csv_bytes = csv_data.encode('utf-8')

        filename = f"financial_data_{scenario_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        return csv_bytes, filename

    def prepare_forecast_export_data(self, forecast_df: pd.DataFrame,
                                   metrics: Dict[str, Any] = None,
                                   scenario_name: str = "Base Case") -> Dict[str, Any]:
        """
        Prepare data dictionary for export from forecast results

        Args:
            forecast_df: Forecast DataFrame
            metrics: Dictionary of key metrics
            scenario_name: Scenario name

        Returns:
            Dictionary ready for export functions
        """

        export_data = {
            'forecast_data': forecast_df.copy(),
            'scenario_name': scenario_name,
            'export_timestamp': datetime.now().isoformat()
        }

        # Add summary points
        summary_points = [
            f"Scenario: {scenario_name}",
            f"Total Forecast Value: ${forecast_df.select_dtypes(include=[np.number]).sum().sum():,.0f}",
            f"Forecast Periods: {len(forecast_df.columns) if hasattr(forecast_df, 'columns') else 'N/A'}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        ]

        if metrics:
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    summary_points.append(f"{key}: {value:,.2f}")
                else:
                    summary_points.append(f"{key}: {value}")

        export_data['summary'] = summary_points
        export_data['metrics'] = metrics or {}

        return export_data

    def add_export_button(self, data_dict: Dict[str, Any], button_text: str = "📤 Export Results",
                         scenario_name: str = "Analysis"):
        """
        Add a quick export button for common use cases

        Args:
            data_dict: Data to export
            button_text: Text for the button
            scenario_name: Scenario name for filename
        """

        if st.button(button_text, help="Export analysis results"):
            try:
                # Default to Excel export for quick exports
                file_data, filename = self._export_excel(data_dict, scenario_name, include_raw_data=True)
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                # Create download link
                b64 = base64.b64encode(file_data).decode()
                href = f'data:{mime_type};base64,{b64}'

                st.success("✅ Export generated successfully!")
                st.markdown(
                    f'<a href="{href}" download="{filename}" style="display: inline-block; padding: 10px 16px; background-color: #2196F3; color: white; text-decoration: none; border-radius: 4px; margin: 8px 0;">📥 Download Excel</a>',
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"❌ Export failed: {str(e)}")
