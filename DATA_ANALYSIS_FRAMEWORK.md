# 📊 Data Analysis Framework

## 🎯 Data Structure Understanding

Based on your description, here's the data structure:

### **Column Types:**

1. **Total Contract Value (TCV USD)**
   - Total value of the contract
   - Single number per deal
   - Example: $10,000,000

2. **In-Year Revenue (IYR USD)**
   - Amount actually spent/recognized in the current year
   - Single number per deal
   - Example: $2,500,000

3. **Monthly Forecast Columns (BR onwards)**
   - Format: 2025-04, 2025-05, 2025-06, etc.
   - Shows expected quarterly/monthly revenue phasing
   - Multiple columns showing the trend
   - Example: Apr: $500k, May: $600k, Jun: $700k

4. **Margin USD**
   - Profit margin on the deal
   - Single number per deal

---

## 🔍 Current Issue: TCV USD Shows $0

### **Possible Causes:**

1. **Column Name Mismatch**
   ```
   Your file might have: "TCV USD" or "Tcv Usd" or "tcv usd"
   System expects: Exact match to mapped column
   ```

2. **Empty Values**
   ```
   Column exists but all values are empty/null
   ```

3. **Data Type Issue**
   ```
   Values are text instead of numbers
   Example: "10000000" (string) not 10000000 (number)
   ```

4. **Column Not Mapped**
   ```
   TCV USD column not mapped to "Revenue TCV USD" target field
   ```

---

## 📊 Data Analysis Before Forecasting

### **Phase 1: Data Quality Analysis**

#### **1.1 Completeness Check**
```
Questions to Answer:
- How many deals have TCV USD values?
- How many deals have IYR USD values?
- How many deals have monthly forecast data?
- What % of deals are complete vs. incomplete?

Metrics:
- Total Deals: 5000
- Deals with TCV: ? (currently 0)
- Deals with IYR: 5000 (showing $5.9B)
- Deals with Forecast: ?
```

#### **1.2 Consistency Check**
```
Validation Rules:
- Sum of monthly forecasts ≤ TCV USD
- IYR USD ≤ TCV USD
- IYR USD ≤ Sum of current year monthly forecasts
- No negative values
- Dates are sequential

Example:
TCV USD: $10.0M
IYR USD: $2.5M ✓ (25% of TCV)
Monthly Sum: $10.0M ✓ (equals TCV)
```

#### **1.3 Temporal Analysis**
```
Questions:
- What is the date range of forecasts?
- Are there gaps in monthly data?
- How far into the future do forecasts go?
- Are there historical months included?

Example:
Earliest: 2025-04
Latest: 2027-12
Duration: 33 months
Gaps: None
```

---

## 📈 Key Metrics to Calculate

### **1. Revenue Recognition Metrics**

#### **A. Total Contract Value (TCV)**
```
Definition: Total value of all contracts
Calculation: Sum of TCV USD column
Current Status: $0 (needs fixing)
Expected: Should match or exceed IYR + future forecasts
```

#### **B. In-Year Revenue (IYR)**
```
Definition: Revenue recognized in current fiscal year
Calculation: Sum of IYR USD column
Current Status: $5,924,484,838 ✓
Percentage of TCV: ? (need TCV to calculate)
```

#### **C. Forecast Revenue by Period**
```
Definition: Expected revenue by quarter/year
Calculation: Sum monthly columns by fiscal quarter
Quarters: FY26-Q1, Q2, Q3, Q4, FY27-Q1, etc.
```

#### **D. Remaining Contract Value (RCV)**
```
Definition: TCV minus revenue already recognized
Calculation: TCV USD - IYR USD
Purpose: Shows future revenue potential
```

---

### **2. Phasing Analysis Metrics**

#### **A. Revenue Velocity**
```
Definition: How quickly revenue is being recognized
Calculation: Revenue per quarter / Total quarters
Purpose: Identify acceleration or deceleration
```

#### **B. Backlog**
```
Definition: Contracted but not yet recognized revenue
Calculation: TCV - IYR
Purpose: Future revenue pipeline
```

#### **C. Burn Rate**
```
Definition: Rate of revenue recognition
Calculation: IYR / Number of months elapsed
Purpose: Project future recognition
```

