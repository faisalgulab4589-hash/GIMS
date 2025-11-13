import sqlite3
from datetime import datetime
from db import get_connection

def add_new_sample_students():
    conn = get_connection()
    cursor = conn.cursor()

    # These are the additional students I want to add
    new_sample_students = [
        ('1006', 'Kamran Ali', 'Javed Khan', 'Street 6, Lahore', '1995-02-28', 'Male', 'Pakistan', 'Lahore', '03051122334', '03051122334', 'Main Campus', 'KPK Medical Faculty', 'Dip-Anesthesia', '2nd Semester', 'Active', None, 'Paid', 'New admission', datetime.now().isoformat()),
        ('1007', 'Aisha Bibi', 'Rahim Shah', 'Street 7, Karachi', '1996-09-01', 'Female', 'Pakistan', 'Karachi', '03069876543', '03069876543', 'Girl Campus', 'PNC Board', 'BS Nursing', '1st Semester', 'Active', None, 'Paid', 'Transferred', datetime.now().isoformat()),
        ('1008', 'Bilal Ahmed', 'Sultan Khan', 'Street 8, Islamabad', '1997-04-05', 'Male', 'Pakistan', 'Islamabad', '03075566778', '03075566778', 'BS Campus', 'KMU', 'BS-MLT', '4th Semester', 'Active', None, 'Free', 'Scholarship student', datetime.now().isoformat()),
        ('1009', 'Hina Gul', 'Nadir Shah', 'Street 9, Quetta', '1998-08-12', 'Female', 'Pakistan', 'Quetta', '03081234567', '03081234567', 'Main Campus', 'KPK Medical Faculty', 'Dip-Pharmacy', '1st Semester', 'Active', None, 'Paid', 'Regular attendance', datetime.now().isoformat()),
        ('1010', 'Imran Khan', 'Zahid Ali', 'Street 10, Multan', '1999-01-25', 'Male', 'Pakistan', 'Multan', '03097654321', '03097654321', 'Girl Campus', 'PNC Board', 'L.H.V', '2nd year', 'Active', None, 'Paid', 'Good progress', datetime.now().isoformat()),
        ('1011', 'Sanaullah', 'Fazal Khan', 'Street 11, Faisalabad', '1990-03-03', 'Male', 'Pakistan', 'Faisalabad', '03101234567', '03101234567', 'Main Campus', 'KPK Medical Faculty', 'Dip-Anesthesia', '1st Semester', 'Active', None, 'Paid', 'New student', datetime.now().isoformat()),
        ('1012', 'Nida Khan', 'Asif Ali', 'Street 12, Rawalpindi', '1991-06-18', 'Female', 'Pakistan', 'Rawalpindi', '03117654321', '03117654321', 'Girl Campus', 'PNC Board', 'BS Nursing', '2nd Semester', 'Active', None, 'Paid', 'Consistent', datetime.now().isoformat()),
        ('1013', 'Omar Farooq', 'Tariq Mehmood', 'Street 13, Sialkot', '1992-10-07', 'Male', 'Pakistan', 'Sialkot', '03121122334', '03121122334', 'BS Campus', 'KMU', 'BS-MLT', '3rd Semester', 'Active', None, 'Free', 'Needs support', datetime.now().isoformat()),
        ('1014', 'Rabia Basri', 'Khalid Khan', 'Street 14, Gujranwala', '1993-12-01', 'Female', 'Pakistan', 'Gujranwala', '03139876543', '03139876543', 'Main Campus', 'KPK Medical Faculty', 'Dip-Pharmacy', '2nd Semester', 'Active', None, 'Paid', 'Excellent record', datetime.now().isoformat()),
        ('1015', 'Waqas Ahmed', 'Nasir Khan', 'Street 15, Hyderabad', '1994-05-09', 'Male', 'Pakistan', 'Hyderabad', '03145566778', '03145566778', 'Girl Campus', 'PNC Board', 'L.H.V', '1st year', 'Active', None, 'Paid', 'Good attendance', datetime.now().isoformat())
    ]

    inserted_count = 0
    for student_data in new_sample_students:
        admission_no = student_data[0]
        cursor.execute("SELECT id FROM students WHERE admission_no=?", (admission_no,))
        exists = cursor.fetchone()

        if not exists:
            cursor.execute(
                'INSERT INTO students (admission_no, name, father_name, address, dob, gender, nationality, district, phone, sms_phone, campus, board, technology, semester, status, photo_path, student_type, remarks, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                student_data
            )
            inserted_count += 1
            print(f"Inserted student: {admission_no}")
        else:
            print(f"Student with admission no {admission_no} already exists. Skipping.")
    
    conn.commit()
    conn.close()
    print(f"Finished adding {inserted_count} new students.")

if __name__ == '__main__':
    add_new_sample_students()
