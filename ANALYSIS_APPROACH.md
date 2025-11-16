# 📊 Data Analysis Approach

## 🎯 Current Situation

### **Data Structure:**
- **TCV USD**: Total Contract Value (currently showing $0 - needs fixing)
- **IYR USD**: In-Year Revenue (showing $5.9B ✓)
- **Margin USD**: Profit margin
- **Monthly Forecast Columns** (BR onwards): 2025-04, 2025-05, etc. - revenue phasing

### **Issue:**
TCV USD is showing $0 but IYR USD shows $5.9B, indicating a data mapping or quality issue.

---

## 🔍 New Tool: Data Diagnostic View

### **Access:**
```
Select View:
○ 📊 Dynamic Reporting
○ 📈 Forecast Trend
● 🔍 Data Diagnostic  ← NEW!
○ 💼 Sales Pipeline
```

### **What It Does:**
1. **Column Detection** - Finds TCV, IYR, Margin, Close Date columns
2. **Data Quality Metrics** - Missing values, duplicates, data types
3. **Column Analysis** - Statistics for each key column
4. **Forecast Analysis** - Analyzes monthly forecast columns
5. **Relationship Validation** - Checks IYR ≤ TCV, Forecast ≈ TCV
6. **Sample Data** - Preview rows and column details

---

## 📋 Analysis Framework

### **Phase 1: Data Quality (Immediate)**
```
✓ Run Data Diagnostic view
✓ Identify TCV USD column issue
✓ Fix column mapping or data type
✓ Validate all numeric columns
✓ Check for missing values
```

### **Phase 2: Descriptive Analysis**
```
✓ Calculate summary statistics
✓ Total TCV, IYR, Forecast
✓ Top accounts/industries/products
✓ Revenue mix analysis
✓ Distribution charts
```

### **Phase 3: Temporal Analysis**
```
✓ Aggregate monthly to quarterly
✓ Calculate growth rates
✓ Identify trends and seasonality
✓ Create trend visualizations
```

### **Phase 4: Segmentation Analysis**
```
✓ Group by account/industry/product/stage
✓ Compare segments
✓ Identify patterns
✓ Calculate segment metrics
```

### **Phase 5: Forecasting Prep**
```
✓ Validate historical accuracy
✓ Identify forecast drivers
✓ Define scenarios (Base, Optimistic, Conservative)
✓ Set assumptions
✓ Build forecast models
```

---

## 🎯 Key Metrics to Track

### **1. Contract Metrics**
- **Total TCV**: Sum of all contract values
- **Total IYR**: Revenue recognized this year
- **Backlog**: TCV - IYR (remaining revenue)
- **Recognition %**: IYR / TCV * 100

### **2. Phasing Metrics**
- **Quarterly Forecast**: Sum monthly by fiscal quarter
- **Revenue Velocity**: Revenue per quarter
- **Burn Rate**: IYR / months elapsed
- **Forecast Total**: Sum of all monthly forecasts

### **3. Validation Metrics**
- **IYR ≤ TCV**: Check for each deal
- **Forecast ≈ TCV**: Within ±10%
- **No Negatives**: All values ≥ 0
- **Completeness**: % of deals with all data

---

## 📊 Recommended Views

### **View 1: Executive Dashboard**
```
Metrics:
- Total TCV
- Total IYR
- Backlog (TCV - IYR)
- Next 12 months forecast
- Top 5 accounts
- Top 3 industries

Charts:
- KPI cards
- Quarterly trend line
- Industry pie chart
```

### **View 2: Revenue Phasing**
```
Metrics:
- TCV by quarter
- IYR vs Forecast
- Quarterly growth rate
- Cumulative revenue

Charts:
- Waterfall (TCV → IYR → Future)
- Line chart (quarterly trend)
- Stacked bar (by segment)
```

### **View 3: Forecast Trend** (Already Built)
```
Metrics:
- Monthly forecasts aggregated to quarters
- Total TCV vs Total Forecast
- Forecast by account/industry/product

Output:
- Quarterly columns (FY26-Q1, Q2, Q3, Q4)
- Millions formatting
- CSV export
```

