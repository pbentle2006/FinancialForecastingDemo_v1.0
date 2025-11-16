# 📊 Financial Forecast Dashboard - Complete Guide

## Overview
A comprehensive financial forecasting and analysis dashboard built with Streamlit, featuring AI-powered insights, multi-view comparisons, and advanced analytics.

---

## 🚀 Quick Start

### Running the Dashboard
```bash
streamlit run app_complete_dashboard.py --server.port 8507
```

Access at: **http://localhost:8507**

---

## 📅 Fiscal Year Calendar

**Important:** This dashboard uses an **April-March fiscal year**:

| Quarter | Months | Period |
|---------|--------|--------|
| **Q1** | April - June | Start of FY |
| **Q2** | July - September | Mid-year |
| **Q3** | October - December | Year-end calendar |
| **Q4** | January - March | End of FY |
| **FY** | April - March | Full fiscal year |

---

## ✨ Key Features

### 1. **Sample Data Demo**
- Click **"Load Sample Data"** for instant demo
- Pre-loaded FY2026 financial data
- 4-column view: Forecast | vs Prior | Budget | Variance

### 2. **File Upload**
- Supports CSV and Excel files
- Auto-detects quarterly columns (Q1, Q2, Q3, Q4, FY)
- Smart dashboard formatting

### 3. **Multi-View Comparison**
- **Current Forecast**: Latest revenue projections
- **vs Prior Forecast (CFvPF)**: Changes from previous forecast
- **Budget**: Planned financial targets
- **Variance (CFvWB)**: Current Forecast vs Working Budget

### 4. **Key Metrics Dashboard**
- FY Revenue
- Contract Margin ($M and %)
- Services Contribution Margin
- Resale Margin

### 5. **Advanced Visualizations**
- **Quarterly Revenue Comparison**: Side-by-side Forecast vs Budget
- **Variance Analysis**: Color-coded positive/negative variances
- **Margin Trend**: Line chart showing margin progression
- Interactive Plotly charts with hover details

### 6. **AI-Powered Insights** 🤖
Automated analysis across 4 categories:

#### 💡 Key Insights
- Revenue performance highlights
- Trend analysis and patterns

#### 📊 Revenue Analysis
- Growth rate calculations
- Quarterly contribution analysis
- Consistency checks

#### 💰 Margin Analysis
- Margin performance vs thresholds
- Trend identification (improving/declining)
- Average margin calculations

#### ⚠️ Recommendations
- Priority-based action items
- Root cause identification
- Specific corrective actions

### 7. **Export Functionality** 💾
- **Excel Export**: All 4 sheets in one workbook
- **CSV Export**: Individual forecast data
- **Variance CSV**: Variance analysis data
- One-click downloads with fiscal year naming

---

## 📁 Required File Format

For optimal dashboard display, your data should follow this structure:

### Column Structure
```
| Line Item          | Q1    | Q2    | Q3    | Q4    | FY     |
|--------------------|-------|-------|-------|-------|--------|
| Revenue            | 548.3 | 559.9 | 566.0 | 552.9 | 2227.1 |
| Backlog            | 548.3 | 559.9 | 494.5 | 380.9 | 1983.6 |
| Contract Margin    | 149.5 | 156.0 | 159.1 | 158.9 | 623.4  |
| Contract Margin%   | 27.3  | 27.9  | 28.1  | 28.7  | 28.0   |
```

### Key Requirements
- **First column**: Line item names (text)
- **Q1-Q4 columns**: Quarterly numeric values
- **FY column**: Full year totals
- **Percentage rows**: Include "%" in line item name

### Supported Line Items
- Revenue (total, services, resale)
- Backlog
- Sell and Bill
- Contract Margin ($ and %)
- Services CM ($ and %)
- Resale CM ($ and %)
- IYR Live, ABR Live, TCV Live, P2 Live

---

## 🎯 Use Cases

### 1. **Executive Reporting**
- Quick FY overview with key metrics
- Visual performance comparison
- AI-generated insights for board presentations

### 2. **Budget Planning**
- Compare forecasts against budget
- Identify variance drivers
- Adjust plans based on recommendations

### 3. **Performance Tracking**
- Monitor quarterly trends
- Track margin evolution
- Spot revenue consistency issues

### 4. **Variance Analysis**
- Understand forecast vs budget gaps
- Prioritize corrective actions
- Communicate performance to stakeholders

### 5. **Scenario Planning**
- Upload different forecast versions
- Compare multiple scenarios
- Evaluate impact of changes

---

## 🔧 Technical Details

### Technology Stack
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **AI Engine**: Custom FinancialInsightsEngine
- **Export**: openpyxl, CSV

### File Structure
```
FinancialForecastingDemo_v1.0/
├── app_complete_dashboard.py    # Main dashboard application
├── insights_engine.py            # AI insights and recommendations
├── app_simple.py                 # Lightweight version
├── DASHBOARD_GUIDE.md            # This guide
└── requirements.txt              # Python dependencies
```

### Dependencies
```
streamlit
pandas
numpy
plotly
openpyxl
```

---

## 📊 Dashboard Sections Explained

