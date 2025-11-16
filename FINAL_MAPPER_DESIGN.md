# ✅ Final Column Mapper Design

## 🎯 Interface Layout

### **10 Target Fields → Dropdown to Select Source Column**

```
Target Field              ←    Source Column Dropdown       Confidence
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🏢 Account Name ⭐        ←    [Account Name ▼]            ✓ High
Optional

🔑 Opportunity ID         ←    [Opportunity ID ▼]          ✓ High
Optional

📋 Opportunity Name       ←    [Opportunity Name ▼]        ✓ High
Optional

📅 Master Period ⭐       ←    [Master Period ▼]           ✓ High
Required

📆 Close Date             ←    [Close Date ▼]              ✓ High
Optional

🏭 Industry Vertical      ←    [Industry Vertical ▼]       ✓ High
Optional

📦 Product Name           ←    [Product Name ▼]            ✓ High
Optional

💰 Revenue TCV USD ⭐     ←    [Revenue TCV USD ▼]         ✓ High
Required

💵 IYR USD                ←    [IYR USD ▼]                 ✓ High
Optional

📊 Margin USD             ←    [Margin USD ▼]              ✓ High
Optional
```

---

## 🔄 How It Works

### **1. Auto-Detection**
- System analyzes uploaded columns
- Suggests best match for each target field
- Shows confidence level (High/Medium/Low)

### **2. User Confirmation**
- Review each suggested mapping
- Change dropdown if suggestion is wrong
- Select "(None)" to skip optional fields

### **3. Validation**
- Required fields must be mapped (⭐)
- Optional fields can be "(None)"
- Preview shows mapped data

---

## 📋 Dropdown Options

Each target field dropdown contains:
- **(None)** - Skip this field
- **All source columns** from uploaded file

Example:
```
📅 Master Period ⭐ ← [Dropdown Options]
                      • (None)
                      • Account Name
                      • Opportunity ID
                      • Master Period      ← Auto-selected
                      • Close Date
                      • Industry Vertical
                      • Product Name
                      • Revenue TCV USD
                      • IYR USD
                      • Margin USD
```

---

## ✅ Confidence Indicators

**✓ High** (Green) - 90%+ match confidence  
**~ Medium** (Yellow) - 70-89% match confidence  
**? Low** (Blue) - <70% match confidence  
**Manual** (Blue) - User manually selected  
**-** (Gray) - Not mapped

---

## 🎯 Required vs Optional

**Required (⭐):**
- 📅 Master Period
- 💰 Revenue TCV USD

**Optional:**
- All other 8 fields

**Validation:**
- Cannot proceed without required fields
- Optional fields can be "(None)"

---

## 💡 User Experience

**Step 1:** Upload file  
**Step 2:** Review 10 auto-suggested mappings  
**Step 3:** Confirm or adjust each mapping  
**Step 4:** Validate & Continue  

**Benefits:**
- ✅ Fixed list of 10 target fields
- ✅ Auto-suggestions save time
- ✅ Full control to adjust
- ✅ Clear required vs optional
- ✅ Confidence indicators help decision

---

**Refresh your browser to see the new interface!** 🚀
