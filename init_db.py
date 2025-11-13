from db import get_connection
from datetime import datetime

def setup_database():
    conn = get_connection()
    cursor = conn.cursor()

    # Students Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            father_name TEXT NOT NULL,
            address TEXT,
            dob TEXT,
            gender TEXT,
            nationality TEXT,
            district TEXT,
            phone TEXT,
            sms_phone TEXT,
            admission_no TEXT UNIQUE NOT NULL,
            campus TEXT,
            board TEXT,
            semester TEXT,
            technology TEXT,
            status TEXT DEFAULT 'Active',
            photo_path TEXT,
            student_type TEXT DEFAULT 'Paid',
            remarks TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Teachers Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT DEFAULT 'teacher',
            assigned_semesters TEXT,
            employee_id INTEGER,
            subject TEXT,
            technology TEXT,
            technology_assignments TEXT,
            status TEXT DEFAULT 'Active',
            email TEXT,
            phone TEXT,
            cnic TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(id)
        )
    """)

    # Inventory Items Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL,
            category TEXT,
            brand TEXT,
            model_no TEXT,
            quantity_total INTEGER DEFAULT 0,
            quantity_available INTEGER DEFAULT 0,
            purchase_date TEXT,
            expiry_date TEXT,
            unit_price REAL DEFAULT 0,
            total_price REAL DEFAULT 0,
            location TEXT,
            status TEXT DEFAULT 'Active',
            remarks TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS item_issue_records (
            issue_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            issued_to TEXT NOT NULL,
            issued_type TEXT CHECK(issued_type IN ('Student','Teacher','Department')) NOT NULL,
            issue_date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            quantity_returned INTEGER DEFAULT 0,
            return_date TEXT,
            status TEXT DEFAULT 'Issued',
            remarks TEXT,
            receiver_signature TEXT,
            issuer_signature TEXT,
            created_at TEXT,
            updated_at TEXT,
            FOREIGN KEY (item_id) REFERENCES inventory_items(item_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventory_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            requested_by TEXT NOT NULL,
            requested_role TEXT,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            request_date TEXT,
            approval_date TEXT,
            fulfilled_date TEXT,
            remarks TEXT
        )
    """)

    # Semesters Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS semesters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    # Insert initial semesters if not exist
    semesters_data = [('1st Semester',), ('2nd Semester',), ('3rd Semester',), ('4th Semester',)]
    for semester in semesters_data:
        cursor.execute("INSERT OR IGNORE INTO semesters (name) VALUES (?)", semester)

    # Campuses Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    # Insert initial campuses if not exist
    campuses_data = [('Main Campus',), ('Satellite Campus',)]
    for campus in campuses_data:
        cursor.execute("INSERT OR IGNORE INTO campuses (name) VALUES (?)", campus)

    # Boards Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    # Insert initial boards if not exist
    boards_data = [('KPK Medical Faculty',), ('PNC Board',), ('KMU',), ('Pharmacy Council',)]
    for board in boards_data:
        cursor.execute("INSERT OR IGNORE INTO boards (name) VALUES (?)", board)

    # Technologies Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS technologies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)
    # Insert initial technologies if not exist
    technologies_data = []
    for technology in technologies_data:
        cursor.execute("INSERT OR IGNORE INTO technologies (name) VALUES (?)", technology)

    # Attendance Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL, -- Present, Absent, Late, Leave
            notes TEXT,
            created_at TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE (student_id, attendance_date)
        )
    """)

    # Attendance Lock Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance_lock (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            attendance_date TEXT UNIQUE NOT NULL,
            locked_at TEXT NOT NULL,
            locked_by_teacher_id INTEGER,
            FOREIGN KEY (locked_by_teacher_id) REFERENCES teachers (id)
        )
    """)

    # Admin User (for initial login)
    from werkzeug.security import generate_password_hash
    admin_password_hash = generate_password_hash('admin') # Hash the default admin password

    cursor.execute("""
        INSERT OR IGNORE INTO teachers (username, password_hash, name, role, assigned_semesters, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ('admin', admin_password_hash, 'Admin User', 'admin', '[]', datetime.now().isoformat(), datetime.now().isoformat()))

    conn.commit()
    conn.close()
    print("Database & tables created successfully")

if __name__ == "__main__":
    setup_database()
