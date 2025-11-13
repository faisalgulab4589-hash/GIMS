# Attendance Module - Complete Guide

## Overview
A comprehensive attendance management system with daily marking, bulk upload, and detailed reporting features.

---

## 1. DAILY ATTENDANCE PAGE (`/attendance`)

### Features:
✅ **Real-time Student Loading**
- Filter by: Name, Admission No, Father Name, Technology, Semester, Board
- Date selection for marking attendance
- Automatic loading of students for selected date

✅ **Quick Attendance Marking**
- 4 Status Options: **Present**, **Absent**, **Late**, **Leave**
- Color-coded buttons for easy identification
- One-click status change with visual feedback

✅ **Smart Defaults**
- All students default to "Present"
- Only need to mark Absent/Late/Leave students
- Remaining students automatically stay Present

✅ **Bulk Operations**
- **Mark All Present**: Quickly set all students to Present
- **Save All Attendance**: Save all marked attendance at once
- **Clear All**: Reset all selections

✅ **Bulk Upload Feature**
- Upload Excel file with columns: `admission_no`, `date`, `status`, `notes`
- Automatic validation and error reporting
- Shows success/error count

### How to Use:
1. Navigate to **Attendance** from sidebar
2. Select date (defaults to today)
3. Apply filters if needed (Technology, Semester, Board)
4. Click "Load Students"
5. Mark attendance for each student
6. Click "Save All Attendance" to save

---

## 2. ATTENDANCE REPORTS (`/attendance_reports`)

### Daily Attendance Report
**Purpose**: View attendance for a specific date

**Filters Available**:
- Date selection
- Technology
- Semester
- Board

**Output**:
- Student list with attendance status
- Color-coded status badges
- Total student count
- Export to PDF

### Monthly Attendance Report
**Purpose**: Comprehensive monthly analysis with percentages

**Filters Available**:
- Month selection
- Technology
- Semester
- Board

**Output**:
- All students with attendance breakdown:
  - Present count
  - Absent count
  - Late count
  - Leave count
  - Total days
  - **Attendance Percentage**

**Special Feature - Low Attendance Alert**:
- ⚠️ Separate section for students with **< 70% attendance**
- Highlighted in yellow for easy identification
- Shows: Admission No, Name, Present Days, Total Days, Percentage
- Helps identify at-risk students

**Export Options**:
- **PDF**: Professional formatted report with warning section
- **Excel**: Spreadsheet format for further analysis

---

## 3. DATABASE SCHEMA

### Attendance Table
```sql
CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,  -- 'Present', 'Absent', 'Late', 'Leave'
    notes TEXT,
    created_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, attendance_date)
)
```

---

## 4. API ENDPOINTS

### Attendance Management
- `GET /api/attendance/students` - Get students for attendance marking
- `POST /api/attendance/save` - Save single student attendance
- `POST /api/attendance/save_all` - Save all attendance records
- `POST /api/attendance/bulk_upload` - Bulk upload from Excel

### Reports
- `GET /api/attendance/daily_report` - Get daily attendance data
- `GET /api/attendance/monthly_report` - Get monthly attendance with percentages
- `GET /api/attendance/daily_report/export_pdf` - Export daily report to PDF
- `GET /api/attendance/monthly_report/export_pdf` - Export monthly report to PDF
- `GET /api/attendance/monthly_report/export_excel` - Export monthly report to Excel

---

## 5. EXCEL UPLOAD FORMAT

### Required Columns:
| Column | Format | Example |
|--------|--------|---------|
| admission_no | Text | 1001 |
| date | YYYY-MM-DD | 2024-01-15 |
| status | Text | Present/Absent/Late/Leave |
| notes | Text (Optional) | Medical leave |

### Sample File:
```
admission_no,date,status,notes
1001,2024-01-15,Present,
1002,2024-01-15,Absent,
1003,2024-01-15,Late,Traffic
1004,2024-01-15,Leave,Medical
```

---

## 6. KEY FEATURES SUMMARY

| Feature | Daily Page | Reports |
|---------|-----------|---------|
| Mark Attendance | ✅ | ❌ |
| View History | ❌ | ✅ |
| Bulk Upload | ✅ | ❌ |
| Filter by Tech | ✅ | ✅ |
| Filter by Semester | ✅ | ✅ |
| Filter by Board | ✅ | ✅ |
| Export PDF | ❌ | ✅ |
| Export Excel | ❌ | ✅ |
| Low Attendance Alert | ❌ | ✅ (Monthly) |
| Percentage Calculation | ❌ | ✅ |

---

## 7. WORKFLOW EXAMPLE

### Scenario: Mark Daily Attendance
1. Open `/attendance`
2. Date auto-fills with today
3. Select Technology: "BS Nursing"
4. Click "Load Students"
5. Students appear with Present status
6. Click "Absent" for absent students
7. Click "Late" for late students
8. Click "Save All Attendance"
9. Confirmation message appears

### Scenario: Generate Monthly Report
1. Open `/attendance_reports`
2. Click "Monthly Report" tab
3. Select Month: "2024-01"
4. Select Technology: "Dip-Anesthesia"
5. Click "Generate Report"
6. View all students with percentages
7. See low attendance students highlighted
8. Click "Export PDF" or "Export Excel"

---

## 8. NOTES

- Attendance records are unique per student per date (no duplicates)
- Default status is "Present" if not marked
- Low attendance threshold is **70%**
- All timestamps are stored in ISO format
- Bulk upload validates admission numbers against database
- Reports can be filtered by multiple criteria simultaneously

---

## 9. TROUBLESHOOTING

**Issue**: Students not loading
- **Solution**: Check date format (YYYY-MM-DD)
- **Solution**: Ensure students have status = 'Active'

**Issue**: Bulk upload fails
- **Solution**: Verify Excel column names match exactly
- **Solution**: Check admission numbers exist in database

**Issue**: Low attendance not showing
- **Solution**: Ensure attendance records exist for the month
- **Solution**: Check if percentage is actually below 70%

---

**Last Updated**: 2024
**Version**: 1.0

