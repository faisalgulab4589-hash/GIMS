# Certificates Module - Implementation Guide

## Overview
The Certificates section has been successfully integrated into the Student Management System dashboard. This module allows users to generate two types of certificates for students:
1. **Bonafide Certificate** - Certifies that a student is currently enrolled
2. **Course Completion Certificate** - Certifies that a student has completed their course

---

## Features Implemented

### 1. **Certificate Types**
- ✅ Bonafide Certificate
- ✅ Course Completion Certificate

### 2. **Certificate Generation Workflow**
- ✅ Input field for Admission Number
- ✅ Automatic student data fetching
- ✅ Student information display
- ✅ Certificate type selection
- ✅ Certificate preview
- ✅ Generate and Print options

### 3. **Student Information Displayed**
**Bonafide Certificate includes:**
- Student Name
- Father's Name
- Admission Number
- Technology/Program
- Semester

**Course Completion Certificate includes:**
- Student Name
- Father's Name
- Admission Number
- Technology/Program

---

## File Changes

### 1. **templates/dashboard.html**
**Added:**
- Navigation link in sidebar: "Certificates" with icon
- Content section placeholder: `<div id="certificates-content">`
- UI form with:
  - Admission number input field
  - Student data display fields (read-only)
  - Certificate type dropdown
  - Certificate preview area
  - Generate and Print buttons
- JavaScript functions:
  - `fetchStudentForCertificate()` - Fetches student by admission number
  - `updateCertificatePreview()` - Shows certificate preview
  - `generateCertificate()` - Generates PDF certificate
  - `printCertificate()` - Prints certificate directly

### 2. **main.py**
**Added API Endpoints:**

#### `/api/student_by_admission` (GET)
- **Purpose:** Fetch student data by admission number
- **Parameters:** `admission_no` (query parameter)
- **Returns:** Student object with fields: id, admission_no, name, father_name, technology, semester, campus, board, status
- **Error Handling:** Returns 404 if student not found

#### `/api/generate_certificate` (POST)
- **Purpose:** Generate certificate PDF
- **Parameters:** JSON body with:
  - `student_id` (integer)
  - `admission_no` (string)
  - `certificate_type` (string: 'bonafide' or 'course_completion')
- **Returns:** JSON with file_url and filename for download
- **Error Handling:** Validates all required fields and certificate type

---

## How to Use

### Step 1: Navigate to Certificates
1. Click on "Certificates" in the sidebar
2. The Certificates section will load

### Step 2: Fetch Student Data
1. Enter the student's **Admission Number** (4-digit number)
2. Click **"Fetch Student Data"** button
3. Student information will be automatically populated

### Step 3: Select Certificate Type
1. Choose certificate type from dropdown:
   - Bonafide Certificate
   - Course Completion Certificate
2. Certificate preview will update automatically

### Step 4: Generate or Print
- **Generate Certificate:** Downloads PDF file to your computer
- **Print Certificate:** Opens print dialog for direct printing

---

## Certificate Format (Placeholder)

### Bonafide Certificate Template
```
                    BONAFIDE CERTIFICATE
                    
This is to certify that

        [Student Name]
        S/O [Father's Name]

Admission No: [Admission Number]
Technology/Program: [Technology]
Semester: [Semester]

is a bonafide student of this institution.


                    Signature                    Date
```

### Course Completion Certificate Template
```
                COURSE COMPLETION CERTIFICATE
                
This is to certify that

        [Student Name]
        S/O [Father's Name]

Admission No: [Admission Number]
Technology/Program: [Technology]

has successfully completed the course as per the requirements 
of this institution.


                    Signature                    Date
```

---

## Database Schema
No new database tables were created. The feature uses existing `students` table with columns:
- `id` - Student ID
- `admission_no` - Admission Number
- `name` - Student Name
- `father_name` - Father's Name
- `technology` - Technology/Program
- `semester` - Semester
- `campus` - Campus
- `board` - Board
- `status` - Student Status

---

## Technical Details

### Frontend (JavaScript)
- Uses Fetch API for API calls
- Dynamic HTML generation for certificate preview
- Print functionality using window.print()
- Error handling with user alerts

### Backend (Flask)
- RESTful API endpoints
- JSON request/response format
- PDF generation using ReportLab
- File storage in `/uploads` folder
- Proper error handling and validation

---

## Next Steps

### Waiting For:
⏳ **Certificate Format/Template** - User to provide custom certificate design/format

Once the certificate format is provided, the following will be updated:
1. Certificate HTML/PDF layout
2. Certificate styling and branding
3. Additional fields if needed
4. Custom fonts and colors

---

## Testing Checklist

- [ ] Navigate to Certificates section
- [ ] Enter valid admission number
- [ ] Verify student data loads correctly
- [ ] Select Bonafide Certificate
- [ ] Verify preview updates
- [ ] Generate PDF and verify download
- [ ] Print certificate
- [ ] Select Course Completion Certificate
- [ ] Verify preview updates
- [ ] Generate PDF and verify download
- [ ] Test with invalid admission number
- [ ] Test error handling

---

## Notes
- Certificates are generated as PDF files with timestamp
- Files are stored in `/uploads` folder
- Preview is HTML-based and can be customized
- Print functionality uses browser's print dialog
- All student data is fetched from database in real-time

