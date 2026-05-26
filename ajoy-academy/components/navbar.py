import streamlit as st
from auth.session import get_current_user, logout_user

def render_navbar():
    """
    Renders the top navigation bar with logo, app name, and user info/logout.
    """
    container = st.container()
    with container:
        col1, col_back, col2, col3 = st.columns([5, 1.2, 3, 1.5], vertical_alignment="center")
        with col1:
            st.markdown("<h2 style='margin-bottom:0;'>🎓 Joy LMS</h2>", unsafe_allow_html=True)
        
        user = get_current_user()
        if user:
            with col_back:
                if st.session_state.get('nav_history'):
                    if st.button("⬅️ Back", key="navbar_back", use_container_width=True):
                        st.session_state['pending_nav'] = "BACK_ACTION"
                        st.rerun()
            with col2:
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
                        f"<div style='font-weight: bold;'>"
                        f"<img src='data:image/png;base64,{b64_string}' width='30' height='30' style='border-radius: 50%; object-fit: cover; vertical-align: middle; margin-right: 10px;'>"
                        f"{user.full_name or user.username}</div>", 
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(f"<div style='font-weight: bold;'>{user.avatar_emoji} {user.full_name or user.username}</div>", unsafe_allow_html=True)
            with col3:
                if st.button("Logout", key="navbar_logout"):
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
                        st.markdown(f"<div style='pointer-events: none; font-size: 11px; color: gray; margin-top: 0px; margin-bottom: 5px; text-align: right;'>Log in: {login_str}<br>Session Time: {session_time}</div>", unsafe_allow_html=True)
                    except Exception:
                        pass
    st.markdown("---")
