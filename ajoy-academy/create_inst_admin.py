import os
import sys
import bcrypt
from datetime import datetime
import pytz

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.engine import SessionLocal
from database.models import User, Institute, UserInstitute

db = SessionLocal()
try:
    username = "parental_admin"
    password = "1234"
    role = "institute_admin"
    
    inst = db.query(Institute).filter_by(name="Parental").first()
    if not inst:
        print("Parental institute not found.")
        sys.exit(1)
        
    existing = db.query(User).filter_by(username=username).first()
    if existing:
        print("parental_admin already exists.")
    else:
        new_user = User(
            username=username,
            email="parental_admin@example.com",
            password_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode(),
            role=role,
            full_name="Parental Admin",
            avatar_emoji="🛠️",
            created_at=datetime.now(pytz.utc)
        )
        db.add(new_user)
        db.commit()
        db.add(UserInstitute(user_id=new_user.id, institute_id=inst.id))
        db.commit()
        print("Created parental_admin successfully.")
        
    # Update user_password.md
    file_path = r"D:\A_LMS\Dev_plan\user_password.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        table_start_idx = -1
        for i, line in enumerate(lines):
            if "| Role | Username | Password |" in line:
                table_start_idx = i
                break
                
        if table_start_idx != -1:
            user_row_idx = -1
            for i in range(table_start_idx + 2, len(lines)):
                if not lines[i].strip().startswith("|"):
                    break 
                if f"`{username}`" in lines[i]:
                    user_row_idx = i
                    break
                    
            if user_row_idx != -1:
                parts = lines[user_row_idx].split("|")
                if len(parts) >= 4:
                    parts[3] = f" `{password}` "
                    lines[user_row_idx] = "|".join(parts)
            else:
                end_idx = table_start_idx + 2
                while end_idx < len(lines) and lines[end_idx].strip().startswith("|"):
                    end_idx += 1
                new_row = f"| **{role.replace('_', ' ').capitalize()}** | `{username}` | `{password}` | Parental |\n"
                lines.insert(end_idx, new_row)
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            print("user_password.md updated.")
    except Exception as e:
        print(f"Failed to update password file: {e}")

finally:
    db.close()
