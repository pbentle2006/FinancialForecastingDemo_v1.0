# 📅 Fiscal Year Periods from Close Date

## ✅ Updated: Period Calculation from Close Date

The dynamic reporting now uses **Close Date** instead of Master Period, and automatically calculates fiscal quarters based on the April-March fiscal year.

---

## 📆 Fiscal Year Calendar

### **April to March Fiscal Year:**
```
Q1: April - June
Q2: July - September
Q3: October - December
Q4: January - March
```

### **Example:**
```
FY26 runs from:
- April 2025 (Q1 start)
- to March 2026 (Q4 end)
```

---

## 🔄 How It Works

### **1. Read Close Date**
```
Close Date: 2025-05-15
```

### **2. Calculate Fiscal Quarter**
```
Month: May (5)
→ Between April (4) and June (6)
→ Q1

Year: 2025
→ After April, so FY26

Result: FY26-Q1
```

### **3. Group by Fiscal Period**
All records with Close Dates in the same fiscal quarter are grouped together.

---

## 📊 Fiscal Quarter Logic

### **Q1: April - June**
```
Close Date          → Fiscal Period
─────────────────────────────────────
2025-04-01         → FY26-Q1
2025-05-15         → FY26-Q1
2025-06-30         → FY26-Q1
```

### **Q2: July - September**
```
Close Date          → Fiscal Period
─────────────────────────────────────
2025-07-01         → FY26-Q2
2025-08-15         → FY26-Q2
2025-09-30         → FY26-Q2
```

### **Q3: October - December**
```
Close Date          → Fiscal Period
─────────────────────────────────────
2025-10-01         → FY26-Q3
2025-11-15         → FY26-Q3
2025-12-31         → FY26-Q3
```

### **Q4: January - March**
```
Close Date          → Fiscal Period
─────────────────────────────────────
2026-01-01         → FY26-Q4
2026-02-15         → FY26-Q4
2026-03-31         → FY26-Q4
```

---

## 🎯 Complete Example

### **Sample Data:**
```csv
Account Name,Close Date,Revenue TCV USD
Acme Corp,2025-05-15,2500000
Global Bank,2025-08-20,3000000
TechStart,2025-11-10,1200000
FinCo,2026-02-05,950000
```

### **Fiscal Period Calculation:**
```
Acme Corp:    2025-05-15 → May → Q1 → FY26-Q1
Global Bank:  2025-08-20 → Aug → Q2 → FY26-Q2
TechStart:    2025-11-10 → Nov → Q3 → FY26-Q3
FinCo:        2026-02-05 → Feb → Q4 → FY26-Q4
```

### **Report Output:**
```
Account Name   │ FY26-Q1 │ FY26-Q2 │ FY26-Q3 │ FY26-Q4 │ Total
───────────────┼─────────┼─────────┼─────────┼─────────┼────────
Acme Corp      │ 2.50m   │ 0.00m   │ 0.00m   │ 0.00m   │ 2.50m
Global Bank    │ 0.00m   │ 3.00m   │ 0.00m   │ 0.00m   │ 3.00m
TechStart      │ 0.00m   │ 0.00m   │ 1.20m   │ 0.00m   │ 1.20m
FinCo          │ 0.00m   │ 0.00m   │ 0.00m   │ 0.95m   │ 0.95m
```

---

## 📅 Period Filter

### **From/To Selection:**
```
📅 Define Period:

From: [FY26-Q1 ▼]
To:   [FY26-Q4 ▼]
```

### **Available Periods:**
Automatically calculated from all Close Dates in your data:
```
FY25-Q1
FY25-Q2
FY25-Q3
FY25-Q4
FY26-Q1
FY26-Q2
FY26-Q3
FY26-Q4
FY27-Q1
...
```

---

## 🔧 Technical Implementation

### **Fiscal Quarter Function:**
```python
def get_fiscal_quarter(self, date):
    """
    Convert a date to fiscal quarter based on April-March fiscal year
    Q1: April - June
    Q2: July - September
    Q3: October - December
    Q4: January - March
    """
    if pd.isna(date):
        return None
    
    month = date.month
    year = date.year
    
    # Determine fiscal year and quarter
    if month >= 4:  # April onwards
        fiscal_year = year + 1  # FY26 starts April 2025
        if 4 <= month <= 6:
            quarter = 'Q1'
        elif 7 <= month <= 9:
            quarter = 'Q2'
        else:  # 10-12
            quarter = 'Q3'
    else:  # January-March
        fiscal_year = year  # Still in previous FY
        quarter = 'Q4'
    
    return f"FY{str(fiscal_year)[-2:]}-{quarter}"
```

