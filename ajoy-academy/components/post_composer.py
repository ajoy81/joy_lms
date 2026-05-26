import streamlit as st
import os
import uuid
from database.engine import SessionLocal
from database.models import TimelinePost
from modules.rewards import award_points
from modules.activity_tracker import log_activity
from datetime import datetime
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def show_post_composer(user):
    st.markdown("""
    <div style="background-color: #F0F2F6; padding: 15px; border-radius: 12px; margin-bottom: 20px;">
        <h3 style="margin-top:0;">What did you learn today? 🌟</h3>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("post_composer_form", clear_on_submit=True):
        text_content = st.text_area("Share your thoughts or achievements:", height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            uploaded_file = st.file_uploader("📷 Photo / 📎 File", type=["jpg", "png", "jpeg", "pdf"])
        with col2:
            video_url = st.text_input("🎥 YouTube Video URL (optional)")
            
        if st.form_submit_button("✨ Post It!"):
            if not text_content and not uploaded_file and not video_url:
                st.error("Please add some text, an image, or a video URL to post.")
            else:
                media_paths = []
                if uploaded_file:
                    upload_dir = os.path.join(os.getcwd(), "uploads", "timeline_media")
                    os.makedirs(upload_dir, exist_ok=True)
                    ext = uploaded_file.name.split('.')[-1]
                    filename = f"{uuid.uuid4()}.{ext}"
                    filepath = os.path.join(upload_dir, filename)
                    with open(filepath, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    media_paths.append(filepath)
                    
                db = SessionLocal()
                try:
                    post = TimelinePost(
                        author_id=user.id,
                        post_type="mixed" if (text_content and (media_paths or video_url)) else ("text" if text_content else "media"),
                        text_content=text_content,
                        media_paths=media_paths,
                        video_url=video_url,
                        created_at=utcnow(),
                        updated_at=utcnow()
                    )
                    db.add(post)
                    db.commit()
                    
                    # Award points
                    award_points(user.id, 5, "Timeline post", reference_type="timeline_post", reference_id=post.id)
                    log_activity(user.id, "timeline_post_created", metadata={"post_id": post.id})
                    
                    st.success("Post created successfully! +5 pts 🌟")
                    st.rerun()
                finally:
                    db.close()
