import streamlit as st
import os
from datetime import datetime
from config import NOTES_DIR
import pandas as pd

def get_user_notes_dir(user_id):
    """Ensure and return the user's notes directory."""
    user_dir = os.path.join(NOTES_DIR, f"user_{user_id}")
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def show_notes(user):
    st.markdown("## 📝 My Notes")
    user_dir = get_user_notes_dir(user.id)
    
    # List all md files
    files = [f for f in os.listdir(user_dir) if f.endswith('.md')]
    
    if not files:
        st.info("You haven't created any class notes yet. Take notes while watching a video lesson!")
        return

    # Parse metadata from filenames: Coursename_module_date.md
    notes_data = []
    for f in files:
        filepath = os.path.join(user_dir, f)
        created_at = datetime.fromtimestamp(os.path.getmtime(filepath))
        
        # Try to parse the filename
        parts = f.replace('.md', '').split('_')
        if len(parts) >= 3:
            course_name = parts[0]
            module_name = parts[1]
            date_str = parts[2]
        else:
            course_name = "Unknown Course"
            module_name = "Unknown Module"
            date_str = created_at.strftime("%Y%m%d")
            
        notes_data.append({
            "File Name": f,
            "Course": course_name,
            "Module": module_name,
            "Date Modified": created_at.strftime("%Y-%m-%d %H:%M"),
            "path": filepath
        })
        
    df = pd.DataFrame(notes_data)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("### Saved Notes")
        # Display as a dataframe
        selected_file = st.selectbox("Select a note to view/edit", df['File Name'].tolist())
        
        st.dataframe(df[['Course', 'Module', 'Date Modified', 'File Name']], use_container_width=True, hide_index=True)
        
    with col2:
        if selected_file:
            st.markdown(f"### Editing: `{selected_file}`")
            filepath = os.path.join(user_dir, selected_file)
            
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
                
            from streamlit_quill import st_quill
            new_content = st_quill(
                value=content,
                placeholder="Type your notes here... (Rich Text supported)",
                html=True,
                key=f"quill_edit_note"
            )
            
            if st.button("💾 Save Changes", use_container_width=True):
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                st.success("Changes saved successfully!")
                st.rerun()
                
            st.markdown("---")
            st.markdown("### Preview")
            with st.container(border=True):
                st.markdown(new_content, unsafe_allow_html=True)