---

### **3. Segmentation Analysis**

#### **By Account**
```
Metrics:
- TCV per account
- IYR per account
- Forecast trend per account
- Top 10 accounts by TCV
- Top 10 accounts by IYR
```

#### **By Industry**
```
Metrics:
- TCV by industry vertical
- IYR by industry vertical
- Industry growth trends
- Industry concentration risk
```

#### **By Product**
```
Metrics:
- TCV by product
- IYR by product
- Product mix analysis
- Product revenue timing
```

#### **By Sales Stage**
```
Metrics:
- TCV by stage
- IYR by stage
- Conversion probability
- Stage velocity
```

---

## 🎯 Analysis Views to Build

### **View 1: Executive Dashboard**
```
Purpose: High-level overview
Metrics:
- Total TCV
- Total IYR
- Total Forecast (next 12 months)
- Backlog (TCV - IYR)
- Top 5 accounts
- Top 3 industries
- Revenue trend chart

Visualization:
- KPI cards
- Bar chart (quarterly trend)
- Pie chart (industry mix)
```

### **View 2: Revenue Phasing Analysis**
```
Purpose: Understand revenue timing
Metrics:
- TCV by quarter
- IYR vs. Forecast
- Quarterly growth rate
- Cumulative revenue curve

Visualization:
- Waterfall chart (TCV → IYR → Future)
- Line chart (quarterly trend)
- Stacked bar (by dimension)
```

### **View 3: Deal-Level Analysis**
```
Purpose: Drill into individual deals
Metrics:
- Deal size distribution
- Revenue recognition %
- Time to full recognition
- Deal velocity

Visualization:
- Scatter plot (TCV vs. IYR)
- Histogram (deal size)
- Table (top deals)
```

### **View 4: Cohort Analysis**
```
Purpose: Compare groups over time
Metrics:
- Cohort by close date
- Cohort by industry
- Cohort by product
- Retention/expansion

Visualization:
- Cohort table
- Heatmap
- Line chart (cohort trends)
```

### **View 5: Forecast Accuracy**
```
Purpose: Validate forecast reliability
Metrics:
- Forecast vs. Actual (historical)
- Variance analysis
- Forecast bias
- Confidence intervals

Visualization:
- Variance chart
- Accuracy trend
- Error distribution
```

---

## 🔧 Immediate Actions

### **Action 1: Fix TCV USD Column**
```
Steps:
1. Go to Upload & Map page
2. Check column mapping for TCV USD
3. Verify source column is selected
4. Check data preview - are values present?
5. If values are strings, click "🔧 Fix" on validation page
6. Re-run validation
```

### **Action 2: Verify Data Completeness**
```
Create a data quality report:
- Count of deals with TCV
- Count of deals with IYR
- Count of deals with forecast data
- Identify incomplete records
```

### **Action 3: Validate Relationships**
```
Check logical relationships:
- IYR ≤ TCV (for each deal)
- Sum(Monthly Forecast) ≈ TCV
- No negative values
- Dates are valid
```

---

## 📊 Recommended Analysis Sequence

### **Step 1: Data Quality (Week 1)**
```
✓ Fix TCV USD column mapping
✓ Validate all numeric columns
✓ Check for missing values
✓ Verify data types
✓ Identify outliers
```

### **Step 2: Descriptive Analysis (Week 1-2)**
```
✓ Calculate summary statistics
✓ Create distribution charts
✓ Identify top accounts/industries
✓ Analyze revenue mix
✓ Document findings
```

### **Step 3: Temporal Analysis (Week 2)**
```
✓ Aggregate monthly to quarterly
✓ Calculate growth rates
✓ Identify trends
✓ Spot seasonality
✓ Create trend visualizations
```

### **Step 4: Segmentation Analysis (Week 2-3)**
```
✓ Group by account/industry/product
✓ Compare segments
✓ Identify patterns
✓ Calculate segment metrics
✓ Create comparison reports
```

### **Step 5: Forecasting Prep (Week 3)**
```
✓ Validate historical accuracy
✓ Identify forecast drivers
✓ Define scenarios
✓ Set assumptions
✓ Build forecast models
```

---

## 🎯 Key Questions to Answer

