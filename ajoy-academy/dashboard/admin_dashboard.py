import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import func, desc
from database.engine import SessionLocal
from database.models import User, Course, Enrollment, LessonProgress, ActivityLog, Lesson, Module
from auth.session import logout_user
from datetime import datetime, timedelta

from components.navbar import render_navbar
from components.sidebar import render_sidebar
from modules.user_management import show_user_management
from modules.courses import show_course_builder
from modules.analytics import show_analytics
from modules.timeline import show_timeline_feed
from modules.institutes import show_institutes_management

def show_admin_dashboard(user):
    render_navbar()
    selection = render_sidebar()

    if selection == "User Management":
        show_user_management(user)
        return
    elif selection == "Course Management":
        show_course_builder(user)
        return
    elif selection == "Analytics":
        db = SessionLocal()
        query = db.query(User).filter_by(role='child')
        active_inst = st.session_state.get('active_institute_id')
        if active_inst:
            from database.models import UserInstitute
            query = query.join(UserInstitute).filter(UserInstitute.institute_id == active_inst)
        child_ids = [c.id for c in query.all()]
        db.close()
        show_analytics(user, child_ids)
        return
    elif selection == "Timeline Moderation":
        show_timeline_feed(user)
        return
    elif selection == "Institutes":
        show_institutes_management(user)
        return
    elif selection == "User Profiles":
        from modules.profile import show_user_profiles_directory
        show_user_profiles_directory(user)
        return
    elif selection == "My Profile":
        from modules.profile import show_my_profile
        show_my_profile(user)
        return

    st.markdown(f"<h2>Welcome, {user.role.replace('_', ' ').capitalize()}>> <span style='color: #3b82f6;'>{user.full_name}!</span> 🛠️</h2>", unsafe_allow_html=True)

    if user.role == 'admin':
        tab1, tab2, tab3 = st.tabs(["📚 LMS Stats", "⚙️ System Performance", "🔐 Admin Control"])
    else:
        tab1, tab3 = st.tabs(["📚 LMS Stats", "🔐 Admin Control"])
        tab2 = None
    
    db = SessionLocal()
    
    try:
        # -----------------------------------------------------
        # TAB 1: LMS STATS
        # -----------------------------------------------------
        with tab1:
            st.subheader("Platform Overview")
            c1, c2, c3, c4 = st.columns(4)
            
            inst_id = st.session_state.get('active_institute_id')
            
            cq = db.query(Course)
            eq = db.query(Enrollment)
            if user.role == 'institute_admin' and inst_id:
                cq = cq.filter(Course.institute_id == inst_id)
                eq = eq.join(Course).filter(Course.institute_id == inst_id)
                
            total_users = db.query(User).count()
            total_courses = cq.count()
            total_enrollments = eq.count()
            total_lessons_completed = db.query(LessonProgress).filter_by(is_completed=True).count()
            
            with c1:
                st.metric("Total Users", total_users)
                if st.button("Manage Users", key="drill_admin_users", use_container_width=True):
                    st.session_state['pending_nav'] = "User Management"
                    st.rerun()
            with c2:
                st.metric("Total Courses", total_courses)
                if st.button("Manage Courses", key="drill_admin_courses", use_container_width=True):
                    st.session_state['pending_nav'] = "Course Management"
                    st.rerun()
            with c3:
                st.metric("Total Enrollments", total_enrollments)
                if st.button("View Courses", key="drill_admin_enroll", use_container_width=True):
                    st.session_state['pending_nav'] = "Course Management"
                    st.rerun()
            with c4:
                st.metric("Lessons Completed", total_lessons_completed)
                if st.button("View Analytics", key="drill_admin_analytics", use_container_width=True):
                    st.session_state['pending_nav'] = "Analytics"
                    st.rerun()
            
            st.markdown("---")
            if user.role == 'admin':
                cols = st.columns(4)
                col_a, col_b, col_c, col_d = cols[0], cols[1], cols[2], cols[3]
            else:
                cols = st.columns(3)
                col_a, col_b, col_c = cols[0], cols[1], cols[2]
            
            with col_a:
                st.markdown("#### 🏆 Top Courses")
                tc_q = db.query(Course.title, func.count(Enrollment.id).label('enrollment_count')).select_from(Course).join(Enrollment, Course.id == Enrollment.course_id)
                if user.role == 'institute_admin' and inst_id:
                    tc_q = tc_q.filter(Course.institute_id == inst_id)
                top_courses = tc_q.group_by(Course.id).order_by(desc('enrollment_count')).limit(5).all()
                
                if top_courses:
                    for idx, tc in enumerate(top_courses):
                        st.markdown(f"**{idx+1}. {tc.title}** - {tc.enrollment_count} enrollments")
                else:
                    st.info("No courses or enrollments yet.")
                    
            with col_b:
                st.markdown("#### 🌟 Top Lessons")
                top_lessons = db.query(
                    Lesson.title, func.count(LessonProgress.id).label('completion_count')
                ).select_from(Lesson).join(LessonProgress, Lesson.id == LessonProgress.lesson_id).filter(LessonProgress.is_completed == True).group_by(Lesson.id).order_by(desc('completion_count')).limit(5).all()
                
                if top_lessons:
                    for idx, tl in enumerate(top_lessons):
                        st.markdown(f"**{idx+1}. {tl.title}** - {tl.completion_count} completions")
                else:
                    st.info("No completed lessons yet.")
                    
            with col_c:
                st.markdown("#### 🥇 Top Students")
                # Top students based on completed lessons for simplicity, could also use rewards
                top_students = db.query(
                    User.full_name, User.username, func.count(LessonProgress.id).label('completions')
                ).select_from(User).join(LessonProgress, User.id == LessonProgress.child_id).filter(LessonProgress.is_completed == True, User.role == 'child').group_by(User.id).order_by(desc('completions')).limit(5).all()
                
                if top_students:
                    for idx, ts in enumerate(top_students):
                        name = ts.full_name or ts.username
                        st.markdown(f"**{idx+1}. {name}** - {ts.completions} lessons done")
                else:
                    st.info("No student activity yet.")
                    
            if user.role == 'admin':
                with col_d:
                    st.markdown("#### 🏫 Top Institutes")
                    from database.models import Institute, UserInstitute
                    top_institutes = db.query(
                        Institute.name, func.count(UserInstitute.id).label('user_count')
                    ).select_from(Institute).join(UserInstitute, Institute.id == UserInstitute.institute_id).group_by(Institute.id).order_by(desc('user_count')).limit(5).all()
                    
                    if top_institutes:
                        for idx, ti in enumerate(top_institutes):
                            st.markdown(f"**{idx+1}. {ti.name}** - {ti.user_count} users")
                    else:
                        st.info("No institutes with users yet.")

        # -----------------------------------------------------
        # TAB 2: SYSTEM PERFORMANCE
        # -----------------------------------------------------
        if tab2:
            with tab2:
                st.subheader("Website Performance & Logs")
                st.info("Note: Showing simulated metrics for latency and bug tracking.")
                
                p1, p2, p3 = st.columns(3)
                p1.metric("Bugs Observed (Last 24h)", "12", "-3")
                p2.metric("Loading Failures", "0.2%", "-0.1%")
                p3.metric("Avg Latency", "120ms", "+5ms")
                
                st.markdown("#### Latency Logs (Last 7 Days)")
                # Generate mock latency data
                dates = pd.date_range(end=datetime.today(), periods=7)
                latency_data = pd.DataFrame({
                    "Date": dates,
                    "Latency (ms)": np.random.randint(80, 200, size=7)
                }).set_index("Date")
                
                st.line_chart(latency_data)
                
                st.markdown("#### Recent Errors")
                mock_errors = pd.DataFrame([
                    {"Time": (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d %H:%M:%S"), "Error": "Connection Timeout", "Endpoint": "/api/video_stream"},
                    {"Time": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"), "Error": "Database Lock", "Endpoint": "/api/submit_quiz"},
                    {"Time": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"), "Error": "Image Load Failure", "Endpoint": "/assets/badge.png"}
                ])
                st.dataframe(mock_errors, use_container_width=True, hide_index=True)

        # -----------------------------------------------------
        # TAB 3: ADMIN CONTROL
        # -----------------------------------------------------
        with tab3:
            st.subheader("System Administration & Logs")
            
            st.markdown("#### Login & Logout Activity")
            
            log_query = db.query(ActivityLog).filter(ActivityLog.action_type.in_(['login', 'logout']))
            if user.role == 'institute_admin':
                active_inst = st.session_state.get('active_institute_id')
                if active_inst:
                    from database.models import UserInstitute
                    log_query = log_query.join(User, User.id == ActivityLog.user_id).join(UserInstitute, UserInstitute.user_id == User.id).filter(UserInstitute.institute_id == active_inst)
                    
            logs = log_query.order_by(desc(ActivityLog.timestamp)).limit(20).all()
            if logs:
                from database.models import UserInstitute, Institute
                log_data = []
                for l in logs:
                    inst_names = []
                    ui_records = db.query(UserInstitute).filter_by(user_id=l.user_id).all()
                    if ui_records:
                        inst_ids = [ui.institute_id for ui in ui_records]
                        institutes = db.query(Institute).filter(Institute.id.in_(inst_ids)).all()
                        inst_names = [inst.name for inst in institutes]
                    
                    inst_display = ", ".join(inst_names) if inst_names else "None"
                    
                    log_data.append({
                        "Time": l.timestamp.strftime("%Y-%m-%d %H:%M:%S") if l.timestamp else "-",
                        "User ID": l.user_id,
                        "Action": l.action_type,
                        "Institute Name": inst_display
                    })
                st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
            else:
                st.info("No login/logout logs found.")
                
            st.markdown("---")
            st.markdown("#### Time Spent Analytics")
            
            t1, t2 = st.columns(2)
            
            with t1:
                st.markdown("**Module-wise Time Spent (Minutes)**")
                # Calculate time spent per module based on LessonProgress watch_duration_seconds
                mod_query = db.query(
                    Module.title, 
                    func.sum(LessonProgress.watch_duration_seconds).label('total_seconds')
                ).select_from(Module).join(Lesson, Module.id == Lesson.module_id).join(LessonProgress, Lesson.id == LessonProgress.lesson_id)
                
                if user.role == 'institute_admin':
                    active_inst = st.session_state.get('active_institute_id')
                    if active_inst:
                        from database.models import UserInstitute
                        mod_query = mod_query.join(UserInstitute, UserInstitute.user_id == LessonProgress.child_id).filter(UserInstitute.institute_id == active_inst)
                
                mod_time = mod_query.group_by(Module.id).all()
                
                if mod_time:
                    mod_df = pd.DataFrame([
                        {"Module": m.title, "Minutes": round(m.total_seconds / 60, 2) if m.total_seconds else 0} 
                        for m in mod_time
                    ]).sort_values("Minutes", ascending=False)
                    st.dataframe(mod_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No module time data available.")
                    
            with t2:
                st.markdown("**Lesson-wise Time Spent (Minutes)**")
                les_query = db.query(
                    Lesson.title, 
                    func.sum(LessonProgress.watch_duration_seconds).label('total_seconds')
                ).select_from(Lesson).join(LessonProgress, Lesson.id == LessonProgress.lesson_id)
                
                if user.role == 'institute_admin':
                    active_inst = st.session_state.get('active_institute_id')
                    if active_inst:
                        from database.models import UserInstitute
                        les_query = les_query.join(UserInstitute, UserInstitute.user_id == LessonProgress.child_id).filter(UserInstitute.institute_id == active_inst)
                
                les_time = les_query.group_by(Lesson.id).all()
                
                if les_time:
                    les_df = pd.DataFrame([
                        {"Lesson": l.title, "Minutes": round(l.total_seconds / 60, 2) if l.total_seconds else 0} 
                        for l in les_time
                    ]).sort_values("Minutes", ascending=False)
                    st.dataframe(les_df, use_container_width=True, hide_index=True)
                else:
                    st.info("No lesson time data available.")
                    
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
    finally:
        db.close()
