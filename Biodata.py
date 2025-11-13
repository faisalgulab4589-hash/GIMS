# biodata.py
# Full Biodata form implementation
# - Loads dropdown lists from DB (editable later)
# - Validates phone numbers (11 digits, Pakistan mobile like 03xxxxxxxxx)
# - Saves student record to students table (admission_no is required)
# - Single admission form file per student (saved to students_files/<AdmissionNo>/admission_form.<ext>)
# - Image preview for images, filename shown for PDFs/others
# - Open file and Delete file (with confirmation)

import os
import shutil
import subprocess
from pathlib import Path

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QFileDialog, QMessageBox, QComboBox, QTextEdit, QDateEdit, QGridLayout
)
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
from PyQt5.QtGui import QPixmap, QPainter, QFont
from PyQt5.QtCore import QDate

# Corrected imports to match the new project structure
from db import get_connection
from config import FILES_DIR
from import_students_from_excel import import_students_from_excel # Import the excel import function

# ensure files dir exists
Path(FILES_DIR).mkdir(parents=True, exist_ok=True)

# helper: ensure dropdown-list tables exist and provide defaults if empty
def ensure_list_table(table_name, defaults):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (id INTEGER PRIMARY KEY, name TEXT UNIQUE)")
    conn.commit()
    cur.execute(f"SELECT COUNT(*) FROM {table_name}")
    cnt = cur.fetchone()[0]
    if cnt == 0 and defaults:
        for v in defaults:
            try:
                cur.execute(f"INSERT INTO {table_name} (name) VALUES (?)", (v,))
            except Exception:
                pass
        conn.commit()
    conn.close()

# load values from a list table
def load_list(table_name):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT name FROM {table_name} ORDER BY name")
        rows = [r[0] for r in cur.fetchall()]
    except Exception:
        rows = []
    conn.close()
    return rows

# initialize list tables with some sensible defaults
ensure_list_table('genders', ['Male', 'Female', 'Other'])
ensure_list_table('nationalities', ['Pakistan'])
ensure_list_table('districts', ['Peshawar', 'Mardan', 'Swat', 'Charsadda', 'Other'])
ensure_list_table('boards', ['KPK Medical Faculty', 'PNC Board', 'Pharmacy Council', 'KMU'])
ensure_list_table('technologies', ['BS Nursing', 'Dip-Pathology', 'BS-MLT', 'DPT', 'Dip-Anesthesia', 'Dip-Cardiology', 'Dip-Health', 'Dip-Pharmacy', 'Dip-Radiology', 'Dip-Surgical', 'Dip-Dialysis', 'Dip-Physiotherapy', 'Pharmacy-B', 'BS-Anesthesia', 'BS-Health', 'BS-Cardiology', 'BS-Surgical', 'BS-Radiology', 'BS-Emergency Care'])
ensure_list_table('semesters', ['1st Semester', '2nd Semester', '3rd Semester', '4th Semester', '5th Semester', '6th Semester', '7th Semester', '8th Semester', '9th Semester', '10th Semester', '1st year', '2nd year', 'Sept-2023', 'Sept-2024', 'Sept-2025'])
ensure_list_table('campuses', ['Main Campus', 'Girl Campus', 'BS Campus', 'Nursing Campus'])
ensure_list_table('student_types', ['Paid', 'Free']) # Added for student type


class BioDataForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ghazali Institute of Medical Sciences, Peshawar")
        self.file_path = None
        self.admission_no_field = QLineEdit()
        self.init_ui()
        self.admission_no_field.editingFinished.connect(self.load_student_on_enter)

    def init_ui(self):
        # Top: Status combo (right aligned)
        self.status_combo = QComboBox()
        self.status_combo.addItems(['Active', 'Course Completed', 'Left', 'Demoted'])

        top_h = QHBoxLayout()
        top_h.addStretch()
        top_h.addWidget(QLabel('Students Status:'))
        top_h.addWidget(self.status_combo)

        # Form fields
        self.name = QLineEdit()
        self.fname = QLineEdit()
        self.address = QTextEdit()
        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate())

        self.gender = QComboBox()
        self.gender.addItems(load_list('genders'))
        self.nationality = QComboBox()
        self.nationality.addItems(load_list('nationalities'))
        self.district = QComboBox()
        self.district.addItems(load_list('districts'))

        self.campus = QComboBox()
        self.campus.addItems(load_list('campuses'))

        self.phone = QLineEdit()
        self.sms_phone = QLineEdit()

        self.board = QComboBox()
        self.board.addItems(load_list('boards'))
        self.technology = QComboBox()
        self.technology.addItems(load_list('technologies'))
        self.semester = QComboBox()
        self.semester.addItems(load_list('semesters'))

        self.student_type = QComboBox()
        self.student_type.addItems(load_list('student_types'))

        # File upload widgets
        self.upload_btn = QPushButton('Upload Admission Picture')
        self.upload_btn.clicked.connect(self.upload_file)
        self.image_preview = QLabel('No File Selected')
        self.open_btn = QPushButton('Open File')
        self.open_btn.setEnabled(False)
        self.open_btn.clicked.connect(self.open_file)
        self.delete_btn = QPushButton('Delete File')
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_file)

        # Buttons: Save / Clear
        self.add_student_btn = QPushButton('Add Student')
        self.add_student_btn.clicked.connect(self.save_student)
        self.save_btn = QPushButton('SAVE')
        self.save_btn.clicked.connect(self.save_student)
        self.clear_btn = QPushButton('RESET')
        self.clear_btn.clicked.connect(self.clear_form)
        self.print_btn = QPushButton('Print')
        self.print_btn.clicked.connect(self.print_biodata)

        # Layout assembly using a grid for a cleaner look
        layout = QVBoxLayout(self)
        layout.addLayout(top_h)

        grid = QGridLayout()
        # Admission No with a Load button
        adm_h_layout = QHBoxLayout()
        adm_h_layout.addWidget(self.admission_no_field)
        load_btn = QPushButton('Load')
        load_btn.clicked.connect(self.load_student)
        adm_h_layout.addWidget(load_btn)

        # adding widgets to grid
        grid.addWidget(QLabel('Admission No / Adm No *'), 0, 0)
        grid.addLayout(adm_h_layout, 0, 1)
        grid.addWidget(QLabel('Name / Naam'), 1, 0)
        grid.addWidget(self.name, 1, 1)
        grid.addWidget(QLabel("Father's Name"), 2, 0)
        grid.addWidget(self.fname, 2, 1)
        grid.addWidget(QLabel('Address'), 3, 0)
        grid.addWidget(self.address, 3, 1)
        grid.addWidget(QLabel('D.O.B (YYYY-MM-DD)'), 4, 0)
        grid.addWidget(self.dob, 4, 1)
        grid.addWidget(QLabel('Gender'), 5, 0)
        grid.addWidget(self.gender, 5, 1)
        grid.addWidget(QLabel('Nationality'), 6, 0)
        grid.addWidget(self.nationality, 6, 1)
        grid.addWidget(QLabel('District'), 7, 0)
        grid.addWidget(self.district, 7, 1)
        grid.addWidget(QLabel('Campus'), 8, 0)
        grid.addWidget(self.campus, 8, 1)
        grid.addWidget(QLabel('Phone # (11 digits)'), 9, 0)
        grid.addWidget(self.phone, 9, 1)
        grid.addWidget(QLabel('SMS Phone # (11 digits)'), 10, 0)
        grid.addWidget(self.sms_phone, 10, 1)
        grid.addWidget(QLabel('Board'), 11, 0)
        grid.addWidget(self.board, 11, 1)
        grid.addWidget(QLabel('Technology / Program'), 12, 0)
        grid.addWidget(self.technology, 12, 1)
        grid.addWidget(QLabel('Semester / Session'), 13, 0)
        grid.addWidget(self.semester, 13, 1)
        grid.addWidget(QLabel('Student Type'), 14, 0) # New row for student type
        grid.addWidget(self.student_type, 14, 1) # New row for student type

        layout.addLayout(grid)

        # File upload and preview section
        file_v_layout = QVBoxLayout()
        file_v_layout.addWidget(self.upload_btn)
        file_v_layout.addWidget(self.image_preview)
        layout.addLayout(file_v_layout)

        # Bottom buttons
        # Bottom buttons (first row)
        action_btn_row = QHBoxLayout()
        action_btn_row.addWidget(self.add_student_btn)
        action_btn_row.addWidget(self.save_btn)
        action_btn_row.addWidget(self.clear_btn)
        action_btn_row.addWidget(self.open_btn)
        action_btn_row.addWidget(self.delete_btn)
        action_btn_row.addWidget(self.print_btn)
        layout.addLayout(action_btn_row)

        # Import from Excel button (second row)
        import_btn_row = QHBoxLayout()
        self.import_excel_btn = QPushButton('Import from Excel')
        self.import_excel_btn.clicked.connect(self.import_excel_students)
        import_btn_row.addStretch() # Push button to the right
        import_btn_row.addWidget(self.import_excel_btn)
        import_btn_row.addStretch() # Center the button
        layout.addLayout(import_btn_row)

    def import_excel_students(self):
        # Pass 'self' as the parent for QFileDialog and QMessageBox
        import_students_from_excel(self)

    def print_biodata(self):
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter()
            painter.begin(printer)
            
            # Set up fonts
            header_font = QFont('Arial', 16, QFont.Bold)
            label_font = QFont('Arial', 12, QFont.Bold)
            text_font = QFont('Arial', 12)

            # Start drawing
            y_position = 500
            
            # Title
            painter.setFont(header_font)
            painter.drawText(1000, y_position, "Ghazali Institute of Medical Sciences, Peshawar")
            y_position += 500

            # Student Details
            details = {
                "Admission No": self.admission_no_field.text(),
                "Name": self.name.text(),
                "Father's Name": self.fname.text(),
                "Address": self.address.toPlainText(),
                "Date of Birth": self.dob.date().toString('yyyy-MM-dd'),
                "Gender": self.gender.currentText(),
                "Campus": self.campus.currentText(),
                "Board": self.board.currentText(),
                "Semester/Year": self.semester.currentText(),
                "Technology/Program": self.technology.currentText(),
                "Phone #": self.phone.text(),
                "SMS Number": self.sms_phone.text(),
            }

            for label, text in details.items():
                painter.setFont(label_font)
                painter.drawText(500, y_position, f"{label}:")
                painter.setFont(text_font)
                painter.drawText(2000, y_position, text)
                y_position += 300

            # Student Picture (on a new page if available)
            if self.file_path and os.path.exists(self.file_path):
                lower = self.file_path.lower()
                if lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')):
                    printer.newPage() # Move to a new page for the image
                    pixmap = QPixmap(self.file_path)
                    if not pixmap.isNull():
                        # Scale pixmap to fit page width, maintaining aspect ratio
                        page_rect = printer.pageRect()
                        scaled_pixmap = pixmap.scaled(page_rect.size(), 
                                                     aspectRatioMode=1, # Qt.KeepAspectRatio
                                                     transformMode=1) # Qt.SmoothTransformation
                        # Center the image on the page
                        x = page_rect.x() + (page_rect.width() - scaled_pixmap.width()) / 2
                        y = page_rect.y() + (page_rect.height() - scaled_pixmap.height()) / 2
                        painter.drawPixmap(int(x), int(y), scaled_pixmap)
                    else:
                        # If pixmap is null, just show filename on new page
                        printer.newPage()
                        painter.setFont(text_font)
                        painter.drawText(500, 500, f"Admission Picture: {Path(self.file_path).name}")
                elif lower.endswith('.pdf'):
                    # For PDFs, inform the user that it will not be printed directly
                    printer.newPage()
                    painter.setFont(text_font)
                    painter.drawText(500, 500, f"Admission Form (PDF): {Path(self.file_path).name}")
                    painter.drawText(500, 800, "PDF files cannot be directly embedded in this printout.")
                    painter.drawText(500, 1100, "Please open and print the PDF separately using the 'Open File' button.")
                else:
                    # For other file types, just show filename on new page
                    printer.newPage()
                    painter.setFont(text_font)
                    painter.drawText(500, 500, f"Admission File: {Path(self.file_path).name}")

            painter.end()
            QMessageBox.information(self, 'Print', 'Sent to printer.')

    # ---------------- File handling ----------------
    def upload_file(self):
        # allow many common types; preview images only
        fname, _ = QFileDialog.getOpenFileName(self, 'Select Admission Picture', '',
                                              'All Files (*.*);;Images (*.png *.jpg *.jpeg *.bmp);;PDF Files (*.pdf)')
        if not fname:
            return
        adm = self.admission_no_field.text().strip()
        if not adm:
            QMessageBox.warning(self, 'Admission No Required', 'Please enter Admission No before uploading file.')
            return
        folder = Path(FILES_DIR) / adm
        folder.mkdir(parents=True, exist_ok=True)
        ext = Path(fname).suffix
        dest = folder / f'admission_form{ext}'
        try:
            shutil.copy2(fname, dest)
            self.file_path = str(dest)
            self.show_preview()
            QMessageBox.information(self, 'Uploaded', f'File saved to: {dest}')
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Could not copy file: {e}')

    def show_preview(self):
        if not self.file_path:
            self.image_preview.setText('No File Selected')
            self.open_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        lower = self.file_path.lower()
        if lower.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')):
            try:
                pix = QPixmap(self.file_path)
                if not pix.isNull():
                    pix = pix.scaledToWidth(300)
                    self.image_preview.setPixmap(pix)
                else:
                    self.image_preview.setText(Path(self.file_path).name)
            except Exception:
                self.image_preview.setText(Path(self.file_path).name)
        else:
            # PDF or other - show filename
            self.image_preview.setText(Path(self.file_path).name + ' (Preview not available)')
        self.open_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)

    def open_file(self):
        if not self.file_path or not os.path.exists(self.file_path):
            QMessageBox.warning(self, 'File not found', 'File does not exist on disk.')
            return
        try:
            if os.name == 'nt':
                os.startfile(self.file_path)
            else:
                subprocess.Popen(['xdg-open', self.file_path])
        except Exception as e:
            QMessageBox.warning(self, 'Open Failed', str(e))

    def delete_file(self):
        if not self.file_path:
            return
        reply = QMessageBox.question(self, 'Confirm Delete', 'Delete this file? Are you sure?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(self.file_path)
                # if folder empty remove folder
                folder = Path(self.file_path).parent
                self.file_path = None
                self.image_preview.setText('No File Selected')
                self.open_btn.setEnabled(False)
                self.delete_btn.setEnabled(False)
                try:
                    if not any(folder.iterdir()):
                        folder.rmdir()
                except Exception:
                    pass
                QMessageBox.information(self, 'Deleted', 'File deleted successfully')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not delete file: {e}')

    # ---------------- Validation ----------------
    def _valid_phone(self, num):
        if not num:
            return True  # allow empty phone
        if not num.isdigit():
            return False
        return len(num) == 11 and num.startswith('03')

    # ---------------- Load / Save / Clear ----------------
    def load_student_on_enter(self):
        # convenience: load student if admission no is typed and enter is pressed
        self.load_student()

    def load_student(self):
        adm = self.admission_no_field.text().strip()
        if not adm:
            self.clear_form()
            return
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE admission_no=?", (adm,))
        student = cur.fetchone()
        conn.close()
        if not student:
            self.clear_form(clear_admission=False) # keep adm no
            QMessageBox.information(self, 'Not Found', 'No student found with this admission number.')
            return

        # Unpack student data from the dictionary-like row object
        self.name.setText(student['name'])
        self.fname.setText(student['father_name'])
        self.address.setPlainText(student['address'])
        self.dob.setDate(QDate.fromString(student['dob'], 'yyyy-MM-dd'))
        self.gender.setCurrentText(student['gender'])
        self.nationality.setCurrentText(student['nationality'])
        self.district.setCurrentText(student['district'])
        self.campus.setCurrentText(student['campus'])
        self.phone.setText(student['phone'])
        self.sms_phone.setText(student['sms_phone'])
        self.board.setCurrentText(student['board'])
        self.technology.setCurrentText(student['technology'])
        self.semester.setCurrentText(student['semester'])
        self.status_combo.setCurrentText(student['status'])
        self.student_type.setCurrentText(student['student_type']) # Load student type
        self.file_path = student['photo_path']
        self.show_preview()

    def save_student(self):
        adm = self.admission_no_field.text().strip()
        if not adm:
            QMessageBox.warning(self, 'Admission No Required', 'Admission number is required to save record.')
            return
        name = self.name.text().strip()
        phone = self.phone.text().strip()
        sms_phone = self.sms_phone.text().strip()

        # Phone validation: only validate if phone is not empty
        if phone and not self._valid_phone(phone):
            QMessageBox.warning(self, 'Phone Invalid', 'Phone number must be 11 digits and start with 03... (or leave empty)')
            return
        if sms_phone and not self._valid_phone(sms_phone):
            QMessageBox.warning(self, 'SMS Phone Invalid', 'SMS Phone number must be 11 digits and start with 03... (or leave empty)')
            return

        # prepare data
        data = {
            'admission_no': adm,
            'name': name,
            'father_name': self.fname.text().strip(),
            'address': self.address.toPlainText().strip(),
            'dob': self.dob.date().toString('yyyy-MM-dd'),
            'gender': self.gender.currentText(),
            'nationality': self.nationality.currentText(),
            'district': self.district.currentText(),
            'campus': self.campus.currentText(),
            'phone': phone,
            'sms_phone': sms_phone,
            'board': self.board.currentText(),
            'technology': self.technology.currentText(),
            'semester': self.semester.currentText(),
            'status': self.status_combo.currentText(),
            'photo_path': self.file_path,
            'student_type': self.student_type.currentText() # Added student type
        }

        conn = get_connection()
        cur = conn.cursor()

        # Check if student exists
        cur.execute("SELECT id FROM students WHERE admission_no=?", (adm,))
        exists = cur.fetchone()

        try:
            if exists:
                # Confirm update
                reply = QMessageBox.question(self, 'Confirm Update',
                                             'A student with this admission number already exists. Do you want to update it?',
                                             QMessageBox.Yes | QMessageBox.No)
                if reply == QMessageBox.Yes:
                    cur.execute('''UPDATE students SET 
                                    name=:name, father_name=:father_name, address=:address, dob=:dob,
                                    gender=:gender, nationality=:nationality, district=:district, campus=:campus, phone=:phone,
                                    sms_phone=:sms_phone, board=:board, technology=:technology,
                                    semester=:semester, status=:status, photo_path=:photo_path, student_type=:student_type
                                 WHERE admission_no=:admission_no''', data)
                    conn.commit()
                    QMessageBox.information(self, 'Updated', 'Student record updated successfully')
            else:
                # Insert new record
                data['created_at'] = QDate.currentDate().toString('yyyy-MM-dd')
                cur.execute('''INSERT INTO students (admission_no, name, father_name, address, dob, gender,
                                                   nationality, district, campus, phone, sms_phone, board, technology,
                                                   semester, status, photo_path, student_type, created_at)
                               VALUES (:admission_no, :name, :father_name, :address, :dob, :gender,
                                        :nationality, :district, :campus, :phone, :sms_phone, :board, :technology,
                                        :semester, :status, :photo_path, :student_type, :created_at)''', data)
                conn.commit()
                QMessageBox.information(self, 'Saved', 'Student record saved successfully')
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', f'Could not save record: {e}\n\nPlease ensure all required fields are filled correctly and try again.')
        finally:
            conn.close()

    def clear_form(self, clear_admission=True):
        if clear_admission:
            self.admission_no_field.clear()
        self.name.clear()
        self.fname.clear()
        self.address.clear()
        self.dob.setDate(QDate.currentDate())
        self.gender.setCurrentIndex(0)
        self.nationality.setCurrentIndex(0)
        self.district.setCurrentIndex(0)
        self.campus.setCurrentIndex(0)
        self.phone.clear()
        self.sms_phone.clear()
        self.board.setCurrentIndex(0)
        self.technology.setCurrentIndex(0)
        self.semester.setCurrentIndex(0)
        self.status_combo.setCurrentIndex(0)
        self.file_path = None
        self.image_preview.setText('No File Selected')
        self.open_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
