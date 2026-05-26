import bcrypt
from database.engine import SessionLocal
from database.models import User

def add_admin():
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter_by(username='admin').first()
        if not admin_user:
            admin = User(
                username="admin",
                email="admin@example.com",
                password_hash=bcrypt.hashpw("1234".encode(), bcrypt.gensalt()).decode(),
                role="admin",
                full_name="System Administrator",
                avatar_emoji="🛠️"
            )
            db.add(admin)
            db.commit()
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")
    except Exception as e:
        print(f"Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == '__main__':
    add_admin()
