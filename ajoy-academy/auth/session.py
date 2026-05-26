import streamlit as st
from datetime import datetime
import pytz
from database.engine import SessionLocal
from database.models import User, ActivityLog

def utcnow():
    return datetime.now(pytz.utc)

def init_session():
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None
    if 'role' not in st.session_state:
        st.session_state['role'] = None
    if 'login_time' not in st.session_state:
        st.session_state['login_time'] = None
    if 'has_logged_out_this_session' not in st.session_state:
        st.session_state['has_logged_out_this_session'] = False

    if st.session_state['has_logged_out_this_session']:
        return
        
    # Check for persistent login cookie if not logged in
    if not st.session_state.get('user_id'):
        cookies = getattr(st.context, "cookies", {})
        token = cookies.get("ajoy_auth_token")
        if token:
            db = SessionLocal()
            try:
                user = db.query(User).filter(User.id == int(token)).first()
                if user and user.is_active:
                    st.session_state['user_id'] = user.id
                    st.session_state['username'] = user.username
                    st.session_state['role'] = user.role
                    st.session_state['login_time'] = utcnow().isoformat()
                    
                    if user.role in ['teacher', 'parent', 'institute_admin', 'child']:
                        from database.models import UserInstitute, Institute
                        ui = db.query(UserInstitute).filter_by(user_id=user.id).first()
                        if ui:
                            inst = db.query(Institute).get(ui.institute_id)
                            st.session_state['active_institute_id'] = inst.id
                            st.session_state['active_institute_name'] = inst.name
            except Exception as e:
                pass
            finally:
                db.close()

def login_user(user):
    st.session_state['user_id'] = user.id
    st.session_state['username'] = user.username
    st.session_state['role'] = user.role
    st.session_state['login_time'] = utcnow().isoformat()
    st.session_state['has_logged_out_this_session'] = False
    
    # Log Activity
    db = SessionLocal()
    try:
        log = ActivityLog(user_id=user.id, action_type='login', timestamp=utcnow())
        user_in_db = db.query(User).get(user.id)
        if user_in_db:
            user_in_db.last_login = utcnow()
        db.add(log)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Failed to log login: {e}")
    finally:
        db.close()

def logout_user():
    if is_logged_in():
        # Flush active lesson time if tracking
        current_lesson_id = st.session_state.get('current_lesson_id')
        start_time_str = st.session_state.get('current_lesson_started_at')
        if current_lesson_id and start_time_str:
            try:
                from modules.courses import save_lesson_duration
                now = utcnow()
                start_time = datetime.fromisoformat(start_time_str)
                elapsed = int((now - start_time).total_seconds())
                elapsed = min(elapsed, 900)
                if elapsed > 0:
                    save_lesson_duration(st.session_state['user_id'], current_lesson_id, elapsed)
            except Exception as e:
                print(f"Failed to flush active lesson on logout: {e}")

        db = SessionLocal()
        try:
            # Calculate duration
            login_time = datetime.fromisoformat(st.session_state['login_time'])
            duration = (utcnow() - login_time).total_seconds() / 60.0
            
            log = ActivityLog(
                user_id=st.session_state['user_id'], 
                action_type='logout', 
                session_duration_minutes=duration,
                timestamp=utcnow()
            )
            db.add(log)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Failed to log logout: {e}")
        finally:
            db.close()
            
    st.session_state['user_id'] = None
    st.session_state['username'] = None
    st.session_state['role'] = None
    st.session_state['login_time'] = None
    st.session_state['current_lesson_id'] = None
    st.session_state['current_lesson_started_at'] = None
    st.session_state['has_logged_out_this_session'] = True
    st.session_state['pending_cookie_remove'] = True

def get_current_user():
    if not is_logged_in():
        return None
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == st.session_state['user_id']).first()
        if user:
            db.expunge(user)
        return user
    finally:
        db.close()

def is_logged_in():
    return st.session_state.get('user_id') is not None
