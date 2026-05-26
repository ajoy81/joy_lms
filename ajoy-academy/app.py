import streamlit as st
from database.engine import init_db
from auth.session import init_session, is_logged_in, get_current_user
from auth.login import show_login_page
from auth.register import show_register_page

# Page config
st.set_page_config(
    page_title="🎓 Joy LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
try:
    with open("assets/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# Initialize database
init_db()

# Initialize session
init_session()

from streamlit_cookies_controller import CookieController
cookie_controller = CookieController()

if st.session_state.get('pending_cookie_remove'):
    try:
        cookie_controller.remove("ajoy_auth_token")
    except Exception:
        pass
    st.session_state['pending_cookie_remove'] = False
elif st.session_state.get('pending_cookie_update'):
    try:
        cookie_controller.set("ajoy_auth_token", st.session_state['pending_cookie_update'], max_age=86400 * 30)
    except Exception:
        pass
    st.session_state['pending_cookie_update'] = None

if 'view_mode' not in st.session_state:
    st.session_state['view_mode'] = 'Laptop'
if 'theme_mode' not in st.session_state:
    st.session_state['theme_mode'] = 'Light'



# Apply theme-specific body class using a hack (injecting empty div with script or just CSS variables)
# We will use CSS variables in style injection
if st.session_state['theme_mode'] == 'Dark':
    st.markdown("""
    <style>
        :root {
            --bg-color: #0f172a;       /* Deep blue background */
            --text-color: #f8fafc;     /* Light text */
            --card-bg: #1e293b;        /* Slightly lighter blue for cards */
            --border-color: #334155;
            --primary-color: #3b82f6;
            --secondary-bg: #1e293b;
        }
        .stApp, .block-container {
            background-color: var(--bg-color) !important;
            color: var(--text-color) !important;
        }
        /* Fix sidebar background and text visibility */
        section[data-testid="stSidebar"] {
            background-color: #0f172a !important;
        }
        section[data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        p, span, h1, h2, h3, h4, h5, h6, label, .stMarkdown {
            color: var(--text-color) !important;
        }
        .stButton > button {
            background-color: var(--secondary-bg) !important;
            color: var(--text-color) !important;
            border-color: var(--border-color) !important;
        }
        div[data-testid="stMetric"], .stExpander, .timeline-card {
            background-color: var(--card-bg) !important;
            border-color: var(--border-color) !important;
        }
        input, textarea, select {
            background-color: var(--secondary-bg) !important;
            color: var(--text-color) !important;
            border-color: var(--border-color) !important;
        }
        /* Streamlit radio text fix */
        div[role="radiogroup"] label * {
            color: var(--text-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        :root {
            --bg-color: #ffffff;
            --text-color: #333333;
            --card-bg: #ffffff;
            --border-color: #e0e0e0;
            --primary-color: #ff7e5f;
            --secondary-bg: #f9f9f9;
        }
        /* Explicitly set sidebar text color for light mode to avoid white-on-white issues */
        section[data-testid="stSidebar"] {
            background-color: #f0f2f6 !important;
        }
        section[data-testid="stSidebar"] * {
            color: #333333 !important;
        }
        p, span, h1, h2, h3, h4, h5, h6, label, .stMarkdown {
            color: var(--text-color) !important;
        }
        div[role="radiogroup"] label * {
            color: var(--text-color) !important;
        }
    </style>
    """, unsafe_allow_html=True)

if st.session_state['view_mode'] == 'Mobile':
    st.markdown("""
    <style>
        .block-container {
            max-width: 450px !important;
            margin: 0 auto !important;
            padding: 2rem 1rem !important;
            border-left: 2px solid var(--border-color, #ddd) !important;
            border-right: 2px solid var(--border-color, #ddd) !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
            background-color: var(--bg-color, #fafafa);
        }
    </style>
    """, unsafe_allow_html=True)

# Routing
if not is_logged_in():
    # Centered login/register toggle for non-logged in users
    page = st.sidebar.radio("", ["Login", "Register"])
    if page == "Login":
        show_login_page()
    else:
        show_register_page()
else:
    user = get_current_user()
    if user.role == 'teacher':
        from dashboard.teacher_dashboard import show_teacher_dashboard
        show_teacher_dashboard(user)
    elif user.role == 'parent':
        from dashboard.parent_dashboard import show_parent_dashboard
        show_parent_dashboard(user)
    elif user.role == 'child':
        from dashboard.child_dashboard import show_child_dashboard
        show_child_dashboard(user)
    elif user.role in ['admin', 'institute_admin']:
        from dashboard.admin_dashboard import show_admin_dashboard
        show_admin_dashboard(user)

    if st.session_state.get('nav_history'):
        st.markdown("---")
        if st.button("⬅️ Back to Previous", key="footer_back", type="primary"):
            st.session_state['pending_nav'] = "BACK_ACTION"
            st.rerun()

st.sidebar.markdown("---")
# Global Toggles for View Mode and Theme
col1, col2 = st.sidebar.columns(2)
with col1:
    mode = st.radio("📱💻 View Mode", ["Laptop", "Mobile"], index=0 if st.session_state['view_mode'] == 'Laptop' else 1)
with col2:
    theme = st.radio("🌓 Theme", ["Light", "Dark"], index=0 if st.session_state['theme_mode'] == 'Light' else 1)

if mode != st.session_state['view_mode'] or theme != st.session_state['theme_mode']:
    st.session_state['view_mode'] = mode
    st.session_state['theme_mode'] = theme
    st.rerun()
