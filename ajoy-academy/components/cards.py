import streamlit as st

def render_course_card(course, button_text="View Course", key_suffix="", disabled=False):
    """
    Renders a reusable course card.
    """
    html_content = f"""
    <div style="border: 2px solid #FFD93D; border-radius: 15px; padding: 15px; margin-bottom: 15px; background-color: #FFFFFF; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h3 style="margin-top: 0; color: #FF6B6B;">{course.title}</h3>
        <p style="margin-bottom: 5px;"><strong>Category:</strong> {course.category} | <strong>Difficulty:</strong> {course.difficulty_level}</p>
        <p style="margin-bottom: 5px;"><strong>Age Group:</strong> {course.age_group} | <strong>Hours:</strong> {course.estimated_hours or 0}</p>
        <p style="color: #555;">{course.description[:100] + '...' if course.description and len(course.description) > 100 else (course.description or 'No description')}</p>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    return st.button(button_text, key=f"course_btn_{course.id}_{key_suffix}", disabled=disabled)

def render_user_card(user):
    """
    Renders a reusable user card (e.g., for children linked to parent/teacher).
    """
    st.markdown(f"""
    <div style="border: 2px solid #4ECDC4; border-radius: 15px; padding: 15px; margin-bottom: 15px; background-color: #FFFFFF; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
        <h3 style="margin-top: 0; margin-bottom: 5px;">{user.avatar_emoji} {user.full_name or user.username}</h3>
        <p style="margin-bottom: 0;"><strong>Role:</strong> {user.role.capitalize()}</p>
    </div>
    """, unsafe_allow_html=True)

def render_badge_card(badge):
    """
    Renders a badge icon with its details.
    """
    st.markdown(f"""
    <div style="text-align: center; border: 2px solid #FFD93D; border-radius: 15px; padding: 10px; background-color: #FAFAFA; width: 100px; display: inline-block; margin: 5px;">
        <div style="font-size: 2rem;">{badge.emoji_icon}</div>
        <div style="font-weight: bold; font-size: 0.8rem; margin-top: 5px;">{badge.name}</div>
        <div style="font-size: 0.7rem; color: #777;">{badge.tier}</div>
    </div>
    """, unsafe_allow_html=True)

def render_timeline_post_card(post, author):
    """
    Renders a timeline post card.
    """
    # Just basic HTML representation for now
    st.markdown(f"""
    <div class="timeline-card" style="background: white; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border-left: 5px solid #FF6B6B;">
        <div style="font-weight: bold; margin-bottom: 10px;">{author.avatar_emoji} {author.username} · {post.created_at.strftime('%Y-%m-%d %H:%M')}</div>
        <div style="margin-bottom: 10px;">{post.text_content or ''}</div>
        {'<div style="color: #888; font-size: 0.8em;">Includes media</div>' if post.media_paths else ''}
    </div>
    """, unsafe_allow_html=True)
