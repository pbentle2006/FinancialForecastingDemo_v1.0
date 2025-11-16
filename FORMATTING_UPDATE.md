# 📊 Number Formatting Update

## ✅ Changes Made

### **1. Columns Split by Quarter**
All metrics are now split by Master Period (quarters) from your uploaded data.

**Before:**
```
Industry        │ Revenue TCV USD
────────────────┼─────────────────
Banking         │ 6450000.00
Technology      │ 1200000.00
```

**After:**
```
Industry        │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total
────────────────┼─────────┼─────────┼─────────┼────────
Banking         │ 2.50m   │ 3.00m   │ 0.95m   │ 6.45m
Technology      │ 1.20m   │ 0.00m   │ 0.00m   │ 1.20m
```

---

### **2. Numbers Formatted in Millions**
All financial values are now displayed as "X.XXm" format with 2 decimal places.

**Format Examples:**
- $3,100,000 → **3.10m**
- $1,200,000 → **1.20m**
- $950,000 → **0.95m**
- $0 → **0.00m**

---

## 📋 Report Structure

### **Example: By Industry Vertical**

```
┌──────────────────────┬─────────┬─────────┬─────────┬─────────┐
│ Industry Vertical    │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total   │
├──────────────────────┼─────────┼─────────┼─────────┼─────────┤
│ Banking              │ 2.50m   │ 3.00m   │ 0.95m   │ 6.45m   │
│ Healthcare           │ 0.00m   │ 1.80m   │ 0.00m   │ 1.80m   │
│ Technology           │ 1.20m   │ 0.00m   │ 0.00m   │ 1.20m   │
│ Retail               │ 0.00m   │ 0.00m   │ 0.95m   │ 0.95m   │
└──────────────────────┴─────────┴─────────┴─────────┴─────────┘
```

---

### **Multiple Metrics Example:**

When you select multiple metrics (e.g., Revenue TCV USD + Margin USD):

```
┌──────────────┬────────────────────┬────────────────────┬────────────────────┬─────────┐
│ Industry     │ FY26-Q2_Revenue    │ FY26-Q3_Revenue    │ FY26-Q4_Revenue    │ Total   │
├──────────────┼────────────────────┼────────────────────┼────────────────────┼─────────┤
│ Banking      │ 2.50m              │ 3.00m              │ 0.95m              │ 6.45m   │
│ Technology   │ 1.20m              │ 0.00m              │ 0.00m              │ 1.20m   │
├──────────────┼────────────────────┼────────────────────┼────────────────────┼─────────┤
│              │ FY26-Q2_Margin     │ FY26-Q3_Margin     │ FY26-Q4_Margin     │ Total   │
├──────────────┼────────────────────┼────────────────────┼────────────────────┼─────────┤
│ Banking      │ 0.75m              │ 0.90m              │ 0.29m              │ 1.94m   │
│ Technology   │ 0.36m              │ 0.00m              │ 0.00m              │ 0.36m   │
└──────────────┴────────────────────┴────────────────────┴────────────────────┴─────────┘
```

---

## 🎯 Key Features

### **1. Automatic Quarter Detection**
- Reads Master Period from your uploaded data
- Automatically sorts quarters (FY26-Q1, FY26-Q2, etc.)
- Creates separate columns for each quarter

### **2. Metric Separation**
- Each metric gets its own set of quarter columns
- Format: `{Quarter}_{Metric}` (e.g., FY26-Q2_revenue_tcv_usd)
- Total column calculated for each metric

### **3. Consistent Formatting**
- All numbers: **X.XXm** (2 decimal places)
- Percentages: **XX.XX%** (2 decimal places)
- Zero values: **0.00m**

### **4. Readable Column Names**
- Quarters shown as-is from your data (FY26-Q2, FY26-Q3, etc.)
- Metric names cleaned up for display
- Total column clearly labeled

---

## 💡 Usage Tips

### **Reading the Format:**
```
3.10m = $3,100,000
1.20m = $1,200,000
0.95m = $950,000
0.00m = $0
```

### **Interpreting the Report:**
1. **Rows** = Your grouping dimension (Account, Industry, or Product)
2. **Columns** = Quarters from Master Period
3. **Values** = Metrics in millions (2 decimals)
4. **Total** = Sum across all quarters

---

## 📊 Complete Example

### **Sample Data:**
```csv
Account Name,Master Period,Revenue TCV USD,Margin USD
Acme Corp,FY26-Q2,2500000,750000
Global Bank,FY26-Q3,3000000,900000
TechStart,FY26-Q2,1200000,360000
```

### **Report Output (By Account):**
```
┌──────────────┬─────────────────┬─────────────────┬─────────────────┬─────────┐
│ Account Name │ FY26-Q2_Revenue │ FY26-Q3_Revenue │ FY26-Q4_Revenue │ Total   │
├──────────────┼─────────────────┼─────────────────┼─────────────────┼─────────┤
│ Acme Corp    │ 2.50m           │ 0.00m           │ 0.00m           │ 2.50m   │
│ Global Bank  │ 0.00m           │ 3.00m           │ 0.00m           │ 3.00m   │
│ TechStart    │ 1.20m           │ 0.00m           │ 0.00m           │ 1.20m   │
├──────────────┼─────────────────┼─────────────────┼─────────────────┼─────────┤
│              │ FY26-Q2_Margin  │ FY26-Q3_Margin  │ FY26-Q4_Margin  │ Total   │
├──────────────┼─────────────────┼─────────────────┼─────────────────┼─────────┤
│ Acme Corp    │ 0.75m           │ 0.00m           │ 0.00m           │ 0.75m   │
│ Global Bank  │ 0.00m           │ 0.90m           │ 0.00m           │ 0.90m   │
│ TechStart    │ 0.36m           │ 0.00m           │ 0.00m           │ 0.36m   │
└──────────────┴─────────────────┴─────────────────┴─────────────────┴─────────┘
```

---

## 🎨 Visual Improvements

### **Before:**
- Single column with large numbers
- Hard to read: 10576794.67
- No quarter breakdown
- Difficult to compare periods

### **After:**
- Separate columns per quarter
- Easy to read: 10.58m
- Clear period comparison
- Professional formatting
- Total column for quick reference

---

## 🔧 Technical Details

### **Formatting Function:**
```python
def format_number_millions(value):
    if pd.isna(value) or value == 0:
        return "0.00m"
    millions = value / 1_000_000
    return f"{millions:.2f}m"
```

### **Quarter Splitting:**
```python
# Groups by dimension + master_period
df.groupby(['industry_vertical', 'master_period']).sum()

# Pivots to create quarter columns
pivot(index='industry_vertical', columns='master_period', values='revenue_tcv_usd')

# Result: FY26-Q2_revenue_tcv_usd, FY26-Q3_revenue_tcv_usd, etc.
```

---

## ✅ Benefits

1. **Easier to Read** - "3.10m" vs "3,100,000.00"
2. **Quarter Comparison** - See all quarters side-by-side
3. **Professional Format** - Standard financial reporting format
4. **Consistent Decimals** - Always 2 decimal places
5. **Quick Totals** - Total column for each metric
6. **Flexible** - Works with any quarters in your data

---

**Refresh your browser to see the new formatting!** 🚀
