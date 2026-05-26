import streamlit as st
from auth.session import get_current_user, logout_user

def render_sidebar():
    """
    Renders the role-based sidebar menu.
    Returns the selected menu option.
    """
    user = get_current_user()
    if not user:
        return None

    with st.sidebar:
        st.markdown(f"## 🎓 Joy LMS")
        if st.button("🏠 Home", use_container_width=True, type="primary"):
            if user.role == 'teacher':
                st.session_state['pending_nav'] = "Teacher Dashboard"
            elif user.role == 'parent':
                st.session_state['pending_nav'] = "Parent Dashboard"
            elif user.role == 'child':
                st.session_state['pending_nav'] = "Learner Dashboard"
            elif user.role == 'admin':
                st.session_state['pending_nav'] = "System Admin Dashboard"
            elif user.role == 'institute_admin':
                st.session_state['pending_nav'] = "Institute Admin Dashboard"
            st.rerun()
        st.markdown("---")
        
        menu_options = []
        if user.role == 'teacher':
            menu_options = [
                "Teacher Dashboard",
                "Manage Users",
                "Course Management",
                "Homework Grading",
                "Analytics",
                "User Profiles",
                "My Profile"
            ]
        elif user.role == 'parent':
            menu_options = [
                "Parent Dashboard",
                "Course Management",
                "Analytics",
                "Timeline Moderation",
                "User Profiles",
                "My Profile"
            ]
        elif user.role == 'child':
            menu_options = [
                "Learner Dashboard",
                "Course Catalog",
                "My Courses",
                "My Notes",
                "Timeline",
                "Leaderboard",
                "My Profile"
            ]
        elif user.role == 'admin':
            menu_options = [
                "System Admin Dashboard",
                "User Management",
                "Course Management",
                "Institutes",
                "Analytics",
                "Timeline Moderation",
                "My Profile"
            ]
        elif user.role == 'institute_admin':
            menu_options = [
                "Institute Admin Dashboard",
                "User Management",
                "Course Management",
                "Analytics",
                "Timeline Moderation",
                "My Profile"
            ]
            
        def on_sidebar_nav_change():
            new_val = st.session_state['sidebar_nav']
            old_val = st.session_state.get('last_sidebar_nav')
            if old_val and old_val != new_val:
                if 'nav_history' not in st.session_state:
                    st.session_state['nav_history'] = []
                st.session_state['nav_history'].append(old_val)
            st.session_state['last_sidebar_nav'] = new_val

        if st.session_state.get('pending_nav') == "BACK_ACTION":
            if st.session_state.get('nav_history'):
                prev = st.session_state['nav_history'].pop()
                st.session_state['sidebar_nav'] = prev
                st.session_state['last_sidebar_nav'] = prev
            st.session_state['pending_nav'] = None
        elif st.session_state.get('pending_nav'):
            if st.session_state['pending_nav'] in menu_options:
                if 'sidebar_nav' in st.session_state and st.session_state['sidebar_nav'] != st.session_state['pending_nav']:
                    if 'nav_history' not in st.session_state:
                        st.session_state['nav_history'] = []
                    st.session_state['nav_history'].append(st.session_state['sidebar_nav'])
                st.session_state['sidebar_nav'] = st.session_state['pending_nav']
                st.session_state['last_sidebar_nav'] = st.session_state['pending_nav']
            st.session_state['pending_nav'] = None
            
        selection = st.radio("Navigation", menu_options, key="sidebar_nav", on_change=on_sidebar_nav_change)
        if 'last_sidebar_nav' not in st.session_state:
            st.session_state['last_sidebar_nav'] = selection
        
        st.markdown("---")
        st.markdown("📖 [Online Dictionary 'Xobdo'](https://www.xobdo.org/)")
        
        st.markdown("---")
        
        import os
        from database.engine import SessionLocal
        from database.models import User
        db = SessionLocal()
        db_user = db.query(User).get(user.id)
        db.close()
        
        if db_user and db_user.profile_photo and os.path.exists(db_user.profile_photo):
            import base64
            with open(db_user.profile_photo, "rb") as img_file:
                b64_string = base64.b64encode(img_file.read()).decode('utf-8')
            st.markdown(
                f'<img src="data:image/png;base64,{b64_string}" width="40" height="40" style="border-radius: 50%; object-fit: cover; vertical-align: middle; margin-right: 10px;">'
                f'**{user.full_name or user.username}**',
                unsafe_allow_html=True
            )
        else:
            st.markdown(f"**{user.avatar_emoji} {user.full_name or user.username}**")
        st.markdown(f"*Role: {user.role.replace('_', ' ').capitalize()}*")
        
        if st.button("Logout", key="sidebar_logout_btn"):
            logout_user()
            st.rerun()
            
        login_time_str = st.session_state.get('login_time')
        if login_time_str:
            try:
                from datetime import datetime
                import pytz
                login_dt = datetime.fromisoformat(login_time_str)
                now_dt = datetime.now(pytz.utc)
                diff = now_dt - login_dt
                mins = int(diff.total_seconds() // 60)
                secs = int(diff.total_seconds() % 60)
                session_time = f"{mins:02d}:{secs:02d} mins"
                login_str = login_dt.astimezone().strftime("%H:%M")
                st.markdown(f"<div style='pointer-events: none; font-size: 11px; color: gray; margin-top: 0px; margin-bottom: 5px; text-align: left;'>Log in: {login_str}<br>Session Time: {session_time}</div>", unsafe_allow_html=True)
            except Exception:
                pass
            
        return selection
