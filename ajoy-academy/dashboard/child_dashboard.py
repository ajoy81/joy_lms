import streamlit as st
from database.engine import SessionLocal
from database.models import Reward, Streak, UserBadge, Badge, TimelinePost, Enrollment, Course
from modules.rewards import update_streak
from modules.courses import show_course_catalog, show_course_player
from modules.homework import show_child_homework
from modules.timeline import show_timeline_feed
from modules.leaderboard import show_leaderboard
from modules.certificates import show_certificates
from modules.notes import show_notes
from components.navbar import render_navbar
from components.sidebar import render_sidebar

def get_child_stats(user_id, db):
    points = sum([r.points for r in db.query(Reward).filter_by(child_id=user_id).all()])
    streak = db.query(Streak).filter_by(child_id=user_id).first()
    streak_days = streak.current_streak if streak else 0
    return points, streak_days

def show_child_dashboard(user):
    # Setup layout
    render_navbar()
    selection = render_sidebar()
    
    # Handle routing based on sidebar
    if selection == "Course Catalog":
        show_course_catalog(user)
        return
    elif selection == "My Courses":
        show_course_player(user)
        return
    elif selection == "My Notes":
        show_notes(user)
        return
    elif selection == "Timeline":
        show_timeline_feed(user)
        return
    elif selection == "Leaderboard":
        show_leaderboard(user)
        return
    elif selection == "My Profile":
        from modules.profile import show_my_profile
        show_my_profile(user)
        return
        
    # Main Dashboard View
    db = SessionLocal()
    try:
        # Trigger daily streak logic on dashboard load
        update_streak(user.id)
        
        points, streak = get_child_stats(user.id, db)
        
        st.markdown(f"## 👋 Hi {user.full_name or user.username}! Welcome back!")
        
        # Stats Cards
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #FF9A9E 0%, #FECFEF 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
                <h1 style="margin:0; font-size: 2.5em;">🌟 {points}</h1>
                <p style="margin:0; font-size: 1.2em;">Total Points</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Leaderboard 🏆", key="drill_child_leader_pts", use_container_width=True):
                st.session_state['pending_nav'] = "Leaderboard"
                st.rerun()
        with col2:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f6d365 0%, #fda085 100%); padding: 20px; border-radius: 15px; color: white; text-align: center;">
                <h1 style="margin:0; font-size: 2.5em;">🔥 {streak}</h1>
                <p style="margin:0; font-size: 1.2em;">Day Streak</p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("View Timeline 📱", key="drill_child_streak", use_container_width=True):
                st.session_state['pending_nav'] = "Timeline"
                st.rerun()
            
        st.markdown("---")
        
        # Continue Learning
        st.markdown("### 🎬 Continue Learning")
        enrollments = db.query(Enrollment).filter_by(child_id=user.id).limit(2).all()
        if enrollments:
            for e in enrollments:
                course = db.query(Course).get(e.course_id)
                if course:
                    from database.models import Lesson, Module, LessonProgress
                    total_lessons = db.query(Lesson).join(Module).filter(Module.course_id == course.id).count()
                    completed = 0
                    if total_lessons > 0:
                        completed = db.query(LessonProgress).join(Lesson).join(Module).filter(
                            Module.course_id == course.id,
                            LessonProgress.child_id == user.id,
                            LessonProgress.is_completed == True
                        ).count()
                        actual_progress = int((completed / total_lessons) * 100)
                    else:
                        actual_progress = 0
                        
                    with st.container():
                        st.markdown(f"**{course.title}** - Progress: {actual_progress}%")
                        st.progress(actual_progress / 100.0)
            
            def nav_to_my_courses():
                st.session_state['pending_nav'] = "My Courses"
            st.button("Go to My Courses 🚀", on_click=nav_to_my_courses)
        else:
            st.info("You haven't enrolled in any courses yet!")
            
            def nav_to_catalog():
                st.session_state['pending_nav'] = "Course Catalog"
            st.button("Explore Courses 🚀", on_click=nav_to_catalog)
                
        st.markdown("---")
        
        # My Badges
        st.markdown("### 🏆 My Badges")
        user_badges = db.query(UserBadge).filter_by(user_id=user.id).all()
        if user_badges:
            cols = st.columns(min(len(user_badges), 5))
            for i, ub in enumerate(user_badges[:5]):
                badge = db.query(Badge).get(ub.badge_id)
                with cols[i]:
                    st.markdown(f"<div style='text-align:center; font-size:2em;'>{badge.emoji_icon}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div style='text-align:center; font-size:0.8em;'>{badge.name}</div>", unsafe_allow_html=True)
        else:
            st.info("Complete lessons and quizzes to earn your first badge!")
            
        st.markdown("---")
        
        # Pending Homework
        st.markdown("### 📝 Pending Homework")
        # Reuse homework view or just show a summary
        show_child_homework(user)
        
    finally:
        db.close()
