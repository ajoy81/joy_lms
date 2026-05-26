import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'ajoy_academy.db')

def add_quiz_results_column():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("ALTER TABLE lesson_progresses ADD COLUMN quiz_results JSON;")
        print("Successfully added quiz_results column to lesson_progresses table.")
    except sqlite3.OperationalError as e:
        print(f"OperationalError (column might already exist): {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    add_quiz_results_column()
