# 📊 Dual File Upload - Integrated Forecast & P&L Platform

## 🎯 Overview

The enhanced platform now supports **dual file uploads** allowing you to:
1. Upload **Forecast Revenue Data** (project-based revenue forecasts)
2. Upload **Profit & Loss Data** (P&L statements with actuals)
3. **Aggregate and analyze** both datasets together
4. Generate **integrated insights** and **improved forecasts**

## 🚀 Quick Start

### Access the Platform
```bash
streamlit run app_dual_upload.py --server.port 8504
```

**URL**: http://localhost:8504

---

## 📁 File Upload Process

### **Step 1: Upload Forecast Revenue File**

**Left Panel - Forecast Data Section**

#### What to Upload:
- Project-based revenue forecast data
- Contains project details and monthly revenue projections
- Typical format: Rows = Projects, Columns = Project info + Monthly periods

#### Required Columns:
- **Project ID**: Unique identifier for each project
- **Project Name**: Name or description
- **Client**: Client/customer name
- **Total Value**: Total contract value
- **Status**: Project status (Active, Pipeline, etc.)
- **Monthly Columns**: Revenue amounts by period (e.g., FY2025-01, 2025-02, etc.)

#### Optional Columns:
- **Offering**: Service offering or solution type
- **Industry**: Client industry vertical
- **Sales Org**: Sales organization or region

#### Example Structure:
```
Project ID | Project Name | Client | Total Value | Status | FY2025-01 | FY2025-02 | ...
PROJ001   | Website Dev  | Acme   | 500000     | Active | 50000     | 50000     | ...
PROJ002   | Cloud Mig    | Beta   | 750000     | Active | 75000     | 75000     | ...
```

---

### **Step 2: Upload P&L File**

**Right Panel - P&L Data Section**

#### What to Upload:
- Profit & Loss statement with financial actuals
- Contains line items (Revenue, COGS, Expenses, etc.) and monthly amounts
- Typical format: Rows = P&L line items, Columns = Line item name + Monthly periods

#### Required Columns:
- **Line Item Column**: P&L account names (Revenue, COGS, Operating Expenses, etc.)
- **Monthly Columns**: Actual amounts by period

#### Optional Columns:
- **Entity/Department**: For multi-entity or departmental P&L

#### Detected P&L Categories:
The system automatically detects and categorizes:
- **Revenue**: Sales, income, turnover
- **COGS**: Cost of goods sold, direct costs
- **Gross Profit**: Gross margin
- **Operating Expenses**: OPEX, SG&A, overhead
- **EBITDA**: Operating income
- **Depreciation & Amortization**: D&A
- **EBIT**: Earnings before interest and tax
- **Interest**: Finance costs
- **Tax**: Income tax
- **Net Income**: Net profit, bottom line

#### Example Structure:
```
Line Item          | FY2025-01 | FY2025-02 | FY2025-03 | ...
Revenue           | 1000000   | 1050000   | 1100000   | ...
Cost of Sales     | 400000    | 420000    | 440000    | ...
Gross Profit      | 600000    | 630000    | 660000    | ...
Operating Expenses| 300000    | 310000    | 320000    | ...
EBITDA           | 300000    | 320000    | 340000    | ...
Net Income       | 200000    | 215000    | 230000    | ...
```

---

## 🔧 Column Mapping

### Forecast Data Mapping

After uploading the forecast file, map your columns:

1. **Core Fields**:
   - Project ID → Your project identifier column
   - Project Name → Your project name column
   - Client → Your client name column

2. **Financial Fields**:
   - Total Value → Contract value column
   - Status → Project status column

3. **Business Dimensions**:
   - Offering → Service offering column
   - Industry → Industry vertical column

### P&L Data Mapping

After uploading the P&L file, map your columns:

1. **Core P&L Fields**:
   - Line Item / Account Name → Column with P&L line items
   - Entity / Department → (Optional) Multi-entity breakdown

The system will automatically:
- Detect monthly/period columns
- Categorize line items (Revenue, COGS, etc.)
- Show detected categories for verification

---

## 🔗 Data Integration

### Step 3: Integrate & Analyze

Once both files are uploaded and mapped, click **"🔗 Integrate & Analyze Data"**

The system will:
1. **Aggregate** forecast revenue by period
2. **Aggregate** P&L revenue by period
3. **Calculate variances** between forecast and actuals
4. **Generate insights** and recommendations
5. **Create integrated dashboards**

---

## 📊 Integrated Analysis Dashboard

### **Tab 1: Executive Summary**

**Key Metrics:**
- **Forecast Revenue**: Total from project pipeline
- **P&L Revenue**: Actual revenue from P&L
- **Revenue Variance**: Difference and percentage
- **Avg Net Margin**: Profitability from P&L

**Recommendations:**
- Automated insights based on variance analysis
- Profitability alerts and suggestions
- Action items for improvement

### **Tab 2: Revenue Analysis**

**Forecast Revenue Insights:**
- Revenue by period (bar chart)
- Top 10 projects by revenue
- Historical vs future breakdown
- Project count and distribution

### **Tab 3: P&L Analysis**

**Profit & Loss Insights:**
- Complete P&L summary table
- Gross margin trends
- Net margin trends
- Category breakdowns by period

### **Tab 4: Variance Analysis**

**Forecast vs P&L Comparison:**
- Side-by-side revenue comparison chart
- Detailed variance table by period
- Variance percentage analysis
- Trend identification

