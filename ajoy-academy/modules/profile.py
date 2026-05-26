import streamlit as st
import os
import shutil
from database.engine import SessionLocal
from database.models import User
from PIL import Image

def show_my_profile(user):
    st.markdown("## 👤 My Profile")
    
    # Refresh user from DB to get latest
    db = SessionLocal()
    db_user = db.query(User).get(user.id)
    
    if not db_user:
        st.error("User not found.")
        db.close()
        return

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Profile Photo")
        if db_user.profile_photo and os.path.exists(db_user.profile_photo):
            try:
                img = Image.open(db_user.profile_photo)
                st.image(img, width=200)
            except:
                st.markdown(f"<h1 style='font-size: 100px;'>{db_user.avatar_emoji}</h1>", unsafe_allow_html=True)
        else:
            st.markdown(f"<h1 style='font-size: 100px;'>{db_user.avatar_emoji}</h1>", unsafe_allow_html=True)
            
        uploaded_file = st.file_uploader("Upload a new photo", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            if st.button("Save Photo", type="primary"):
                upload_dir = "uploads/profiles"
                os.makedirs(upload_dir, exist_ok=True)
                file_ext = uploaded_file.name.split('.')[-1]
                file_path = os.path.join(upload_dir, f"user_{db_user.id}.{file_ext}")
                
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                    
                db_user.profile_photo = file_path
                db.commit()
                st.success("Profile photo updated!")
                st.rerun()
                
    with col2:
        st.markdown("### Edit Information")
        with st.form("profile_form"):
            role_map = {"teacher": "Teacher 👨‍🏫", "parent": "Parent 👪", "child": "Child 👧", "admin": "System Admin", "institute_admin": "Institute Admin"}
            st.text_input("Role", value=role_map.get(db_user.role, db_user.role.capitalize()), disabled=True)
            st.text_input("Username", value=db_user.username or "", disabled=True)
            avatar_opts = ["👤", "👧", "👦", "👨‍🏫", "👩‍🏫", "👪", "🦁", "🐼", "🦄", "🚀", "🌟", "🛠️", "📚"]
            avatar_val = st.selectbox("Choose an Avatar", avatar_opts, index=avatar_opts.index(db_user.avatar_emoji) if db_user.avatar_emoji in avatar_opts else 0)
            
            name_val = st.text_input("Full Name *", value=db_user.full_name or "")
            email_val = st.text_input("Email *", value=db_user.email or "")
            mobile_val = st.text_input("Mobile No *", value=db_user.mobile_no or "")
            desc_val = st.text_area("Description (Max 100 chars)", value=db_user.description or "", max_chars=100)
            addr_val = st.text_area("Contact Address", value=db_user.contact_address or "")
            
            st.markdown("* indicates mandatory fields")
            
            submitted = st.form_submit_button("Save Profile")
            if submitted:
                if not name_val.strip():
                    st.error("Full Name is mandatory.")
                elif not mobile_val.strip():
                    st.error("Mobile No is mandatory.")
                elif not email_val.strip():
                    st.error("Email is mandatory.")
                else:
                    # Check email uniqueness if changed
                    if email_val != db_user.email:
                        existing_email = db.query(User).filter(User.email == email_val, User.id != db_user.id).first()
                        if existing_email:
                            st.error("This email is already in use by another account.")
                            db.close()
                            st.stop()
                            
                    db_user.avatar_emoji = avatar_val
                    db_user.email = email_val
                    db_user.full_name = name_val
                    db_user.mobile_no = mobile_val
                    db_user.description = desc_val
                    db_user.contact_address = addr_val
                    db.commit()
                    st.success("Profile information updated successfully!")
                    st.rerun()

    db.close()

def show_user_profiles_directory(user):
    st.markdown("## ?? User Profiles")
    
    db = SessionLocal()
    try:
        from database.models import UserInstitute, UserRelation, Course, Enrollment
        query = db.query(User).order_by(User.id.desc())
        
        # Enforce Role-Based Access Controls
        if user.role == 'admin':
            # System Admin: all users (no filter)
            pass
        elif user.role == 'institute_admin':
            # Institute Admin: only attached to that institute
            inst_id = st.session_state.get('active_institute_id')
            if inst_id:
                query = query.join(UserInstitute).filter(UserInstitute.institute_id == inst_id)
        elif user.role == 'parent':
            # Parents: Only own child
            relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
            child_ids = [r.child_id for r in relations]
            query = query.filter(User.id.in_(child_ids))
        elif user.role == 'teacher':
            # Teacher: learners enrolled to their courses
            courses = db.query(Course).filter_by(created_by=user.id).all()
            course_ids = [c.id for c in courses]
            enrollments = db.query(Enrollment).filter(Enrollment.course_id.in_(course_ids)).all()
            learner_ids = [e.child_id for e in enrollments]
            query = query.filter(User.id.in_(learner_ids))
        
        users = query.all()
        
        if not users:
            st.info("No profiles available to view based on your permissions.")
            return
            
        # Draw the directory grid
        st.markdown("Select a user to view their profile.")
        cols = st.columns(3)
        for idx, u in enumerate(users):
            with cols[idx % 3]:
                with st.container(border=True):
                    # Show mini-profile card
                    if u.profile_photo and os.path.exists(u.profile_photo):
                        import base64
                        with open(u.profile_photo, "rb") as img_file:
                            b64 = base64.b64encode(img_file.read()).decode('utf-8')
                        st.markdown(f'<img src="data:image/png;base64,{b64}" width="60" height="60" style="border-radius:50%; object-fit:cover;">', unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h2 style='margin:0;'>{u.avatar_emoji}</h2>", unsafe_allow_html=True)
                    
                    st.markdown(f"**{u.full_name or u.username}**")
                    st.caption(f"Role: {u.role.capitalize()}")
                    
                    if st.button("View Profile", key=f"view_prof_{u.id}", use_container_width=True):
                        st.session_state['viewing_user_id'] = u.id
                        st.rerun()

        # Handle detailed profile view pop-up/rendering
        if st.session_state.get('viewing_user_id'):
            v_user = db.query(User).get(st.session_state['viewing_user_id'])
            if v_user:
                st.markdown("---")
                st.markdown(f"### Profile: {v_user.full_name or v_user.username}")
                c1, c2 = st.columns([1, 2])
                with c1:
                    if v_user.profile_photo and os.path.exists(v_user.profile_photo):
                        try:
                            img = Image.open(v_user.profile_photo)
                            st.image(img, width=150)
                        except:
                            st.markdown(f"<h1 style='font-size: 80px;'>{v_user.avatar_emoji}</h1>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<h1 style='font-size: 80px;'>{v_user.avatar_emoji}</h1>", unsafe_allow_html=True)
                
                with c2:
                    st.markdown(f"**Role:** {v_user.role.capitalize()}")
                    st.markdown(f"**Email:** {v_user.email}")
                    if v_user.mobile_no:
                        st.markdown(f"**Contact:** {v_user.mobile_no}")
                    if v_user.contact_address:
                        st.markdown(f"**Address:** {v_user.contact_address}")
                    if v_user.description:
                        st.markdown(f"**About:** {v_user.description}")
                        
                if st.button("Close Profile"):
                    st.session_state['viewing_user_id'] = None
                    st.rerun()

    finally:
        db.close()
