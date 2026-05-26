import streamlit as st
import pandas as pd
from database.engine import SessionLocal
from database.models import Institute, User, UserInstitute

def show_institutes_management(admin_user):
    st.markdown("## 🏫 Institute Management")
    st.info("Manage institutes and map users (Teachers/Parents) to them.")
    
    tab1, tab2 = st.tabs(["Institutes List", "Map Users"])
    
    with tab1:
        st.subheader("All Institutes")
        db = SessionLocal()
        try:
            institutes = db.query(Institute).order_by(Institute.name).all()
            
            # Add New Institute
            with st.expander("➕ Add New Institute"):
                with st.form("add_institute_form"):
                    new_inst_name = st.text_input("Institute Name*")
                    if st.form_submit_button("Create Institute"):
                        if new_inst_name.strip():
                            existing = db.query(Institute).filter_by(name=new_inst_name.strip()).first()
                            if existing:
                                st.error("Institute already exists.")
                            else:
                                db.add(Institute(name=new_inst_name.strip()))
                                db.commit()
                                st.success("Institute created successfully!")
                                st.rerun()
                        else:
                            st.error("Name cannot be empty.")
            
            st.markdown("---")
            if institutes:
                for inst in institutes:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([3, 1, 1], vertical_alignment="center")
                        with c1:
                            user_count = db.query(UserInstitute).filter_by(institute_id=inst.id).count()
                            st.markdown(f"**{inst.name}**")
                            st.caption(f"Mapped Users: {user_count} | Created: {inst.created_at.strftime('%Y-%m-%d')}")
                        with c2:
                            new_name = st.text_input("Rename", key=f"ren_{inst.id}", label_visibility="collapsed", placeholder="New name...")
                            if st.button("✏️ Rename", key=f"btn_ren_{inst.id}"):
                                if new_name.strip():
                                    inst.name = new_name.strip()
                                    db.commit()
                                    st.success("Renamed!")
                                    st.rerun()
                        with c3:
                            if st.button("🗑️ Delete", type="primary", key=f"btn_del_{inst.id}"):
                                db.delete(inst)
                                db.commit()
                                st.success("Deleted!")
                                st.rerun()
            else:
                st.info("No institutes found.")
        finally:
            db.close()
            
    with tab2:
        st.subheader("Map Users to Institutes")
        db = SessionLocal()
        try:
            institutes = db.query(Institute).order_by(Institute.name).all()
            if not institutes:
                st.warning("Please create an institute first.")
                return
                
            inst_options = {inst.id: inst.name for inst in institutes}
            
            users = db.query(User).filter(User.role.in_(['teacher', 'parent'])).order_by(User.username).all()
            if not users:
                st.info("No teachers or parents found to map.")
                return
                
            for u in users:
                # get current mapped institutes
                mapped_insts = db.query(UserInstitute).filter_by(user_id=u.id).all()
                mapped_ids = [m.institute_id for m in mapped_insts]
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1], vertical_alignment="center")
                    with c1:
                        st.markdown(f"**{u.avatar_emoji} {u.full_name or u.username}** (`{u.username}`)")
                        st.caption(f"Role: {u.role.capitalize()}")
                    with c2:
                        selected_insts = st.multiselect(
                            "Select Institutes",
                            options=list(inst_options.keys()),
                            format_func=lambda x: inst_options[x],
                            default=mapped_ids,
                            key=f"map_{u.id}",
                            label_visibility="collapsed"
                        )
                    with c3:
                        if st.button("💾 Save Map", key=f"save_map_{u.id}", use_container_width=True):
                            # clear old
                            db.query(UserInstitute).filter_by(user_id=u.id).delete()
                            # add new
                            for inst_id in selected_insts:
                                db.add(UserInstitute(user_id=u.id, institute_id=inst_id))
                            db.commit()
                            st.success("Mapping updated!")
                            
        finally:
            db.close()
