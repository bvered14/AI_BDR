# 🎯 Multiple Airtable Tables Setup

## ✅ **New Feature: Multiple Table Support**

Your pipeline now supports **multiple Airtable tables**! Here's how to configure it:

## 🔧 **Configuration Options**

### **Option 1: Single Table (Current)**
```bash
# In your .env file
AIRTABLE_TABLE_NAME=Leads
AIRTABLE_TABLES=Leads
```

### **Option 2: Multiple Tables (New)**
```bash
# In your .env file
AIRTABLE_TABLE_NAME=Leads  # Default/primary table
AIRTABLE_TABLES=Leads,Companies,Contacts  # All tables (comma-separated)
```

## 📝 **How to Set Up Multiple Tables**

### **1. Update Your `.env` File**
```bash
# Add this line to your .env file:
AIRTABLE_TABLES=Leads,Companies,Contacts
```

### **2. Table Names**
- **Comma-separated**: `Leads,Companies,Contacts`
- **No spaces**: `Leads,Companies,Contacts` (not `Leads, Companies, Contacts`)
- **Case-sensitive**: Match exact table names in Airtable

### **3. Example Configurations**

#### **Basic Setup (3 tables)**
```bash
AIRTABLE_TABLES=Leads,Companies,Contacts
```

#### **Advanced Setup (5 tables)**
```bash
AIRTABLE_TABLES=Leads,Companies,Contacts,Deals,Activities
```

#### **Single Table (backward compatible)**
```bash
AIRTABLE_TABLES=Leads
```

## 🎯 **What This Enables**

### **✅ New Features**
- **Multi-table testing**: Tests connection to all configured tables
- **Table validation**: Ensures all tables exist before running
- **Flexible structure**: Easy to add/remove tables
- **Backward compatible**: Still works with single table

### **🔍 Testing Multiple Tables**
```bash
# Test all configured tables
python -c "from airtable_api import AirtableAPI; AirtableAPI().test_connection()"
```

**Output:**
```
🔍 Testing connection to 3 tables...
✅ Table 'Leads' connection successful
✅ Table 'Companies' connection successful
✅ Table 'Contacts' connection successful
✅ All Airtable tables accessible
```

## 📊 **Table Structure Recommendations**

### **Recommended 3-Table Setup**
1. **`Leads`** - Individual prospects and contacts
2. **`Companies`** - Company information and details
3. **`Contacts`** - Contact history and interactions

### **Advanced 5-Table Setup**
1. **`Leads`** - Prospects and contacts
2. **`Companies`** - Company information
3. **`Contacts`** - Contact history
4. **`Deals`** - Sales opportunities
5. **`Activities`** - Outreach activities and notes

## 🚀 **Quick Start**

### **1. Update Your `.env`**
```bash
# Add this line to your existing .env file:
AIRTABLE_TABLES=Leads,Companies,Contacts
```

### **2. Test Connection**
```bash
python -c "from airtable_api import AirtableAPI; AirtableAPI().test_connection()"
```

### **3. Run Pipeline**
```bash
python main.py --demo
```

## ✅ **Benefits**

- **Scalable**: Easy to add new tables
- **Organized**: Better data structure
- **Flexible**: Works with any table combination
- **Tested**: Validates all tables before running
- **Backward compatible**: Still works with single table

## 🎉 **Ready to Use!**

Your pipeline now supports multiple Airtable tables. Just add the `AIRTABLE_TABLES` line to your `.env` file and you're good to go!
