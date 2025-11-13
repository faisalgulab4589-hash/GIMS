# Attendance Reports Testing Guide

## Quick Testing Steps:

### 1. Start the Server
```bash
python main.py
```

### 2. Login to Dashboard
- Navigate to `http://127.0.0.1:5000/login`
- Login with your credentials

### 3. Open Attendance Reports
- Click on "Attendance Reports" in the sidebar
- Or navigate directly to: `http://127.0.0.1:5000/attendance_reports`

### 4. Test Each Tab:

#### **Daily Report Tab:**
1. Select a date
2. Choose filters (Technology, Semester, Board, Campus) - Optional
3. Click "Generate Report"
4. Check if students appear
5. Try "Export PDF" button

#### **Monthly Report Tab:**
1. Select month (e.g., November 2025)
2. Choose filters (Campus, Board, Semester, Technology) - Optional
3. Enter Admission No. (optional)
4. Click "Generate Report"
5. Check if attendance percentages appear
6. Try "Export PDF" and "Export Excel" buttons
7. Click info button (i) to see daily attendance details

#### **Meeting Reports Tab:**
1. Select month
2. Click "Generate Report"
3. Check if student strength report appears by board and semester

### 5. Check Browser Console (F12)

Open Developer Tools (Press F12) and check the Console tab for:
- "Loading filter options..." - Should appear on page load
- "Technologies:", "Semesters:", "Boards:", "Campuses:" - Check if data is loaded
- Any error messages in red

## Common Issues & Solutions:

### Issue 1: Dropdowns are empty
**Solution:**
- Check browser console for errors
- Verify you're logged in
- Check if database has data in campuses, boards, semesters, technologies tables

### Issue 2: "No attendance records found"
**Possible Causes:**
- No attendance has been marked for that date/month
- Filters are too restrictive
- Try selecting "All" for all filters

### Issue 3: Export buttons don't work
**Solution:**
- Make sure you generated a report first
- Check if you're logged in
- Check browser console for errors

### Issue 4: Page shows "Content not found"
**Solution:**
- Clear browser cache (Ctrl + Shift + Delete)
- Hard refresh (Ctrl + Shift + R)
- Restart the server

## Debug Mode:

All console logs are now active. Check the console for:
1. Filter loading status
2. API response status codes
3. Data being fetched
4. Any JavaScript errors

## Expected Behavior:

✅ All dropdowns should populate automatically on page load
✅ Default dates should be set to today/current month
✅ Reports should generate when clicking "Generate Report"
✅ Export buttons should appear after generating a report
✅ Export buttons should download PDF/Excel files
✅ Monthly report should show attendance percentages
✅ Low attendance warning should appear if any student has <70%

## API Endpoints Being Used:

- `/api/technologies` - Get all technologies
- `/api/semesters` - Get all semesters
- `/api/boards` - Get all boards
- `/api/campuses` - Get all campuses
- `/api/attendance/daily_report` - Get daily attendance data
- `/api/attendance/monthly_report` - Get monthly attendance summary
- `/api/meeting_reports/monthly` - Get monthly student strength report
- `/api/attendance/daily_report/export_pdf` - Export daily report as PDF
- `/api/attendance/monthly_report/export_pdf` - Export monthly report as PDF
- `/api/attendance/monthly_report/export_excel` - Export monthly report as Excel
- `/api/attendance/monthly_detail_report` - Get student's daily attendance for a month

## Data Requirements:

For reports to work, you need:
1. Students in database with Active status
2. Attendance records marked in the attendance table
3. Technologies, Semesters, Boards, Campuses configured in database
4. User must be logged in

## Browser Console Commands:

To manually test API calls, open console and try:

```javascript
// Test filter loading
fetch('/api/technologies').then(r => r.json()).then(console.log);
fetch('/api/campuses').then(r => r.json()).then(console.log);

// Test report generation
fetch('/api/attendance/daily_report?date=2025-11-04').then(r => r.json()).then(console.log);
fetch('/api/attendance/monthly_report?month=2025-11').then(r => r.json()).then(console.log);
```

If these commands return errors, check:
- If you're logged in
- Server is running
- Database has data