### Header Section
- **Version Selector**: Choose forecast version
- **Fiscal Year**: Select FY2024, FY2025, or FY2026
- **Units**: Display in Millions, Thousands, or Dollars

### Data Tables
- **4-column layout**: Easy side-by-side comparison
- **Color coding**: Highlights for key metrics
- **Scrollable**: 600px height for detailed review

### Metrics Row
- **5 key metrics**: Quick performance snapshot
- **Delta indicators**: Show change from prior period
- **Color coding**: Green (positive), Red (negative)

### Visualizations
- **Interactive charts**: Hover for details
- **Fiscal quarter labels**: Shows month ranges
- **Responsive design**: Adapts to screen size

### Insights Engine
- **Automated analysis**: No manual calculation needed
- **Priority-based**: High/Medium/Low impact classification
- **Actionable**: Specific recommendations with context

### Export Options
- **Multi-sheet Excel**: All data in organized workbook
- **CSV formats**: For further analysis
- **Fiscal year naming**: Auto-includes FY in filename

---

## 💡 Tips & Best Practices

### Data Preparation
1. **Clean your data**: Remove empty rows/columns
2. **Consistent naming**: Use standard line item names
3. **Numeric values**: Ensure Q1-Q4 and FY are numbers
4. **Percentage rows**: Add "%" to line item name

### Using Insights
1. **Review Key Insights first**: Get high-level overview
2. **Check Recommendations**: Focus on high-priority items
3. **Drill into specifics**: Use Revenue/Margin tabs for details
4. **Export for sharing**: Download Excel for stakeholder review

### Performance Optimization
1. **Use sample data**: For quick demos
2. **Limit file size**: Keep uploads under 10MB
3. **Close unused tabs**: Improves browser performance
4. **Refresh periodically**: Clear cache if slow

---

## 🐛 Troubleshooting

### File Upload Issues
**Problem**: File not loading
- **Solution**: Ensure file has Q1, Q2, Q3, Q4, FY columns
- **Solution**: Check for special characters in column names
- **Solution**: Verify file is CSV or Excel format

### Dashboard Not Displaying
**Problem**: Blank screen after upload
- **Solution**: Click "Process Uploaded File" button
- **Solution**: Check browser console for errors
- **Solution**: Refresh page and try again

### Charts Not Showing
**Problem**: Visualizations missing
- **Solution**: Ensure data has numeric values in quarterly columns
- **Solution**: Check for NaN or empty cells
- **Solution**: Verify line item names match expected format

### Insights Not Generating
**Problem**: No AI insights displayed
- **Solution**: Ensure "Revenue" and "Contract Margin%" rows exist
- **Solution**: Check that quarterly values are populated
- **Solution**: Verify numeric data types

---

## 🔄 Version History

### v1.0 (Current)
- ✅ Multi-view dashboard (4 columns)
- ✅ AI-powered insights engine
- ✅ Advanced visualizations
- ✅ Excel/CSV export
- ✅ Fiscal year calendar (Apr-Mar)
- ✅ File upload with auto-detection
- ✅ Variance analysis
- ✅ Margin trend tracking

### Planned Features
- 🔄 Scenario comparison tool
- 🔄 Historical trend analysis
- 🔄 PDF report generation
- 🔄 Email alerts for thresholds
- 🔄 Custom metric definitions

---

## 📞 Support

### Common Questions

**Q: Can I change the fiscal year calendar?**
A: Yes, modify `get_fiscal_quarter_info()` function in `app_complete_dashboard.py`

**Q: How do I add custom line items?**
A: Simply include them in your uploaded file with Q1-Q4 and FY columns

**Q: Can I compare more than 2 scenarios?**
A: Currently supports Forecast vs Budget. Multi-scenario coming in v2.0

**Q: How are insights calculated?**
A: See `insights_engine.py` for full algorithm details

**Q: Can I customize the thresholds?**
A: Yes, edit threshold values in `FinancialInsightsEngine` class

---

## 🎓 Learning Resources

### Understanding Fiscal Years
- [Fiscal Year vs Calendar Year](https://www.investopedia.com/terms/f/fiscalyear.asp)
- [Why Companies Use Different Fiscal Years](https://www.accountingtools.com/articles/fiscal-year.html)

### Financial Metrics
- **Contract Margin**: Revenue minus direct costs
- **Contribution Margin**: Revenue minus variable costs
- **Variance Analysis**: Actual vs Budget comparison

### Dashboard Best Practices
- Keep metrics focused and actionable
- Use consistent time periods
- Highlight exceptions and outliers
- Provide context with trends

---

## 📝 License & Credits

**Built with:**
- Streamlit (Dashboard framework)
- Plotly (Interactive visualizations)
- Pandas (Data processing)

**Created for:** Financial planning and analysis teams

**Version:** 1.0

**Last Updated:** November 2025

---

## 🚀 Next Steps

1. **Load Sample Data**: Click button to see demo
2. **Upload Your Data**: Use your own financial files
3. **Review Insights**: Check AI-generated recommendations
4. **Export Results**: Download for sharing
5. **Take Action**: Implement high-priority recommendations

---

**Happy Forecasting! 📊📈💰**
