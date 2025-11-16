# 🔍 Troubleshooting: Empty Revenue TCV USD

## ❌ Issue: Revenue TCV USD shows $0

The dynamic reporting is showing $0 for Revenue TCV USD even though data exists in the upload file.

---

## 🎯 Possible Causes

### **1. Period Filter Mismatch**
**Problem:** Selected periods (FY24-Q4 to FY26-Q4) don't match Close Dates in your data

**Check:**
- What are the actual Close Date values in your upload file?
- Do they fall within April 2023 - March 2027?

**Example:**
```
If your Close Dates are in 2023:
- Close Date: 2023-05-15 → FY24-Q1
- Close Date: 2023-08-20 → FY24-Q2

But you selected: FY24-Q4 to FY26-Q4
Result: No data matches, shows $0
```

**Solution:**
- Check your Close Date column values
- Adjust the From/To period filter to match your data
- Or ensure Close Dates are in the correct range

---

### **2. Column Mapping Issue**
**Problem:** "TCV USD" column not mapped to "Revenue TCV USD"

**Check:**
- Go back to Column Mapping page
- Verify "TCV USD" is mapped to "💰 Revenue TCV USD"
- Look for confidence indicator (should be "High")

**Solution:**
```
Target Field: 💰 Revenue TCV USD
Source Column: [TCV USD ▼]  ← Should be selected
Confidence: ✓ High
```

---

### **3. Data Type Issue**
**Problem:** TCV USD column contains text instead of numbers

**Check:**
- Values like "2500000" (string) instead of 2500000 (number)
- Validation page should show error about data type

**Solution:**
- Click "🔧 Fix" button on validation page
- Or manually convert: `pd.to_numeric(df['TCV USD'], errors='coerce')`

---

### **4. Missing Close Date**
**Problem:** Close Date column is empty or not mapped

**Check:**
- Verify Close Date column is mapped
- Check if Close Date values are valid dates

**Solution:**
- Map Close Date in column mapper
- Ensure dates are in standard format (YYYY-MM-DD, MM/DD/YYYY, etc.)

---

## 🔧 Quick Fixes

### **Fix 1: Check Column Mapping**
```
1. Go to Upload & Map page
2. Scroll to column mapping
3. Find: 💰 Revenue TCV USD
4. Verify dropdown shows: TCV USD
5. If not, select it manually
6. Click "Validate & Continue"
```

### **Fix 2: Adjust Period Filter**
```
1. On Dynamic Reporting page
2. Look at "Define Period" section
3. Try selecting wider range:
   From: FY23-Q1
   To: FY27-Q4
4. Check if data appears
```

### **Fix 3: Check Your Data**
```
1. Go back to Upload page
2. Expand "Data Preview"
3. Look at TCV USD column - are there values?
4. Look at Close Date column - are there dates?
5. Note the date range (earliest to latest)
```

### **Fix 4: Re-upload File**
```
1. Go to Upload & Map page
2. Upload your file again
3. Let auto-mapping detect columns
4. Verify all mappings are correct
5. Proceed through validation
```

---

## 📊 Diagnostic Steps

### **Step 1: Verify Data Exists**
```
Upload Page → Data Preview
- Check TCV USD column has values
- Check Close Date column has dates
- Note: 5000 rows loaded
```

### **Step 2: Verify Mapping**
```
Column Mapping Section
- TCV USD → Revenue TCV USD ✓
- Close Date → Close Date ✓
- Account Name → Account Name ✓
```

### **Step 3: Check Validation**
```
Validation Page
- Score: 80/100 or higher
- No errors about TCV USD being object type
- No errors about missing Close Date
```

### **Step 4: Check Period Range**
```
Dynamic Reporting Page
- From: [Check earliest fiscal period]
- To: [Check latest fiscal period]
- Should cover your data's date range
```

### **Step 5: Check Fiscal Quarter Calculation**
```
Example Close Dates → Fiscal Periods:
- 2024-04-15 → FY25-Q1 (Apr-Jun)
- 2024-08-20 → FY25-Q2 (Jul-Sep)
- 2024-11-10 → FY25-Q3 (Oct-Dec)
- 2025-02-05 → FY25-Q4 (Jan-Mar)
```

---

## 🎯 Expected Behavior

