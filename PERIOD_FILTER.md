# 📅 Period Filter Added to Dynamic Reporting

## ✅ New Feature: Define Period

The Dynamic Reporting now includes a **Define Period** filter that allows you to select specific years and quarters to display.

---

## 🎯 Three-Column Layout

### **Control Panel:**
```
┌─────────────────┬─────────────────┬─────────────────┐
│ 📊 Group By     │ 💰 Metrics      │ 📅 Define Period│
├─────────────────┼─────────────────┼─────────────────┤
│ ○ By Account    │ ☑ Revenue TCV   │ Select Years:   │
│ ● By Industry   │ ☑ IYR USD       │ ☑ FY25          │
│ ○ By Product    │ ☑ Margin USD    │ ☑ FY26          │
│ ○ By Sales Stage│                 │                 │
│                 │                 │ Select Quarters:│
│                 │                 │ ☑ Q1            │
│                 │                 │ ☑ Q2            │
│                 │                 │ ☑ Q3            │
│                 │                 │ ☑ Q4            │
└─────────────────┴─────────────────┴─────────────────┘
```

---

## 📅 How It Works

### **1. Automatic Period Detection**
The system reads your Master Period column and extracts:
- **Years:** FY25, FY26, FY27, etc.
- **Quarters:** Q1, Q2, Q3, Q4

### **2. Year Selection**
Multi-select dropdown with all available years:
```
Select Years:
☑ FY25
☑ FY26
☐ FY27
```

### **3. Quarter Selection**
Multi-select dropdown with all available quarters:
```
Select Quarters:
☑ Q1
☑ Q2
☑ Q3
☐ Q4
```

### **4. Dynamic Filtering**
The report automatically updates to show only the selected periods.

---

## 📊 Example Usage

### **Scenario 1: View Full Year**
```
Select Years: FY26
Select Quarters: Q1, Q2, Q3, Q4

Result:
Industry        │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total
────────────────┼─────────┼─────────┼─────────┼─────────┼────────
Banking         │ 1.50m   │ 2.50m   │ 3.00m   │ 0.95m   │ 7.95m
Technology      │ 0.80m   │ 1.20m   │ 0.00m   │ 0.00m   │ 2.00m
```

### **Scenario 2: Compare Specific Quarters**
```
Select Years: FY26
Select Quarters: Q2, Q3

Result:
Industry        │ FY26-Q2 │ FY26-Q3 │ Total
────────────────┼─────────┼─────────┼────────
Banking         │ 2.50m   │ 3.00m   │ 5.50m
Technology      │ 1.20m   │ 0.00m   │ 1.20m
```

### **Scenario 3: Year-over-Year Comparison**
```
Select Years: FY25, FY26
Select Quarters: Q1, Q2, Q3, Q4

Result:
Industry        │ FY25-Q1 │ FY25-Q2 │ ... │ FY26-Q1 │ FY26-Q2 │ ... │ Total
────────────────┼─────────┼─────────┼─────┼─────────┼─────────┼─────┼────────
Banking         │ 1.20m   │ 2.00m   │ ... │ 1.50m   │ 2.50m   │ ... │ 15.20m
```

### **Scenario 4: Q4 Only Across Years**
```
Select Years: FY25, FY26
Select Quarters: Q4

Result:
Industry        │ FY25-Q4 │ FY26-Q4 │ Total
────────────────┼─────────┼─────────┼────────
Banking         │ 0.80m   │ 0.95m   │ 1.75m
Technology      │ 0.50m   │ 0.00m   │ 0.50m
```

---

## 🎯 Use Cases

### **1. Quarterly Business Reviews**
```
Select: Current Year + Current Quarter
Purpose: Focus on this quarter's performance
```

### **2. Year-End Planning**
```
Select: Current Year + Q3, Q4
Purpose: Plan for end of fiscal year
```

### **3. YoY Comparison**
```
Select: FY25, FY26 + Same Quarters
Purpose: Compare year-over-year growth
```

### **4. Seasonal Analysis**
```
Select: Multiple Years + Q1 only
Purpose: Analyze Q1 performance trends
```

### **5. Rolling Forecast**
```
Select: Current Year + Next 3 Quarters
Purpose: Focus on near-term forecast
```

---

## 🔧 Technical Details

### **Period Parsing:**
```python
# Input: "FY26-Q2"
# Output: ("FY26", "Q2")

def parse_period(period_str):
    if '-' in period_str:
        parts = period_str.split('-')
        return parts[0], parts[1]
    return period_str, ''
```

### **Filtering Logic:**
```python
# Extract unique years and quarters
years = ["FY25", "FY26", "FY27"]
quarters = ["Q1", "Q2", "Q3", "Q4"]

# User selects: FY26, Q2, Q3
selected_years = ["FY26"]
selected_quarters = ["Q2", "Q3"]

# Filter periods
filtered_periods = ["FY26-Q2", "FY26-Q3"]

# Filter dataframe
df_filtered = df[df['master_period'].isin(filtered_periods)]
```

---

## 📋 Complete Control Panel

### **Three Sections:**

**1. Group By (Radio Buttons):**
- 🏢 By Account
- 🏭 By Industry Vertical
- 📦 By Product Name
- 🎯 By Sales Stage

**2. Metrics to Display (Checkboxes):**
- 💰 Revenue TCV USD
- 💵 IYR USD
- 📊 Margin USD

**3. Define Period (Multi-Select Dropdowns):**
- 📅 Select Years (FY25, FY26, FY27...)
- 📅 Select Quarters (Q1, Q2, Q3, Q4)

---

## ✨ Features

### **1. Multi-Select**
- Select multiple years at once
- Select multiple quarters at once
- All combinations supported

### **2. Default Selection**
- All years selected by default
- All quarters selected by default
- Deselect to filter

### **3. Dynamic Updates**
- Report updates automatically
- Summary metrics recalculate
- Totals adjust to filtered data

### **4. Validation**
- Warns if no periods selected
- Warns if no data for selected periods
- Clear error messages

---

## 🎨 User Experience

### **Step 1: Select Grouping**
```
Choose: By Industry Vertical
```

### **Step 2: Select Metrics**
```
Choose: Revenue TCV USD, Margin USD
```

### **Step 3: Define Period**
```
Years: FY26
Quarters: Q2, Q3, Q4
```

### **Step 4: View Report**
```
Industry        │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total
────────────────┼─────────┼─────────┼─────────┼────────
Banking         │ 2.50m   │ 3.00m   │ 0.95m   │ 6.45m
Healthcare      │ 0.00m   │ 1.80m   │ 0.00m   │ 1.80m
Technology      │ 1.20m   │ 0.00m   │ 0.00m   │ 1.20m
```

---

## 💡 Tips

### **Quick Filters:**

**Current Quarter Only:**
```
Years: FY26
Quarters: Q2
```

**Rest of Year:**
```
Years: FY26
Quarters: Q3, Q4
```

**Full Year:**
```
Years: FY26
Quarters: Q1, Q2, Q3, Q4
```

**Compare Two Quarters:**
```
Years: FY26
Quarters: Q2, Q3
```

---

## 🎯 Benefits

### **Before:**
- ❌ See all periods at once
- ❌ Cluttered view with too many columns
- ❌ Hard to focus on specific timeframes
- ❌ No period filtering

### **After:**
- ✅ Filter by year and quarter
- ✅ Clean, focused reports
- ✅ Easy period comparison
- ✅ Flexible time range selection
- ✅ Dynamic filtering

---

**Refresh your browser to see the new Define Period filter!** 🚀
