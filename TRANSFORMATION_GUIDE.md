# 🔄 Data Transformation Guide

## Overview
The dashboard now automatically transforms **transaction-level data** into **quarterly forecast format**!

---

## 📊 What Gets Transformed

### Input: Transaction-Level Data
Your data with columns like:
- **Opportunity Created** (date)
- **Master Period** (e.g., "FY26-Q2")
- **Reporting Period** (e.g., "FY26-Q2")
- **Reporting Month** (date)
- **Close Date** (date)
- **Industry Segment** (text)
- **Sales Stage** (text)
- **Amount/Revenue** (numeric)

### Output: Quarterly Dashboard Format
Transformed into:
```
| Line Item          | Q1    | Q2    | Q3    | Q4    | FY     |
|--------------------|-------|-------|-------|-------|--------|
| Revenue            | 548.3 | 559.9 | 566.0 | 552.9 | 2227.1 |
| Banking            | 200.0 | 250.0 | 275.0 | 225.0 | 950.0  |
| Transportation     | 100.0 | 120.0 | 130.0 | 110.0 | 460.0  |
```

---

## 🚀 How to Use

### Step 1: Upload Your File
1. Click **"📁 Upload Your Data"**
2. Select your CSV or Excel file
3. Dashboard will show a preview

### Step 2: Configure Transformation
The dashboard will detect:
- ✅ **Date columns** automatically (Master Period, Close Date, etc.)
- ✅ **Value columns** automatically (Revenue, Amount, etc.)
- ✅ **Group columns** automatically (Industry Segment, Sales Stage, etc.)

You can adjust these selections:

#### 📅 Date Column
- **Purpose**: Determines which quarter each transaction belongs to
- **Supported formats**:
  - Period strings: `FY26-Q2`, `FY25-Q4`
  - Standard dates: `2025-08-22`, `08/22/2025`
  - Month names: `August 2025`, `Aug-25`

#### 💰 Value Column
- **Purpose**: The numeric value to aggregate (sum) by quarter
- **Common names**: Revenue, Amount, Value, Forecast, Sales, Total

#### 📊 Group By (Optional)
- **Purpose**: Create separate line items for each category
- **Examples**:
  - Industry Segment → Shows revenue by industry
  - Sales Stage → Shows revenue by stage
  - Opportunity Owner → Shows revenue by owner
- **Select "None"** for a single total row

### Step 3: Transform
1. Click **"🔄 Transform to Quarterly Format"**
2. Dashboard processes your data
3. See quarterly totals instantly!

---

## 📅 Fiscal Year Mapping

The transformer uses **April-March fiscal year**:

| Your Data | Maps To | Fiscal Quarter |
|-----------|---------|----------------|
| April 2025 | Q1 | Apr-Jun |
| May 2025 | Q1 | Apr-Jun |
| June 2025 | Q1 | Apr-Jun |
| July 2025 | Q2 | Jul-Sep |
| August 2025 | Q2 | Jul-Sep |
| September 2025 | Q2 | Jul-Sep |
| October 2025 | Q3 | Oct-Dec |
| November 2025 | Q3 | Oct-Dec |
| December 2025 | Q3 | Oct-Dec |
| January 2026 | Q4 | Jan-Mar |
| February 2026 | Q4 | Jan-Mar |
| March 2026 | Q4 | Jan-Mar |

**Note:** January-March dates are part of the **previous fiscal year** (e.g., Jan 2026 is Q4 of FY2026, not FY2027)

---

## 🎯 Examples

### Example 1: Simple Revenue Aggregation

**Input Data:**
```csv
Master Period,Amount
FY26-Q2,100000
FY26-Q2,150000
FY26-Q3,200000
FY26-Q4,175000
```

**Transformation Settings:**
- Date Column: `Master Period`
- Value Column: `Amount`
- Group By: `None`

**Output:**
```
| Line Item | Q1 | Q2     | Q3     | Q4     | FY      |
|-----------|-----|--------|--------|--------|---------|
| Revenue   | 0   | 250000 | 200000 | 175000 | 625000  |
```

### Example 2: Revenue by Industry

**Input Data:**
```csv
Master Period,Industry Segment,Amount
FY26-Q2,Banking,100000
FY26-Q2,Transportation,50000
FY26-Q3,Banking,120000
FY26-Q3,Transportation,80000
```

**Transformation Settings:**
- Date Column: `Master Period`
- Value Column: `Amount`
- Group By: `Industry Segment`

**Output:**
```
| Line Item      | Q1 | Q2     | Q3     | Q4 | FY     |
|----------------|-----|--------|--------|-----|--------|
| Banking        | 0   | 100000 | 120000 | 0   | 220000 |
| Transportation | 0   | 50000  | 80000  | 0   | 130000 |
```

### Example 3: Using Close Dates

**Input Data:**
```csv
Close Date,Revenue
2025-08-15,50000
2025-08-22,75000
2025-09-10,100000
2025-10-05,90000
```

