# Employee Deductions Module - Quick Reference

## Module Location
**URL:** Admin Dashboard → Employee Management → Deductions Tab

---

## Key Features at a Glance

### 1. **Active Employees Overview**
- Displays all active employees with:
  - Name & Father Name
  - Department & Designation
  - Campus
  - Attendance Summary (Present/Absent/Leave/Late badges)
  - Per-day Rate (Auto-calculated: Basic Salary ÷ 30)
  - Current deduction details
- **Search:** Type in "Search by Name or Father Name" field for real-time filtering

### 2. **Add Manual Deduction**
- **Employee:** Select from dropdown
- **Month/Year:** Choose month and year
- **Days to Deduct:** Enter number of days (e.g., 2, 0.5)
- **Per-Day Rate:** Auto-displays (readonly)
- **Deduction Amount:** Auto-calculates from Days × Per-Day Rate, or enter custom amount
- **Deduction Type:** Choose from:
  - Late
  - Absent
  - Leave without Pay
  - Other
- **Remarks/Reason:** Optional notes for audit trail
- **Actions:** 
  - `Save Deduction` - Create new deduction
  - `Reset` - Clear form
  - `Update Deduction` - When editing existing (button changes name)

### 3. **View & Search Deductions**
- **Search Fields:**
  - Employee ID
  - Name
  - Father Name
  - Month
  - Year
- **Columns:**
  - Employee (ID & Father Name)
  - Department/Designation
  - Campus
  - Month/Year
  - Type
  - Days
  - Amount
  - Salary Before/After
  - Date of Entry
  - Remarks
  - Actions (Edit/Delete buttons)
- **Export Options:**
  - 📊 Export to Excel
  - 📄 Print Report
  - 📋 Download PDF

---

## Workflow

### Creating a New Deduction

1. Go to Deductions tab
2. In "Add Manual Deduction" section:
   - Select employee from dropdown
   - Choose month and year
   - Enter days to deduct (optional: enter custom amount)
   - Select deduction type
   - Add remarks (optional)
3. Click `Save Deduction`
4. ✅ Success message appears
5. Report updates automatically

### Editing a Deduction

1. In "View Deductions" section, search for the deduction
2. Click the ✏️ **Edit** button in the row
3. Form pre-populates with existing data
4. Modify fields as needed
5. Click `Update Deduction`
6. ✅ Updated successfully

### Deleting a Deduction

1. In "View Deductions" section, find the deduction
2. Click the 🗑️ **Delete** button
3. Confirm deletion in popup
4. ✅ Removed successfully

### Generating Reports

1. Search for deductions (optional filters)
2. Choose export method:
   - **Excel:** Click `Export to Excel` → Downloads XLSX
   - **PDF:** Click `Download PDF` → Downloads PDF file
   - **Print:** Click `Print Report` → Opens print dialog

---

## Automatic Calculations

### Per-Day Rate
```
Per-Day Rate = Basic Salary ÷ 30
```
Example: Rs. 30,000 ÷ 30 = Rs. 1,000/day

### Deduction Amount (if not manually entered)
```
Amount = Per-Day Rate × Days Deducted
```
Example: Rs. 1,000/day × 2 days = Rs. 2,000

### Net Salary (Auto-Updated in Payroll)
```
Net Salary = Basic Salary + Allowances - Total Deductions
```
Where Total Deductions = Manual Deductions + Security Deductions

---

## Search Examples

### Search by Employee Name
- Type "Ali" → Shows all employees with "Ali" in name

### Search by Father Name
- Type "Khan" → Shows all employees with "Khan" as father name

### Multi-Criteria Search
- Employee ID: `1`
- Month: `November`
- Year: `2025`
- Click Search → Shows only deductions for employee #1 in Nov 2025

---

## API Reference (for Developers)

### Get Deductions
```bash
GET /api/deductions?employee_name=Ali&month=11&year=2025
```

### Create Deduction
```bash
POST /api/deductions/manual
Content-Type: application/json

{
    "employee_id": 1,
    "month": 11,
    "year": 2025,
    "days": 2,
    "deduction_type": "Absent",
    "reason": "Unauthorized absence"
}
```

### Update Deduction
```bash
PUT /api/deductions/5
Content-Type: application/json

{
    "days": 3,
    "reason": "Updated reason"
}
```

### Delete Deduction
```bash
DELETE /api/deductions/5
```

---

## Database Schema

### Relevant Tables

**employee_deductions**
```
id (auto)
employee_id
month (1-12)
year (YYYY)
days_deducted
amount
reason
deduction_type
created_at
```

**payroll**
```
id (auto)
employee_id
month
year
basic_salary
allowances
deductions (total)
net_salary
generated_date
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Loading..." doesn't go away | Refresh browser, clear cache |
| Can't find an employee | Search is case-insensitive, try partial name |
| Payroll not updated | Wait a few seconds, then refresh |
| Amount not auto-calculating | Check if basic salary is set for employee |
| PDF export blank | Check if you have search results |
| No employees showing | Check that employees are marked as "Active" |

---

## Important Notes

⚠️ **Only Admin users** can:
- Create deductions
- Edit deductions
- Delete deductions
- Generate reports

✅ **Both Admins and Teachers** can:
- View deductions
- Search deductions
- View employee overview

📌 **Deductions are monthly:**
- Each month/year combination creates separate deduction record
- Payroll auto-updates for that specific month/year

🔄 **Payroll Auto-Sync:**
- Happens automatically on create/update/delete
- No manual refresh needed
- Works with security deductions too

---

## Keyboard Shortcuts

- `Tab` - Move between form fields
- `Enter` - Submit forms
- `Esc` - Reset form (on some fields)

---

## Tips & Tricks

1. **Quick Search:** Use Ctrl+F in browser to search within search results
2. **Bulk Export:** Search with minimal filters → Export all → Use Excel for further filtering
3. **Print Friendly:** Use "Print Report" for professional printouts with institute header
4. **Audit Trail:** Always add remarks when creating special deductions
5. **Month Planning:** Review "Employees Overview" to see attendance before adding deductions

---

## Support

For issues or questions:
1. Check the testing checklist in the complete guide
2. Clear browser cache and try again
3. Ensure you're logged in as Admin
4. Check that all required fields are filled
5. Contact system administrator if problem persists

---

**Last Updated:** November 13, 2025  
**Module Status:** ✅ Production Ready
