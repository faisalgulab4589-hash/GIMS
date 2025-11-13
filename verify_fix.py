#!/usr/bin/env python
"""
Verification script to test the Phone #, SMS Number, and Semester import fix
"""
import sqlite3
from db import get_connection

print("=" * 80)
print("VERIFICATION: Phone #, SMS Number, and Semester Import Fix")
print("=" * 80)

conn = get_connection()
cur = conn.cursor()

# Check the database schema
print("\n1. Checking Database Schema:")
print("-" * 80)
cur.execute("PRAGMA table_info(students)")
columns = cur.fetchall()
column_names = [col[1] for col in columns]
print(f"✓ Database has {len(column_names)} columns")
print(f"✓ Required columns present:")
print(f"  - phone: {'✓' if 'phone' in column_names else '✗'}")
print(f"  - sms_phone: {'✓' if 'sms_phone' in column_names else '✗'}")
print(f"  - semester: {'✓' if 'semester' in column_names else '✗'}")

# Check sample data
print("\n2. Checking Sample Student Data:")
print("-" * 80)
cur.execute('''
    SELECT admission_no, name, phone, sms_phone, semester, technology 
    FROM students 
    LIMIT 5
''')
students = cur.fetchall()

if students:
    print(f"Found {len(students)} students in database\n")
    for i, student in enumerate(students, 1):
        print(f"Student {i}:")
        print(f"  Admission No: {student[0]}")
        print(f"  Name: {student[1]}")
        print(f"  Phone: {student[2] if student[2] else '(empty)'}")
        print(f"  SMS Phone: {student[3] if student[3] else '(empty)'}")
        print(f"  Semester: {student[4] if student[4] else '(empty)'}")
        print(f"  Technology: {student[5] if student[5] else '(empty)'}")
        print()
else:
    print("No students found in database")

# Check for data completeness
print("\n3. Data Completeness Check:")
print("-" * 80)
cur.execute("SELECT COUNT(*) FROM students WHERE phone IS NOT NULL AND phone != ''")
phone_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM students WHERE sms_phone IS NOT NULL AND sms_phone != ''")
sms_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM students WHERE semester IS NOT NULL AND semester != ''")
semester_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM students")
total_count = cur.fetchone()[0]

print(f"Total students: {total_count}")
print(f"Students with Phone #: {phone_count} ({phone_count*100//total_count if total_count > 0 else 0}%)")
print(f"Students with SMS Phone: {sms_count} ({sms_count*100//total_count if total_count > 0 else 0}%)")
print(f"Students with Semester: {semester_count} ({semester_count*100//total_count if total_count > 0 else 0}%)")

conn.close()

print("\n" + "=" * 80)
print("✅ Verification Complete!")
print("=" * 80)
print("\nNext Steps:")
print("1. Try importing your Excel file again")
print("2. Check if Phone #, SMS Number, and Semester are now displayed correctly")
print("3. Verify the data in the students list and biodata form")