**Transformation Settings:**
- Date Column: `Close Date`
- Value Column: `Revenue`
- Group By: `None`

**Output:**
```
| Line Item | Q1 | Q2     | Q3    | Q4 | FY     |
|-----------|-----|--------|-------|-----|--------|
| Revenue   | 0   | 225000 | 90000 | 0   | 315000 |
```

---

## 🔍 Supported Date Formats

### Period Strings
- `FY26-Q2` → Fiscal Year 2026, Quarter 2
- `FY25-Q4` → Fiscal Year 2025, Quarter 4
- `2026-Q1` → Year 2026, Quarter 1

### Standard Dates
- `2025-08-22` (ISO format)
- `08/22/2025` (US format)
- `22-08-2025` (European format)
- `August 22, 2025` (Long format)
- `Aug-25` (Short format)

### Month/Year
- `August 2025`
- `Aug 2025`
- `2025-08`

---

## ✅ Validation & Quality Checks

After transformation, the dashboard shows:
- ✅ **Total records processed**
- ✅ **Quarterly totals** (Q1, Q2, Q3, Q4, FY)
- ✅ **Date range** of source data
- ✅ **Columns used** for transformation

---

## 💡 Tips & Best Practices

### Data Preparation
1. **Clean dates**: Ensure date columns have valid dates
2. **Numeric values**: Value columns should be numbers (not text)
3. **Consistent format**: Use same date format throughout
4. **Remove nulls**: Filter out rows with missing dates

### Choosing Columns
1. **Date Column**: Pick the most reliable date field
   - `Master Period` → Best for pre-categorized data
   - `Close Date` → Best for actual closed deals
   - `Reporting Period` → Best for forecast data

2. **Value Column**: Pick the primary metric
   - `Revenue` → For revenue forecasts
   - `Amount` → For deal amounts
   - `Forecast` → For projected values

3. **Group By**: Choose based on analysis needs
   - `Industry Segment` → Industry analysis
   - `Sales Stage` → Pipeline analysis
   - `Opportunity Owner` → Team performance
   - `None` → Overall totals only

### Performance
- **Large files** (>10,000 rows): May take 5-10 seconds
- **Many groups** (>50 categories): Consider filtering first
- **Multiple date columns**: Try each to see which works best

---

## 🐛 Troubleshooting

### "No valid dates found"
**Problem**: Transformer can't parse your date column

**Solutions**:
1. Check date format is consistent
2. Try a different date column
3. Ensure dates are not text strings
4. Remove rows with invalid dates

### "No numeric value columns detected"
**Problem**: No numeric columns found

**Solutions**:
1. Ensure value column contains numbers
2. Remove currency symbols ($, €, etc.)
3. Remove commas from numbers
4. Convert text numbers to numeric

### Quarters are wrong
**Problem**: Transactions in wrong quarters

**Solutions**:
1. Verify fiscal year calendar (Apr-Mar)
2. Check if dates are parsed correctly
3. Use `Master Period` if available (more reliable)
4. Review date format interpretation

### Missing data
**Problem**: Some transactions not showing up

**Solutions**:
1. Check for null/empty dates
2. Verify date range is within fiscal year
3. Ensure value column has non-zero values
4. Review original data for completeness

---

## 📊 After Transformation

Once transformed, you get:
- ✅ **Quarterly dashboard view**
- ✅ **Interactive visualizations**
- ✅ **AI-powered insights**
- ✅ **Export options** (Excel, CSV)
- ✅ **Variance analysis** (if budget data available)

---

## 🔄 Re-Transformation

To transform again with different settings:
1. Click **"🔄 Reset Dashboard"** in sidebar
2. Upload file again
3. Choose different columns
4. Transform with new settings

---

## 📞 Need Help?

### Common Questions

**Q: Can I transform multiple files?**
A: Currently one file at a time. For multiple files, combine them first.

**Q: Does it work with Excel?**
A: Yes! Both CSV and Excel (.xlsx, .xls) are supported.

**Q: Can I see the original data?**
A: Yes, it's stored in session state. Use "View Original Data" option.

**Q: What if I have monthly data?**
A: The transformer automatically rolls up months into quarters based on fiscal calendar.

**Q: Can I change the fiscal year?**
A: Yes, modify `fiscal_quarters` in `data_transformer.py` for custom fiscal years.

---

## 🎓 Advanced Usage

### Custom Fiscal Year
Edit `data_transformer.py`:
```python
self.fiscal_quarters = {
    'Q1': [1, 2, 3],    # Jan-Mar
    'Q2': [4, 5, 6],    # Apr-Jun
    'Q3': [7, 8, 9],    # Jul-Sep
    'Q4': [10, 11, 12]  # Oct-Dec
}
```

### Multiple Value Columns
To aggregate multiple metrics, run transformation multiple times with different value columns, then combine results.

### Custom Grouping
For complex grouping (e.g., by region AND industry), pre-process your data to create a combined column:
```python
df['Region_Industry'] = df['Region'] + ' - ' + df['Industry']
```

---

**Happy Transforming! 🔄📊**
