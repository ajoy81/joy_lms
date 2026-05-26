import sqlite3

def upgrade_db():
    conn = sqlite3.connect('ajoy_academy.db')
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE enrollments ADD COLUMN assignment_type VARCHAR(20) DEFAULT 'Suggested';")
        print("Added assignment_type to enrollments.")
    except sqlite3.OperationalError as e:
        print("enrollments change:", e)

    try:
        cursor.execute("ALTER TABLE lessons ADD COLUMN video_file_path VARCHAR(500);")
        print("Added video_file_path to lessons.")
    except sqlite3.OperationalError as e:
        print("lessons video_file_path change:", e)

    try:
        cursor.execute("ALTER TABLE lessons ADD COLUMN quiz_data JSON;")
        print("Added quiz_data to lessons.")
    except sqlite3.OperationalError as e:
        print("lessons quiz_data change:", e)

    conn.commit()
    conn.close()

if __name__ == '__main__':
    upgrade_db()
