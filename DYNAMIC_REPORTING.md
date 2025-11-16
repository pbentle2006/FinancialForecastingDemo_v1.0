# 📊 Dynamic Reporting View

## 🎯 New Flexible Reporting System

Instead of fixed P&L line items (Services COGS, Product Revenue, etc.), the reporting is now **completely dynamic** based on your mapped columns.

---

## 🔄 How It Works

### **1. Choose Your Grouping Dimension**

Select how you want to group your data:

```
📊 Group By:
  ○ 🏢 By Account
  ○ 🏭 By Industry Vertical  
  ○ 📦 By Product Name
```

### **2. Select Metrics to Display**

Choose which financial metrics to show:

```
💰 Metrics to Display:
  ☑ Revenue TCV USD
  ☑ IYR USD
  ☑ Margin USD
```

### **3. View Report by Master Period**

The system automatically groups by Master Period (quarters) and shows metrics for each period.

---

## 📋 Example Reports

### **Example 1: By Account**

```
Account Name    │ FY26-Q2_Revenue │ FY26-Q3_Revenue │ FY26-Q4_Revenue │ Total_Revenue │ Margin %
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
Acme Corp       │ $2,500,000      │ $0              │ $0              │ $2,500,000    │ 30.0%
Global Bank     │ $0              │ $3,000,000      │ $0              │ $3,000,000    │ 30.0%
HealthCo        │ $0              │ $1,800,000      │ $0              │ $1,800,000    │ 30.0%
TechStart Inc   │ $1,200,000      │ $0              │ $0              │ $1,200,000    │ 30.0%
Retail Giant    │ $0              │ $0              │ $950,000        │ $950,000      │ 30.0%
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
TOTAL           │ $3,700,000      │ $4,800,000      │ $950,000        │ $9,450,000    │
```

### **Example 2: By Industry Vertical**

```
Industry        │ FY26-Q2_Revenue │ FY26-Q3_Revenue │ FY26-Q4_Revenue │ Total_Revenue │ Margin %
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
Banking         │ $2,500,000      │ $3,000,000      │ $950,000        │ $6,450,000    │ 30.0%
Healthcare      │ $0              │ $1,800,000      │ $0              │ $1,800,000    │ 30.0%
Technology      │ $1,200,000      │ $0              │ $0              │ $1,200,000    │ 30.0%
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
TOTAL           │ $3,700,000      │ $4,800,000      │ $950,000        │ $9,450,000    │
```

### **Example 3: By Product Name**

```
Product         │ FY26-Q2_Revenue │ FY26-Q3_Revenue │ FY26-Q4_Revenue │ Total_Revenue │ Margin %
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
Platform Suite  │ $2,500,000      │ $0              │ $0              │ $2,500,000    │ 30.0%
Cloud Services  │ $1,200,000      │ $0              │ $0              │ $1,200,000    │ 30.0%
Consulting      │ $0              │ $3,000,000      │ $0              │ $3,000,000    │ 30.0%
AI Platform     │ $0              │ $1,800,000      │ $0              │ $1,800,000    │ 30.0%
Analytics       │ $0              │ $0              │ $950,000        │ $950,000      │ 30.0%
────────────────┼─────────────────┼─────────────────┼─────────────────┼───────────────┼──────────
TOTAL           │ $3,700,000      │ $4,800,000      │ $950,000        │ $9,450,000    │
```

---

## 📊 Summary Metrics

At the top of each report, you'll see summary metrics:

```
┌──────────────┬──────────────────┬──────────────────┬──────────────────┐
│ Accounts     │ Revenue TCV USD  │ IYR USD          │ Margin USD       │
│ 5            │ $9,450,000       │ $4,725,000       │ $2,835,000       │
└──────────────┴──────────────────┴──────────────────┴──────────────────┘
```

---

## ✨ Key Features

### **1. Automatic Column Detection**
- System detects which grouping dimensions are available
- Only shows options that exist in your data
- Works with any column names (normalized automatically)

### **2. Flexible Metric Selection**
- Choose one or multiple metrics
- Revenue TCV USD
- IYR USD (In-Year Revenue)
- Margin USD
- Margin % (auto-calculated when both revenue and margin selected)

