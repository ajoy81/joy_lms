import streamlit as st
import bcrypt
import re
from database.engine import SessionLocal
from database.models import User, UserRelation

def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def show_register_page():
    st.markdown("<h1 style='text-align: center;'>🎓 Joy LMS</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Create a new account 🚀")
        
        with st.form("register_form"):
            role = st.selectbox("I am a...", ["Teacher 👨‍🏫", "Parent 👪", "Child 👧"])
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            
            password = st.text_input("Password", type="password", help="Minimum 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            avatar_emoji = st.selectbox("Choose an Avatar", ["👤", "👧", "👦", "👨‍🏫", "👩‍🏫", "👪", "🦁", "🐼", "🦄", "🚀", "🌟", "📚"])
            
            guardian_username = None
            if "Child" in role:
                st.info("Children need to be linked to a Parent or Teacher.")
                guardian_username = st.text_input("Guardian's Username (Teacher/Parent)")
            
            submit = st.form_submit_button("Register ✨", use_container_width=True)
            
            if submit:
                # Validation
                if not username or not email or not password or not confirm_password:
                    st.error("Please fill in all required fields.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                elif not is_valid_email(email):
                    st.error("Invalid email address format.")
                elif "Child" in role and not guardian_username:
                    st.error("Children must provide a Guardian's Username.")
                else:
                    db = SessionLocal()
                    try:
                        # Check unique username and email
                        if db.query(User).filter_by(username=username).first():
                            st.error("Username already taken. Please choose another one.")
                        elif db.query(User).filter_by(email=email).first():
                            st.error("Email already registered. Please login instead.")
                        else:
                            guardian_user = None
                            if "Child" in role:
                                guardian_user = db.query(User).filter_by(username=guardian_username).first()
                                if not guardian_user or guardian_user.role not in ['teacher', 'parent']:
                                    st.error("Guardian username not found or invalid role.")
                                    return
                                    
                            parsed_role = 'teacher' if 'Teacher' in role else ('parent' if 'Parent' in role else 'child')
                            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                            
                            new_user = User(
                                full_name=full_name,
                                username=username,
                                email=email,
                                password_hash=hashed_pw,
                                role=parsed_role,
                                avatar_emoji=avatar_emoji
                            )
                            db.add(new_user)
                            db.commit()
                            db.refresh(new_user)
                            
                            if guardian_user:
                                link = UserRelation(guardian_id=guardian_user.id, child_id=new_user.id, relation_type=guardian_user.role)
                                db.add(link)
                                db.commit()
                                
                            st.success("Account created successfully! 🎉 You can now login.")
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error during registration: {e}")
                    finally:
                        db.close()
