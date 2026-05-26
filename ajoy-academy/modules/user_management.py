import streamlit as st
import pandas as pd
import bcrypt
import os
from database.engine import SessionLocal
from database.models import User
from datetime import datetime
import pytz

def update_password_file(username, password, role):
    file_path = r"D:\A_LMS\Dev_plan\user_password.md"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        table_start_idx = -1
        for i, line in enumerate(lines):
            if "| Role | Username | Password |" in line:
                table_start_idx = i
                break
                
        if table_start_idx != -1:
            user_row_idx = -1
            for i in range(table_start_idx + 2, len(lines)):
                if not lines[i].strip().startswith("|"):
                    break 
                if f"`{username}`" in lines[i]:
                    user_row_idx = i
                    break
                    
            if user_row_idx != -1:
                parts = lines[user_row_idx].split("|")
                if len(parts) >= 4:
                    parts[3] = f" `{password}` "
                    lines[user_row_idx] = "|".join(parts)
            else:
                end_idx = table_start_idx + 2
                while end_idx < len(lines) and lines[end_idx].strip().startswith("|"):
                    end_idx += 1
                new_row = f"| **{role.capitalize()}** | `{username}` | `{password}` | - |\n"
                lines.insert(end_idx, new_row)
                
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
    except Exception as e:
        print(f"Failed to update password file: {e}")

@st.dialog("Manage User Profile", width="large")
def _manage_user_dialog(user_id, admin_id):
    db = SessionLocal()
    try:
        u = db.query(User).get(user_id)
        if not u:
            st.error("User not found.")
            return

        c1, c2 = st.columns([1, 2])
        with c1:
            st.markdown("### Profile Photo")
            if u.profile_photo and os.path.exists(u.profile_photo):
                try:
                    from PIL import Image
                    img = Image.open(u.profile_photo)
                    st.image(img, width=150)
                except:
                    st.markdown(f"<h1 style='font-size: 80px;'>{u.avatar_emoji}</h1>", unsafe_allow_html=True)
            else:
                st.markdown(f"<h1 style='font-size: 80px;'>{u.avatar_emoji}</h1>", unsafe_allow_html=True)
                
            st.markdown("---")
            new_pass = st.text_input("New Password", type="password")
            if st.button("🔑 Reset Password", use_container_width=True):
                if new_pass:
                    u.password_hash = bcrypt.hashpw(new_pass.encode('utf-8'), bcrypt.gensalt()).decode()
                    db.commit()
                    update_password_file(u.username, new_pass, u.role)
                    st.success("Password reset and saved to user_password.md!")
                else:
                    st.error("Please enter a new password.")
                    
            if u.id != admin_id:
                st.markdown("---")
                if st.button("🗑️ Delete User", type="primary", use_container_width=True):
                    db.delete(u)
                    db.commit()
                    st.success("User deleted!")
                    st.rerun()

        with c2:
            st.markdown("### Edit Information")
            role_map = {"teacher": "Teacher 👨‍🏫", "parent": "Parent 👪", "child": "Child 👧", "admin": "System Admin", "institute_admin": "Institute Admin"}
            st.text_input("Role", value=role_map.get(u.role, u.role.capitalize()), disabled=True)
            st.text_input("Username", value=u.username or "", disabled=True)
            avatar_opts = ["👤", "👧", "👦", "👨‍🏫", "👩‍🏫", "👪", "🦁", "🐼", "🦄", "🚀", "🌟", "🛠️", "📚"]
            edit_avatar = st.selectbox("Choose an Avatar", avatar_opts, index=avatar_opts.index(u.avatar_emoji) if u.avatar_emoji in avatar_opts else 0)
            
            edit_fullname = st.text_input("Full Name *", value=u.full_name or "")
            edit_email = st.text_input("Email *", value=u.email or "")
            edit_mobile = st.text_input("Mobile No", value=u.mobile_no or "")
            edit_desc = st.text_area("Description (Max 100 chars)", value=u.description or "", max_chars=100)
            edit_addr = st.text_area("Contact Address", value=u.contact_address or "")

            if st.button("💾 Save Profile", use_container_width=True):
                if not edit_fullname.strip() or not edit_email.strip():
                    st.error("Full Name and Email are mandatory.")
                else:
                    u.avatar_emoji = edit_avatar
                    u.full_name = edit_fullname
                    u.email = edit_email
                    u.mobile_no = edit_mobile
                    u.description = edit_desc
                    u.contact_address = edit_addr
                    db.commit()
                    st.success("Profile saved!")
                    st.rerun()

    finally:
        db.close()