### **Correct Flow:**
```
1. Upload file with TCV USD and Close Date
2. Map TCV USD → Revenue TCV USD
3. Map Close Date → Close Date
4. Validate (should pass)
5. Go to Dynamic Reporting
6. Select period range that includes your dates
7. See revenue values in report
```

### **What You Should See:**
```
📊 Summary Metrics:
Account: 50
Revenue TCV USD: $5,924,484,838  ← Should show actual total

📋 Detailed Report:
Account Name   │ FY25-Q1 │ FY25-Q2 │ Total
───────────────┼─────────┼─────────┼────────
Acme Corp      │ 2.50m   │ 3.00m   │ 5.50m
Global Bank    │ 1.20m   │ 0.00m   │ 1.20m
```

---

## 💡 Common Mistakes

### **Mistake 1: Wrong Period Selected**
```
❌ Data has dates in 2024-2025
❌ But selected FY26-Q1 to FY26-Q4 (2025-2026)
✅ Should select FY25-Q1 to FY26-Q4
```

### **Mistake 2: Column Not Mapped**
```
❌ TCV USD column left as "(None)"
✅ Should map to Revenue TCV USD
```

### **Mistake 3: Data Type Not Fixed**
```
❌ TCV USD is text: "2500000"
❌ Validation shows error but not fixed
✅ Click "🔧 Fix" button to convert to numeric
```

### **Mistake 4: Close Date Missing**
```
❌ Close Date column not mapped
❌ Or Close Date values are empty
✅ Map Close Date and ensure values exist
```

---

## 🔍 Debug Checklist

Use this checklist to diagnose the issue:

- [ ] **Data Preview:** TCV USD column has values (not empty)
- [ ] **Data Preview:** Close Date column has dates (not empty)
- [ ] **Column Mapping:** TCV USD mapped to Revenue TCV USD
- [ ] **Column Mapping:** Close Date mapped to Close Date
- [ ] **Column Mapping:** Confidence shows "High" or "Medium"
- [ ] **Validation:** Score is 80/100 or higher
- [ ] **Validation:** No errors about TCV USD data type
- [ ] **Validation:** No errors about missing Close Date
- [ ] **Period Filter:** From/To range covers your data dates
- [ ] **Period Filter:** At least one period selected
- [ ] **Metrics:** Revenue TCV USD checkbox is checked
- [ ] **Grouping:** A dimension is selected (Account, Industry, etc.)

---

## 📞 Next Steps

### **If Revenue Still Shows $0:**

1. **Check the uploaded file directly:**
   - Open your CSV/Excel file
   - Verify TCV USD column has numeric values
   - Verify Close Date column has valid dates
   - Note the date range

2. **Try a wider period range:**
   - Set From: FY23-Q1 (or earliest available)
   - Set To: FY27-Q4 (or latest available)
   - See if any data appears

3. **Re-upload and re-map:**
   - Start fresh with Upload & Map
   - Let auto-detection work
   - Verify all mappings before proceeding

4. **Check for data filtering:**
   - Ensure no filters are applied elsewhere
   - Check if grouping dimension has valid values
   - Verify account names exist in data

---

## 📋 Sample Data Format

### **Correct Format:**
```csv
Account Name,Close Date,TCV USD,IYR USD,Margin USD
Acme Corp,2024-05-15,2500000,1000000,500000
Global Bank,2024-08-20,3000000,1200000,600000
TechStart,2024-11-10,1200000,500000,250000
```

### **Fiscal Period Mapping:**
```
2024-05-15 → FY25-Q1 (Apr-Jun 2024)
2024-08-20 → FY25-Q2 (Jul-Sep 2024)
2024-11-10 → FY25-Q3 (Oct-Dec 2024)
```

### **Expected Report:**
```
Account Name   │ FY25-Q1 │ FY25-Q2 │ FY25-Q3 │ Total
───────────────┼─────────┼─────────┼─────────┼────────
Acme Corp      │ 2.50m   │ 0.00m   │ 0.00m   │ 2.50m
Global Bank    │ 0.00m   │ 3.00m   │ 0.00m   │ 3.00m
TechStart      │ 0.00m   │ 0.00m   │ 1.20m   │ 1.20m
───────────────┼─────────┼─────────┼─────────┼────────
TOTAL          │ 2.50m   │ 3.00m   │ 1.20m   │ 6.70m
```

---

**Most Likely Issue:** Period filter doesn't match your Close Date values. Try selecting a wider date range! 🎯
