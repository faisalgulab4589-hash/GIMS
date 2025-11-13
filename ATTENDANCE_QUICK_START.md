# Attendance Module - Quick Start Guide

## 🚀 Getting Started

### Access Points:
- **Daily Attendance**: Click "Attendance" in sidebar → `/attendance`
- **Reports**: Click "Attendance Reports" in sidebar → `/attendance_reports`

---

## 📋 Daily Attendance (Mark Attendance)

### Step-by-Step:
1. **Select Date** → Defaults to today
2. **Apply Filters** (Optional):
   - Search by Name/Admission No/Father Name
   - Filter by Technology
   - Filter by Semester
   - Filter by Board
3. **Click "Load Students"** → Students appear with Present status
4. **Mark Attendance**:
   - Click **Present** (Green) - Already selected by default
   - Click **Absent** (Red) - For absent students
   - Click **Late** (Yellow) - For late students
   - Click **Leave** (Blue) - For on leave students
5. **Save Options**:
   - **Save All Attendance** → Saves all marked records
   - **Mark All Present** → Quick set all to Present
   - **Clear All** → Reset all selections

### Bulk Upload:
1. Prepare Excel file with columns: `admission_no`, `date`, `status`, `notes`
2. Click "Upload" button
3. Select file
4. System shows success/error count

---

## 📊 Attendance Reports

### Daily Report:
**Purpose**: See who was present/absent on a specific date

**Steps**:
1. Select Date
2. Apply filters (optional)
3. Click "Generate Report"
4. View attendance status for each student
5. Export to PDF if needed

**Output**: Student list with attendance status

---

### Monthly Report:
**Purpose**: Analyze attendance patterns with percentages

**Steps**:
1. Select Month (e.g., 2024-01)
2. Apply filters (optional)
3. Click "Generate Report"
4. View attendance breakdown:
   - Present/Absent/Late/Leave counts
   - Total days
   - **Attendance Percentage**
5. Check ⚠️ **Low Attendance Section** (< 70%)
6. Export to PDF or Excel

**Output**: 
- Complete attendance table
- Low attendance students highlighted
- Percentage calculations

---

## 🎯 Key Features

### ✅ Smart Defaults
- All students default to "Present"
- Only mark exceptions (Absent/Late/Leave)
- Saves time for large groups

### ✅ Quick Actions
- **Mark All Present**: One click to set all students
- **Save All**: Save entire class at once
- **Clear All**: Reset if needed

### ✅ Bulk Operations
- Upload multiple records from Excel
- Automatic validation
- Error reporting

### ✅ Advanced Filtering
- By Name/Admission No/Father Name
- By Technology
- By Semester
- By Board
- Combine multiple filters

### ✅ Comprehensive Reports
- Daily attendance view
- Monthly attendance analysis
- Attendance percentage calculation
- Low attendance alerts (< 70%)
- Export to PDF & Excel

---

## 📈 Attendance Percentage Calculation

**Formula**: (Present Days / Total Days) × 100

**Example**:
- Present: 18 days
- Total: 20 days
- Percentage: (18/20) × 100 = **90%** ✅

**Low Attendance Alert**:
- If percentage < 70% → Highlighted in yellow
- Separate section in monthly report
- Helps identify at-risk students

---

## 📁 Excel Upload Format

### Required Columns:
```
admission_no | date       | status  | notes
1001         | 2024-01-15 | Present | 
1002         | 2024-01-15 | Absent  | 
1003         | 2024-01-15 | Late    | Traffic
1004         | 2024-01-15 | Leave   | Medical
```

### Valid Status Values:
- `Present`
- `Absent`
- `Late`
- `Leave`

### Date Format:
- Must be: `YYYY-MM-DD`
- Example: `2024-01-15`

---

## 🎨 Status Colors

| Status | Color | Meaning |
|--------|-------|---------|
| Present | 🟢 Green | Student attended |
| Absent | 🔴 Red | Student did not attend |
| Late | 🟡 Yellow | Student arrived late |
| Leave | 🔵 Blue | Student on approved leave |

---

## ⚡ Pro Tips

1. **Mark Attendance Daily**: Don't wait until month-end
2. **Use Filters**: Filter by technology to mark specific groups
3. **Bulk Upload**: For large batches, use Excel upload
4. **Check Reports**: Review monthly reports to identify patterns
5. **Export Reports**: Keep PDF copies for records
6. **Monitor Low Attendance**: Act on students below 70%

---

## ❓ Common Questions

**Q: Can I edit attendance after saving?**
A: Yes, just load the same date and update the status

**Q: What if a student is not in the list?**
A: Only Active students appear. Check student status in database

**Q: Can I upload past attendance?**
A: Yes, specify the date in Excel file

**Q: How is low attendance calculated?**
A: Present days ÷ Total days × 100. Below 70% is flagged

**Q: Can I export reports?**
A: Yes, both PDF and Excel formats available

---

## 🔗 Quick Links

- Daily Attendance: `http://localhost:8080/attendance`
- Reports: `http://localhost:8080/attendance_reports`
- API Docs: See ATTENDANCE_MODULE_GUIDE.md

---

**Version**: 1.0  
**Last Updated**: 2024

