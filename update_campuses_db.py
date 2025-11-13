import sqlite3
from config import DB_NAME

def update_campus_names():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Define the desired list of campus names
    desired_campuses = ['Main Campus', 'Girl Campus', 'BS Campus', 'Nursing Campus']

    # Get existing campus names from the database
    cursor.execute("SELECT name FROM campuses")
    existing_campuses = {row[0] for row in cursor.fetchall()}

    # Identify campuses to remove
    campuses_to_remove = existing_campuses - set(desired_campuses)
    # Identify campuses to add
    campuses_to_add = set(desired_campuses) - existing_campuses

    print("Synchronizing campus names in the 'campuses' table...")

    # Remove unwanted campuses
    for campus_name in campuses_to_remove:
        try:
            # First, update student records that reference this campus to NULL
            cursor.execute("UPDATE students SET campus = NULL WHERE campus = ?", (campus_name,))
            print(f"Updated {cursor.rowcount} student records from campus '{campus_name}' to NULL.")

            # Then, delete the campus from the campuses table
            cursor.execute("DELETE FROM campuses WHERE name = ?", (campus_name,))
            print(f"Removed campus '{campus_name}' from 'campuses' table.")
        except sqlite3.Error as e:
            print(f"Error removing campus '{campus_name}': {e}")

    # Add new campuses
    for campus_name in campuses_to_add:
        try:
            cursor.execute("INSERT INTO campuses (name) VALUES (?)", (campus_name,))
            print(f"Added campus '{campus_name}' to 'campuses' table.")
        except sqlite3.IntegrityError:
            print(f"Campus '{campus_name}' already exists, skipping insertion.")
        except sqlite3.Error as e:
            print(f"Error adding campus '{campus_name}': {e}")

    conn.commit()
    conn.close()
    print("\nDatabase synchronization complete.")
    print("Student records associated with removed campuses have been set to NULL.")

if __name__ == "__main__":
    update_campus_names()
