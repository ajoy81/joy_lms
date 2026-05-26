import streamlit as st
from database.engine import SessionLocal
from database.models import User, UserRelation, Course, ActivityLog, Enrollment
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from components.cards import render_user_card
from modules.courses import show_course_builder
from modules.homework import show_homework_grading
from modules.analytics import show_analytics
from datetime import datetime
import pytz

def show_teacher_dashboard(user):
    render_navbar()
    selection = render_sidebar()
    
    if selection == "Course Management":
        tab1, tab2 = st.tabs(["🌐 Course Explorer", "🏗️ Course Builder"])
        with tab1:
            from modules.courses import show_course_explorer
            show_course_explorer(user)
        with tab2:
            show_course_builder(user)
        return
    elif selection == "Homework Grading":
        show_homework_grading(user)
        return
    elif selection == "Analytics":
        db = SessionLocal()
        child_ids = [r.child_id for r in db.query(UserRelation).filter_by(guardian_id=user.id).all()]
        db.close()
        show_analytics(user, child_ids)
        return
    elif selection == "User Profiles":
        from modules.profile import show_user_profiles_directory
        show_user_profiles_directory(user)
        return
    elif selection == "My Profile":
        from modules.profile import show_my_profile
        show_my_profile(user)
        return
        
    # Overview (Default)
    st.markdown(f"## 👨‍🏫 Welcome, {user.full_name or user.username}!")
    
    db = SessionLocal()
    try:
        # Stats
        relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
        child_ids = [r.child_id for r in relations]
        total_students = len(child_ids)
        total_courses = db.query(Course).filter_by(created_by=user.id).count()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("My Students", total_students)
            if st.button("Manage Students", key="drill_teacher_students", use_container_width=True):
                st.session_state['pending_nav'] = "Manage Users"
                st.rerun()
        with col2:
            st.metric("My Courses", total_courses)
            if st.button("Manage Courses", key="drill_teacher_courses", use_container_width=True):
                st.session_state['pending_nav'] = "Course Management"
                st.rerun()
        
        # Today's active
        today_start = datetime.now(pytz.utc).replace(hour=0, minute=0, second=0)
        active_today = db.query(ActivityLog).filter(ActivityLog.user_id.in_(child_ids), ActivityLog.timestamp >= today_start).distinct(ActivityLog.user_id).count()
        with col3:
            st.metric("Active Today", active_today)
            if st.button("View Analytics", key="drill_teacher_analytics", use_container_width=True):
                st.session_state['pending_nav'] = "Analytics"
                st.rerun()
        
        st.markdown("---")
        
        # Link Children
        st.markdown("### 🔗 Link a Student")
        with st.form("link_student_form"):
            student_username = st.text_input("Student Username")
            if st.form_submit_button("Link Student"):
                student = db.query(User).filter_by(username=student_username, role="child").first()
                if not student:
                    st.error("Student not found.")
                else:
                    from database.models import UserInstitute
                    active_inst = st.session_state.get('active_institute_id')
                    if active_inst:
                        is_in_inst = db.query(UserInstitute).filter_by(user_id=student.id, institute_id=active_inst).first()
                        if not is_in_inst:
                            st.error("This student does not belong to your institute.")
                            st.stop()
                            
                    existing = db.query(UserRelation).filter_by(guardian_id=user.id, child_id=student.id).first()
                    if existing:
                        st.warning("Student is already linked to you.")
                    else:
                        new_rel = UserRelation(guardian_id=user.id, child_id=student.id, relation_type="teacher", created_at=datetime.now(pytz.utc))
                        db.add(new_rel)
                        db.commit()
                        st.success(f"Successfully linked {student.username}!")
                        st.rerun()
                        
        st.markdown("---")
        
        # Manage Users (Linked Children)
        st.markdown("### 👥 My Students")
        if not child_ids:
            st.info("You haven't linked any students yet.")
        else:
            students = db.query(User).filter(User.id.in_(child_ids)).all()
            for student in students:
                with st.expander(f"{student.avatar_emoji} {student.username} - {student.full_name or ''}"):
                    enrollments = db.query(Enrollment).filter_by(child_id=student.id).all()
                    st.write(f"**Enrolled Courses:** {len(enrollments)}")
                    last_log = db.query(ActivityLog).filter_by(user_id=student.id).order_by(ActivityLog.timestamp.desc()).first()
                    st.write(f"**Last Active:** {last_log.timestamp.strftime('%Y-%m-%d %H:%M') if last_log else 'Never'}")
                    
    finally:
        db.close()