### **View 4: Data Diagnostic** (Already Built)
```
Analysis:
- Column detection
- Data quality metrics
- Relationship validation
- Sample data preview

Purpose:
- Identify data issues
- Validate mappings
- Check completeness
```

---

## 🔮 Forecasting Scenarios

### **Scenario 1: Base Case**
```
Assumptions:
- Historical recognition rate continues
- No new deals
- Current phasing holds

Output:
- Quarterly revenue forecast
- Annual projection
- Confidence intervals
```

### **Scenario 2: Optimistic**
```
Assumptions:
- 10% faster recognition
- 20% new deal growth
- 5% larger deal sizes

Output:
- Upside potential
- Growth trajectory
- Resource needs
```

### **Scenario 3: Conservative**
```
Assumptions:
- 10% slower recognition
- 10% deal attrition
- 5% smaller deals

Output:
- Downside risk
- Mitigation strategies
- Contingency plans
```

### **Scenario 4: What-If**
```
Variables:
- Win rate by stage
- Deal size by industry
- Recognition rate by product
- Seasonality factors

Output:
- Sensitivity analysis
- Driver impact
- Optimization opportunities
```

---

## 🚀 Immediate Next Steps

### **Step 1: Run Data Diagnostic** (Now)
```
1. Go to Forecasting & Reporting page
2. Select "🔍 Data Diagnostic" view
3. Review all sections
4. Identify TCV USD issue
5. Document findings
```

### **Step 2: Fix TCV USD** (Today)
```
1. Check column mapping
2. Verify source column selected
3. Check data type (string vs number)
4. Click "🔧 Fix" if needed
5. Re-validate data
```

### **Step 3: Validate Relationships** (Today)
```
1. Check IYR ≤ TCV for all deals
2. Verify Forecast ≈ TCV (±10%)
3. Ensure no negative values
4. Document any anomalies
```

### **Step 4: Build Analysis Views** (This Week)
```
1. Executive Dashboard
2. Revenue Phasing Analysis
3. Segment Comparison
4. Trend Visualizations
```

### **Step 5: Forecasting Setup** (Next Week)
```
1. Define scenarios
2. Set assumptions
3. Build forecast models
4. Create what-if analysis
```

---

## 💡 Key Questions to Answer

### **Business Questions:**

1. **What is our total contracted revenue?**
   - TCV USD (need to fix)
   - Currently showing $0

2. **How much have we recognized this year?**
   - IYR USD: $5,924,484,838 ✓
   - Need TCV to calculate %

3. **What is our backlog?**
   - Backlog = TCV - IYR
   - Need TCV to calculate

4. **When will we recognize remaining revenue?**
   - Use monthly forecast columns
   - Aggregate to fiscal quarters
   - Show phasing trend

5. **Which accounts/industries drive the most revenue?**
   - Group by dimension
   - Calculate TCV, IYR, Forecast
   - Rank and compare

---

## 📋 Data Quality Checklist

Use Data Diagnostic view to check:

- [ ] TCV USD column found and mapped
- [ ] TCV USD has non-zero values
- [ ] TCV USD is numeric (not text)
- [ ] IYR USD ≤ TCV USD for all deals
- [ ] Monthly forecast columns detected
- [ ] Forecast columns are numeric
- [ ] Sum of forecasts ≈ TCV (±10%)
- [ ] No negative values
- [ ] Close Date column exists
- [ ] Account Name column exists
- [ ] No excessive missing values
- [ ] No duplicate rows

---

## 🎨 Visualization Roadmap

### **Week 1:**
- Executive Dashboard KPIs
- Quarterly trend line chart
- Industry/Product pie charts

### **Week 2:**
- Revenue waterfall chart
- Forecast accuracy chart
- Segment comparison bars

### **Week 3:**
- Phasing heatmap
- Cohort analysis
- Deal velocity funnel

### **Week 4:**
- Scenario comparison
- What-if sensitivity
- Forecast confidence bands

---

**Start with Data Diagnostic view to identify and fix the TCV USD issue!** 🎯
