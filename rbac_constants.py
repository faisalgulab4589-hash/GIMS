"""
Central definitions for RBAC modules, default roles, and permission rules.
This keeps database seeding and runtime checks in sync.
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass(frozen=True)
class ModuleDefinition:
    key: str
    label: str
    description: str


DEFAULT_MODULES: List[ModuleDefinition] = [
    ModuleDefinition("admissions", "Admissions", "Student intake, biodata, imports, and promotions"),
    ModuleDefinition("fees", "Fees", "Fee collection and receipt issuance"),
    ModuleDefinition("payroll", "Payroll", "Employee payroll, allowances, and deductions"),
    ModuleDefinition("expenses", "Expenses", "Operational and academic expense tracking"),
    ModuleDefinition("dmc", "Exam & DMC", "Midterm exams, registration, DMC and result preparation"),
    ModuleDefinition("inventory", "Inventory", "Inventory, assets, and requisitions"),
    ModuleDefinition("reports", "Reports", "Analytics, summaries, and exports"),
    ModuleDefinition("vendors", "Vendors", "Vendor master data and procurement"),
    ModuleDefinition("attendance", "Attendance", "Student/staff attendance entry and overview"),
    ModuleDefinition("documents", "Documents", "Student documents, certificates, and ID cards"),
]


DEFAULT_ROLE_PERMISSIONS: Dict[str, Dict[str, object]] = {
    "Admin": {
        "description": "Full-access system administrator",
        "modules": [m.key for m in DEFAULT_MODULES],
        "is_system": True,
    },
    "Receptionist": {
        "description": "Front-desk operations for admissions and fee collection",
        "modules": ["admissions", "fees", "documents"],
        "is_system": True,
    },
    "Accounts": {
        "description": "Payroll, expense, and vendor management",
        "modules": ["payroll", "expenses", "vendors", "reports"],
        "is_system": True,
    },
    "Exam Section": {
        "description": "Exam scheduling, DMC generation, and academic reports",
        "modules": ["dmc", "reports", "documents"],
        "is_system": True,
    },
    "Clerk": {
        "description": "Student documents and admissions follow ups",
        "modules": ["documents", "admissions"],
        "is_system": True,
    },
    "Principal": {
        "description": "Institution head with reporting and attendance visibility",
        "modules": ["reports", "attendance", "admissions"],
        "is_system": True,
    },
}


# Route-to-module guard definitions used by before_request hook.
ROUTE_PERMISSION_RULES = [
    {
        "module": "inventory",
        "prefixes": [
            "/api/inventory",
            "/inventory",
        ],
    },
    {
        "module": "payroll",
        "prefixes": [
            "/api/deductions",
            "/api/payroll",
            "/api/employee_reports/payroll_summary",
        ],
    },
    {
        "module": "reports",
        "prefixes": [
            "/reports_page",
            "/free_students_report",
            "/api/report",
            "/api/student_count",
            "/api/active_student_count",
            "/api/students_by",
            "/api/students_for_sms_group",
            "/api/search_students_for_sms",
        ],
    },
    {
        "module": "admissions",
        "prefixes": [
            "/api/students",
            "/import_excel_web",
            "/import_biodata_excel",
            "/api/promote",
            "/api/demote",
            "/api/promote_selected_students",
            "/api/demote_selected_students",
            "/api/students_for_promotion",
            "/api/promote_students",
            "/api/demote_students",
            "/api/students_for_demotion",
        ],
    },
    {
        "module": "attendance",
        "prefixes": [
            "/attendance",
            "/api/attendance",
        ],
    },
    {
        "module": "dmc",
        "prefixes": [
            "/api/dmc",
            "/dmc",
            "/student_exam",
        ],
    },
]