### **Business Questions:**

1. **Revenue Recognition**
   - What is our total contracted revenue (TCV)?
   - How much have we recognized this year (IYR)?
   - What is our backlog (TCV - IYR)?

2. **Revenue Timing**
   - When will we recognize the remaining revenue?
   - What is our quarterly revenue forecast?
   - Are we accelerating or decelerating?

3. **Customer Concentration**
   - Who are our top 10 customers by TCV?
   - What % of revenue comes from top 10?
   - Are we too concentrated?

4. **Industry Mix**
   - Which industries drive the most revenue?
   - Which industries are growing fastest?
   - Where should we focus sales efforts?

5. **Product Performance**
   - Which products have highest TCV?
   - Which products have fastest recognition?
   - What is our product mix trend?

6. **Sales Pipeline**
   - What is the TCV by sales stage?
   - What is the conversion rate by stage?
   - How long does it take to close deals?

---

## 🔮 Forecasting Scenarios to Build

### **Scenario 1: Base Case**
```
Assumptions:
- Historical recognition rate continues
- No new deals added
- No deal delays or accelerations
- Current phasing holds

Output:
- Quarterly revenue forecast
- Annual revenue projection
- Confidence intervals
```

### **Scenario 2: Optimistic Case**
```
Assumptions:
- 10% faster recognition rate
- 20% new deal growth
- 5% deal size increase
- Earlier close dates

Output:
- Upside revenue potential
- Growth trajectory
- Resource requirements
```

### **Scenario 3: Conservative Case**
```
Assumptions:
- 10% slower recognition rate
- 10% deal attrition
- 5% deal size decrease
- Delayed close dates

Output:
- Downside risk assessment
- Mitigation strategies
- Contingency planning
```

### **Scenario 4: What-If Analysis**
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

## 📋 Data Structure Recommendations

### **Current Structure:**
```
Columns:
- Account Name
- Opportunity ID
- TCV USD (total contract value)
- IYR USD (in-year revenue)
- Margin USD
- Close Date
- Industry Vertical
- Product Name
- Sales Stage
- 2025-04, 2025-05, 2025-06, ... (monthly forecasts)
```

### **Recommended Additions:**
```
Calculated Fields:
- Remaining Contract Value (RCV = TCV - IYR)
- Recognition % (IYR / TCV * 100)
- Forecast Total (sum of monthly columns)
- Variance (Forecast Total - TCV)
- Fiscal Quarter (from Close Date)
- Deal Age (days since close)
- Recognition Rate (IYR / Deal Age)
```

---

## 🎨 Visualization Recommendations

### **Chart 1: Revenue Waterfall**
```
Shows: TCV → IYR → Remaining
Purpose: Understand revenue recognition status
Type: Waterfall chart
```

### **Chart 2: Quarterly Trend**
```
Shows: Revenue by quarter (historical + forecast)
Purpose: Identify growth trajectory
Type: Line + bar combo chart
```

### **Chart 3: Segment Comparison**
```
Shows: TCV/IYR by account/industry/product
Purpose: Compare segment performance
Type: Stacked bar chart
```

### **Chart 4: Phasing Heatmap**
```
Shows: Revenue intensity by month/account
Purpose: Identify concentration periods
Type: Heatmap
```

### **Chart 5: Forecast Accuracy**
```
Shows: Forecast vs. Actual over time
Purpose: Validate forecast reliability
Type: Line chart with confidence bands
```

---

## 🚀 Next Steps

### **Immediate (Today):**
1. Fix TCV USD column mapping issue
2. Verify data is loading correctly
3. Run data quality checks
4. Document current state

### **Short-term (This Week):**
1. Build Executive Dashboard view
2. Create Revenue Phasing Analysis
3. Implement segmentation reports
4. Validate all calculations

### **Medium-term (Next 2 Weeks):**
1. Build forecasting scenarios
2. Create what-if analysis tool
3. Implement visualization charts
4. Add export capabilities

### **Long-term (Next Month):**
1. Historical accuracy tracking
2. Automated forecast updates
3. Alert system for variances
4. Integration with other systems

---

**Let's start by fixing the TCV USD issue, then we can build out the analysis framework!** 🎯
