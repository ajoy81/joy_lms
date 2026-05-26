import streamlit as st
from database.engine import SessionLocal
from database.models import User, UserRelation, ActivityLog, Reward, Course, Enrollment
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from modules.courses import show_course_builder
from modules.analytics import show_analytics
from modules.timeline import show_timeline_feed
from datetime import datetime
import pytz

def _render_assign_course_tab(db, parent_user, child_ids):
    st.markdown("### Assign a Course")
    
    selected_child_id = st.selectbox(
        "Select Child to Assign Course", 
        child_ids, 
        format_func=lambda x: db.query(User).get(x).username,
        key="assign_course_child_sel"
    )
    
    active_inst = st.session_state.get('active_institute_id')
    query = db.query(Course).filter_by(is_published=True)
    if active_inst:
        query = query.filter_by(institute_id=active_inst)
    all_published_courses = query.all()
    if not all_published_courses:
        st.info("No published courses available for your institute.")
        return
        
    st.markdown("#### Available Courses")
    for course in all_published_courses:
        with st.container(border=True):
            col_info, col_action = st.columns([2, 1], vertical_alignment="center")
            with col_info:
                st.markdown(f"**{course.title}** ({course.category or 'Uncategorized'})")
                st.markdown(f"<span style='font-size:12px;color:gray;'>{course.difficulty_level or 'All Levels'} | Age: {course.age_group or 'Any'}</span>", unsafe_allow_html=True)
                
            with col_action:
                existing = db.query(Enrollment).filter_by(child_id=selected_child_id, course_id=course.id).first()
                if existing:
                    st.success(f"Enrolled ({existing.assignment_type})")
                else:
                    assign_type = st.radio("Assignment Type", ["Suggested", "Mandatory"], key=f"type_{course.id}", horizontal=True, label_visibility="collapsed")
                    if st.button("Assign to Child", key=f"enroll_{course.id}"):
                        new_enrollment = Enrollment(
                            child_id=selected_child_id,
                            course_id=course.id,
                            assignment_type=assign_type
                        )
                        db.add(new_enrollment)
                        db.commit()
                        st.success(f"Enrolled in {course.title}!")
                        st.rerun()

