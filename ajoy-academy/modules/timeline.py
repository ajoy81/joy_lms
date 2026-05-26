import streamlit as st
import os
from database.engine import SessionLocal
from database.models import TimelinePost, TimelineReaction, TimelineComment, User, UserRelation
from components.post_composer import show_post_composer
from modules.videos import render_video_player
from datetime import datetime
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def show_timeline_feed(user):
    st.markdown("## 📢 Timeline")
    
    db = SessionLocal()
    try:
        if user.role == "child":
            show_post_composer(user)
            st.markdown("### Institute Activity")
            query = db.query(TimelinePost).filter_by(is_approved=True)
            active_inst = st.session_state.get('active_institute_id')
            if active_inst:
                from database.models import UserInstitute
                query = query.join(UserInstitute, TimelinePost.author_id == UserInstitute.user_id).filter(UserInstitute.institute_id == active_inst)
            posts = query.order_by(TimelinePost.created_at.desc()).all()
        else:
            if user.role in ['admin', 'institute_admin']:
                st.markdown("### Institute Activity Moderation")
                query = db.query(User).filter_by(role="child")
                active_inst = st.session_state.get('active_institute_id')
                if active_inst:
                    from database.models import UserInstitute
                    query = query.join(UserInstitute).filter(UserInstitute.institute_id == active_inst)
                child_ids = [c.id for c in query.all()]
            else:
                st.markdown("### Linked Children Activity")
                # Get linked children
                relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
                child_ids = [r.child_id for r in relations]
            
            if not child_ids:
                st.info("No children found for moderation.")
                return
                
            selected_child = st.selectbox("Filter by Child", ["All"] + child_ids, format_func=lambda x: "All" if x == "All" else db.query(User).get(x).username)
            
            query = db.query(TimelinePost).filter(TimelinePost.author_id.in_(child_ids))
            if selected_child != "All":
                query = query.filter_by(author_id=selected_child)
            
            # Teachers/Parents can see all unapproved or approved, but for now just show all for moderation
            posts = query.order_by(TimelinePost.created_at.desc()).all()
            
        if not posts:
            st.info("No timeline posts to display.")
            return
            
        for post in posts:
            author = db.query(User).get(post.author_id)
            
            # Styling based on auto-generated
            bg_color = "#FFFDE7" if post.is_auto_generated else "#FFFFFF"
            border_color = "#FFD93D" if post.is_auto_generated else "#E0E0E0"
            
            with st.container():
                st.markdown(f"""
                <div style="background: {bg_color}; border: 2px solid {border_color}; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <div style="font-weight: bold; margin-bottom: 10px;">
                        {author.avatar_emoji} {author.full_name or author.username} · <span style="color:#888; font-size:0.8em;">{post.created_at.strftime('%Y-%m-%d %H:%M')}</span>
                        { "✨ [Auto Achievement]" if post.is_auto_generated else "" }
                    </div>
                    <div style="margin-bottom: 15px; font-size: 1.1em;">
                        {post.text_content}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Render Media
                if post.video_url:
                    render_video_player(post.video_url)
                if post.media_paths:
                    for media in post.media_paths:
                        if os.path.exists(media):
                            if media.lower().endswith(('.png', '.jpg', '.jpeg')):
                                st.image(media, use_column_width=True)
                            else:
                                with open(media, "rb") as f:
                                    st.download_button("📎 Download Attachment", f, file_name=os.path.basename(media), key=f"dl_{post.id}_{os.path.basename(media)}")
                
                # Interactions
                col1, col2 = st.columns([3, 1])
                with col1:
                    reactions = db.query(TimelineReaction).filter_by(post_id=post.id).all()
                    reaction_counts = {}
                    for r in reactions:
                        reaction_counts[r.reaction_type] = reaction_counts.get(r.reaction_type, 0) + 1
                    
                    reaction_str = " ".join([f"{k} {v}" for k, v in reaction_counts.items()])
                    st.markdown(f"**Reactions:** {reaction_str if reaction_str else 'None yet'}")
                    
                with col2:
                    if user.role != "child":
                        # Moderate
                        if post.is_approved:
                            if st.button("🚫 Hide Post", key=f"hide_{post.id}"):
                                post.is_approved = False
                                db.commit()
                                st.rerun()
                        else:
                            if st.button("✅ Approve Post", key=f"approve_{post.id}"):
                                post.is_approved = True
                                db.commit()
                                st.rerun()
                                
                if user.role != "child":
                    with st.expander("React / Comment"):
                        # Reactions
                        r_cols = st.columns(5)
                        emojis = ['⭐', '👏', '❤️', '🎉', '💡']
                        for i, emoji in enumerate(emojis):
                            if r_cols[i].button(emoji, key=f"react_{post.id}_{emoji}"):
                                existing_react = db.query(TimelineReaction).filter_by(post_id=post.id, user_id=user.id).first()
                                if existing_react:
                                    existing_react.reaction_type = emoji
                                else:
                                    new_react = TimelineReaction(post_id=post.id, user_id=user.id, reaction_type=emoji, created_at=utcnow())
                                    db.add(new_react)
                                db.commit()
                                st.rerun()
                                
                        # Comment
                        with st.form(f"comment_form_{post.id}"):
                            comment_text = st.text_input("Write a comment...")
                            if st.form_submit_button("Post Comment"):
                                new_comment = TimelineComment(post_id=post.id, user_id=user.id, comment_text=comment_text, created_at=utcnow())
                                db.add(new_comment)
                                db.commit()
                                st.rerun()
                                
                # Show comments
                comments = db.query(TimelineComment).filter_by(post_id=post.id).order_by(TimelineComment.created_at).all()
                if comments:
                    for c in comments:
                        c_author = db.query(User).get(c.user_id)
                        st.markdown(f"<div style='margin-left: 20px; padding: 5px; border-left: 2px solid #EEE;'><strong>{c_author.avatar_emoji} {c_author.username}:</strong> {c.comment_text}</div>", unsafe_allow_html=True)
                        
                st.markdown("---")
    finally:
        db.close()
