import streamlit as st
from functools import wraps
from database.engine import SessionLocal
from database.models import User, UserRelation, Course
from auth.session import is_logged_in, get_current_user

def require_role(*roles):
    """
    Decorator to protect views based on role.
    Example: @require_role('teacher', 'parent')
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not is_logged_in():
                st.warning("Please login to access this page.")
                st.stop()
            
            user = get_current_user()
            if not user or (user.role not in roles and user.role != 'admin'):
                st.error("You do not have permission to access this page.")
                st.stop()
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

def can_manage_child(user_id, child_id):
    db = SessionLocal()
    try:
        relation = db.query(UserRelation).filter_by(guardian_id=user_id, child_id=child_id).first()
        return relation is not None
    finally:
        db.close()

def is_course_creator(user_id, course_id):
    db = SessionLocal()
    try:
        course = db.query(Course).filter_by(id=course_id, created_by=user_id).first()
        return course is not None
    finally:
        db.close()

def get_linked_children(user_id):
    db = SessionLocal()
    try:
        relations = db.query(UserRelation).filter_by(guardian_id=user_id).all()
        child_ids = [r.child_id for r in relations]
        children = db.query(User).filter(User.id.in_(child_ids)).all()
        for child in children:
            db.expunge(child)
        return children
    finally:
        db.close()

def get_linked_guardians(child_id):
    db = SessionLocal()
    try:
        relations = db.query(UserRelation).filter_by(child_id=child_id).all()
        guardian_ids = [r.guardian_id for r in relations]
        guardians = db.query(User).filter(User.id.in_(guardian_ids)).all()
        for guardian in guardians:
            db.expunge(guardian)
        return guardians
    finally:
        db.close()
