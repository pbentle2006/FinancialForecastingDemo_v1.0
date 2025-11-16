# 📅 From/To Period Filter

## ✅ Updated: Period Range Selection

The period filter now uses a simple **From** and **To** dropdown format instead of multi-select year/quarter lists.

---

## 🎯 New Design

### **Define Period Section:**
```
📅 Define Period:

From: [FY26-Q1 ▼]

To:   [FY26-Q4 ▼]
```

---

## 📊 How It Works

### **1. From Dropdown**
Select the starting period:
```
From: FY26-Q1 ▼
      FY26-Q2
      FY26-Q3
      FY26-Q4
      FY27-Q1
      ...
```

### **2. To Dropdown**
Select the ending period:
```
To:   FY26-Q1
      FY26-Q2
      FY26-Q3
      FY26-Q4 ▼
      FY27-Q1
      ...
```

### **3. Automatic Range**
All periods between From and To are included:
```
From: FY26-Q2
To:   FY26-Q4

Result: FY26-Q2, FY26-Q3, FY26-Q4
```

---

## 📋 Example Usage

### **Example 1: Single Quarter**
```
From: FY26-Q2
To:   FY26-Q2

Report Shows:
Industry        │ FY26-Q2 │ Total
────────────────┼─────────┼────────
Banking         │ 2.50m   │ 2.50m
Technology      │ 1.20m   │ 1.20m
```

### **Example 2: Two Quarters**
```
From: FY26-Q2
To:   FY26-Q3

Report Shows:
Industry        │ FY26-Q2 │ FY26-Q3 │ Total
────────────────┼─────────┼─────────┼────────
Banking         │ 2.50m   │ 3.00m   │ 5.50m
Technology      │ 1.20m   │ 0.00m   │ 1.20m
```

### **Example 3: Full Year**
```
From: FY26-Q1
To:   FY26-Q4

Report Shows:
Industry        │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total
────────────────┼─────────┼─────────┼─────────┼─────────┼────────
Banking         │ 1.50m   │ 2.50m   │ 3.00m   │ 0.95m   │ 7.95m
Technology      │ 0.80m   │ 1.20m   │ 0.00m   │ 0.00m   │ 2.00m
```

### **Example 4: Cross-Year Range**
```
From: FY26-Q3
To:   FY27-Q2

Report Shows:
Industry        │ FY26-Q3 │ FY26-Q4 │ FY27-Q1 │ FY27-Q2 │ Total
────────────────┼─────────┼─────────┼─────────┼─────────┼────────
Banking         │ 3.00m   │ 0.95m   │ 1.50m   │ 2.50m   │ 7.95m
Technology      │ 0.00m   │ 0.00m   │ 0.80m   │ 1.20m   │ 2.00m
```

---

## 🎯 Use Cases

### **1. Quarterly Review**
```
From: FY26-Q2
To:   FY26-Q2
Purpose: Focus on current quarter only
```

### **2. Half-Year Analysis**
```
From: FY26-Q1
To:   FY26-Q2
Purpose: H1 performance review
```

### **3. Remaining Year**
```
From: FY26-Q3
To:   FY26-Q4
Purpose: Plan for rest of fiscal year
```

### **4. Rolling 4 Quarters**
```
From: FY26-Q2
To:   FY27-Q1
Purpose: 12-month rolling view
```

### **5. Year-End Planning**
```
From: FY26-Q4
To:   FY27-Q1
Purpose: Year-end close and new year start
```

---

## ✨ Features

### **1. Simple Selection**
- Two dropdowns: From and To
- No multi-select confusion
- Clear start and end points

### **2. Automatic Range**
- Includes all periods between From and To
- No need to select individual periods
- Continuous range guaranteed

### **3. Validation**
- Warns if From is after To
- Falls back to From period only
- Clear error messages

### **4. Default Selection**
- From: First available period
- To: Last available period
- Shows full range by default

---

## 🔧 Technical Details

### **Period List:**
```python
available_periods = [
    "FY26-Q1",
    "FY26-Q2", 
    "FY26-Q3",
    "FY26-Q4",
    "FY27-Q1",
    "FY27-Q2"
]
```

### **Range Selection:**
```python
from_period = "FY26-Q2"  # User selects
to_period = "FY26-Q4"    # User selects

from_idx = 1  # Index of FY26-Q2
to_idx = 3    # Index of FY26-Q4

# Get range (inclusive)
filtered_periods = available_periods[1:4]
# Result: ["FY26-Q2", "FY26-Q3", "FY26-Q4"]
```

### **Validation:**
```python
if from_idx <= to_idx:
    # Valid range
    filtered_periods = available_periods[from_idx:to_idx + 1]
else:
    # Invalid: From is after To
    st.warning("'From' must be before or equal to 'To'")
    filtered_periods = [from_period]
```

---

## 📊 Complete Control Panel

### **Three Sections:**

**1. Group By:**
```
📊 Group By:
○ 🏢 By Account
● 🏭 By Industry Vertical
○ 📦 By Product Name
○ 🎯 By Sales Stage
```

**2. Metrics to Display:**
```
💰 Metrics to Display:
☑ Revenue TCV USD
☑ IYR USD
☑ Margin USD
```

**3. Define Period:**
```
📅 Define Period:

From: [FY26-Q1 ▼]

To:   [FY26-Q4 ▼]
```

---

## 💡 Quick Selections

### **Current Quarter:**
```
From: FY26-Q2
To:   FY26-Q2
```

### **Next Two Quarters:**
```
From: FY26-Q3
To:   FY26-Q4
```

### **Full Year:**
```
From: FY26-Q1
To:   FY26-Q4
```

### **Last 3 Quarters:**
```
From: FY26-Q2
To:   FY26-Q4
```

---

## 🎯 Benefits

### **Before (Multi-Select):**
- ❌ 12 individual month selections (01-12)
- ❌ Confusing multi-select interface
- ❌ Hard to select continuous ranges
- ❌ Easy to miss periods

### **After (From/To):**
- ✅ Simple two-dropdown interface
- ✅ Clear start and end points
- ✅ Automatic continuous range
- ✅ Shows proper quarters (Q1, Q2, Q3, Q4)
- ✅ Intuitive period selection

---

## 📅 Period Format

The system automatically reads your Master Period column format:

**Common Formats:**
- `FY26-Q1` (Fiscal Year 2026, Quarter 1)
- `FY26-Q2` (Fiscal Year 2026, Quarter 2)
- `FY26-Q3` (Fiscal Year 2026, Quarter 3)
- `FY26-Q4` (Fiscal Year 2026, Quarter 4)

**Works with any format in your data:**
- `2024-Q1`
- `Q1-2024`
- `2024Q1`
- Custom formats

---

**Refresh your browser to see the new From/To period filter!** 🚀
