import sqlite3
import os
from config import BASE_DIR

db_path = os.path.join(BASE_DIR, 'ajoy_academy.db')
print(f"Connecting to database at: {db_path}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current columns in lesson_progresses
cursor.execute("PRAGMA table_info(lesson_progresses)")
columns = [row[1] for row in cursor.fetchall()]
print("Current columns:", columns)

if 'watch_percentage' not in columns:
    print("Adding watch_percentage column...")
    cursor.execute("ALTER TABLE lesson_progresses ADD COLUMN watch_percentage FLOAT DEFAULT 0.0")
    conn.commit()

if 'last_accessed_at' not in columns:
    print("Adding last_accessed_at column...")
    cursor.execute("ALTER TABLE lesson_progresses ADD COLUMN last_accessed_at DATETIME")
    conn.commit()

print("Migration completed successfully.")
conn.close()
