# 📈 Forecast Trend View

## ✅ New Feature: Monthly Forecast Aggregation

A new view that aggregates monthly forecast columns (starting from column BR onwards) into fiscal quarters, showing how Total TCV is phased over time.

---

## 🎯 Purpose

### **The Problem:**
- You have **Total TCV** (total contract value)
- You have **monthly forecast columns** (2025-04, 2025-05, etc.) showing revenue phasing
- You need to see how that TCV is **distributed across fiscal quarters**

### **The Solution:**
The Forecast Trend View:
1. Identifies monthly forecast columns (BR onwards: 2025-04, 2025-05, etc.)
2. Aggregates them into fiscal quarters (Q1, Q2, Q3, Q4)
3. Shows Total TCV alongside the quarterly trend
4. Groups by Account, Industry, Product, or Sales Stage

---

## 📊 How It Works

### **Step 1: Identify Monthly Columns**
```
Columns BR onwards:
2025-04, 2025-05, 2025-06, 2025-07, 2025-08, ...
```

### **Step 2: Map to Fiscal Quarters**
```
2025-04 (April)   → FY26-Q1
2025-05 (May)     → FY26-Q1
2025-06 (June)    → FY26-Q1
2025-07 (July)    → FY26-Q2
2025-08 (August)  → FY26-Q2
2025-09 (Sept)    → FY26-Q2
...
```

### **Step 3: Aggregate**
```
FY26-Q1 = Sum(2025-04, 2025-05, 2025-06)
FY26-Q2 = Sum(2025-07, 2025-08, 2025-09)
FY26-Q3 = Sum(2025-10, 2025-11, 2025-12)
FY26-Q4 = Sum(2026-01, 2026-02, 2026-03)
```

### **Step 4: Display**
```
Account Name   │ Total TCV │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total Forecast
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
Acme Corp      │ 10.00m    │ 2.50m   │ 3.00m   │ 2.50m   │ 2.00m   │ 10.00m
Global Bank    │ 8.00m     │ 2.00m   │ 2.00m   │ 2.00m   │ 2.00m   │ 8.00m
TechStart      │ 5.00m     │ 1.25m   │ 1.25m   │ 1.25m   │ 1.25m   │ 5.00m
```

---

## 🎨 User Interface

### **View Selector:**
```
Select View:
○ 📊 Dynamic Reporting
● 📈 Forecast Trend  ← NEW!
○ 💼 Sales Pipeline
```

### **Control Panel:**
```
┌─────────────────────────────┬─────────────────────────────┐
│ 📊 Group By:                │ 💰 Include Total TCV:       │
├─────────────────────────────┼─────────────────────────────┤
│ ● 📊 Total Only             │ ☑ Show Total TCV column     │
│ ○ 🏢 By Account             │                             │
│ ○ 🏭 By Industry Vertical   │                             │
│ ○ 📦 By Product Name        │                             │
│ ○ 🎯 By Sales Stage         │                             │
└─────────────────────────────┴─────────────────────────────┘
```

