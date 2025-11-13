import sqlite3
import json
from datetime import datetime
from config import DB_NAME # Import DB_NAME from config
from werkzeug.security import generate_password_hash, check_password_hash
from rbac_constants import DEFAULT_MODULES, DEFAULT_ROLE_PERMISSIONS

try:
    import bcrypt
except ImportError:  # pragma: no cover - optional dependency
    bcrypt = None
    print("Warning: bcrypt module not found. Falling back to Werkzeug PBKDF2 hashing.")


def bcrypt_hash(password: str) -> str:
    """Hash a plain-text password using bcrypt when available."""
    if not password:
        raise ValueError("Password is required")
    if bcrypt:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    return generate_password_hash(password)

def get_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    # Using Row factory makes it possible to access columns by name
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database by creating tables if they don't exist and
    populating list tables with default values if they are empty.
    """
    conn = get_connection()
    cur = conn.cursor()

    # Create students table if it doesn't exist
    # This schema is designed to match the fields in the BioDataForm
    cur.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admission_no TEXT UNIQUE NOT NULL,
    name TEXT,
    father_name TEXT,
    address TEXT,
    dob TEXT,
    gender TEXT,
    nationality TEXT,
    district TEXT,
    phone TEXT,
    sms_phone TEXT,
    campus TEXT,
    board TEXT,
    technology TEXT,
    semester TEXT,
    status TEXT,
    photo_path TEXT,
    student_type TEXT DEFAULT 'Paid',
    remarks TEXT,
    created_at TEXT
)
''')

    # Helper function to check and add column
    def add_column_if_not_exists(column_name, column_definition):
        cur.execute("PRAGMA table_info(students)")
        columns = [col[1] for col in cur.fetchall()]
        if column_name not in columns:
            try:
                cur.execute(f"ALTER TABLE students ADD COLUMN {column_name} {column_definition}")
                conn.commit()
                print(f"Added {column_name} column to students")
            except Exception as e:
                print(f"{column_name} column already exists or error: {e}")
    
    # Add student_type column if it doesn't exist
    add_column_if_not_exists('student_type', 'TEXT DEFAULT \'Paid\'')
    
    # Add remarks column if it doesn't exist
    add_column_if_not_exists('remarks', 'TEXT')
    
    # Add nationality column if it doesn't exist
    add_column_if_not_exists('nationality', 'TEXT')
    
    # Add district column if it doesn't exist
    add_column_if_not_exists('district', 'TEXT')
    
    # Add student login credentials columns if they don't exist
    add_column_if_not_exists('username', 'TEXT')
    add_column_if_not_exists('password_hash', 'TEXT')
    add_column_if_not_exists('account_status', 'TEXT DEFAULT \'Active\'')
    add_column_if_not_exists('last_login', 'TEXT')
    
    # Try to add UNIQUE constraint to username if it doesn't exist
    # Note: SQLite doesn't support adding UNIQUE constraint to existing column directly
    # We'll handle uniqueness at application level if needed
    
    # Create student_activity_log table
    cur.execute('''
CREATE TABLE IF NOT EXISTS student_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    activity_description TEXT,
    related_id INTEGER,
    related_type TEXT,
    ip_address TEXT,
    created_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id)
)
''')

    # Create attendance table
    cur.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,
    notes TEXT,
    created_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(student_id, attendance_date)
)
''')

    # Create teachers table
    cur.execute('''
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
    status TEXT DEFAULT 'Active',
    email TEXT,
    phone TEXT,
    cnic TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')
    
    # Check and add new columns to teachers table if they don't exist
    cur.execute("PRAGMA table_info(teachers)")
    teacher_columns = [col[1] for col in cur.fetchall()]
    
    new_columns = {
        'employee_id': 'INTEGER',
        'subject': 'TEXT',
        'technology': 'TEXT',
        'technology_assignments': 'TEXT',
        'status': 'TEXT DEFAULT "Active"',
        'email': 'TEXT',
        'phone': 'TEXT',
        'cnic': 'TEXT'
    }
    
    for col_name, col_type in new_columns.items():
        if col_name not in teacher_columns:
            try:
                cur.execute(f"ALTER TABLE teachers ADD COLUMN {col_name} {col_type}")
                print(f"Added {col_name} column to teachers table")
            except Exception as e:
                print(f"{col_name} column already exists or error: {e}")
    
    # Create teacher_permissions table
    cur.execute('''
CREATE TABLE IF NOT EXISTS teacher_permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    permission_name TEXT NOT NULL,
    granted INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    UNIQUE(teacher_id, permission_name)
)
''')
    
    # Create teacher_activity_log table
    cur.execute('''
CREATE TABLE IF NOT EXISTS teacher_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    teacher_id INTEGER NOT NULL,
    activity_type TEXT NOT NULL,
    activity_description TEXT,
    related_id INTEGER,
    related_type TEXT,
    ip_address TEXT,
    created_at TEXT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id)
)
''')

    # ==================== USER & ROLE MANAGEMENT (RBAC) ====================

    cur.execute('''
CREATE TABLE IF NOT EXISTS access_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_key TEXT UNIQUE NOT NULL,
    label TEXT NOT NULL,
    description TEXT,
    created_at TEXT,
    updated_at TEXT
)
''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    is_system INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id INTEGER NOT NULL,
    module_id INTEGER NOT NULL,
    granted INTEGER DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    PRIMARY KEY (role_id, module_id),
    FOREIGN KEY (role_id) REFERENCES user_roles(id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES access_modules(id) ON DELETE CASCADE
)
''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Active',
    last_login_at TEXT,
    last_login_ip TEXT,
    login_attempts INTEGER DEFAULT 0,
    last_failed_login_at TEXT,
    suspended_until TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (role_id) REFERENCES user_roles(id)
)
''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS user_activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    role_snapshot TEXT,
    action TEXT NOT NULL,
    module_key TEXT,
    entity_type TEXT,
    entity_id TEXT,
    description TEXT,
    metadata TEXT,
    ip_address TEXT,
    created_at TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')

    # Seed default modules and roles along with an admin user
    timestamp = datetime.now().isoformat()
    module_id_map = {}
    for module in DEFAULT_MODULES:
        existing_module = cur.execute(
            'SELECT id FROM access_modules WHERE module_key = ?',
            (module.key,)
        ).fetchone()
        if existing_module:
            module_id = existing_module['id']
            cur.execute(
                'UPDATE access_modules SET label = ?, description = ?, updated_at = ? WHERE id = ?',
                (module.label, module.description, timestamp, module_id)
            )
        else:
            cur.execute(
                'INSERT INTO access_modules (module_key, label, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (module.key, module.label, module.description, timestamp, timestamp)
            )
            module_id = cur.lastrowid
        module_id_map[module.key] = module_id

    def upsert_role(role_name, payload):
        role = cur.execute('SELECT id FROM user_roles WHERE name = ?', (role_name,)).fetchone()
        if role:
            role_id = role['id']
            cur.execute(
                'UPDATE user_roles SET description = ?, is_system = ?, updated_at = ? WHERE id = ?',
                (payload.get('description'), 1 if payload.get('is_system') else 0, timestamp, role_id)
            )
        else:
            cur.execute(
                'INSERT INTO user_roles (name, description, is_system, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
                (role_name, payload.get('description'), 1 if payload.get('is_system') else 0, timestamp, timestamp)
            )
            role_id = cur.lastrowid
        return role_id

    role_ids = {}
    for role_name, payload in DEFAULT_ROLE_PERMISSIONS.items():
        role_id = upsert_role(role_name, payload)
        role_ids[role_name] = role_id
        perm_count = cur.execute('SELECT COUNT(*) AS c FROM role_permissions WHERE role_id = ?', (role_id,)).fetchone()['c']
        if perm_count == 0:
            for module_key in payload.get('modules', []):
                module_id = module_id_map.get(module_key)
                if module_id:
                    cur.execute(
                        'INSERT INTO role_permissions (role_id, module_id, granted, created_at, updated_at) VALUES (?, ?, 1, ?, ?)',
                        (role_id, module_id, timestamp, timestamp)
                    )

    admin_role_id = role_ids.get('Admin')
    if admin_role_id:
        existing_users = cur.execute('SELECT COUNT(*) AS c FROM users').fetchone()['c']
        if existing_users == 0:
            admin_password_hash = bcrypt_hash('Admin@123')
            cur.execute(
                '''INSERT INTO users (full_name, username, password_hash, role_id, status, created_at, updated_at)
                   VALUES (?, ?, ?, ?, 'Active', ?, ?)''',
                ('System Administrator', 'sysadmin', admin_password_hash, admin_role_id, timestamp, timestamp)
            )

    # ==================== INVENTORY MANAGEMENT TABLES ====================

    cur.execute('''
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
''')

    cur.execute('''
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
''')

    cur.execute('''
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
''')

    # Ensure new columns exist after deployments
    def add_column_if_missing(table_name, column_name, definition):
        cur.execute(f"PRAGMA table_info({table_name})")
        cols = [col[1] for col in cur.fetchall()]
        if column_name not in cols:
            cur.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {definition}")

    add_column_if_missing('item_issue_records', 'quantity_returned', 'INTEGER DEFAULT 0')
    add_column_if_missing('item_issue_records', 'receiver_signature', 'TEXT')
    add_column_if_missing('item_issue_records', 'issuer_signature', 'TEXT')
    add_column_if_missing('inventory_requests', 'requested_role', 'TEXT')
    add_column_if_missing('inventory_requests', 'fulfilled_date', 'TEXT')

    # ==================== EMPLOYEE MANAGEMENT TABLES ====================
    
    # Departments Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')
    
    # Designations Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS designations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')
    
    # Employees Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    father_name TEXT,
    cnic TEXT UNIQUE NOT NULL,
    contact TEXT,
    email TEXT,
    department_id INTEGER,
    designation_id INTEGER,
    campus TEXT,
    joining_date TEXT,
    basic_salary REAL DEFAULT 0,
    status TEXT DEFAULT 'Active',
    photo_path TEXT,
    created_at TEXT,
    updated_at TEXT,
    security_mode TEXT DEFAULT 'none',
    security_amount REAL DEFAULT 0,
    security_notes TEXT,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (designation_id) REFERENCES designations(id)
)
''')
    
    cur.execute("PRAGMA table_info(employees)")
    employee_columns = [col[1] for col in cur.fetchall()]

    def add_employee_column(column_name, column_definition):
        if column_name not in employee_columns:
            try:
                cur.execute(f"ALTER TABLE employees ADD COLUMN {column_name} {column_definition}")
                conn.commit()
                employee_columns.append(column_name)
                print(f"Added {column_name} column to employees")
            except Exception as e:
                print(f"{column_name} column already exists or error: {e}")

    add_employee_column('security_mode', "TEXT DEFAULT 'none'")
    add_employee_column('security_amount', 'REAL DEFAULT 0')
    add_employee_column('security_notes', 'TEXT')
    
    # Employee Attendance Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS employee_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    attendance_date TEXT NOT NULL,
    status TEXT NOT NULL,
    check_in_time TEXT,
    check_out_time TEXT,
    marked_at TEXT,
    marked_by INTEGER,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (marked_by) REFERENCES teachers(id),
    UNIQUE(employee_id, attendance_date)
)
''')
    
    # Employee Attendance Lock Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS employee_attendance_lock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_date TEXT NOT NULL UNIQUE,
    locked_at TEXT NOT NULL,
    locked_by_teacher_id INTEGER,
    FOREIGN KEY (locked_by_teacher_id) REFERENCES teachers(id)
)
''')
    
    # Leave Types Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS leave_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
)
''')
    
    # Leave Requests Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS leave_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    leave_type_id INTEGER NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    days INTEGER,
    reason TEXT,
    status TEXT DEFAULT 'Pending',
    approved_by INTEGER,
    approved_date TEXT,
    rejection_reason TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    FOREIGN KEY (leave_type_id) REFERENCES leave_types(id),
    FOREIGN KEY (approved_by) REFERENCES teachers(id)
)
''')
    
    # Leave Balance Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS leave_balance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    total_allotted INTEGER DEFAULT 30,
    used INTEGER DEFAULT 0,
    remaining INTEGER DEFAULT 30,
    updated_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')
    
    # Payroll Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS payroll (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    basic_salary REAL,
    allowances REAL DEFAULT 0,
    deductions REAL DEFAULT 0,
    net_salary REAL,
    generated_date TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id),
    UNIQUE(employee_id, month, year)
)
''')

    # Employee Deductions Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS employee_deductions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    month INTEGER NOT NULL,
    year INTEGER NOT NULL,
    days_deducted REAL DEFAULT 0,
    amount REAL DEFAULT 0,
    reason TEXT,
    deduction_type TEXT DEFAULT 'Other',
    created_at TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')

    # Ensure new columns exist for deductions table
    cur.execute("PRAGMA table_info(employee_deductions)")
    deduction_columns = [col[1] for col in cur.fetchall()]
    if 'deduction_type' not in deduction_columns:
        try:
            cur.execute("ALTER TABLE employee_deductions ADD COLUMN deduction_type TEXT DEFAULT 'Other'")
            conn.commit()
            print("Added deduction_type column to employee_deductions")
        except Exception as e:
            print(f"deduction_type column exists or error: {e}")
    
    # Allowances Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS allowances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    amount REAL,
    type TEXT,
    effective_from TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')
    
    # Employee Documents Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS employee_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    doc_type TEXT,
    file_path TEXT,
    uploaded_date TEXT,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
''')
    
    # ==================== END EMPLOYEE MANAGEMENT TABLES ====================

    # ==================== MIDTERM & TESTS MODULE TABLES ====================
    
    # Midterm Exams Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_exams (
    exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    subject TEXT,
    campus TEXT,
    board TEXT,
    technology TEXT,
    semester TEXT,
    exam_date TEXT,
    start_time TEXT,
    end_time TEXT,
    duration INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    marks_per_question REAL DEFAULT 1.0,
    passing_marks REAL,
    negative_marking INTEGER DEFAULT 0,
    negative_marks_value REAL DEFAULT 0.0,
    randomize_questions INTEGER DEFAULT 0,
    randomize_options INTEGER DEFAULT 0,
    allowed_devices TEXT,
    ip_restrictions TEXT,
    max_focus_losses INTEGER DEFAULT 3,
    heartbeat_interval INTEGER DEFAULT 30,
    auto_submit_violations INTEGER DEFAULT 5,
    config_json TEXT,
    status TEXT DEFAULT 'Draft',
    created_by INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (created_by) REFERENCES teachers(id)
)
''')
    
    # Midterm Questions Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    option_a TEXT,
    option_b TEXT,
    option_c TEXT,
    option_d TEXT,
    correct_option TEXT NOT NULL,
    correct_index INTEGER NOT NULL,
    marks REAL DEFAULT 1.0,
    is_selected INTEGER DEFAULT 0,
    media_path TEXT,
    difficulty TEXT,
    topic TEXT,
    created_at TEXT,
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id) ON DELETE CASCADE
)
''')

    # Ensure newer columns exist on older databases
    cur.execute("PRAGMA table_info(midterm_questions)")
    question_columns = [col[1] for col in cur.fetchall()]
    if 'is_selected' not in question_columns:
        try:
            cur.execute("ALTER TABLE midterm_questions ADD COLUMN is_selected INTEGER DEFAULT 0")
            print("Added is_selected column to midterm_questions")
        except Exception as e:
            print(f"is_selected column exists or error: {e}")
    
    # Midterm Instances Table (one per student per exam)
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_instances (
    instance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    start_time TEXT,
    end_time TEXT,
    status TEXT DEFAULT 'Not Started',
    token TEXT UNIQUE,
    ip_address TEXT,
    created_at TEXT,
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(exam_id, student_id)
)
''')
    
    # Midterm Instance Questions (maps instance to questions with randomization)
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_instance_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    question_order INTEGER NOT NULL,
    option_order_json TEXT,
    created_at TEXT,
    FOREIGN KEY (instance_id) REFERENCES midterm_instances(instance_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES midterm_questions(question_id),
    UNIQUE(instance_id, question_id)
)
''')
    
    # Midterm Responses Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_responses (
    response_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option TEXT,
    selected_index INTEGER,
    is_correct INTEGER DEFAULT 0,
    marks_obtained REAL DEFAULT 0.0,
    timestamp TEXT,
    FOREIGN KEY (instance_id) REFERENCES midterm_instances(instance_id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES midterm_questions(question_id),
    UNIQUE(instance_id, question_id)
)
''')
    
    # Student Answers Tracking Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS student_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    instance_id INTEGER NOT NULL,
    question_id INTEGER NOT NULL,
    selected_option TEXT,
    selected_index INTEGER,
    status TEXT NOT NULL DEFAULT 'skipped',
    updated_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id),
    FOREIGN KEY (instance_id) REFERENCES midterm_instances(instance_id),
    FOREIGN KEY (question_id) REFERENCES midterm_questions(question_id),
    UNIQUE(student_id, exam_id, question_id)
)
''')
    
    # Midterm Results Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS midterm_results (
    result_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL UNIQUE,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    total_marks REAL DEFAULT 0.0,
    obtained_marks REAL DEFAULT 0.0,
    percentage REAL DEFAULT 0.0,
    grade TEXT,
    published_flag INTEGER DEFAULT 0,
    published_at TEXT,
    published_by INTEGER,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY (instance_id) REFERENCES midterm_instances(instance_id),
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (published_by) REFERENCES teachers(id)
)
''')
    
    # Exam Attendance Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS exam_attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Absent',
    start_time TEXT,
    end_time TEXT,
    created_at TEXT,
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    UNIQUE(exam_id, student_id)
)
''')
    
    # Exam Proctor Logs Table
    cur.execute('''
CREATE TABLE IF NOT EXISTS exam_proctor_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    instance_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    details TEXT,
    timestamp TEXT,
    FOREIGN KEY (instance_id) REFERENCES midterm_instances(instance_id),
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (exam_id) REFERENCES midterm_exams(exam_id)
)
''')

    cur.execute('''
CREATE TABLE IF NOT EXISTS dmc_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    exam_ids TEXT NOT NULL,
    subject_rows_json TEXT NOT NULL,
    summary_json TEXT,
    created_by INTEGER,
    created_at TEXT,
    FOREIGN KEY (student_id) REFERENCES students(id),
    FOREIGN KEY (created_by) REFERENCES teachers(id)
)
''')
    
    # ==================== END MIDTERM & TESTS MODULE TABLES ====================

    # Create attendance_lock table
    cur.execute('''
CREATE TABLE IF NOT EXISTS attendance_lock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_date TEXT UNIQUE NOT NULL,
    locked_at TEXT NOT NULL,
    locked_by_teacher_id INTEGER,
    FOREIGN KEY (locked_by_teacher_id) REFERENCES teachers(id)
)
''')

    # Add a default admin user if no teachers exist
    cur.execute("SELECT COUNT(*) FROM teachers")
    if cur.fetchone()[0] == 0:
        print("Adding default admin user...")
        admin_password_hash = generate_password_hash('admin') # Default password 'admin'
        cur.execute(
            'INSERT INTO teachers (username, password_hash, name, role, assigned_semesters, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('admin', admin_password_hash, 'Admin User', 'admin', json.dumps([]), datetime.now().isoformat(), datetime.now().isoformat())
        )
        print("Default admin user added: username='admin', password='admin'")

    # List of tables for dropdowns and their default values
    list_tables = {
        'campuses': ['Main Campus', 'Girl Campus', 'BS Campus', 'Nursing Campus'],
        'genders': ['Male', 'Female', 'Other'],
        'nationalities': ['Pakistan'],
        'districts': ['Peshawar', 'Mardan', 'Swat', 'Charsadda', 'Other'],
        'boards': ['KPK Medical Faculty', 'PNC Board', 'Pharmacy Council', 'KMU', 'TTB'],
        'technologies': [
            'Dip-Anesthesia', 'Dip-Cardiology', 'Dip-Health', 'Dip-Pharmacy',
            'Dip-Radiology', 'Dip-Surgical', 'Dip-Dialysis', 'Dip-Physiotherapy', 'Dip-Pathology',
            'Pharmacy-B', 'BS Nursing', 'BS-Anesthesia', 'BS-Health',
            'BS-MLT', 'BS-Cardiology', 'BS-Surgical', 'BS-Radiology', 'BS-Emergency Care', 'DPT'
        ],
        'semesters': [
            '1st Semester', '2nd Semester', '3rd Semester', '4th Semester', '5th Semester',
            '6th Semester', '7th Semester', '8th Semester', '9th Semester', '10th Semester',
            '1st year', '2nd year', 'Sept-2023', 'Sept-2024', 'Sept-2025'
        ],
        'departments': ['Management', 'Teaching Staff', 'Supporting Staff'],
        'designations': ['Principal', 'Lecturer', 'Assistant Professor', 'HOD', 'Demonstrator', 'Instructor', 'Lab Assistant', 'Computer Operator', 'Finance Manager', 'Accountant', 'Student Affairs', 'IT Manager', 'Receptionist', 'Media Manager', 'Librarian', 'Consultant', 'HR Manager', 'HR Director', 'Managing Director', 'Web Developer', 'Office Assistant', 'Admin Officer', 'Peon', 'Security Guard'],
        'leave_types': ['Casual Leave', 'Sick Leave', 'Annual Leave', 'Maternity Leave', 'Paternity Leave', 'Compassionate Leave', 'Study Leave']
    }

    # Create and populate each list table if needed
    for table_name, defaults in list_tables.items():
        cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
        cur.execute(f"SELECT COUNT(*) FROM {table_name}")
        if cur.fetchone()[0] == 0 and defaults:
            cur.executemany(f"INSERT OR IGNORE INTO {table_name} (name) VALUES (?)", [(v,) for v in defaults])

    # Add sample students if the students table is empty
    cur.execute("SELECT COUNT(*) FROM students")
    if cur.fetchone()[0] == 0:
        print("Adding sample students...")
        sample_students = [
            ('1001', 'Ali Khan', 'Ahmed Khan', 'Street 1, Peshawar', '1990-01-01', 'Male', 'Pakistan', 'Peshawar', '03001234567', '03001234567', 'Main Campus', 'KPK Medical Faculty', 'Dip-Anesthesia', '1st Semester', 'Active', None, 'Paid', 'Some remarks', datetime.now().isoformat()),
            ('1002', 'Sara Bibi', 'Gul Khan', 'Street 2, Mardan', '1992-05-15', 'Female', 'Pakistan', 'Mardan', '03017654321', '03017654321', 'Girl Campus', 'PNC Board', 'BS Nursing', '2nd Semester', 'Active', None, 'Paid', 'Good student', datetime.now().isoformat()),
            ('1003', 'Usman Ali', 'Akbar Khan', 'Street 3, Swat', '1991-11-20', 'Male', 'Pakistan', 'Swat', '03021122334', '03021122334', 'Main Campus', 'KPK Medical Faculty', 'Dip-Cardiology', '1st Semester', 'Active', None, 'Free', 'Needs attention', datetime.now().isoformat()),
            ('1004', 'Fatima Zahra', 'Muhammad Khan', 'Street 4, Charsadda', '1993-03-10', 'Female', 'Pakistan', 'Charsadda', '03039876543', '03039876543', 'Girl Campus', 'PNC Board', 'L.H.V', '1st year', 'Active', None, 'Paid', 'Regular', datetime.now().isoformat()),
            ('1005', 'Zainab Khan', 'Imran Khan', 'Street 5, Peshawar', '1994-07-22', 'Female', 'Pakistan', 'Peshawar', '03045566778', '03045566778', 'BS Campus', 'KMU', 'BS-MLT', '3rd Semester', 'Active', None, 'Paid', 'Excellent', datetime.now().isoformat()),
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
        cur.executemany(
            'INSERT INTO students (admission_no, name, father_name, address, dob, gender, nationality, district, phone, sms_phone, campus, board, technology, semester, status, photo_path, student_type, remarks, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            sample_students
        )

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # This allows the database to be initialized from the command line
    print("Initializing database...")
    init_db()
    print("Database initialized successfully.")
