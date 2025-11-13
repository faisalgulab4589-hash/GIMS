import sqlite3
from datetime import datetime

def add_student():
    conn = sqlite3.connect('students.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO students (admission_no, name, father_name, address, dob, gender, nationality, district, phone, sms_phone, campus, board, technology, semester, status, photo_path, student_type, remarks, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
        (
            '12345',
            'Test Student',
            'Test Father',
            'Test Address',
            '2000-01-01',
            'Male',
            'Pakistani',
            'Test District',
            '1234567890',
            '1234567890',
            'Main Campus',
            'BISE Lahore',
            'Computer Science',
            '1st',
            'Active',
            None,
            'Free',
            'Test Remarks',
            datetime.now().isoformat()
        )
    )
    conn.commit()
    conn.close()
    print("Student added successfully.")

if __name__ == '__main__':
    add_student()