### **3. Period-Based Reporting**
- Automatically groups by Master Period
- Shows each quarter as a separate column
- Calculates totals across all periods
- Editable cells for forecasting

### **4. Dynamic Calculations**
- Total columns calculated automatically
- Margin percentage calculated when applicable
- Supports editing and recalculation

### **5. Multi-Scenario Support**
- Each scenario maintains its own report
- Switch between scenarios instantly
- Compare different groupings per scenario

---

## 🎨 User Interface

### **Control Panel:**
```
┌─────────────────────────────────────────────────────────┐
│ 📊 Dynamic Reporting - Base Case                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📊 Group By:              💰 Metrics to Display:        │
│ ○ 🏢 By Account           ☑ Revenue TCV USD             │
│ ● 🏭 By Industry          ☑ IYR USD                     │
│ ○ 📦 By Product           ☑ Margin USD                  │
│                                                          │
├─────────────────────────────────────────────────────────┤
│ 📈 Summary Metrics:                                     │
│ [Industry Verticals: 4] [Revenue: $9.45M] [Margin: ...] │
├─────────────────────────────────────────────────────────┤
│ 📋 Detailed Report:                                     │
│ [Editable Data Grid]                                    │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Workflow

### **Step 1: Upload & Map Data**
```
Upload CSV → Map columns → Validate
```

### **Step 2: Choose Reporting View**
```
Select "Dynamic Reporting" (instead of Sales Pipeline)
```

### **Step 3: Configure Report**
```
Choose grouping: By Account / Industry / Product
Select metrics: Revenue, IYR, Margin
```

### **Step 4: View & Edit**
```
See report grouped by periods
Edit forecasts inline
View summary metrics
```

### **Step 5: Compare Scenarios**
```
Create new scenario
Change grouping or metrics
Compare side-by-side
```

---

## 💡 Use Cases

### **Use Case 1: Account Planning**
- **Group By:** Account
- **Metrics:** Revenue TCV USD, Margin USD
- **Purpose:** See revenue and margin by customer

### **Use Case 2: Industry Analysis**
- **Group By:** Industry Vertical
- **Metrics:** Revenue TCV USD, IYR USD
- **Purpose:** Understand which industries drive revenue

### **Use Case 3: Product Performance**
- **Group By:** Product Name
- **Metrics:** Revenue TCV USD, Margin USD, Margin %
- **Purpose:** Analyze product profitability

### **Use Case 4: Quarterly Forecasting**
- **Group By:** Any dimension
- **Metrics:** All metrics
- **Purpose:** See quarterly breakdown and forecast future periods

---

## 🎯 Benefits

### **vs Fixed P&L Structure:**

**Before (Fixed):**
- ❌ Hardcoded line items (Services Revenue, Product COGS, etc.)
- ❌ Doesn't match your data structure
- ❌ Can't group by your dimensions
- ❌ Limited flexibility

**After (Dynamic):**
- ✅ Uses YOUR actual data columns
- ✅ Group by Account, Industry, or Product
- ✅ Select which metrics to show
- ✅ Automatically aggregates by period
- ✅ Fully flexible and editable

---

## 🔧 Technical Details

### **Column Name Normalization:**
```python
# Automatically handles different naming conventions
"Account Name" → account_name
"Revenue TCV USD" → revenue_tcv_usd
"Industry Vertical" → industry_vertical
```

### **Automatic Aggregation:**
```python
# Groups by dimension + period, sums metrics
df.groupby(['account_name', 'master_period']).agg({
    'revenue_tcv_usd': 'sum',
    'margin_usd': 'sum'
})
```

### **Pivot to Periods:**
```python
# Transforms to period columns
FY26-Q2_revenue_tcv_usd, FY26-Q3_revenue_tcv_usd, ...
```

---

## 📥 Export Capability

Export your dynamic report to Excel with:
- Formatted currency columns
- Percentage formatting
- Multiple sheets (one per metric)
- Professional styling

---

**Refresh your browser to see the new Dynamic Reporting view!** 🚀
