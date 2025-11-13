# 🧪 Testing Guide - Demoted Student Status

## Quick Test Checklist

### ✅ Desktop Application (Biodata.py)

#### Test 1: Create Student with Demoted Status
1. Open the desktop application
2. Click "Add New Student" or open Biodata form
3. Fill in student details
4. In **"Students Status"** dropdown, select **"Demoted"**
5. Click **"Save"**
6. ✅ Verify: Student is saved with "Demoted" status

#### Test 2: Edit Student to Demoted Status
1. Open existing student record
2. Change **"Students Status"** to **"Demoted"**
3. Click **"Save"**
4. ✅ Verify: Status is updated to "Demoted"

#### Test 3: View Demoted Students in List
1. Open Students List
2. Look for students with "Demoted" status
3. ✅ Verify: Demoted students are visible in the list

---

### ✅ Web Application (Flask)

#### Test 4: Add Demoted Status in Biodata Form
1. Go to **Dashboard → Biodata**
2. Fill in student details
3. In **"Student Status"** dropdown, select **"Demoted"**
4. Click **"Save"**
5. ✅ Verify: Student is saved with "Demoted" status

#### Test 5: Bulk Demotion Feature
1. Go to **Dashboard → Student Promotion**
2. You should see two sections:
   - 📈 **Promote Students** (top)
   - 📉 **Demote Students** (bottom)
3. In Demote section:
   - Select **Campus** (e.g., "Main Campus")
   - Select **Board** (e.g., "Federal")
   - Select **Current Semester** (e.g., "Semester 2")
4. Click **"Generate List"**
5. ✅ Verify: Students from that semester appear in table
6. Check students you want to demote
7. Select **"Demote to Semester"** (e.g., "Semester 1")
8. Click **"Demote Selected Students"**
9. Confirm the action
10. ✅ Verify: Success message appears
11. ✅ Verify: Students are marked as "Demoted"
12. ✅ Verify: Semester is updated to lower level

#### Test 6: Report Filter - Demoted Students
1. Go to **Dashboard → Reports**
2. Select **Report 1** (Free/Active/Left/Course Completed/Demoted)
3. In **"Student Status"** dropdown, select **"Demoted Students"**
4. Click **"Generate Report"**
5. ✅ Verify: Only demoted students appear in report
6. Click **"Export to Excel"** or **"Export to PDF"**
7. ✅ Verify: Export works correctly

#### Test 7: Report 2 - Demoted Students
1. Go to **Dashboard → Reports**
2. Select **Report 2** (Campus/Board/Technology)
3. In **"Student Status"** dropdown, select **"Demoted Students"**
4. Select Campus, Board, Technology filters
5. Click **"Generate Report"**
6. ✅ Verify: Demoted students matching filters appear

#### Test 8: Report 3 - All Students with Demoted Filter
1. Go to **Dashboard → Reports**
2. Select **Report 3** (All Students)
3. In **"Student Status"** dropdown, select **"Demoted Students"**
4. Click **"Generate Report"**
5. ✅ Verify: All demoted students appear
6. Export to Excel/PDF
7. ✅ Verify: Export includes demoted students

---

### ✅ Database Verification

#### Test 9: Check Database Status Column
```sql
SELECT admission_no, name, status, semester FROM students WHERE status = 'Demoted';
```
✅ Verify: Returns all demoted students with correct status

#### Test 10: Verify Semester Update on Demotion
```sql
SELECT admission_no, name, status, semester FROM students WHERE status = 'Demoted' LIMIT 5;
```
✅ Verify: Demoted students have lower semester than before

---

### ✅ Edge Cases

#### Test 11: Cannot Demote to Same Semester
1. In Demotion section, select same semester for "Current" and "Demote to"
2. Click "Demote Selected Students"
3. ✅ Verify: Error message: "Cannot demote to the same semester"

#### Test 12: No Students Selected
1. In Demotion section, don't check any students
2. Click "Demote Selected Students"
3. ✅ Verify: Error message: "Please select at least one student"

#### Test 13: Missing Required Fields
1. In Demotion section, leave Campus/Board/Semester empty
2. Click "Generate List"
3. ✅ Verify: Error message: "Please select Campus, Board, and Current Semester"

---

### ✅ Data Integrity

#### Test 14: Demoted Students Appear in All Reports
1. Create/demote a student
2. Go to each report type
3. Filter by "Demoted Students"
4. ✅ Verify: Student appears in all applicable reports

#### Test 15: Status Persists After Refresh
1. Demote a student
2. Refresh the page
3. Go back to student record
4. ✅ Verify: Status is still "Demoted"

#### Test 16: Excel Import with Demoted Status
1. Create Excel file with "Demoted" in Status column
2. Import via **Dashboard → Biodata → Import from Excel**
3. ✅ Verify: Students are imported with "Demoted" status

---

## 📋 Test Results Template

```
Test Date: _______________
Tester: ___________________

Desktop Application:
[ ] Test 1: Create with Demoted - PASS / FAIL
[ ] Test 2: Edit to Demoted - PASS / FAIL
[ ] Test 3: View in List - PASS / FAIL

Web Application:
[ ] Test 4: Biodata Form - PASS / FAIL
[ ] Test 5: Bulk Demotion - PASS / FAIL
[ ] Test 6: Report 1 Filter - PASS / FAIL
[ ] Test 7: Report 2 Filter - PASS / FAIL
[ ] Test 8: Report 3 Filter - PASS / FAIL

Database:
[ ] Test 9: Status Column - PASS / FAIL
[ ] Test 10: Semester Update - PASS / FAIL

Edge Cases:
[ ] Test 11: Same Semester - PASS / FAIL
[ ] Test 12: No Selection - PASS / FAIL
[ ] Test 13: Missing Fields - PASS / FAIL

Data Integrity:
[ ] Test 14: All Reports - PASS / FAIL
[ ] Test 15: Persist After Refresh - PASS / FAIL
[ ] Test 16: Excel Import - PASS / FAIL

Overall Status: ___________
Notes: _____________________
```

---

## 🚀 Quick Start

**Fastest way to test:**
1. Open web app → Dashboard → Student Promotion
2. Scroll down to "📉 Demote Students" section
3. Select Campus, Board, Semester
4. Click "Generate List"
5. Check a student and demote them
6. Go to Reports and filter by "Demoted Students"
7. ✅ Done!