### **Summary Metrics:**
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Total TCV    │ Total        │ Forecast     │ Number of    │
│              │ Forecast     │ Periods      │ Accounts     │
│ $23.0M       │ $23.0M       │ 12           │ 50           │
└──────────────┴──────────────┴──────────────┴──────────────┘
```

---

## 📋 Example Data Structure

### **Input Data (Columns BR onwards):**
```csv
Account Name,Total TCV,2025-04,2025-05,2025-06,2025-07,2025-08,2025-09,...
Acme Corp,10000000,800000,850000,850000,1000000,1000000,1000000,...
Global Bank,8000000,650000,650000,700000,650000,650000,700000,...
TechStart,5000000,400000,425000,425000,400000,425000,400000,...
```

### **Output Report:**
```
Account Name   │ Total TCV │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total Forecast
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
Acme Corp      │ 10.00m    │ 2.50m   │ 3.00m   │ 2.50m   │ 2.00m   │ 10.00m
Global Bank    │ 8.00m     │ 2.00m   │ 2.00m   │ 2.00m   │ 2.00m   │ 8.00m
TechStart      │ 5.00m     │ 1.25m   │ 1.23m   │ 1.27m   │ 1.25m   │ 5.00m
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
TOTAL          │ 23.00m    │ 5.75m   │ 6.23m   │ 5.77m   │ 5.25m   │ 23.00m
```

---

## 🔧 Technical Details

### **Column Detection:**
```python
def identify_forecast_columns(self, df):
    """
    Identify columns that contain monthly forecast data
    Format: YYYY-MM (e.g., 2025-04, 2025-05)
    """
    forecast_cols = []
    
    for col in df.columns:
        col_str = str(col)
        # Check if column name matches YYYY-MM format
        if '-' in col_str and len(col_str.split('-')) == 2:
            try:
                parts = col_str.split('-')
                year = int(parts[0])
                month = int(parts[1])
                if 2020 <= year <= 2030 and 1 <= month <= 12:
                    forecast_cols.append(col)
            except:
                continue
    
    return sorted(forecast_cols)
```

### **Fiscal Quarter Mapping:**
```python
def get_fiscal_quarter_from_month(self, year_month_str):
    """
    Convert year-month string to fiscal quarter
    Format: '2025-04' → 'FY26-Q1'
    """
    year, month = map(int, year_month_str.split('-'))
    
    if month >= 4:  # April onwards
        fiscal_year = year + 1
        if 4 <= month <= 6:
            quarter = 'Q1'
        elif 7 <= month <= 9:
            quarter = 'Q2'
        else:  # 10-12
            quarter = 'Q3'
    else:  # January-March
        fiscal_year = year
        quarter = 'Q4'
    
    return f"FY{str(fiscal_year)[-2:]}-{quarter}"
```

### **Aggregation:**
```python
# For each fiscal quarter, sum the monthly columns
for quarter in sorted_quarters:
    month_cols = quarter_mapping[quarter]
    
    # Convert columns to numeric
    for col in month_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Sum by group
    quarter_data = df.groupby(group_by)[month_cols].sum().sum(axis=1)
