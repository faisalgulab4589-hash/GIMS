# Backend Plan for Dashboard Statistics

This plan outlines the necessary backend changes to support the new semester-wise and program-wise student count statistics on the dashboard.

**Assumptions:**
*   The application uses Flask.
*   Database interactions are handled via a `db.py` module or similar.
*   The student data is stored in a table (e.g., `students`) with columns for `semester` and `technology` (or program).

**1. Examine `main.py` and Database Structure:**
*   **Action:** Review `main.py` to understand the existing API route structure and database connection/query methods.
*   **Action:** Inspect `db.py` (or equivalent) and the database schema to identify the exact table and column names for student semester and program information.

**2. Implement `/api/students_by_semester` Endpoint:**
*   **Objective:** Create an API endpoint that returns a JSON object mapping semester names to student counts.
*   **Database Query (Conceptual):**
    ```sql
    SELECT semester, COUNT(*) FROM students GROUP BY semester ORDER BY semester;
    ```
*   **Python Implementation (Example):**
    ```python
    from flask import Flask, jsonify
    from db import get_db_connection # Assuming this function exists

    app = Flask(__name__)

    @app.route('/api/students_by_semester', methods=['GET'])
    def get_students_by_semester():
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Adjust table and column names based on actual schema
            cursor.execute("SELECT semester, COUNT(*) FROM students GROUP BY semester ORDER BY semester;")
            results = cursor.fetchall()

            semester_counts = {}
            for row in results:
                semester_name = row[0]
                count = row[1]
                # Map numerical semesters to names if necessary (e.g., '1' -> '1st')
                semester_counts[semester_name] = count

            return jsonify(semester_counts)
        except Exception as e:
            print(f"Error fetching students by semester: {e}")
            return jsonify({"error": "Could not retrieve semester counts"}), 500
        finally:
            if conn:
                conn.close()
    ```

**3. Implement `/api/students_by_program` Endpoint:**
*   **Objective:** Create an API endpoint that returns a JSON object mapping program names to student counts.
*   **Database Query (Conceptual):**
    ```sql
    SELECT technology, COUNT(*) FROM students GROUP BY technology ORDER BY technology;
    ```
*   **Python Implementation (Example):**
    ```python
    # ... (assuming previous imports and app setup)

    @app.route('/api/students_by_program', methods=['GET'])
    def get_students_by_program():
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Adjust table and column names based on actual schema
            cursor.execute("SELECT technology, COUNT(*) FROM students GROUP BY technology ORDER BY technology;")
            results = cursor.fetchall()

            program_counts = {}
            for row in results:
                program_name = row[0]
                count = row[1]
                program_counts[program_name] = count

            return jsonify(program_counts)
        except Exception as e:
            print(f"Error fetching students by program: {e}")
            return jsonify({"error": "Could not retrieve program counts"}), 500
        finally:
            if conn:
                conn.close()
    ```

**Next Steps:**
*   **Implement the outlined endpoints** in `main.py` or the appropriate backend file.
*   **Test the API endpoints** to ensure they return correct data.
*   **Verify the dashboard** displays the data correctly after the backend is functional.
