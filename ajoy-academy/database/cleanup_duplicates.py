import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.engine import SessionLocal
from database.models import Course

def cleanup_duplicates():
    db = SessionLocal()
    try:
        courses = db.query(Course).order_by(Course.id).all()
        seen = set()
        deleted_count = 0
        for c in courses:
            key = (c.title, c.created_by)
            if key in seen:
                print(f"Deleting duplicate course ID {c.id}: {c.title}")
                db.delete(c)
                deleted_count += 1
            else:
                seen.add(key)
        db.commit()
        print(f"Cleanup complete. Deleted {deleted_count} duplicate courses.")
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_duplicates()