```

---

## 📊 Use Cases

### **Use Case 1: Revenue Phasing Analysis**
```
Question: How is our Total TCV distributed over time?
View: Total Only (No Grouping)
Result: See overall revenue trend by quarter
```

### **Use Case 2: Account-Level Forecasting**
```
Question: Which accounts have the most revenue in Q2?
View: By Account
Result: See each account's quarterly breakdown
```

### **Use Case 3: Industry Trend Analysis**
```
Question: Which industries have growing vs. declining trends?
View: By Industry Vertical
Result: Compare industry revenue patterns
```

### **Use Case 4: Product Revenue Timing**
```
Question: When will each product generate revenue?
View: By Product Name
Result: See product-specific phasing
```

### **Use Case 5: Pipeline Stage Forecasting**
```
Question: How is revenue phased by sales stage?
View: By Sales Stage
Result: See when deals in each stage will close
```

---

## 🎯 Key Features

### **1. Automatic Column Detection**
- ✅ Finds all columns with YYYY-MM format
- ✅ Starts from column BR onwards
- ✅ Validates year (2020-2030) and month (1-12)
- ✅ Sorts chronologically

### **2. Fiscal Year Alignment**
- ✅ April-March fiscal year
- ✅ Q1: Apr-Jun, Q2: Jul-Sep, Q3: Oct-Dec, Q4: Jan-Mar
- ✅ Automatic quarter calculation
- ✅ Multi-year support

### **3. Flexible Grouping**
- ✅ Total only (no grouping)
- ✅ By Account
- ✅ By Industry Vertical
- ✅ By Product Name
- ✅ By Sales Stage

### **4. Total TCV Comparison**
- ✅ Show Total TCV alongside forecast
- ✅ Verify forecast matches TCV
- ✅ Identify discrepancies

### **5. Number Formatting**
- ✅ Millions format (3.10m)
- ✅ Two decimal places
- ✅ Consistent across all columns

### **6. Export Capability**
- ✅ Download as CSV
- ✅ Includes all columns
- ✅ Formatted for Excel

---

## 📅 Fiscal Quarter Mapping

### **Complete Mapping:**
```
Month      → Quarter
─────────────────────
April      → Q1
May        → Q1
June       → Q1
July       → Q2
August     → Q2
September  → Q2
October    → Q3
November   → Q3
December   → Q3
January    → Q4
February   → Q4
March      → Q4
```

### **Example:**
```
2025-04 → FY26-Q1
2025-05 → FY26-Q1
2025-06 → FY26-Q1
2025-07 → FY26-Q2
2025-08 → FY26-Q2
2025-09 → FY26-Q2
2025-10 → FY26-Q3
2025-11 → FY26-Q3
2025-12 → FY26-Q3
2026-01 → FY26-Q4
2026-02 → FY26-Q4
2026-03 → FY26-Q4
2026-04 → FY27-Q1 (New fiscal year)
```

---

## 💡 Benefits

### **For Finance Teams:**
- ✅ See revenue phasing at a glance
- ✅ Validate forecast vs. Total TCV
- ✅ Identify timing issues
- ✅ Plan cash flow

### **For Sales Teams:**
- ✅ Track when deals will close
- ✅ See pipeline timing
- ✅ Plan resource allocation
- ✅ Forecast accuracy

### **For Leadership:**
- ✅ Strategic revenue planning
- ✅ Quarterly performance visibility
- ✅ Trend analysis
- ✅ Scenario comparison

---

## 🔍 Validation

### **Check 1: Total Forecast = Total TCV**
```
If Total TCV = $10.0M
And Total Forecast = $10.0M
✓ Forecast is complete and accurate
```

### **Check 2: No Missing Periods**
```
If you have columns 2025-04 to 2026-03
✓ Should show FY26-Q1, Q2, Q3, Q4
```

### **Check 3: Numeric Values**
```
All monthly columns should be numbers
If not, validation will show error
Click "🔧 Fix" to convert
```

---

## 📋 Requirements

### **Data Requirements:**
1. **Monthly forecast columns** starting from column BR
2. **Column format:** YYYY-MM (e.g., 2025-04, 2025-05)
3. **Numeric values** in monthly columns
4. **Optional:** Total TCV column for comparison

### **Column Format:**
```
✓ Correct: 2025-04, 2025-05, 2025-06
✗ Wrong: Apr-2025, 04/2025, April 2025
```

---

## 🎨 Example Report

### **By Account:**
```
Account Name   │ Total TCV │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total Forecast
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
Acme Corp      │ 10.00m    │ 2.50m   │ 3.00m   │ 2.50m   │ 2.00m   │ 10.00m
Global Bank    │ 8.00m     │ 2.00m   │ 2.00m   │ 2.00m   │ 2.00m   │ 8.00m
TechStart      │ 5.00m     │ 1.25m   │ 1.23m   │ 1.27m   │ 1.25m   │ 5.00m
FinCo          │ 3.50m     │ 0.88m   │ 0.87m   │ 0.88m   │ 0.87m   │ 3.50m
HealthCorp     │ 4.20m     │ 1.05m   │ 1.05m   │ 1.05m   │ 1.05m   │ 4.20m
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
TOTAL          │ 30.70m    │ 7.68m   │ 8.15m   │ 7.70m   │ 7.17m   │ 30.70m
```

### **By Industry:**
```
Industry       │ Total TCV │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total Forecast
───────────────┼───────────┼─────────┼─────────┼─────────┼─────────┼───────────────
Banking        │ 12.00m    │ 3.00m   │ 3.00m   │ 3.00m   │ 3.00m   │ 12.00m
Technology     │ 10.00m    │ 2.50m   │ 2.50m   │ 2.50m   │ 2.50m   │ 10.00m
Healthcare     │ 8.70m     │ 2.18m   │ 2.17m   │ 2.18m   │ 2.17m   │ 8.70m
```

---

**Refresh your browser and select "📈 Forecast Trend" to see the new view!** 🚀
