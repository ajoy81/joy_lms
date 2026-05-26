import bcrypt
import sys
import os

# Ensure the parent directory is in the sys.path so we can import from database
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.engine import SessionLocal, init_db
from database.models import User, UserRelation

def add_test_users():
    db = SessionLocal()
    try:
        print("Adding test users...")
        
        # 1. Parent: monali
        monali = db.query(User).filter_by(username="monali").first()
        if not monali:
            monali = User(
                username="monali",
                email="monali@example.com",
                password_hash=bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
                role="parent",
                full_name="Monali (Parent)",
                avatar_emoji="👩"
            )
            db.add(monali)

        # 2. Teacher: rashi
        rashi = db.query(User).filter_by(username="rashi").first()
        if not rashi:
            rashi = User(
                username="rashi",
                email="rashi@example.com",
                password_hash=bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
                role="teacher",
                full_name="Rashi (Teacher)",
                avatar_emoji="👩‍🏫"
            )
            db.add(rashi)

        # 3. Kid: pablo
        pablo = db.query(User).filter_by(username="pablo").first()
        if not pablo:
            pablo = User(
                username="pablo",
                email="pablo@example.com",
                password_hash=bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
                role="child",
                full_name="Pablo (Kid)",
                avatar_emoji="👦"
            )
            db.add(pablo)

        db.commit()

        # Link them if not already linked
        if monali and pablo:
            link1 = db.query(UserRelation).filter_by(guardian_id=monali.id, child_id=pablo.id).first()
            if not link1:
                db.add(UserRelation(guardian_id=monali.id, child_id=pablo.id, relation_type="parent"))
                
        if rashi and pablo:
            link2 = db.query(UserRelation).filter_by(guardian_id=rashi.id, child_id=pablo.id).first()
            if not link2:
                db.add(UserRelation(guardian_id=rashi.id, child_id=pablo.id, relation_type="teacher"))
                
        db.commit()
        print("Test users added and linked successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error adding test users: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    add_test_users()
