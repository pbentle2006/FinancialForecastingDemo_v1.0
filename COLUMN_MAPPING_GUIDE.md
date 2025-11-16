# 📋 Column Mapping Guide

## 🎯 Required Fields for CRM/Financial Data

The column mapper now focuses on 10 key CRM and financial fields:

---

## 📊 Field Definitions

### **1. 🏢 Account Name**
- **Description:** Customer or client company name
- **Keywords:** account name, account, customer, client, company
- **Required:** No
- **Example:** "Acme Corp", "Global Bank"

### **2. 🔑 Opportunity ID**
- **Description:** Unique identifier for the opportunity/deal
- **Keywords:** opportunity id, opp id, deal id, id, opportunity number
- **Required:** No
- **Example:** "OPP-001", "DEAL-12345"

### **3. 📋 Opportunity Name**
- **Description:** Name or description of the opportunity
- **Keywords:** opportunity name, opp name, deal name, opportunity
- **Required:** No
- **Example:** "Enterprise Platform Deal", "Cloud Migration"

### **4. 📅 Master Period** ⭐ REQUIRED
- **Description:** Fiscal period (quarter or month)
- **Keywords:** master period, period, fiscal period, reporting period, quarter
- **Required:** **YES**
- **Format:** FY26-Q2, Q2 FY2026, 2026-Q2
- **Example:** "FY26-Q2", "FY26-Q3"

### **5. 📆 Close Date**
- **Description:** Expected or actual close date
- **Keywords:** close date, closing date, expected close, date
- **Required:** No
- **Format:** YYYY-MM-DD, MM/DD/YYYY
- **Example:** "2025-12-15", "12/15/2025"

### **6. 🏭 Industry Vertical**
- **Description:** Industry sector or vertical
- **Keywords:** industry vertical, industry, vertical, sector, segment
- **Required:** No
- **Example:** "Banking", "Healthcare", "Technology"

### **7. 📦 Product Name**
- **Description:** Product or service being sold
- **Keywords:** product name, product, solution, service
- **Required:** No
- **Example:** "Platform Suite", "Cloud Services"

### **8. 💰 Revenue TCV USD** ⭐ REQUIRED
- **Description:** Total Contract Value in USD
- **Keywords:** revenue tcv usd, tcv, total contract value, revenue, tcv usd
- **Required:** **YES**
- **Format:** Numeric (dollars)
- **Example:** 2500000, 1200000

### **9. 💵 IYR USD**
- **Description:** In-Year Revenue (first year revenue) in USD
- **Keywords:** iyr usd, iyr, in year revenue, first year revenue
- **Required:** No
- **Format:** Numeric (dollars)
- **Example:** 1000000, 600000

### **10. 📊 Margin USD**
- **Description:** Gross margin in USD
- **Keywords:** margin usd, margin, gross margin, profit
- **Required:** No
- **Format:** Numeric (dollars)
- **Example:** 750000, 360000

---

## ✅ Required Fields Summary

**Must have:**
1. ✅ **Master Period** - For time-based analysis
2. ✅ **Revenue TCV USD** - Primary revenue metric

**Optional but recommended:**
- Account Name (for customer analysis)
- Opportunity ID (for tracking)
- Close Date (for forecasting)
- Industry Vertical (for segmentation)
- IYR USD (for first-year analysis)
- Margin USD (for profitability)

---

## 📝 Sample Data Structure

```csv
Account Name,Opportunity ID,Opportunity Name,Master Period,Close Date,Industry Vertical,Product Name,Revenue TCV USD,IYR USD,Margin USD
Acme Corp,OPP-001,Enterprise Platform Deal,FY26-Q2,2025-12-15,Banking,Platform Suite,2500000,1000000,750000
TechStart Inc,OPP-002,Cloud Migration,FY26-Q2,2025-11-30,Technology,Cloud Services,1200000,600000,360000
Global Bank,OPP-003,Digital Transform,FY26-Q3,2026-02-28,Banking,Consulting,3000000,1200000,900000
HealthCo,OPP-004,AI Solution,FY26-Q3,2026-01-15,Healthcare,AI Platform,1800000,900000,540000
Retail Giant,OPP-005,Data Analytics,FY26-Q4,2026-03-31,Retail,Analytics,950000,475000,285000
```

---

## 🔍 Auto-Detection

The column mapper will automatically detect your columns based on:

1. **Exact matches** (100% confidence)
   - Column name exactly matches keyword
   
2. **Starts with** (90% confidence)
   - Column name starts with keyword
   
3. **Contains** (70% confidence)
   - Column name contains keyword
   
4. **Ends with** (80% confidence)
   - Column name ends with keyword

---

## 💡 Mapping Tips

### **If your columns don't match:**
1. Use the dropdown to manually select the correct field
2. Save your mapping as a template for reuse
3. The system is flexible - partial matches work

### **Common column name variations:**
- **Master Period:** "Period", "Fiscal Quarter", "FQ", "Quarter"
- **Revenue TCV USD:** "TCV", "Total Value", "Contract Value", "Revenue"
- **IYR USD:** "First Year", "Year 1", "IYR", "Initial Revenue"
- **Margin USD:** "Gross Margin", "Profit", "GM", "Contribution Margin"
- **Industry Vertical:** "Industry", "Sector", "Vertical", "Segment"

### **Date formats supported:**
- ISO: 2025-12-15
- US: 12/15/2025
- Fiscal: FY26-Q2, Q2 FY2026
- Text: "December 2025", "Q2 2026"

---

## 🎯 Use Cases

### **Sales Pipeline Analysis**
Required: Master Period, Revenue TCV USD, Close Date
Optional: Opportunity Name, Account Name, Industry Vertical

### **Revenue Forecasting**
Required: Master Period, Revenue TCV USD
Optional: IYR USD, Product Name, Industry Vertical

### **Margin Analysis**
Required: Master Period, Revenue TCV USD, Margin USD
Optional: Product Name, Industry Vertical

### **Customer Segmentation**
Required: Master Period, Revenue TCV USD, Account Name
Optional: Industry Vertical, Product Name

---

## 🚀 Quick Start

1. **Upload your CRM export** (CSV or Excel)
2. **Review auto-detected mappings** (check confidence scores)
3. **Adjust any incorrect mappings** (use dropdowns)
4. **Save template** (for future uploads)
5. **Validate & Continue** (proceed to forecasting)

---

## ❓ FAQ

**Q: What if I don't have all 10 fields?**  
A: Only Master Period and Revenue TCV USD are required. Others are optional.

**Q: Can I map multiple columns to the same field?**  
A: No, each field can only be mapped once. Choose the most relevant column.

**Q: What if my revenue is in different currency?**  
A: Convert to USD before uploading, or note the currency for manual adjustment.

**Q: Can I skip the mapping step?**  
A: No, mapping ensures data is correctly interpreted for forecasting.

**Q: How do I save my mapping for next time?**  
A: Use the "Save Mapping Template" button after mapping columns.

---

**Ready to map your data! 🎯**