def show_parent_dashboard(user):
    render_navbar()
    selection = render_sidebar()
    
    if selection == "Course Management":
        from modules.courses import show_course_explorer
        show_course_explorer(user)
        return
    elif selection == "Analytics":
        db = SessionLocal()
        child_ids = [r.child_id for r in db.query(UserRelation).filter_by(guardian_id=user.id).all()]
        db.close()
        show_analytics(user, child_ids)
        return
    elif selection == "Timeline Moderation":
        show_timeline_feed(user)
        return
    elif selection == "User Profiles":
        from modules.profile import show_user_profiles_directory
        show_user_profiles_directory(user)
        return
    elif selection == "My Profile":
        from modules.profile import show_my_profile
        show_my_profile(user)
        return
        
    st.markdown(f"## 👪 Welcome, {user.full_name or user.username}!")
    
    db = SessionLocal()
    try:
        from sqlalchemy import func
        relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
        child_ids = [r.child_id for r in relations]
        
        total_children = len(child_ids)
        total_assigned = db.query(Enrollment).filter(Enrollment.child_id.in_(child_ids)).count() if child_ids else 0
        total_points = db.query(func.sum(Reward.points)).filter(Reward.child_id.in_(child_ids)).scalar() if child_ids else 0
        
        st.markdown("### 📊 Overview")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Children", total_children)
        with c2:
            st.metric("Courses Assigned", total_assigned)
            if st.button("Assign Courses", key="drill_parent_assign", use_container_width=True):
                st.session_state['pending_nav'] = "Course Management"
                st.rerun()
        with c3:
            st.metric("Total Points", total_points or 0)
            if st.button("View Progress", key="drill_parent_prog", use_container_width=True):
                st.session_state['pending_nav'] = "Analytics"
                st.rerun()
                
        st.markdown("---")
        
        # My Children
        st.markdown("### 👧 My Children")
        relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
        child_ids = [r.child_id for r in relations]
        
        if not child_ids:
            st.info("You haven't linked your children's accounts yet.")
            st.markdown("#### Link a Child")
            with st.form("link_child_form"):
                child_username = st.text_input("Child Username")
                if st.form_submit_button("Link Child"):
                    child = db.query(User).filter_by(username=child_username, role="child").first()
                    if not child:
                        st.error("Child account not found.")
                    else:
                        from database.models import UserInstitute
                        active_inst = st.session_state.get('active_institute_id')
                        if active_inst:
                            is_in_inst = db.query(UserInstitute).filter_by(user_id=child.id, institute_id=active_inst).first()
                            if not is_in_inst:
                                st.error("This child does not belong to your institute.")
                                st.stop()
                                
                        existing = db.query(UserRelation).filter_by(guardian_id=user.id, child_id=child.id).first()
                        if existing:
                            st.warning("Child is already linked to you.")
                        else:
                            new_rel = UserRelation(guardian_id=user.id, child_id=child.id, relation_type="parent", created_at=datetime.now(pytz.utc))
                            db.add(new_rel)
                            db.commit()
                            st.success(f"Successfully linked {child.username}!")
                            st.rerun()
        else:
            children = db.query(User).filter(User.id.in_(child_ids)).all()
            cols = st.columns(len(children))
            for i, child in enumerate(children):
                with cols[i]:
                    points = sum([r.points for r in db.query(Reward).filter_by(child_id=child.id).all()])
                    st.markdown(f"""
                    <div style="border: 2px solid #4ECDC4; border-radius: 15px; padding: 15px; text-align: center; margin-bottom: 15px;">
                        <h2 style="margin: 0;">{child.avatar_emoji}</h2>
                        <h3>{child.full_name or child.username}</h3>
                        <p style="color: #FF6B6B; font-weight: bold; margin-bottom: 5px;">{points} pts</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    enrollments = db.query(Enrollment).filter_by(child_id=child.id).all()
                    if enrollments:
                        st.markdown("**📚 Enrolled Courses:**")
                        for enc in enrollments:
                            course = db.query(Course).get(enc.course_id)
                            if course:
                                st.markdown(f"- {course.title} *({enc.assignment_type})*")
                    else:
                        st.caption("No courses enrolled yet.")
                        
                    def nav_to_analytics(cid=child.id):
                        st.session_state['pending_nav'] = "Analytics"
                        st.session_state['selected_child_for_analytics'] = cid
                        
                    st.button("📊 View Progress", key=f"drill_{child.id}", use_container_width=True, on_click=nav_to_analytics)
                        
            st.markdown("---")
            
            st.markdown("### 🏗️ Create Courses for My Kids")
            st.info("You can create custom courses and assign them to your children.")
            
            def nav_to_course_builder():
                st.session_state['pending_nav'] = "Course Management"
                
            st.button("Open Course Builder 🚀", on_click=nav_to_course_builder)
                
            st.markdown("---")
            tab_activity, tab_assign = st.tabs(["📜 Recent Activity", "📚 Assign Course"])
            
            with tab_activity:
                st.markdown("### Recent Activity")
                selected_child_id = st.selectbox("Select Child", child_ids, format_func=lambda x: db.query(User).get(x).username)
                logs = db.query(ActivityLog).filter_by(user_id=selected_child_id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
                if logs:
                    for log in logs:
                        st.markdown(f"- **{log.timestamp.strftime('%Y-%m-%d %H:%M')}**: {log.action_type.replace('_', ' ').capitalize()} *(Metadata: {log.metadata_info})*")
                else:
                    st.info("No recent activity.")
                    
            with tab_assign:
                _render_assign_course_tab(db, user, child_ids)
    finally:
        db.close()
