import streamlit as st
import bcrypt
from database.engine import SessionLocal
from database.models import User
from auth.session import login_user

def show_login_page():
    st.markdown("<h1 style='text-align: center;'>🎓 Joy LMS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Where Learning Meets Fun! 🚀</h3>", unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<div class='stExpander'>", unsafe_allow_html=True)
        st.subheader("Login to your account")
        
        
        
        db = SessionLocal()
        try:
            from database.models import Institute, UserInstitute
            institutes = db.query(Institute).order_by(Institute.name).all()
            inst_options = {inst.id: inst.name for inst in institutes} if institutes else {}
            
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                
                keep_logged_in = st.checkbox("Keep me logged in", value=True)
                submit = st.form_submit_button("Login ✨", use_container_width=True)
                
                if submit:
                    if not username or not password:
                        st.error("Please enter both username and password.")
                    else:
                        user = db.query(User).filter(User.username == username).first()
                        if user and bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                            if not user.is_active:
                                st.error("This account has been deactivated.")
                            else:
                                login_user(user)
                                
                                # Auto-assign first mapped institute if applicable
                                if user.role in ['teacher', 'parent', 'institute_admin', 'child']:
                                    ui = db.query(UserInstitute).filter_by(user_id=user.id).first()
                                    if ui:
                                        inst = db.query(Institute).get(ui.institute_id)
                                        if inst:
                                            st.session_state['active_institute_id'] = inst.id
                                            st.session_state['active_institute_name'] = inst.name
                                
                                if keep_logged_in:
                                    st.session_state['pending_cookie_update'] = str(user.id)
                                st.success(f"Welcome back, {user.full_name or user.username}! 🎉")
                                st.rerun()
                        else:
                            st.error("Invalid username or password.")
        except Exception as e:
            st.error(f"Login error: {e}")
        finally:
            db.close()
        st.markdown("</div>", unsafe_allow_html=True)