def show_user_management(admin_user):
    st.markdown("## 👥 User Management")
    st.info("Create new user accounts and view existing users.")
    
    tab1, tab2 = st.tabs(["➕ Create User", "📋 View Users"])
    
    with tab1:
        st.subheader("Create New Account")
        
        db = SessionLocal()
        try:
            from database.models import Institute, UserInstitute
            institutes = db.query(Institute).order_by(Institute.name).all()
            inst_options = {inst.id: inst.name for inst in institutes} if institutes else {}
        finally:
            db.close()
            
        with st.form("create_user_form"):
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                full_name = st.text_input("Full Name")
                email = st.text_input("Email Address*")
            with col2:
                password = st.text_input("Password*", type="password")
                role = st.selectbox("Role*", ["teacher", "parent", "child", "admin", "institute_admin"])
                avatar = st.selectbox("Avatar Emoji", ["👨‍🏫", "👩‍🏫", "👪", "👨‍👦", "👧", "👦", "🛠️", "👤"])
                
            selected_insts = []
            if inst_options:
                selected_insts = st.multiselect(
                    "Assign Institutes",
                    options=list(inst_options.keys()),
                    format_func=lambda x: inst_options[x]
                )
                
            submitted = st.form_submit_button("Create Account", use_container_width=True)
            
            if submitted:
                if not username or not password or not email:
                    st.error("Please fill in all required fields marked with *.")
                else:
                    db = SessionLocal()
                    try:
                        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
                        if existing_user:
                            st.error("A user with that username or email already exists.")
                        else:
                            new_user = User(
                                username=username,
                                email=email,
                                password_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode(),
                                role=role,
                                full_name=full_name,
                                avatar_emoji=avatar,
                                created_at=datetime.now(pytz.utc)
                            )
                            db.add(new_user)
                            db.commit()
                            
                            if role in ['teacher', 'parent', 'institute_admin', 'child'] and selected_insts:
                                for inst_id in selected_insts:
                                    db.add(UserInstitute(user_id=new_user.id, institute_id=inst_id))
                                db.commit()
                                
                            st.success(f"User '{username}' created successfully as a {role.capitalize()}! 🎉")
                            update_password_file(username, password, role)
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error creating user: {e}")
                    finally:
                        db.close()
                        
    with tab2:
        st.subheader("Registered Users")
        db = SessionLocal()
        try:
            from database.models import UserInstitute
            query = db.query(User).order_by(User.id.desc())
            
            if admin_user.role == 'institute_admin':
                inst_id = st.session_state.get('active_institute_id')
                if inst_id:
                    query = query.join(UserInstitute).filter(UserInstitute.institute_id == inst_id)
            
            users = query.all()
            if users:
                all_roles = list(set([u.role.capitalize() for u in users]))
                role_filter = st.selectbox("Filter by Role", ["All"] + all_roles)
                
                if role_filter != "All":
                    users = [u for u in users if u.role.capitalize() == role_filter]
                    
                if not users:
                    st.info("No users match the selected role.")
                
                for u in users:
                    with st.container(border=True):
                        c1, c2 = st.columns([3, 1], vertical_alignment="center")
                        with c1:
                            st.markdown(f"**{u.avatar_emoji} {u.full_name or u.username}** (`{u.username}`)")
                            st.caption(f"Role: {u.role.capitalize()} | Email: {u.email} | Active: {u.is_active}")
                        with c2:
                            if st.button("⚙️ Manage", key=f"manage_{u.id}", use_container_width=True):
                                _manage_user_dialog(u.id, admin_user.id)
            else:
                st.info("No users found.")
        finally:
            db.close()
