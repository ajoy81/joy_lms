import os
import sys
import sqlite3

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ajoy_academy.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE courses ADD COLUMN institute_id INTEGER REFERENCES institutes(id);")
    conn.commit()
    print("Successfully added institute_id to courses.")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
