import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.engine import Base, engine, SessionLocal
from database.models import Institute

# Create new tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    initial_institutes = ["Joy LMS", "Parental", "ATI GOA", "DIA"]
    for name in initial_institutes:
        existing = db.query(Institute).filter_by(name=name).first()
        if not existing:
            print(f"Creating Institute: {name}")
            db.add(Institute(name=name))
    db.commit()
    print("Database seeded with institutes.")
finally:
    db.close()