### **Example Calculations:**
```python
# April 2025 → FY26-Q1
get_fiscal_quarter(datetime(2025, 4, 15))  # "FY26-Q1"

# August 2025 → FY26-Q2
get_fiscal_quarter(datetime(2025, 8, 20))  # "FY26-Q2"

# November 2025 → FY26-Q3
get_fiscal_quarter(datetime(2025, 11, 10)) # "FY26-Q3"

# February 2026 → FY26-Q4
get_fiscal_quarter(datetime(2026, 2, 5))   # "FY26-Q4"

# April 2026 → FY27-Q1 (new fiscal year)
get_fiscal_quarter(datetime(2026, 4, 1))   # "FY27-Q1"
```

---

## 📊 Reporting Flow

### **Step 1: Load Data**
```
Read Close Date column from uploaded file
```

### **Step 2: Calculate Fiscal Periods**
```
For each row:
  Parse Close Date → Calculate Fiscal Quarter
```

### **Step 3: Extract Available Periods**
```
Get unique fiscal periods from all rows
Sort chronologically: FY26-Q1, FY26-Q2, FY26-Q3, FY26-Q4
```

### **Step 4: User Selects Range**
```
From: FY26-Q2
To:   FY26-Q4
```

### **Step 5: Filter Data**
```
Keep only rows where fiscal period is in [FY26-Q2, FY26-Q3, FY26-Q4]
```

### **Step 6: Group and Aggregate**
```
Group by: Selected dimension (Account, Industry, Product, Sales Stage)
Split by: Fiscal periods
Aggregate: Sum metrics (Revenue, IYR, Margin)
```

---

## 🎯 Use Cases

### **1. Quarterly Business Review**
```
From: FY26-Q2
To:   FY26-Q2

Shows all deals closing in Q2 (July-September)
```

### **2. Half-Year Analysis**
```
From: FY26-Q1
To:   FY26-Q2

Shows H1 performance (April-September)
```

### **3. Year-End Planning**
```
From: FY26-Q3
To:   FY26-Q4

Shows second half (October-March)
```

### **4. Full Fiscal Year**
```
From: FY26-Q1
To:   FY26-Q4

Shows entire FY26 (April 2025 - March 2026)
```

### **5. Rolling 12 Months**
```
From: FY26-Q2
To:   FY27-Q1

Shows 4 consecutive quarters
```

---

## 📋 Key Changes

### **Before:**
- ❌ Used Master Period column directly
- ❌ Required manual period entry
- ❌ No fiscal year logic

### **After:**
- ✅ Uses Close Date column
- ✅ Automatically calculates fiscal quarters
- ✅ April-March fiscal year logic
- ✅ Q1=Apr-Jun, Q2=Jul-Sep, Q3=Oct-Dec, Q4=Jan-Mar
- ✅ Dynamic period detection

---

## 💡 Benefits

### **For Users:**
- ✅ No need to manually enter fiscal periods
- ✅ Automatic fiscal year calculation
- ✅ Consistent quarter definitions
- ✅ Works with any Close Date format

### **For Reporting:**
- ✅ Accurate fiscal quarter grouping
- ✅ Proper year-over-year comparisons
- ✅ Aligned with financial calendar
- ✅ Standard fiscal reporting

---

## 🔍 Data Requirements

### **Required Column:**
- **Close Date** (mapped in column mapper)

### **Supported Date Formats:**
```
2025-05-15
05/15/2025
15-May-2025
2025/05/15
May 15, 2025
```

All standard date formats are automatically parsed.

---

## ⚠️ Important Notes

### **Fiscal Year Definition:**
```
FY26 = April 2025 to March 2026
FY27 = April 2026 to March 2027
```

### **Quarter Boundaries:**
```
Q1 ends: June 30
Q2 ends: September 30
Q3 ends: December 31
Q4 ends: March 31
```

### **Year Transition:**
```
March 31, 2026  → FY26-Q4 (end of FY26)
April 1, 2026   → FY27-Q1 (start of FY27)
```

---

**Refresh your browser** to see fiscal periods calculated from Close Date! 🚀