### **Tab 5: Integrated Forecasting**

**Enhanced Forecasting:**
- **Scenario Analysis**: Conservative, Most Likely, Optimistic
- **P&L-Adjusted Forecast**: Uses historical variance to adjust forecasts
- **Accuracy Improvement**: Combines pipeline data with actual performance
- **Confidence Scoring**: Based on historical accuracy

---

## 🎯 Key Features

### 1. **Smart Column Detection**
- Automatically detects monthly/period columns
- Identifies P&L line item categories
- Suggests column mappings with confidence scores

### 2. **Flexible Data Formats**
- Supports CSV, XLSX, XLS formats
- Handles various date formats (FY2025-01, 2025-02, Q1 2025, etc.)
- Adapts to different P&L structures

### 3. **Comprehensive Aggregation**
- Combines forecast and P&L data by period
- Calculates variances and trends
- Generates derived metrics (margins, growth rates)

### 4. **Intelligent Insights**
- Automated variance analysis
- Profitability assessment
- Actionable recommendations
- Risk identification

### 5. **Enhanced Forecasting**
- P&L-adjusted forecasts using historical accuracy
- Scenario modeling with confidence intervals
- Integration of pipeline and actuals data

---

## 💡 Use Cases

### **1. Revenue Reconciliation**
- Compare forecasted revenue vs actual P&L revenue
- Identify gaps and variances
- Improve forecast accuracy

### **2. Profitability Analysis**
- Understand profit margins alongside revenue forecasts
- Identify high-margin vs low-margin projects
- Optimize project mix

### **3. Performance Tracking**
- Monitor forecast accuracy over time
- Track actual performance against projections
- Adjust future forecasts based on historical trends

### **4. Executive Reporting**
- Generate comprehensive executive summaries
- Combine pipeline visibility with financial actuals
- Present integrated business performance

### **5. Budget Planning**
- Use historical P&L data to inform future forecasts
- Adjust revenue projections based on cost structures
- Create realistic financial plans

---

## 📋 Best Practices

### Data Preparation

1. **Forecast File**:
   - Ensure project IDs are unique
   - Use consistent date formats in column headers
   - Include all relevant business dimensions
   - Clean data (remove empty rows/columns)

2. **P&L File**:
   - Use clear, consistent line item names
   - Match period formats with forecast file
   - Include all major P&L categories
   - Ensure numeric values are properly formatted

### Mapping Tips

1. **Be Consistent**: Use the same period format in both files
2. **Verify Detection**: Check auto-detected columns before processing
3. **Skip Optional Fields**: Only map fields you need
4. **Review Preview**: Always review data preview before confirming

### Analysis Tips

1. **Start with Executive Summary**: Get high-level overview first
2. **Drill into Variances**: Investigate significant differences
3. **Use P&L-Adjusted Forecasts**: More accurate than pipeline alone
4. **Monitor Trends**: Look for patterns in variance over time

---

## 🔍 Troubleshooting

### Issue: Monthly columns not detected
**Solution**: 
- Ensure column headers contain year (2025, 2026, etc.)
- Use standard formats: YYYY-MM, FY2025-01, Q1 2025
- Check that columns contain numeric data

### Issue: P&L categories not recognized
**Solution**:
- Use standard P&L terminology (Revenue, COGS, etc.)
- Check line item column for proper text values
- Manually verify categorization in detection results

### Issue: Variance calculations seem incorrect
**Solution**:
- Verify both files use same period format
- Check that revenue is in same currency/units
- Ensure periods align between datasets

### Issue: Missing data in integrated view
**Solution**:
- Confirm both files processed successfully
- Check that periods overlap between datasets
- Verify column mappings are correct

---

## 🚀 Advanced Features

### Custom P&L Categories
Extend the P&L processor to recognize custom line items:
```python
pl_processor = PLDataProcessor()
pl_processor.pl_categories['custom_category'] = ['keyword1', 'keyword2']
```

### Export Integrated Data
Export combined analysis:
```python
# In the variance analysis tab
combined_df.to_csv('integrated_analysis.csv')
```

### API Integration
Connect to external data sources:
- ERP systems for P&L data
- CRM systems for forecast data
- Automated data refresh

---

## 📞 Support

For questions or issues:
1. Check this guide first
2. Review example files in `/examples` folder
3. Check error messages for specific guidance
4. Refer to original documentation for single-file features

---

## 🎓 Example Workflow

### Complete End-to-End Example:

1. **Upload Forecast File**
   - Select your project revenue forecast Excel file
   - Click "Process Forecast File"
   - Map columns (Project ID, Name, Client, etc.)
   - Confirm mapping
   - ✅ Forecast data loaded

2. **Upload P&L File**
   - Select your P&L statement Excel file
   - Click "Process P&L File"
   - Map line item column
   - Review detected categories
   - Confirm mapping
   - ✅ P&L data loaded

3. **Integrate Data**
   - Click "Integrate & Analyze Data"
   - Wait for processing
   - ✅ Integration complete

4. **Analyze Results**
   - Review Executive Summary
   - Check variance analysis
   - Examine P&L-adjusted forecasts
   - Export insights

5. **Take Action**
   - Address identified variances
   - Adjust future forecasts
   - Optimize project mix
   - Improve profitability

---

**Built with ❤️ for integrated financial analysis**
