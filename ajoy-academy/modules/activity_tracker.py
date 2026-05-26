from database.engine import SessionLocal
from database.models import ActivityLog
from datetime import datetime
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def log_activity(user_id, action_type, session_duration_minutes=None, metadata=None, ip_address=None):
    db = SessionLocal()
    try:
        log = ActivityLog(
            user_id=user_id,
            action_type=action_type,
            metadata=metadata,
            session_duration_minutes=session_duration_minutes,
            ip_address=ip_address,
            timestamp=utcnow()
        )
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error logging activity: {e}")
    finally:
        db.close()
