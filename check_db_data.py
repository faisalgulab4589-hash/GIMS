#!/usr/bin/env python
import sqlite3
from db import get_connection

conn = get_connection()
cur = conn.cursor()

# Check the first few students
cur.execute('SELECT admission_no, name, phone, sms_phone, semester FROM students LIMIT 5')
students = cur.fetchall()

print('Students in Database:')
print('=' * 100)
for student in students:
    adm = student[0] if student[0] else 'N/A'
    name = student[1] if student[1] else 'N/A'
    phone = student[2] if student[2] else 'EMPTY'
    sms = student[3] if student[3] else 'EMPTY'
    sem = student[4] if student[4] else 'N/A'
    print(f'Admission: {adm:10} | Name: {name:20} | Phone: {phone:15} | SMS: {sms:15} | Semester: {sem}')

print()
print('Checking specific student (4560):')
cur.execute('SELECT admission_no, name, phone, sms_phone, semester FROM students WHERE admission_no = "4560"')
student = cur.fetchone()
if student:
    print(f'  Admission: {student[0]}')
    print(f'  Name: {student[1]}')
    print(f'  Phone: {student[2]}')
    print(f'  SMS Phone: {student[3]}')
    print(f'  Semester: {student[4]}')
else:
    print('  Student not found')

print('\nMidterm Exams in Database:')
print('=' * 100)
try:
    cur.execute('SELECT exam_id, title, subject, campus, semester, status FROM midterm_exams LIMIT 5')
    exams = cur.fetchall()
    if exams:
        for exam in exams:
            exam_id = exam[0] if exam[0] else 'N/A'
            title = exam[1] if exam[1] else 'N/A'
            subject = exam[2] if exam[2] else 'N/A'
            campus = exam[3] if exam[3] else 'N/A'
            semester = exam[4] if exam[4] else 'N/A'
            status = exam[5] if exam[5] else 'N/A'
            print(f'Exam ID: {exam_id:5} | Title: {title:20} | Subject: {subject:15} | Campus: {campus:15} | Semester: {semester:15} | Status: {status}')
    else:
        print('No midterm exams found.')
except sqlite3.OperationalError as e:
    print(f"Error accessing midterm_exams table: {e}. The table might not exist or is empty.")

conn.close()
