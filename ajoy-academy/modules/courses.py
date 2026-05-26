import streamlit as st
from database.engine import SessionLocal
from database.models import Course, Module, Lesson, Enrollment, LessonProgress
from components.cards import render_course_card
from modules.videos import render_video_player
from modules.activity_tracker import log_activity
from datetime import datetime
import pytz
import streamlit.components.v1 as components
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YT_COMPONENT_PATH = os.path.join(BASE_DIR, "components", "youtube_tracker")
PDF_COMPONENT_PATH = os.path.join(BASE_DIR, "components", "pdf_tracker")

_youtube_tracker = components.declare_component("youtube_tracker", path=YT_COMPONENT_PATH)
_pdf_tracker = components.declare_component("pdf_tracker", path=PDF_COMPONENT_PATH)

def save_lesson_duration(child_id, lesson_id, increment_seconds):
    db = SessionLocal()
    try:
        progress = db.query(LessonProgress).filter_by(child_id=child_id, lesson_id=lesson_id).first()
        if not progress:
            progress = LessonProgress(child_id=child_id, lesson_id=lesson_id, watch_duration_seconds=0)
            db.add(progress)
            
        if progress.is_completed:
            rev_key = f"rev_chunk_{lesson_id}"
            chunk = st.session_state.get(rev_key, 0) + increment_seconds
            if chunk >= 300:
                progress.revise_count = (progress.revise_count or 0) + (chunk // 300)
                st.session_state[rev_key] = chunk % 300
            else:
                st.session_state[rev_key] = chunk
                
        progress.watch_duration_seconds += increment_seconds
        progress.last_accessed_at = utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving lesson duration: {e}")
    finally:
        db.close()

def track_lesson_time(user_id, active_lesson_id):
    if 'current_lesson_id' not in st.session_state:
        st.session_state['current_lesson_id'] = None
    if 'current_lesson_started_at' not in st.session_state:
        st.session_state['current_lesson_started_at'] = None

    now = utcnow()
    prev_lesson_id = st.session_state['current_lesson_id']
    start_time_str = st.session_state['current_lesson_started_at']

    if prev_lesson_id != active_lesson_id:
        if prev_lesson_id and start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                elapsed = int((now - start_time).total_seconds())
                elapsed = min(elapsed, 900)
                if elapsed > 0:
                    save_lesson_duration(user_id, prev_lesson_id, elapsed)
            except Exception as e:
                print(f"Error flushing lesson time: {e}")
        
        st.session_state['current_lesson_id'] = active_lesson_id
        st.session_state['current_lesson_started_at'] = now.isoformat()
    else:
        if start_time_str:
            try:
                start_time = datetime.fromisoformat(start_time_str)
                elapsed = int((now - start_time).total_seconds())
                if elapsed > 900:
                    st.session_state['current_lesson_started_at'] = now.isoformat()
                elif elapsed >= 5:
                    save_lesson_duration(user_id, active_lesson_id, elapsed)
                    st.session_state['current_lesson_started_at'] = now.isoformat()
            except Exception as e:
                print(f"Error incrementally tracking lesson time: {e}")

def recalculate_course_progress(child_id, course_id):
    db = SessionLocal()
    try:
        lessons = db.query(Lesson).join(Module).filter(Module.course_id == course_id).all()
        if not lessons:
            return
        
        total_lessons = len(lessons)
        completed_lessons = db.query(LessonProgress).filter(
            LessonProgress.child_id == child_id,
            LessonProgress.lesson_id.in_([l.id for l in lessons]),
            LessonProgress.is_completed == True
        ).count()
        
        progress_pct = (completed_lessons / total_lessons) * 100.0
        
        enrollment = db.query(Enrollment).filter_by(child_id=child_id, course_id=course_id).first()
        if enrollment:
            enrollment.progress_percentage = round(progress_pct, 1)
            if progress_pct >= 100.0 and not enrollment.completed_at:
                enrollment.completed_at = utcnow()
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error recalculating course progress: {e}")
    finally:
        db.close()

def update_progress(child_id, lesson_id, watch_percentage, time_spent_increment, is_completed):
    db = SessionLocal()
    course_id = None
    try:
        lesson = db.query(Lesson).get(lesson_id)
        if lesson and lesson.module:
            course_id = lesson.module.course_id
            
        progress = db.query(LessonProgress).filter_by(child_id=child_id, lesson_id=lesson_id).first()
        if not progress:
            progress = LessonProgress(child_id=child_id, lesson_id=lesson_id, watch_duration_seconds=0)
            db.add(progress)
        
        if watch_percentage > progress.watch_percentage:
            progress.watch_percentage = watch_percentage
            
        if time_spent_increment > 0:
            key = f"yt_last_play_time_{lesson_id}"
            last_play_time = st.session_state.get(key, 0)
            increment = time_spent_increment - last_play_time
            if increment > 0:
                if progress.is_completed:
                    rev_key = f"rev_chunk_{lesson_id}"
                    chunk = st.session_state.get(rev_key, 0) + increment
                    if chunk >= 300:
                        progress.revise_count = (progress.revise_count or 0) + (chunk // 300)
                        st.session_state[rev_key] = chunk % 300
                    else:
                        st.session_state[rev_key] = chunk
                        
                progress.watch_duration_seconds += increment
                st.session_state[key] = time_spent_increment
        
        if is_completed and not progress.is_completed:
            progress.is_completed = True
            progress.completion_count = 1
            progress.completed_at = utcnow()
            log_activity(child_id, "lesson_completed", metadata={"lesson_id": lesson_id, "mode": "youtube_watch"})
            
        progress.last_accessed_at = utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error in update_progress: {e}")
    finally:
        db.close()
        
    if course_id:
        recalculate_course_progress(child_id, course_id)

def update_pdf_progress(child_id, lesson_id, scroll_percentage, is_completed):
    db = SessionLocal()
    course_id = None
    try:
        lesson = db.query(Lesson).get(lesson_id)
        if lesson and lesson.module:
            course_id = lesson.module.course_id
            
        progress = db.query(LessonProgress).filter_by(child_id=child_id, lesson_id=lesson_id).first()
        if not progress:
            progress = LessonProgress(child_id=child_id, lesson_id=lesson_id)
            db.add(progress)
            
        if scroll_percentage > progress.watch_percentage:
            progress.watch_percentage = scroll_percentage
            
        if is_completed and not progress.is_completed:
            progress.is_completed = True
            progress.completion_count = 1
            progress.completed_at = utcnow()
            log_activity(child_id, "lesson_completed", metadata={"lesson_id": lesson_id, "mode": "pdf_scroll"})
            
        progress.last_accessed_at = utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error in update_pdf_progress: {e}")
    finally:
        db.close()
        
    if course_id:
        recalculate_course_progress(child_id, course_id)


def utcnow():
    return datetime.now(pytz.utc)

def show_course_catalog(user):
    st.markdown("## 📚 Course Catalog")
    
    col1, col2, col3 = st.columns(3)
    category = col1.selectbox("Category", ["All", "Math", "Science", "English", "Art", "Coding", "Other"])
    difficulty = col2.selectbox("Difficulty", ["All", "Beginner", "Intermediate", "Advanced"])
    age_group = col3.selectbox("Age Group", ["All", "5-7", "8-10", "11-13", "14-16"])
    
    db = SessionLocal()
    try:
        query = db.query(Course).filter(Course.is_published == True)
        active_inst = st.session_state.get('active_institute_id')
        if active_inst:
            query = query.filter(Course.institute_id == active_inst)
            
        if category != "All":
            query = query.filter(Course.category.ilike(category))
        if difficulty != "All":
            query = query.filter(Course.difficulty_level.ilike(difficulty))
        if age_group != "All":
            query = query.filter(Course.age_group.ilike(age_group))
            
        courses = query.all()
        
        if not courses:
            st.info("No courses found matching your criteria.")
        else:
            for course in courses:
                existing = db.query(Enrollment).filter_by(child_id=user.id, course_id=course.id).first()
                if existing:
                    render_course_card(course, button_text="Already Enrolled ✅", key_suffix="catalog_enrolled", disabled=True)
                else:
                    if render_course_card(course, button_text="Enroll Now 🚀", key_suffix="catalog"):
                        enroll = Enrollment(child_id=user.id, course_id=course.id, enrolled_at=utcnow())
                        db.add(enroll)
                        db.commit()
                        log_activity(user.id, "course_enrolled", metadata={"course_id": course.id})
                        st.success(f"Successfully enrolled in {course.title}!")
                        st.rerun()
    finally:
        db.close()

def show_course_player(user):
    st.markdown("## 🎬 My Courses")
    db = SessionLocal()
    try:
        raw_enrollments = db.query(Enrollment).filter_by(child_id=user.id).all()
        # Filter out enrollments where the course has been deleted
        enrollments = [e for e in raw_enrollments if db.query(Course).get(e.course_id) is not None]
        
        if not enrollments:
            st.info("You haven't enrolled in any courses yet.")
            return

        course_id = st.selectbox("Select a course to resume", [e.course_id for e in enrollments], 
                                 format_func=lambda x: db.query(Course).get(x).title)
        
        if course_id:
            course = db.query(Course).get(course_id)
            modules = db.query(Module).filter_by(course_id=course.id).order_by(Module.order_index).all()
            
            if not modules:
                st.info("This course has no modules yet.")
                return

            # Calculate durations and progress
            course_duration = 0
            completed_duration = 0
            module_durations = {}
            lesson_durations = {}

            all_lessons = []
            for mod in modules:
                mod_lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                all_lessons.extend(mod_lessons)
                mod_dur = 0
                for les in mod_lessons:
                    dur = les.duration_minutes or 0
                    lesson_durations[les.id] = dur
                    mod_dur += dur
                    
                    progress = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=les.id).first()
                    if progress and progress.is_completed:
                        completed_duration += dur
                        
                module_durations[mod.id] = mod_dur
                course_duration += mod_dur

            progress_pct = completed_duration / course_duration if course_duration > 0 else 0.0
            
            st.markdown("""
            <style>
            .stProgress > div > div > div > div {
                background-color: #28a745 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            st.progress(progress_pct)
            st.markdown(f"<div style='font-size:12px; color:gray; margin-top:-10px; margin-bottom:10px;'>Course Progress: {int(progress_pct*100)}% ({completed_duration}m / {course_duration}m)</div>", unsafe_allow_html=True)
            
            st.markdown(f"### {course.title}")
            
            # Simple Sidebar / Main Area for learning
            col1, col2 = st.columns([1.75, 2.25])
            
            with col1:
                st.markdown("#### Course Flow")
                selected_lesson_id = st.session_state.get('selected_lesson_id')
                if not selected_lesson_id and all_lessons:
                    selected_lesson_id = all_lessons[0].id
                    st.session_state['selected_lesson_id'] = selected_lesson_id
                    
                st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center; line-height:1.2;'><b>📕 {course.title}</b><span style='font-size:9px;color:#888;position:relative;top:2px;'>{course_duration} min</span></div>", unsafe_allow_html=True)
                for mod in modules:
                    m_space, m_col = st.columns([1, 10])
                    with m_space:
                        st.markdown("<div style='text-align:right; color:#ccc; margin-top:-5px; font-size:20px;'>↳</div>", unsafe_allow_html=True)
                    with m_col:
                        st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center; line-height:1.2;'><b>📦 Module {mod.order_index}: {mod.title}</b><span style='font-size:9px;color:#888;position:relative;top:2px;'>{module_durations[mod.id]} min</span></div>", unsafe_allow_html=True)
                    
                    lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                    for les in lessons:
                        progress = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=les.id).first()
                        icon = "✅" if progress and progress.is_completed else "🔸"
                        lbl = f"✅ {les.title} ({lesson_durations[les.id]} min)" if les.id == selected_lesson_id else f"{icon} {les.title} ({lesson_durations[les.id]} min)"
                        
                        l_space1, l_space2, l_col = st.columns([1, 1, 9])
                        with l_space2:
                            st.markdown("<div style='text-align:right; color:#ccc; margin-top:-5px; font-size:20px;'>↳</div>", unsafe_allow_html=True)
                        with l_col:
                            if st.button(lbl, key=f"lesson_select_{les.id}", use_container_width=True):
                                st.session_state['selected_lesson_id'] = les.id
                                st.rerun()
            
            with col2:
                if selected_lesson_id:
                    # Time tracking trigger
                    track_lesson_time(user.id, selected_lesson_id)
                    
                    lesson = db.query(Lesson).get(selected_lesson_id)
                    st.markdown(f"### {lesson.title}")
                    
                    # Track index for next/prev buttons
                    current_idx = -1
                    for idx, les in enumerate(all_lessons):
                        if les.id == selected_lesson_id:
                            current_idx = idx
                            break
                            
                    # Read current progress status
                    progress = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=lesson.id).first()
                    is_done = progress and progress.is_completed
                    
                    def render_lesson_actions():
                        watch_percent = progress.watch_percentage if progress else 0.0
                        duration_mins = (progress.watch_duration_seconds / 60.0) if progress and progress.watch_duration_seconds else 0.0
                        rev_count = progress.revise_count if progress else 0
                        comp_count = progress.completion_count if progress else 0
                        
                        st.markdown(f"""
                        <div style='display: flex; gap: 15px; font-size: 16px; margin-bottom: 10px; color: #555; background: #fafafa; padding: 10px; border-radius: 8px;'>
                            <span title='Watch Progress'>📈 {watch_percent:.1f}%</span>
                            <span title='Time Spent'>⏱️ {duration_mins:.1f}m</span>
                            <span title='Revisions'>🔄 {rev_count}</span>
                            <span title='Completions'>✅ {comp_count}</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            if is_done:
                                st.success("Completed! 🎉")
                            else:
                                if st.button("Mark Complete ✅", key="manual_mark_complete", use_container_width=True):
                                    p = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=lesson.id).first()
                                    if not p:
                                        p = LessonProgress(child_id=user.id, lesson_id=lesson.id)
                                        db.add(p)
                                    p.is_completed = True
                                    p.watch_percentage = 100.0
                                    p.completion_count = 1
                                    p.completed_at = utcnow()
                                    db.commit()
                                    log_activity(user.id, "lesson_completed", metadata={"lesson_id": lesson.id, "mode": "manual"})
                                    st.success("Great job!")
                                    st.rerun()
                        with c2:
                            if is_done:
                                revise = st.checkbox("Revise", key="revise_chk")
                                if revise and st.button("Mark Revision 🔄", use_container_width=True):
                                    p = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=lesson.id).first()
                                    p.revise_count = (p.revise_count or 0) + 1
                                    db.commit()
                                    st.success("Revision tracked!")
                                    st.rerun()

                        st.markdown(" ")
                        nav1, nav2 = st.columns(2)
                        with nav1:
                            if current_idx > 0:
                                if st.button("⬅️ Prev", use_container_width=True):
                                    track_lesson_time(user.id, all_lessons[current_idx - 1].id)
                                    st.session_state['selected_lesson_id'] = all_lessons[current_idx - 1].id
                                    st.rerun()
                        with nav2:
                            if current_idx >= 0 and current_idx < len(all_lessons) - 1:
                                if st.button("Next ➡️", use_container_width=True):
                                    track_lesson_time(user.id, all_lessons[current_idx + 1].id)
                                    st.session_state['selected_lesson_id'] = all_lessons[current_idx + 1].id
                                    st.rerun()
                            elif current_idx == len(all_lessons) - 1:
                                st.markdown("<span style='color:#4ECDC4; font-weight:bold;'>🎓 End of course!</span>", unsafe_allow_html=True)
                    
                    # Content Display
                    if lesson.lesson_type == 'video':
                        st.markdown("### 🎥 View & Learn")
                        
                        @st.dialog("Video Player & Class Notes", width="large")
                        def _show_video_popup(vid_id=None, vid_path=None):
                            import streamlit.components.v1 as components
                            components.html("""
                            <script>
                            setTimeout(function() {
                                const parentDoc = window.parent.document;
                                
                                if (!parentDoc.getElementById('max-dialog-style')) {
                                    const style = parentDoc.createElement('style');
                                    style.id = 'max-dialog-style';
                                    style.innerHTML = `
                                    body.st-maximized-dialog div[role="dialog"] {
                                        width: calc(100vw - 24px) !important;
                                        max-width: calc(100vw - 24px) !important;
                                        height: calc(100vh - 24px) !important;
                                        max-height: calc(100vh - 24px) !important;
                                        transform: none !important;
                                        top: 12px !important;
                                        left: 12px !important;
                                        margin: 0 !important;
                                    }
                                    `;
                                    parentDoc.head.appendChild(style);
                                }
                                
                                const dialog = parentDoc.querySelector('div[role="dialog"]');
                                if (!dialog) return;
                                
                                const closeBtn = dialog.querySelector('button[aria-label="Close"]');
                                if (!closeBtn) return;
                                
                                if (!parentDoc.getElementById('custom-maximize-btn')) {
                                    const maxBtn = parentDoc.createElement('button');
                                    maxBtn.id = 'custom-maximize-btn';
                                    maxBtn.innerHTML = '🗖';
                                    
                                    maxBtn.style.position = 'absolute';
                                    maxBtn.style.right = '3rem';
                                    maxBtn.style.top = '0.5rem';
                                    maxBtn.style.background = 'transparent';
                                    maxBtn.style.border = 'none';
                                    maxBtn.style.color = window.getComputedStyle(closeBtn).color;
                                    maxBtn.style.cursor = 'pointer';
                                    maxBtn.style.fontSize = '1.2rem';
                                    maxBtn.style.padding = '0.25rem 0.5rem';
                                    maxBtn.style.borderRadius = '0.25rem';
                                    maxBtn.style.zIndex = '9999';
                                    
                                    maxBtn.onmouseover = function() { maxBtn.style.backgroundColor = 'rgba(151, 166, 196, 0.15)'; };
                                    maxBtn.onmouseout = function() { maxBtn.style.backgroundColor = 'transparent'; };
                                    
                                    dialog.appendChild(maxBtn);
                                    
                                    maxBtn.onclick = function() {
                                        if (parentDoc.body.classList.contains("st-maximized-dialog")) {
                                            parentDoc.body.classList.remove("st-maximized-dialog");
                                            maxBtn.innerHTML = '🗖';
                                        } else {
                                            parentDoc.body.classList.add("st-maximized-dialog");
                                            maxBtn.innerHTML = '🗗';
                                        }
                                    };
                                }
                            }, 500);
                            </script>
                            """, width=0, height=0)
                            
                            # Proportional split to maximize video size (left) vs wordpad (right)
                            col_vid, col_note = st.columns([2.2, 1])
                            
                            with col_vid:
                                if vid_id:
                                    st.video(f"https://www.youtube.com/watch?v={vid_id}")
                                elif vid_path:
                                    st.video(vid_path)
                                    
                            with col_note:
                                st.markdown("### 📝 Wordpad")
                                import datetime, re, os
                                from modules.notes import get_user_notes_dir
                                
                                date_str = datetime.datetime.now().strftime("%Y%m%d")
                                module_title = db.query(Module).get(lesson.module_id).title
                                course_title = course.title
                                
                                safe_course = re.sub(r'[^\w\s-]', '', course_title).strip().replace(' ', '_')
                                safe_module = re.sub(r'[^\w\s-]', '', module_title).strip().replace(' ', '_')
                                default_fn = f"{safe_course}_{safe_module}_{date_str}.md"
                                
                                filename = st.text_input("Filename", value=default_fn, label_visibility="collapsed")
                                from streamlit_quill import st_quill
                                content = st_quill(
                                    value="",
                                    placeholder="Type your notes here... (Rich Text supported)",
                                    html=True,
                                    key=f"quill_note_{lesson.id}"
                                )
                                
                                if st.button("💾 Save to 'My Notes'", use_container_width=True):
                                    if not filename.endswith('.md'):
                                        filename += '.md'
                                    user_dir = get_user_notes_dir(user.id)
                                    filepath = os.path.join(user_dir, filename)
                                    with open(filepath, 'w', encoding='utf-8') as f:
                                        f.write(content)
                                    st.success("Note saved successfully!")

                        if lesson.video_file_path:
                            col_thumb, col_desc = st.columns([1.5, 2.5])
                            with col_thumb:
                                st.markdown("""<div style='text-align:center; padding: 20px; background: #f0f2f6; border-radius: 8px;'>
                                            <h1 style='margin:0;'>🎬</h1><p>Video File</p></div>""", unsafe_allow_html=True)
                                if st.button("🎥 Play Video", key=f"popup_{lesson.id}", use_container_width=True):
                                    _show_video_popup(vid_path=lesson.video_file_path)
                            with col_desc:
                                if lesson.content_text:
                                    st.markdown(lesson.content_text)
                                render_lesson_actions()
                        else:
                            from modules.videos import extract_youtube_id
                            video_id = extract_youtube_id(lesson.video_url)
                            if video_id:
                                col_thumb, col_desc = st.columns([1.5, 2.5])
                                with col_thumb:
                                    thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                                    st.markdown(f'<div class="thumb-anchor-{lesson.id}"></div>', unsafe_allow_html=True)
                                    if st.button("Play Video", key=f"popup_{lesson.id}", use_container_width=True):
                                        _show_video_popup(vid_id=video_id)
                                        
                                    st.markdown(f"""
                                    <style>
                                    button[title="View fullscreen"] {{ display: none !important; }}
                                    div.element-container:has(.thumb-anchor-{lesson.id}) + div.element-container div[data-testid="stButton"] button p {{
                                        visibility: hidden;
                                    }}
                                    div.element-container:has(.thumb-anchor-{lesson.id}) + div.element-container div[data-testid="stButton"] button {{
                                        background-image: url('{thumb_url}');
                                        background-size: cover;
                                        background-position: center;
                                        height: 200px;
                                        width: 100%;
                                        border: none;
                                        border-radius: 12px;
                                        position: relative;
                                    }}
                                    div.element-container:has(.thumb-anchor-{lesson.id}) + div.element-container div[data-testid="stButton"] button::after {{
                                        content: "▶";
                                        color: white;
                                        font-size: 50px;
                                        position: absolute;
                                        top: 50%; left: 50%;
                                        transform: translate(-50%, -50%);
                                        text-shadow: 0px 4px 15px rgba(0,0,0,0.8);
                                    }}
                                    div.element-container:has(.thumb-anchor-{lesson.id}) + div.element-container div[data-testid="stButton"] button:hover {{
                                        opacity: 0.9;
                                        border: 2px solid #FFD93D;
                                        transform: scale(1.02);
                                        transition: all 0.2s;
                                    }}
                                    </style>
                                    """, unsafe_allow_html=True)
                                with col_desc:
                                    if lesson.content_text:
                                        st.markdown(lesson.content_text)
                                    render_lesson_actions()
                            else:
                                st.warning("No valid Video provided.")
                                if lesson.content_text:
                                    st.markdown(lesson.content_text)
                                render_lesson_actions()
                            
                    elif lesson.lesson_type == 'text':
                        st.markdown(lesson.content_text, unsafe_allow_html=True)
                        st.markdown("---")
                        render_lesson_actions()
                        
                    elif lesson.lesson_type == 'external_link':
                        st.markdown(f"[🔗 Open External Link]({lesson.external_url})")
                        st.markdown("---")
                        render_lesson_actions()
                        
                    elif lesson.lesson_type == 'pdf':
                        if lesson.pdf_file_path:
                            import os, base64
                            if os.path.exists(lesson.pdf_file_path):
                                with open(lesson.pdf_file_path, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.error("PDF file not found on disk.")
                            
                            st.markdown(f"[📥 Download PDF Worksheet]({lesson.pdf_file_path})")
                        st.markdown("---")
                        render_lesson_actions()
                            
                    elif lesson.lesson_type == 'quiz':
                        st.markdown("### ❓ Interactive Quiz")
                        if lesson.content_text:
                            st.markdown(lesson.content_text)
                            
                        if not lesson.quiz_data:
                            st.warning("This quiz has no questions uploaded yet.")
                            st.markdown("---")
                            render_lesson_actions()
                        elif is_done and progress and getattr(progress, 'quiz_results', None):
                            st.success("✅ You have already passed this quiz!")
                            attempt = progress.quiz_results
                            if attempt["score"] < len(attempt["questions"]):
                                with st.expander("🔍 Review Incorrect Answers", expanded=False):
                                    for idx, q in enumerate(attempt["questions"]):
                                        user_ans = attempt["answers"].get(q["UniqueID"])
                                        if user_ans != q["Right_Answer"]:
                                            st.markdown(f"**Q{idx+1}. {q['Question']}**")
                                            st.markdown(f"<span style='color:#d9534f;'>❌ Your Answer: {user_ans if user_ans else 'No answer provided'}</span>", unsafe_allow_html=True)
                                            st.markdown(f"<span style='color:#28a745;'>✅ Correct Answer: {q['Right_Answer']}</span>", unsafe_allow_html=True)
                                            st.markdown("---")
                            render_lesson_actions()
                        else:
                            import random
                            state_key = f"quiz_attempt_{lesson.id}"
                            if state_key not in st.session_state:
                                questions = lesson.quiz_data.copy()
                                if len(questions) > 10:
                                    questions = random.sample(questions, 10)
                                else:
                                    random.shuffle(questions)
                                for q in questions:
                                    random.shuffle(q["Options"])
                                st.session_state[state_key] = {
                                    "questions": questions,
                                    "answers": {},
                                    "submitted": False,
                                    "score": 0,
                                    "passed": False
                                }
                            
                            attempt = st.session_state[state_key]
                            
                            if attempt["submitted"]:
                                if attempt["passed"]:
                                    st.success(f"🎉 **Congratulations!** You passed with a score of {attempt['score']}/{len(attempt['questions'])} ({(attempt['score']/len(attempt['questions']))*100:.0f}%)!")
                                    st.balloons()
                                    st.markdown("---")
                                else:
                                    st.error(f"Keep trying! You scored {attempt['score']}/{len(attempt['questions'])}. You need 70% to pass.")
                                    if st.button("🔄 Retake Quiz", key=f"retake_{lesson.id}", type="primary"):
                                        del st.session_state[state_key]
                                        st.rerun()
                                    st.markdown("---")
                                    
                                if attempt["score"] < len(attempt["questions"]):
                                    with st.expander("🔍 Review Incorrect Answers", expanded=False):
                                        for idx, q in enumerate(attempt["questions"]):
                                            user_ans = attempt["answers"].get(q["UniqueID"])
                                            if user_ans != q["Right_Answer"]:
                                                st.markdown(f"**Q{idx+1}. {q['Question']}**")
                                                st.markdown(f"<span style='color:#d9534f;'>❌ Your Answer: {user_ans if user_ans else 'No answer provided'}</span>", unsafe_allow_html=True)
                                                st.markdown(f"<span style='color:#28a745;'>✅ Correct Answer: {q['Right_Answer']}</span>", unsafe_allow_html=True)
                                                st.markdown("---")
                                                
                                if attempt["passed"]:
                                    render_lesson_actions()
                                else:
                                    nav1, nav2 = st.columns(2)
                                    with nav1:
                                        if current_idx > 0:
                                            if st.button("⬅️ Prev", key="quiz_fail_prev", use_container_width=True):
                                                track_lesson_time(user.id, all_lessons[current_idx - 1].id)
                                                st.session_state['selected_lesson_id'] = all_lessons[current_idx - 1].id
                                                st.rerun()
                                    with nav2:
                                        if current_idx >= 0 and current_idx < len(all_lessons) - 1:
                                            if st.button("Next ➡️", key="quiz_fail_next", use_container_width=True):
                                                track_lesson_time(user.id, all_lessons[current_idx + 1].id)
                                                st.session_state['selected_lesson_id'] = all_lessons[current_idx + 1].id
                                                st.rerun()
                            else:
                                with st.form(f"quiz_form_{lesson.id}"):
                                    for idx, q in enumerate(attempt["questions"]):
                                        st.markdown(f"**Q{idx+1}. {q['Question']}**")
                                        ans = st.radio("Select an answer:", q["Options"], key=f"q_{lesson.id}_{q['UniqueID']}", index=None)
                                        attempt["answers"][q["UniqueID"]] = ans
                                        st.markdown("---")
                                        
                                    if st.form_submit_button("Submit Quiz", type="primary", use_container_width=True):
                                        score = 0
                                        for q in attempt["questions"]:
                                            if attempt["answers"].get(q["UniqueID"]) == q["Right_Answer"]:
                                                score += 1
                                        attempt["score"] = score
                                        pass_mark = int(len(attempt["questions"]) * 0.7)
                                        attempt["passed"] = score >= pass_mark
                                        attempt["submitted"] = True
                                        
                                        if attempt["passed"] and not is_done:
                                            p = db.query(LessonProgress).filter_by(child_id=user.id, lesson_id=lesson.id).first()
                                            if not p:
                                                p = LessonProgress(child_id=user.id, lesson_id=lesson.id)
                                                db.add(p)
                                            p.is_completed = True
                                            p.watch_percentage = 100.0
                                            p.completion_count = (p.completion_count or 0) + 1
                                            p.completed_at = utcnow()
                                            p.quiz_results = attempt
                                            db.commit()
                                            log_activity(user.id, "lesson_completed", metadata={"lesson_id": lesson.id, "mode": "quiz_passed"})
                                            st.toast("✅ Quiz Passed!")
                                            
                                            from modules.rewards import award_points, award_badge
                                            points_earned = lesson.points_reward or 10
                                            award_points(user.id, points_earned, f"Passed Quiz: {lesson.title}", "lesson", lesson.id)
                                            
                                            from database.models import Badge
                                            b1 = db.query(Badge).filter_by(name="Quiz Master").first()
                                            if b1: award_badge(db, user.id, b1.id)
                                            
                                            total_les = db.query(Lesson).join(Module).filter(Module.course_id == course_id).count()
                                            if total_les > 0:
                                                comp_les = db.query(LessonProgress).join(Lesson).join(Module).filter(
                                                    Module.course_id == course_id, 
                                                    LessonProgress.child_id == user.id, 
                                                    LessonProgress.is_completed == True
                                                ).count()
                                                if comp_les / total_les >= 0.5:
                                                    b2 = db.query(Badge).filter_by(name="Halfway There").first()
                                                    if b2: award_badge(db, user.id, b2.id)
                                            
                                        st.rerun()
                else:
                    st.info("Select a lesson from the left to start learning.")
    finally:
        db.close()

def _get_lesson_icon(lesson_type):
    """Return emoji icon for lesson type."""
    icons = {
        'video': '🎥',
        'text': '📄',
        'pdf': '📑',
        'external_link': '🔗',
        'quiz': '❓',
    }
    return icons.get(lesson_type, '📝')


def _get_next_order(db, model_class, parent_field, parent_id):
    """Return the next order_index for a new item under a given parent."""
    from sqlalchemy import func
    max_order = db.query(func.max(model_class.order_index)).filter(
        getattr(model_class, parent_field) == parent_id
    ).scalar()
    return (max_order or 0) + 1


def _reorder_item(db, model_class, item_id, direction, parent_field):
    """Move an item up (-1) or down (+1) within its parent's ordering."""
    item = db.query(model_class).get(item_id)
    if not item:
        return
    parent_id = getattr(item, parent_field)
    siblings = db.query(model_class).filter(
        getattr(model_class, parent_field) == parent_id
    ).order_by(model_class.order_index, model_class.created_at).all()

    idx = next((i for i, s in enumerate(siblings) if s.id == item.id), None)
    if idx is None:
        return

    swap_idx = idx + direction
    if 0 <= swap_idx < len(siblings):
        # Normalize order_index sequentially to fix any existing duplicates
        for i, s in enumerate(siblings):
            s.order_index = i + 1
            
        # Swap order_index values
        siblings[idx].order_index, siblings[swap_idx].order_index = \
            siblings[swap_idx].order_index, siblings[idx].order_index
        db.commit()


def _handle_pdf_upload(uploaded_file, course_title):
    """Save an uploaded PDF file and return the saved file path."""
    import re, uuid
    from config import PDFS_DIR
    safe_name = re.sub(r'[^\w\s-]', '', course_title).strip().replace(' ', '_')[:50]
    course_dir = os.path.join(PDFS_DIR, safe_name)
    os.makedirs(course_dir, exist_ok=True)
    ext = os.path.splitext(uploaded_file.name)[1] or '.pdf'
    filename = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    filepath = os.path.join(course_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return filepath

def _handle_video_upload(uploaded_file, course_title):
    """Save an uploaded Video file and return the saved file path."""
    import re, uuid
    from config import VIDEOS_DIR
    safe_name = re.sub(r'[^\w\s-]', '', course_title).strip().replace(' ', '_')[:50]
    course_dir = os.path.join(VIDEOS_DIR, safe_name)
    os.makedirs(course_dir, exist_ok=True)
    ext = os.path.splitext(uploaded_file.name)[1] or '.mp4'
    filename = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
    filepath = os.path.join(course_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    return filepath


def _inject_course_builder_css():
    """Inject CSS for the course builder tree-view UI, styled per design system."""
    st.markdown("""
    <style>
    /* ============================================ */
    /*  COURSE BUILDER — TREE VIEW CSS              */
    /* ============================================ */

    .cb-header {
        background: linear-gradient(135deg, #FF6B35, #FF8F65);
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        color: white;
    }
    .cb-header h2 {
        margin: 0;
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 22px;
        font-weight: 600;
        color: white;
    }
    .cb-header .subtitle {
        font-size: 13px;
        opacity: 0.9;
        margin-top: 2px;
    }

    /* Tree panel */
    .tree-panel {
        background: var(--bg-secondary, #FFFFFF);
        border: 1px solid var(--border-light, #E2E8F0);
        border-radius: 12px;
        padding: 12px;
        min-height: 400px;
    }

    /* Course node in tree */
    .course-tree-node {
        background: var(--bg-tertiary, #F0F2F8);
        border-radius: 8px;
        padding: 8px 12px;
        margin-bottom: 8px;
        border-left: 4px solid #FF6B35;
        transition: all 0.2s ease;
    }
    .course-tree-node:hover {
        box-shadow: 0 2px 8px rgba(255, 107, 53, 0.15);
    }
    .course-tree-node .course-title {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 15px;
        font-weight: 600;
        color: var(--text-primary, #1A1A2E);
        margin: 0;
    }
    .course-tree-node .course-meta {
        font-size: 12px;
        color: var(--text-secondary, #5A5A7A);
        margin-top: 2px;
    }
    .badge-published {
        background: #10B981;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }
    .badge-draft {
        background: #F59E0B;
        color: white;
        font-size: 10px;
        padding: 2px 6px;
        border-radius: 9999px;
        font-weight: 600;
        display: inline-block;
    }

    /* Module node */
    .module-tree-node {
        background: var(--bg-secondary, #FFFFFF);
        border: 1px solid var(--border-light, #E2E8F0);
        border-radius: 6px;
        padding: 6px 10px;
        margin: 4px 0 4px 16px;
        border-left: 3px solid #4361EE;
        transition: all 0.2s ease;
    }
    .module-tree-node:hover {
        border-left-color: #FF6B35;
        background: var(--bg-hover, #E8EAF6);
    }
    .module-tree-node .module-title {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        font-weight: 500;
        color: var(--text-primary, #1A1A2E);
        margin: 0;
    }

    /* Lesson node */
    .lesson-tree-node {
        background: var(--bg-tertiary, #F0F2F8);
        border-radius: 6px;
        padding: 4px 10px;
        margin: 2px 0 2px 32px;
        font-size: 13px;
        color: var(--text-primary, #1A1A2E);
        display: flex;
        align-items: center;
        gap: 6px;
        transition: all 0.15s ease;
        border: 1px solid transparent;
    }
    .lesson-tree-node:hover {
        border-color: #FF6B35;
        background: var(--bg-hover, #E8EAF6);
    }
    .lesson-icon {
        font-size: 14px;
        flex-shrink: 0;
    }
    .lesson-name {
        flex: 1;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Editor panel */
    .editor-panel {
        background: var(--bg-secondary, #FFFFFF);
        border: 1px solid var(--border-light, #E2E8F0);
        border-radius: 12px;
        padding: 16px;
        min-height: 400px;
    }
    .editor-title {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 18px;
        font-weight: 600;
        color: var(--text-primary, #1A1A2E);
        margin-bottom: 12px;
        padding-bottom: 8px;
        border-bottom: 1px solid var(--border-light, #E2E8F0);
    }
    .editor-section-label {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary, #5A5A7A);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin: 12px 0 6px 0;
    }

    /* Add buttons */
    .add-item-btn {
        background: transparent;
        border: 1.5px dashed var(--border-light, #E2E8F0);
        border-radius: 6px;
        padding: 6px 12px;
        color: var(--text-secondary, #5A5A7A);
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
        margin: 4px 0;
    }
    .add-item-btn:hover {
        border-color: #FF6B35;
        color: #FF6B35;
        background: rgba(255, 107, 53, 0.05);
    }

    /* Empty state */
    .cb-empty-state {
        text-align: center;
        padding: 30px 16px;
        color: var(--text-tertiary, #8E8EA0);
    }
    .cb-empty-state .empty-icon {
        font-size: 36px;
        margin-bottom: 8px;
    }
    .cb-empty-state .empty-text {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 15px;
        font-weight: 500;
    }

    /* Analytics cards within builder */
    .analytics-metric {
        background: var(--bg-tertiary, #F0F2F8);
        border-radius: 8px;
        padding: 10px 14px;
        text-align: center;
    }
    .analytics-metric .metric-value {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif;
        font-size: 24px;
        font-weight: 700;
        color: #FF6B35;
    }
    .analytics-metric .metric-label {
        font-size: 11px;
        color: var(--text-secondary, #5A5A7A);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Delete confirmation */
    .delete-warning {
        background: #FEE2E2;
        border: 1px solid #FCA5A5;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #991B1B;
        font-size: 13px;
    }

    /* Remove button boxes in course tree (keep symbols only) */
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stColumn"] button {
        padding: 0 !important;
        min-height: 2.2rem !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: inherit !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stColumn"] button:hover {
        background: rgba(0,0,0,0.05) !important;
        border-radius: 50% !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _init_builder_state():
    """Initialize session state for the course builder tree navigation."""
    defaults = {
        'cb_selected_type': None,      # 'course', 'module', 'lesson'
        'cb_selected_id': None,        # ID of selected entity
        'cb_creating': None,           # 'course', 'module', 'lesson'
        'cb_creating_parent': None,    # Parent ID when creating module/lesson
        'cb_expanded': set(),          # Set of expanded course IDs
        'cb_confirm_delete': None,     # (type, id) for pending deletion
        'cb_show_analytics': None,     # Course ID if showing analytics
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _select_item(item_type, item_id):
    """Set the selected item in the tree and clear creation mode."""
    st.session_state['cb_selected_type'] = item_type
    st.session_state['cb_selected_id'] = item_id
    st.session_state['cb_creating'] = None
    st.session_state['cb_creating_parent'] = None
    st.session_state['cb_confirm_delete'] = None
    st.session_state['cb_show_analytics'] = None


def _start_creating(item_type, parent_id=None):
    """Enter creation mode for a new item."""
    st.session_state['cb_creating'] = item_type
    st.session_state['cb_creating_parent'] = parent_id
    st.session_state['cb_selected_type'] = None
    st.session_state['cb_selected_id'] = None
    st.session_state['cb_confirm_delete'] = None
    st.session_state['cb_show_analytics'] = None


def show_course_builder(user):
    """Main course builder with tree-view UI."""
    _init_builder_state()
    _inject_course_builder_css()

    # Header
    st.markdown("""
    <div class="cb-header">
        <div>
            <h2>🏗️ Course Builder</h2>
            <div class="subtitle">Create and manage your courses, modules, and lessons</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tabs = ["🏗️ Builder Mode", "👁️ Student Preview"]
    if user.role in ['admin', 'institute_admin']:
        tabs = ["🌐 Global Course Explorer", "🏗️ Builder Mode", "👁️ Student Preview"]

    if 'cb_active_tab' not in st.session_state:
        st.session_state['cb_active_tab'] = tabs[0]
        
    cols = st.columns(len(tabs))
    for i, tab in enumerate(tabs):
        with cols[i]:
            if st.button(tab, key=f"cb_tab_{i}", use_container_width=True, type="primary" if st.session_state['cb_active_tab'] == tab else "secondary"):
                st.session_state['cb_active_tab'] = tab
                st.rerun()

    st.markdown("---")
    
    active_tab = st.session_state.get('cb_active_tab', "🏗️ Builder Mode")

    if active_tab == "🏗️ Builder Mode":
        # Two-column layout: Tree (left) | Editor (right)
        col_tree, col_editor = st.columns([1.2, 2.0])

        with col_tree:
            _render_course_tree(user)

        with col_editor:
            _render_editor_panel(user)
            
    elif active_tab == "👁️ Student Preview":
        _render_student_preview(user)
        
    elif active_tab == "🌐 Global Course Explorer" and user.role in ['admin', 'institute_admin']:
        _render_global_course_explorer(user)

def _render_global_course_explorer(user):
    from database.models import User
    db = SessionLocal()
    try:
        st.markdown("### 🌐 Global Course Explorer")
        role_txt = "Admin" if user.role == "admin" else "Institute Admin"
        st.info(f"As an {role_txt}, you can view all courses across the platform, see their enrollments, and manage them.")
        
        courses = db.query(Course).order_by(Course.created_at.desc()).all()
        if not courses:
            st.info("No courses found on the platform.")
            return
            
        for course in courses:
            enrollments = db.query(Enrollment).filter_by(course_id=course.id).count()
            creator = db.query(User).get(course.created_by)
            creator_name = creator.full_name or creator.username if creator else "Unknown"
            status = "Published" if course.is_published else "Draft"
            
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 2, 1, 1], vertical_alignment="center")
                with c1:
                    st.markdown(f"**{course.title}**")
                    st.caption(f"Created by: {creator_name} | Status: {status} | Category: {course.category}")
                with c2:
                    st.markdown(f"**{enrollments} Enrollments**")
                with c3:
                    can_edit = True
                    if user.role == 'institute_admin':
                        if course.institute_id != st.session_state.get('active_institute_id'):
                            can_edit = False
                            
                    if can_edit:
                        if st.button("✏️ Edit", key=f"glb_edit_{course.id}", use_container_width=True):
                            _select_item('course', course.id)
                            st.session_state['cb_active_tab'] = "🏗️ Builder Mode"
                            st.toast(f"Course '{course.title}' loaded in Builder Mode.")
                            st.rerun()
                    else:
                        st.button("✏️ Edit", key=f"glb_edit_dis_{course.id}", disabled=True, use_container_width=True, help="You can only edit courses belonging to your active institute.")
                with c4:
                    if can_edit:
                        if st.button("🗑️ Delete", key=f"glb_del_{course.id}", type="primary", use_container_width=True):
                            st.session_state['cb_confirm_delete'] = ('course', course.id)
                            st.toast(f"Confirm deletion in 'Builder Mode' tab.")
                            st.rerun()
                    else:
                        st.button("🗑️ Delete", key=f"glb_del_dis_{course.id}", type="primary", disabled=True, use_container_width=True)
    finally:
        db.close()


def _render_course_tree(user):
    """Render the left-panel course tree with expandable modules and lessons."""

    # New Course button
    if st.button("➕ Create New Course", key="cb_new_course_btn", use_container_width=True):
        _start_creating('course')
        st.rerun()

    st.markdown("---")

    db = SessionLocal()
    try:
        if user.role == 'admin':
            active_course_id = None
            sel_type = st.session_state.get('cb_selected_type')
            sel_id = st.session_state.get('cb_selected_id')
            if sel_type == 'course' and sel_id:
                active_course_id = sel_id
            elif sel_type == 'module' and sel_id:
                m = db.query(Module).get(sel_id)
                if m: active_course_id = m.course_id
            elif sel_type == 'lesson' and sel_id:
                l = db.query(Lesson).get(sel_id)
                if l:
                    m = db.query(Module).get(l.module_id)
                    if m: active_course_id = m.course_id
                    
            if active_course_id:
                courses = db.query(Course).filter(
                    (Course.created_by == user.id) | (Course.id == active_course_id)
                ).order_by(Course.created_at.desc()).all()
            else:
                courses = db.query(Course).filter(Course.created_by == user.id).order_by(Course.created_at.desc()).all()
                
        elif user.role == 'institute_admin' and st.session_state.get('active_institute_id'):
            courses = db.query(Course).filter(Course.institute_id == st.session_state['active_institute_id']).order_by(Course.created_at.desc()).all()
        else:
            courses = db.query(Course).filter(Course.created_by == user.id).order_by(Course.created_at.desc()).all()

        if not courses:
            st.markdown("""
            <div class="cb-empty-state">
                <div class="empty-icon">📚</div>
                <div class="empty-text">No courses yet</div>
                <div style="font-size:13px;margin-top:4px;">Click above to create your first course!</div>
            </div>
            """, unsafe_allow_html=True)
            return

        for course in courses:
            is_selected = (st.session_state.get('cb_selected_type') == 'course'
                           and st.session_state.get('cb_selected_id') == course.id)
            status_badge = '<span class="badge-published">Published</span>' if course.is_published else '<span class="badge-draft">Draft</span>'
            module_count = db.query(Module).filter_by(course_id=course.id).count()

            # Course node
            with st.container(border=True):
                c_title, c1, c2, c3 = st.columns([5, 1, 1, 1], vertical_alignment="center")
                with c_title:
                    st.markdown(f"<div style='display: flex; align-items: center; min-height: 2.2rem;'><b>📕 {course.title}</b>&nbsp;&nbsp;{status_badge}&nbsp;&nbsp;<span style='font-size:12px;color:gray;'>{course.category or ''} · {module_count} modules</span></div>", unsafe_allow_html=True)
                with c1:
                    if st.button("✏️", help="Edit Course", key=f"cb_edit_c_{course.id}", type="tertiary", use_container_width=True):
                        _select_item('course', course.id)
                        st.rerun()
                with c2:
                    if st.button("📊", help="View Stats", key=f"cb_stats_c_{course.id}", type="tertiary", use_container_width=True):
                        st.session_state['cb_show_analytics'] = course.id
                        st.session_state['cb_selected_type'] = None
                        st.session_state['cb_selected_id'] = None
                        st.session_state['cb_creating'] = None
                        st.rerun()
                with c3:
                    if st.button("🗑️", help="Delete Course", key=f"cb_del_c_{course.id}", type="tertiary", use_container_width=True):
                        st.session_state['cb_confirm_delete'] = ('course', course.id)
                        st.rerun()

            # Modules under this course
            course_id = course.id  # capture for use below
            modules = db.query(Module).filter_by(course_id=course_id).order_by(Module.order_index).all()

            for mod in modules:
                is_mod_sel = (st.session_state.get('cb_selected_type') == 'module'
                              and st.session_state.get('cb_selected_id') == mod.id)
                lesson_count = db.query(Lesson).filter_by(module_id=mod.id).count()

                m_space, m_col = st.columns([1, 20])
                with m_space:
                    st.markdown("<div style='text-align:right; color:#ccc; margin-top:20px; font-size:24px;'>↳</div>", unsafe_allow_html=True)
                with m_col:
                    with st.container(border=True):
                        st.markdown(f"<div style='font-size:11px; color:#888; font-weight:600; text-transform:uppercase; margin-bottom:-10px; padding-left: 2px;'>Module {mod.order_index}</div>", unsafe_allow_html=True)
                        m_title, mc1, mc2, mc3, mc4 = st.columns([8, 1, 1, 1, 1], vertical_alignment="center")
                        with m_title:
                            st.markdown(f"<div style='display: flex; align-items: center; min-height: 2.2rem;'><b>📦 {mod.title}</b>&nbsp;&nbsp;<span style='font-size:11px;color:gray;'>({lesson_count} lessons)</span></div>", unsafe_allow_html=True)
                        with mc1:
                            if st.button("✏️", help="Edit Module", key=f"cb_edit_m_{mod.id}", type="tertiary", use_container_width=True):
                                _select_item('module', mod.id)
                                st.rerun()
                        with mc2:
                            if st.button("▲", help="Move Up", key=f"cb_up_m_{mod.id}", type="tertiary", use_container_width=True):
                                _reorder_item(db, Module, mod.id, -1, 'course_id')
                                st.rerun()
                        with mc3:
                            if st.button("▼", help="Move Down", key=f"cb_down_m_{mod.id}", type="tertiary", use_container_width=True):
                                _reorder_item(db, Module, mod.id, 1, 'course_id')
                                st.rerun()
                        with mc4:
                            if st.button("🗑️", help="Delete Module", key=f"cb_del_m_{mod.id}", type="tertiary", use_container_width=True):
                                st.session_state['cb_confirm_delete'] = ('module', mod.id)
                                st.rerun()

                # Lessons under this module
                lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                for les in lessons:
                    is_les_sel = (st.session_state.get('cb_selected_type') == 'lesson'
                                  and st.session_state.get('cb_selected_id') == les.id)
                    icon = _get_lesson_icon(les.lesson_type)

                    l_space1, l_space2, l_col = st.columns([1, 1, 19])
                    with l_space2:
                        st.markdown("<div style='text-align:right; color:#ccc; margin-top:10px; font-size:24px;'>↳</div>", unsafe_allow_html=True)
                    with l_col:
                        with st.container(border=True):
                            l_title, lc1, lc2, lc3, lc4 = st.columns([8, 1, 1, 1, 1], vertical_alignment="center")
                            with l_title:
                                st.markdown(f"<div style='display: flex; align-items: center; min-height: 2.2rem;'>{icon} {les.title}</div>", unsafe_allow_html=True)
                            with lc1:
                                if st.button("✏️", help="Edit Lesson", key=f"cb_edit_l_{les.id}", type="tertiary", use_container_width=True):
                                    _select_item('lesson', les.id)
                                    st.rerun()
                            with lc2:
                                if st.button("▲", help="Move Up", key=f"cb_up_l_{les.id}", type="tertiary", use_container_width=True):
                                    _reorder_item(db, Lesson, les.id, -1, 'module_id')
                                    st.rerun()
                            with lc3:
                                if st.button("▼", help="Move Down", key=f"cb_down_l_{les.id}", type="tertiary", use_container_width=True):
                                    _reorder_item(db, Lesson, les.id, 1, 'module_id')
                                    st.rerun()
                            with lc4:
                                if st.button("🗑️", help="Delete Lesson", key=f"cb_del_l_{les.id}", type="tertiary", use_container_width=True):
                                    st.session_state['cb_confirm_delete'] = ('lesson', les.id)
                                    st.rerun()

                # Add lesson button
                l_space1, l_space2, l_col = st.columns([1, 1, 19])
                with l_col:
                    if st.button(f"➕ Add Lesson", key=f"cb_add_les_{mod.id}", use_container_width=True):
                        _start_creating('lesson', mod.id)
                        st.rerun()

            # Add module button
            m_space, m_col = st.columns([1, 20])
            with m_col:
                if st.button(f"➕ Add Module", key=f"cb_add_mod_{course_id}", use_container_width=True):
                    _start_creating('module', course_id)
                    st.rerun()

            st.markdown("---")

    finally:
        db.close()


def _render_editor_panel(user):
    """Render the right-panel editor based on current selection or creation mode."""

    # Check for delete confirmation first
    if st.session_state.get('cb_confirm_delete'):
        _render_delete_confirmation()
        return

    # Check for analytics view
    if st.session_state.get('cb_show_analytics'):
        _render_course_analytics_panel(st.session_state['cb_show_analytics'])
        return

    # Creation mode
    if st.session_state.get('cb_creating'):
        creating = st.session_state['cb_creating']
        parent_id = st.session_state.get('cb_creating_parent')
        if creating == 'course':
            _render_course_form(user)
        elif creating == 'module':
            _render_module_form(parent_id)
        elif creating == 'lesson':
            _render_lesson_form(parent_id)
        return

    # Edit mode
    sel_type = st.session_state.get('cb_selected_type')
    sel_id = st.session_state.get('cb_selected_id')

    if sel_type == 'course' and sel_id:
        _render_course_form(user, course_id=sel_id)
    elif sel_type == 'module' and sel_id:
        _render_module_form(module_id=sel_id)
    elif sel_type == 'lesson' and sel_id:
        _render_lesson_form(lesson_id=sel_id)
    else:
        # Default empty state
        st.markdown("""
        <div class="cb-empty-state">
            <div class="empty-icon">👈</div>
            <div class="empty-text">Select an item from the tree</div>
            <div style="font-size:13px;margin-top:8px;">
                Click on any course, module, or lesson to edit it.<br>
                Or click <strong>+ Create New Course</strong> to get started.
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_course_form(user, course_id=None):
    """Render course create/edit form."""
    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id) if course_id else None
        is_edit = course is not None

        title_text = "✏️ Edit Course" if is_edit else "📕 Create New Course"
        st.markdown(f'<div class="editor-title">{title_text}</div>', unsafe_allow_html=True)

        with st.form(f"course_form_{course_id or 'new'}", clear_on_submit=not is_edit):
            title = st.text_input("Course Title *", value=course.title if is_edit else "")
            desc = st.text_area("Description", value=course.description if is_edit and course.description else "", height=100)

            col1, col2 = st.columns(2)
            categories = ["Math", "Science", "English", "Art", "Coding", "Other"]
            difficulties = ["Beginner", "Intermediate", "Advanced"]
            age_groups = ["5-7", "8-10", "11-13", "14-16"]

            with col1:
                cat_idx = categories.index(course.category.capitalize()) if is_edit and course.category and course.category.capitalize() in categories else 0
                category = st.selectbox("Category", categories, index=cat_idx)
                difficulty = st.selectbox("Difficulty", difficulties,
                                          index=difficulties.index(course.difficulty_level.capitalize()) if is_edit and course.difficulty_level and course.difficulty_level.capitalize() in difficulties else 0)
                access_types = ["Open", "Restricted"]
                access_type = st.selectbox("Access Type", access_types, index=access_types.index(course.access_type) if is_edit and hasattr(course, 'access_type') and course.access_type in access_types else 0)

            with col2:
                age_group = st.selectbox("Age Group", age_groups,
                                         index=age_groups.index(course.age_group) if is_edit and course.age_group and course.age_group in age_groups else 0)
                est_hours = st.number_input("Estimated Hours", min_value=0.5, value=float(course.estimated_hours or 1.0) if is_edit else 1.0, step=0.5)
                
                if user.role == 'admin':
                    from database.models import Institute
                    all_inst = db.query(Institute).all()
                    inst_options = {"None (Global)": None}
                    for inst in all_inst:
                        inst_options[inst.name] = inst.id
                    
                    default_idx = 0
                    if is_edit and course.institute_id:
                        for i, (k, v) in enumerate(inst_options.items()):
                            if v == course.institute_id:
                                default_idx = i
                                break
                    inst_name = st.selectbox("Institute", list(inst_options.keys()), index=default_idx)
                    selected_institute_id = inst_options[inst_name]
                else:
                    selected_institute_id = st.session_state.get('active_institute_id')
                    inst_name = st.session_state.get('active_institute_name', 'None')
                    st.text_input("Institute", value=inst_name, disabled=True)

            thumbnail = st.text_input("Thumbnail URL (optional)", value=course.thumbnail_url or "" if is_edit else "")
            is_published = st.checkbox("Published", value=course.is_published if is_edit else True)

            btn_label = "💾 Save Changes" if is_edit else "📕 Create Course"
            if st.form_submit_button(btn_label, use_container_width=True):
                if not title.strip():
                    st.error("Please provide a Course Title!")
                else:
                    try:
                        if is_edit:
                            course.title = title.strip()
                            course.description = desc
                            course.category = category.lower()
                            course.difficulty_level = difficulty.lower()
                            course.age_group = age_group
                            course.estimated_hours = est_hours
                            course.access_type = access_type
                            course.institute_id = selected_institute_id
                            course.thumbnail_url = thumbnail or None
                            course.is_published = is_published
                            course.updated_at = utcnow()
                            db.commit()
                            st.success(f"✅ Course '{title}' updated!")
                        else:
                            new_course = Course(
                                title=title.strip(),
                                description=desc,
                                category=category.lower(),
                                difficulty_level=difficulty.lower(),
                                age_group=age_group,
                                estimated_hours=est_hours,
                                access_type=access_type,
                                thumbnail_url=thumbnail or None,
                                is_published=is_published,
                                created_by=user.id,
                                institute_id=selected_institute_id,
                                created_at=utcnow(),
                                updated_at=utcnow()
                            )
                            db.add(new_course)
                            db.commit()
                            st.success(f"✅ Course '{title}' created!")
                            _select_item('course', new_course.id)
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error saving course: {e}")
    finally:
        db.close()


def _render_module_form(course_id=None, module_id=None):
    """Render module create/edit form."""
    db = SessionLocal()
    try:
        module = db.query(Module).get(module_id) if module_id else None
        if module:
            course_id = module.course_id
        course = db.query(Course).get(course_id) if course_id else None
        is_edit = module is not None

        title_text = f"✏️ Edit Module" if is_edit else "📦 Add New Module"
        st.markdown(f'<div class="editor-title">{title_text}</div>', unsafe_allow_html=True)
        if course:
            st.caption(f"Course: **{course.title}**")

        with st.form(f"module_form_{module_id or 'new'}", clear_on_submit=not is_edit):
            title = st.text_input("Module Title *", value=module.title if is_edit else "")
            desc = st.text_area("Description", value=module.description or "" if is_edit else "", height=80)

            col1, col2 = st.columns(2)
            with col1:
                default_order = module.order_index if is_edit else _get_next_order(db, Module, 'course_id', course_id)
                order = st.number_input("Order", min_value=1, value=max(1, default_order), step=1)
            with col2:
                is_locked = st.checkbox("🔒 Locked", value=module.is_locked if is_edit else False)

            # Unlock-after selector
            other_modules = db.query(Module).filter(
                Module.course_id == course_id, Module.id != (module_id or -1)
            ).order_by(Module.order_index).all()
            unlock_options = {"None": None}
            for m in other_modules:
                unlock_options[f"{m.order_index}. {m.title}"] = m.id
            unlock_keys = list(unlock_options.keys())
            current_unlock = 0
            if is_edit and module.unlock_after_module_id:
                for i, (k, v) in enumerate(unlock_options.items()):
                    if v == module.unlock_after_module_id:
                        current_unlock = i
                        break
            unlock_after = st.selectbox("Unlock after module", unlock_keys, index=current_unlock)

            btn_label = "💾 Save Changes" if is_edit else "📦 Add Module"
            if st.form_submit_button(btn_label, use_container_width=True):
                if not title.strip():
                    st.error("Please provide a Module Title!")
                else:
                    try:
                        if is_edit:
                            module.title = title.strip()
                            module.description = desc or None
                            module.order_index = order
                            module.is_locked = is_locked
                            module.unlock_after_module_id = unlock_options[unlock_after]
                            db.commit()
                            st.success(f"✅ Module '{title}' updated!")
                        else:
                            new_mod = Module(
                                course_id=course_id,
                                title=title.strip(),
                                description=desc or None,
                                order_index=order,
                                is_locked=is_locked,
                                unlock_after_module_id=unlock_options[unlock_after],
                                created_at=utcnow()
                            )
                            db.add(new_mod)
                            db.commit()
                            st.success(f"✅ Module '{title}' added!")
                            _select_item('module', new_mod.id)
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error saving module: {e}")
    finally:
        db.close()


def _render_lesson_form(module_id=None, lesson_id=None):
    """Render lesson create/edit form with type-specific content fields."""
    db = SessionLocal()
    try:
        lesson = db.query(Lesson).get(lesson_id) if lesson_id else None
        if lesson:
            module_id = lesson.module_id
        module = db.query(Module).get(module_id) if module_id else None
        course = db.query(Course).get(module.course_id) if module else None
        is_edit = lesson is not None

        title_text = f"✏️ Edit Lesson" if is_edit else "📝 Add New Lesson"
        st.markdown(f'<div class="editor-title">{title_text}</div>', unsafe_allow_html=True)
        if module and course:
            st.caption(f"Course: **{course.title}** → Module: **{module.title}**")

        # Lesson type selector (outside form for dynamic content)
        lesson_types = ["video", "text", "pdf", "external_link", "quiz"]
        type_labels = {"video": "🎥 Video", "text": "📄 Text Reading", "pdf": "📑 PDF Document", "external_link": "🔗 External Link", "quiz": "❓ Quiz"}
        current_type_idx = lesson_types.index(lesson.lesson_type) if is_edit and lesson.lesson_type in lesson_types else 0

        les_type = st.selectbox(
            "Lesson Type",
            lesson_types,
            index=current_type_idx,
            format_func=lambda x: type_labels.get(x, x),
            key=f"les_type_{lesson_id or 'new'}"
        )

        with st.form(f"lesson_form_{lesson_id or 'new'}", clear_on_submit=not is_edit):
            title = st.text_input("Lesson Title *", value=lesson.title if is_edit else "")

            col1, col2 = st.columns(2)
            with col1:
                default_order = lesson.order_index if is_edit else _get_next_order(db, Lesson, 'module_id', module_id)
                order = st.number_input("Order", min_value=1, value=max(1, default_order), step=1)
            with col2:
                points = st.number_input("Points Reward", min_value=0, value=lesson.points_reward if is_edit else 10, step=5)

            duration = st.number_input("Duration (minutes)", min_value=0,
                                       value=lesson.duration_minutes or 0 if is_edit else 0, step=5)

            # Type-specific fields
            les_url = None
            les_content = None
            les_pdf_path = None
            les_ext_url = None
            les_vid_path = None

            st.markdown(f'<div class="editor-section-label">{type_labels.get(les_type, les_type)} Content</div>', unsafe_allow_html=True)

            if les_type == 'video':
                if is_edit and lesson.video_url:
                    st.markdown("**🎥 Current Video Preview:**")
                    from modules.videos import extract_youtube_id
                    vid_id = extract_youtube_id(lesson.video_url)
                    if vid_id:
                        st.video(f"https://www.youtube.com/watch?v={vid_id}")
                    else:
                        st.warning("Invalid YouTube URL saved.")
                elif is_edit and lesson.video_file_path:
                    st.markdown(f"**🎥 Current Video:** `{os.path.basename(lesson.video_file_path)}`")
                        
                les_url = st.text_input("YouTube / Video URL (Leave blank to use File Upload instead)",
                                        value=lesson.video_url or "" if is_edit else "",
                                        help="Paste the full YouTube link here. If you paste an iframe embed code, the system will try to extract the link automatically upon save.")
                
                if is_edit:
                    les_vid_path = lesson.video_file_path
                    
                les_content = st.text_area("Description / Notes",
                                           value=lesson.content_text or "" if is_edit else "", height=100)
            elif les_type == 'text':
                from streamlit_quill import st_quill
                st.markdown("**Content (Rich Text supported) ***")
                les_content = st_quill(
                    value=lesson.content_text or "" if is_edit else "",
                    placeholder="Type or paste your content here...",
                    html=True,
                    key=f"quill_edit_{lesson.id}" if is_edit else "quill_new"
                )
            elif les_type == 'pdf':
                if is_edit and lesson.pdf_file_path:
                    st.info(f"📎 Current PDF: `{os.path.basename(lesson.pdf_file_path)}`")
                les_pdf_path = st.text_input("PDF URL or file path",
                                             value=lesson.pdf_file_path or "" if is_edit else "")
                les_content = st.text_area("Description (Optional)",
                                           value=lesson.content_text or "" if is_edit else "", height=80)
            elif les_type == 'external_link':
                les_ext_url = st.text_input("External URL *",
                                            value=lesson.external_url or "" if is_edit else "")
                les_content = st.text_area("Description (Optional)",
                                           value=lesson.content_text or "" if is_edit else "", height=80)
            elif les_type == 'quiz':
                st.info("The lesson is marked as a Quiz. Students will see the quiz interface when viewing this lesson.")
                les_content = st.text_area("Quiz Description / Instructions",
                                           value=lesson.content_text or "" if is_edit else "", height=100)

            btn_label = "💾 Save Changes" if is_edit else "📝 Add Lesson"
            if st.form_submit_button(btn_label, use_container_width=True):
                if not title.strip():
                    st.error("Please provide a Lesson Title!")
                else:
                    try:
                        if is_edit:
                            from modules.videos import extract_youtube_id
                            if les_type == 'video' and les_url:
                                extracted_id = extract_youtube_id(les_url)
                                final_video_url = f"https://www.youtube.com/watch?v={extracted_id}" if extracted_id else les_url
                            else:
                                final_video_url = None

                            lesson.title = title.strip()
                            lesson.lesson_type = les_type
                            lesson.order_index = order
                            lesson.points_reward = points
                            lesson.duration_minutes = duration or None
                            lesson.video_url = final_video_url if les_type == 'video' else None
                            # preserve existing file path if not overridden
                            if les_type != 'video':
                                lesson.video_file_path = None
                            lesson.content_text = les_content
                            lesson.pdf_file_path = les_pdf_path if les_type == 'pdf' else None
                            lesson.external_url = les_ext_url if les_type == 'external_link' else None
                            db.commit()
                            st.success(f"✅ Lesson '{title}' updated!")
                        else:
                            from modules.videos import extract_youtube_id
                            if les_type == 'video' and les_url:
                                extracted_id = extract_youtube_id(les_url)
                                final_video_url = f"https://www.youtube.com/watch?v={extracted_id}" if extracted_id else les_url
                            else:
                                final_video_url = None

                            new_les = Lesson(
                                module_id=module_id,
                                title=title.strip(),
                                lesson_type=les_type,
                                order_index=order,
                                points_reward=points,
                                duration_minutes=duration or None,
                                video_url=final_video_url,
                                content_text=les_content,
                                pdf_file_path=les_pdf_path if les_type == 'pdf' else None,
                                external_url=les_ext_url if les_type == 'external_link' else None,
                                created_at=utcnow()
                            )
                            db.add(new_les)
                            db.commit()
                            st.success(f"✅ Lesson '{title}' added!")
                            _select_item('lesson', new_les.id)
                        st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"Error saving lesson: {e}")

        # File uploaders
        if les_type == 'pdf':
            st.markdown("---")
            st.markdown("**📤 Upload PDF File**")
            uploaded = st.file_uploader("Choose a PDF file", type=['pdf'], key=f"pdf_upload_{lesson_id or 'new'}")
            if uploaded is not None:
                course_title = course.title if course else "uncategorized"
                saved_path = _handle_pdf_upload(uploaded, course_title)
                if saved_path:
                    # Update lesson with new PDF path
                    if is_edit:
                        lesson.pdf_file_path = saved_path
                        db.commit()
                        st.success(f"✅ PDF uploaded: `{os.path.basename(saved_path)}`")
                        st.rerun()
                    else:
                        st.info(f"📎 PDF saved: `{os.path.basename(saved_path)}`. Create the lesson first, then upload.")
                        
        elif les_type == 'video' and not les_url:
            st.markdown("---")
            st.markdown("**📤 Upload Video File** (Leave YouTube URL blank to use this)")
            uploaded_vid = st.file_uploader("Choose a Video file", type=['mp4', 'mov', 'avi'], key=f"vid_upload_{lesson_id or 'new'}")
            if uploaded_vid is not None:
                course_title = course.title if course else "uncategorized"
                saved_vid_path = _handle_video_upload(uploaded_vid, course_title)
                if saved_vid_path:
                    if is_edit:
                        lesson.video_file_path = saved_vid_path
                        lesson.video_url = None # ensure URL is empty
                        db.commit()
                        st.success(f"✅ Video uploaded: `{os.path.basename(saved_vid_path)}`")
                        st.rerun()
                    else:
                        st.info(f"📎 Video saved: `{os.path.basename(saved_vid_path)}`. Create the lesson first, then upload.")
                        
        elif les_type == 'quiz':
            st.markdown("---")
            st.markdown("**📤 Upload Quiz Questions (Excel/CSV)**")
            
            import pandas as pd
            import io
            import uuid
            template_df = pd.DataFrame(columns=["Question", "Option-1", "Option-2", "Option-3", "Option-4", "Right Answer"])
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                template_df.to_excel(writer, index=False)
            st.download_button(
                label="📥 Download Quiz Template (.xlsx)",
                data=buffer.getvalue(),
                file_name="Quiz_Template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"dl_template_{lesson_id or 'new'}"
            )
            
            if is_edit and lesson.quiz_data:
                st.success(f"✅ Currently loaded: {len(lesson.quiz_data)} questions.")
                
            uploaded_quiz = st.file_uploader("Upload filled template", type=['csv', 'xls', 'xlsx'], key=f"quiz_upload_{lesson_id or 'new'}")
            if uploaded_quiz is not None:
                if is_edit:
                    try:
                        if uploaded_quiz.name.endswith('.csv'):
                            df = pd.read_csv(uploaded_quiz)
                        else:
                            df = pd.read_excel(uploaded_quiz)
                            
                        required_cols = ["Question", "Option-1", "Option-2", "Option-3", "Option-4", "Right Answer"]
                        missing = [c for c in required_cols if c not in df.columns]
                        if missing:
                            st.error(f"Missing columns: {', '.join(missing)}")
                        else:
                            df = df.fillna("")
                            quiz_list = []
                            has_error = False
                            for idx, row in df.iterrows():
                                if not str(row["Question"]).strip(): continue
                                options = [str(row["Option-1"]).strip(), str(row["Option-2"]).strip(), str(row["Option-3"]).strip(), str(row["Option-4"]).strip()]
                                right_answer = str(row["Right Answer"]).strip()
                                if right_answer not in options:
                                    st.error(f"Right Answer '{right_answer}' does not match any options for question: {row['Question']}")
                                    has_error = True
                                    break
                                q_dict = {
                                    "UniqueID": str(uuid.uuid4()),
                                    "Question_ID": f"Q{idx+1}",
                                    "Question": str(row["Question"]).strip(),
                                    "Options": options,
                                    "Right_Answer": right_answer
                                }
                                quiz_list.append(q_dict)
                                
                            if not has_error and quiz_list:
                                lesson.quiz_data = quiz_list
                                db.commit()
                                st.success(f"✅ Successfully uploaded {len(quiz_list)} questions!")
                                # Clear the uploader by avoiding a rerun with the same key, but Streamlit uploader persists until cleared manually. We can rerun.
                                st.rerun()
                    except Exception as e:
                        st.error(f"Error parsing file: {e}")
                else:
                    st.info("📎 Please click 'Add Lesson' to create the quiz lesson first, then you can upload the questions.")
    finally:
        db.close()


def _render_delete_confirmation():
    """Render delete confirmation dialog."""
    del_type, del_id = st.session_state['cb_confirm_delete']
    db = SessionLocal()
    try:
        if del_type == 'course':
            item = db.query(Course).get(del_id)
            if not item:
                st.session_state['cb_confirm_delete'] = None
                st.rerun()
                return
            module_count = db.query(Module).filter_by(course_id=del_id).count()
            lesson_count = db.query(Lesson).join(Module).filter(Module.course_id == del_id).count()
            st.markdown(f'<div class="editor-title">⚠️ Delete Course</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="delete-warning">
                <strong>Are you sure you want to delete "{item.title}"?</strong><br>
                This will also delete <strong>{module_count} module(s)</strong> and <strong>{lesson_count} lesson(s)</strong>.<br>
                This action <strong>cannot be undone</strong>.
            </div>
            """, unsafe_allow_html=True)
        elif del_type == 'module':
            item = db.query(Module).get(del_id)
            if not item:
                st.session_state['cb_confirm_delete'] = None
                st.rerun()
                return
            lesson_count = db.query(Lesson).filter_by(module_id=del_id).count()
            st.markdown(f'<div class="editor-title">⚠️ Delete Module</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="delete-warning">
                <strong>Are you sure you want to delete module "{item.title}"?</strong><br>
                This will also delete <strong>{lesson_count} lesson(s)</strong>.<br>
                This action <strong>cannot be undone</strong>.
            </div>
            """, unsafe_allow_html=True)
        elif del_type == 'lesson':
            item = db.query(Lesson).get(del_id)
            if not item:
                st.session_state['cb_confirm_delete'] = None
                st.rerun()
                return
            st.markdown(f'<div class="editor-title">⚠️ Delete Lesson</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="delete-warning">
                <strong>Are you sure you want to delete lesson "{item.title}"?</strong><br>
                This action <strong>cannot be undone</strong>.
            </div>
            """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ Yes, Delete", key="cb_confirm_del_yes", use_container_width=True):
                try:
                    if del_type == 'course':
                        item = db.query(Course).get(del_id)
                        if item:
                            db.delete(item)
                            db.commit()
                            st.success("Course deleted.")
                    elif del_type == 'module':
                        item = db.query(Module).get(del_id)
                        if item:
                            db.delete(item)
                            db.commit()
                            st.success("Module deleted.")
                    elif del_type == 'lesson':
                        item = db.query(Lesson).get(del_id)
                        if item:
                            db.delete(item)
                            db.commit()
                            st.success("Lesson deleted.")
                except Exception as e:
                    db.rollback()
                    st.error(f"Error deleting: {e}")
                st.session_state['cb_confirm_delete'] = None
                st.session_state['cb_selected_type'] = None
                st.session_state['cb_selected_id'] = None
                st.rerun()

        with col2:
            if st.button("❌ Cancel", key="cb_confirm_del_no", use_container_width=True):
                st.session_state['cb_confirm_delete'] = None
                st.rerun()

    finally:
        db.close()


def _render_course_analytics_panel(course_id):
    """Render analytics for a specific course in the editor panel."""
    st.markdown(f'<div class="editor-title">📊 Course Analytics</div>', unsafe_allow_html=True)

    db = SessionLocal()
    try:
        course = db.query(Course).get(course_id)
        if not course:
            st.warning("Course not found.")
            return

        st.markdown(f"**{course.title}**")

        enrollments = db.query(Enrollment).filter_by(course_id=course_id).all()
        module_count = db.query(Module).filter_by(course_id=course_id).count()
        lesson_count = db.query(Lesson).join(Module).filter(Module.course_id == course_id).count()

        # Metrics row
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""
            <div class="analytics-metric">
                <div class="metric-value">{len(enrollments)}</div>
                <div class="metric-label">Students</div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="analytics-metric">
                <div class="metric-value">{module_count}</div>
                <div class="metric-label">Modules</div>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            st.markdown(f"""
            <div class="analytics-metric">
                <div class="metric-value">{lesson_count}</div>
                <div class="metric-label">Lessons</div>
            </div>
            """, unsafe_allow_html=True)

        if not enrollments:
            st.info("No students enrolled yet.")
        else:
            avg_progress = sum(e.progress_percentage for e in enrollments) / len(enrollments)
            st.metric("Average Progress", f"{avg_progress:.1f}%")

            st.markdown("#### Student Progress")
            for e in enrollments:
                from database.models import User
                student = db.query(User).get(e.child_id)
                name = student.full_name if student else f"User {e.child_id}"
                with st.expander(f"{name} — {e.progress_percentage:.1f}%"):
                    course_lessons = db.query(Lesson).join(Module).filter(Module.course_id == course_id).all()
                    lesson_ids = [l.id for l in course_lessons]
                    if lesson_ids:
                        progress_records = db.query(LessonProgress).filter(
                            LessonProgress.child_id == e.child_id,
                            LessonProgress.lesson_id.in_(lesson_ids)
                        ).all()
                        if progress_records:
                            import pandas as pd
                            data = []
                            for pr in progress_records:
                                l_title = next((l.title for l in course_lessons if l.id == pr.lesson_id), "Unknown")
                                data.append({
                                    "Lesson": l_title,
                                    "Progress %": f"{pr.watch_percentage:.0f}%",
                                    "Time (mins)": round((pr.watch_duration_seconds or 0) / 60, 1),
                                    "Done": "✅" if pr.is_completed else "❌",
                                })
                            st.dataframe(pd.DataFrame(data), use_container_width=True)
                        else:
                            st.caption("No lesson activity yet.")

        # Close analytics button
        if st.button("← Back to Editor", key="cb_close_analytics", use_container_width=True):
            st.session_state['cb_show_analytics'] = None
            st.rerun()

    finally:
        db.close()


def _render_student_preview(user):
    """Render a student-like preview of the currently active course."""
    db = SessionLocal()
    try:
        active_course_id = None
        sel_type = st.session_state.get('cb_selected_type')
        sel_id = st.session_state.get('cb_selected_id')
        if sel_type == 'course' and sel_id:
            active_course_id = sel_id
        elif sel_type == 'module' and sel_id:
            m = db.query(Module).get(sel_id)
            if m: active_course_id = m.course_id
        elif sel_type == 'lesson' and sel_id:
            l = db.query(Lesson).get(sel_id)
            if l:
                m = db.query(Module).get(l.module_id)
                if m: active_course_id = m.course_id

        if not active_course_id:
            st.info("👈 Please select a course in Builder Mode first to see its preview.")
            return

        course = db.query(Course).get(active_course_id)
        if not course:
            st.info("Selected course not found.")
            return

        st.markdown("### 👁️ Student Preview")
        st.caption("This shows exactly what a student sees when they open your course.")
        
        course_id = active_course_id
        
        if course_id:
            course = db.query(Course).get(course_id)
            modules = db.query(Module).filter_by(course_id=course.id).order_by(Module.order_index).all()
            
            if not modules:
                st.info("This course has no modules yet.")
                return

            # Calculate durations and mock progress
            course_duration = 0
            module_durations = {}
            lesson_durations = {}

            all_lessons = []
            for mod in modules:
                mod_lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                all_lessons.extend(mod_lessons)
                mod_dur = 0
                for les in mod_lessons:
                    dur = les.duration_minutes or 0
                    lesson_durations[les.id] = dur
                    mod_dur += dur
                module_durations[mod.id] = mod_dur
                course_duration += mod_dur

            progress_pct = 0.0 # Mock progress for preview
            
            st.markdown("---")
            st.markdown("""
            <style>
            .stProgress > div > div > div > div {
                background-color: #28a745 !important;
            }
            </style>
            """, unsafe_allow_html=True)
            st.progress(progress_pct)
            st.markdown(f"<div style='font-size:12px; color:gray; margin-top:-10px; margin-bottom:10px;'>Course Progress: 0% (0m / {course_duration}m) [PREVIEW]</div>", unsafe_allow_html=True)
            
            st.markdown(f"## {course.title}")
            
            # Simple Sidebar / Main Area for learning
            col1, col2 = st.columns([1.75, 2.25])
            
            with col1:
                st.markdown("#### Course Flow")
                selected_lesson_id = st.session_state.get('preview_selected_lesson_id')
                if not selected_lesson_id and all_lessons:
                    selected_lesson_id = all_lessons[0].id
                    st.session_state['preview_selected_lesson_id'] = selected_lesson_id
                    
                st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center; line-height:1.2;'><b>📕 {course.title}</b><span style='font-size:9px;color:#888;position:relative;top:2px;'>{course_duration} min</span></div>", unsafe_allow_html=True)
                for mod in modules:
                    m_space, m_col = st.columns([1, 10])
                    with m_space:
                        st.markdown("<div style='text-align:right; color:#ccc; margin-top:-5px; font-size:20px;'>↳</div>", unsafe_allow_html=True)
                    with m_col:
                        st.markdown(f"<div style='display: flex; justify-content: space-between; align-items: center; line-height:1.2;'><b>📦 Module {mod.order_index}: {mod.title}</b><span style='font-size:9px;color:#888;position:relative;top:2px;'>{module_durations[mod.id]} min</span></div>", unsafe_allow_html=True)
                        
                    lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                    for les in lessons:
                        lbl = f"✅ {les.title} ({lesson_durations[les.id]} min)" if les.id == selected_lesson_id else f"🔸 {les.title} ({lesson_durations[les.id]} min)"
                        
                        l_space1, l_space2, l_col = st.columns([1, 1, 9])
                        with l_space2:
                            st.markdown("<div style='text-align:right; color:#ccc; margin-top:-5px; font-size:20px;'>↳</div>", unsafe_allow_html=True)
                        with l_col:
                            if st.button(lbl, key=f"preview_lesson_select_{les.id}", use_container_width=True):
                                st.session_state['preview_selected_lesson_id'] = les.id
                                st.rerun()
            
            with col2:
                if selected_lesson_id:
                    lesson = db.query(Lesson).get(selected_lesson_id)
                    st.markdown(f"### {lesson.title}")
                    
                    current_idx = -1
                    for idx, les in enumerate(all_lessons):
                        if les.id == selected_lesson_id:
                            current_idx = idx
                            break
                    
                    def _render_mock_lesson_actions():
                        st.markdown(f"""
                        <div style='display: flex; gap: 15px; font-size: 16px; margin-bottom: 10px; color: #555; background: #fafafa; padding: 10px; border-radius: 8px;'>
                            <span title='Watch Progress'>📈 100.0%</span>
                            <span title='Time Spent'>⏱️ 5.0m</span>
                            <span title='Revisions'>🔄 0</span>
                            <span title='Completions'>✅ 1</span>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            st.success("Completed! 🎉 (Preview)")
                        with c2:
                            revise = st.checkbox("Revise", key=f"prev_revise_chk_{lesson.id}")
                            if revise:
                                st.button("Mark Revision 🔄", use_container_width=True, key=f"prev_rev_btn_{lesson.id}")
                                
                        st.markdown(" ")
                        nav1, nav2 = st.columns(2)
                        with nav1:
                            if current_idx > 0:
                                if st.button("⬅️ Prev", use_container_width=True, key="prev_btn_prev"):
                                    st.session_state['preview_selected_lesson_id'] = all_lessons[current_idx - 1].id
                                    st.rerun()
                        with nav2:
                            if current_idx >= 0 and current_idx < len(all_lessons) - 1:
                                if st.button("Next ➡️", use_container_width=True, key="prev_btn_next"):
                                    st.session_state['preview_selected_lesson_id'] = all_lessons[current_idx + 1].id
                                    st.rerun()
                            elif current_idx == len(all_lessons) - 1:
                                st.markdown("<span style='color:#4ECDC4; font-weight:bold;'>🎓 End of course!</span>", unsafe_allow_html=True)

                    # Content Display
                    if lesson.lesson_type == 'video':
                        st.markdown("### 🎥 View & Learn")
                        
                        @st.dialog("Video Player & Class Notes", width="large")
                        def _show_video_popup(vid_id=None, vid_path=None):
                            if vid_id:
                                st.video(f"https://www.youtube.com/watch?v={vid_id}")
                            elif vid_path:
                                st.video(vid_path)
                                
                        if lesson.video_file_path:
                            # Local video file
                            col_thumb, col_desc = st.columns([1.5, 2.5])
                            with col_thumb:
                                st.markdown("""<div style='text-align:center; padding: 20px; background: #f0f2f6; border-radius: 8px;'>
                                            <h1 style='margin:0;'>🎬</h1><p>Video File</p></div>""", unsafe_allow_html=True)
                                if st.button("🎥 Play Video", key=f"popup_{lesson.id}", use_container_width=True):
                                    _show_video_popup(vid_path=lesson.video_file_path)
                            with col_desc:
                                if lesson.content_text:
                                    st.markdown(lesson.content_text, unsafe_allow_html=True)
                                _render_mock_lesson_actions()
                        else:
                            from modules.videos import extract_youtube_id
                            video_id = extract_youtube_id(lesson.video_url)
                            
                            if video_id:
                                col_thumb, col_desc = st.columns([1.5, 2.5])
                                with col_thumb:
                                    thumb_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
                                    st.markdown(f'<div class="thumb-anchor-preview-{lesson.id}"></div>', unsafe_allow_html=True)
                                    if st.button("Play Video", key=f"popup_{lesson.id}", use_container_width=True):
                                        _show_video_popup(vid_id=video_id)
                                        
                                    st.markdown(f"""
                                    <style>
                                    button[title="View fullscreen"] {{ display: none !important; }}
                                    div.element-container:has(.thumb-anchor-preview-{lesson.id}) + div.element-container div[data-testid="stButton"] button p {{
                                        visibility: hidden;
                                    }}
                                    div.element-container:has(.thumb-anchor-preview-{lesson.id}) + div.element-container div[data-testid="stButton"] button {{
                                        background-image: url('{thumb_url}');
                                        background-size: cover;
                                        background-position: center;
                                        height: 200px;
                                        width: 100%;
                                        border: none;
                                        border-radius: 12px;
                                        position: relative;
                                    }}
                                    div.element-container:has(.thumb-anchor-preview-{lesson.id}) + div.element-container div[data-testid="stButton"] button::after {{
                                        content: "▶";
                                        color: white;
                                        font-size: 50px;
                                        position: absolute;
                                        top: 50%; left: 50%;
                                        transform: translate(-50%, -50%);
                                        text-shadow: 0px 4px 15px rgba(0,0,0,0.8);
                                    }}
                                    div.element-container:has(.thumb-anchor-preview-{lesson.id}) + div.element-container div[data-testid="stButton"] button:hover {{
                                        opacity: 0.9;
                                        border: 2px solid #FFD93D;
                                        transform: scale(1.02);
                                        transition: all 0.2s;
                                    }}
                                    </style>
                                    """, unsafe_allow_html=True)
                                with col_desc:
                                    if lesson.content_text:
                                        st.markdown(lesson.content_text, unsafe_allow_html=True)
                                    _render_mock_lesson_actions()
                            else:
                                st.warning("No valid Video provided.")
                                if lesson.content_text:
                                    st.markdown(lesson.content_text, unsafe_allow_html=True)
                                _render_mock_lesson_actions()
                            
                    elif lesson.lesson_type == 'text':
                        st.markdown(lesson.content_text, unsafe_allow_html=True)
                        st.markdown("---")
                        _render_mock_lesson_actions()
                        
                    elif lesson.lesson_type == 'external_link':
                        st.markdown(f"[🔗 Open External Link]({lesson.external_url})")
                        st.markdown("---")
                        _render_mock_lesson_actions()
                        
                    elif lesson.lesson_type == 'pdf':
                        if lesson.pdf_file_path:
                            import os, base64
                            st.markdown(f"**PDF File:** `{os.path.basename(lesson.pdf_file_path)}`")
                            
                            if os.path.exists(lesson.pdf_file_path):
                                with open(lesson.pdf_file_path, "rb") as f:
                                    base64_pdf = base64.b64encode(f.read()).decode('utf-8')
                                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.error("PDF file not found on disk.")
                                
                            st.markdown(f"[📥 Download PDF Worksheet]({lesson.pdf_file_path})")
                            st.info("PDF scroll tracker preview is disabled in Teacher Preview mode.")
                        st.markdown("---")
                        _render_mock_lesson_actions()
                            
                    elif lesson.lesson_type == 'quiz':
                        st.markdown("### ❓ Interactive Quiz")
                        if lesson.content_text:
                            st.markdown(lesson.content_text)
                            
                        if not lesson.quiz_data:
                            st.warning("This quiz has no questions uploaded yet.")
                            st.markdown("---")
                            _render_mock_lesson_actions()
                        else:
                            import random
                            state_key = f"prev_quiz_attempt_{lesson.id}"
                            if state_key not in st.session_state:
                                questions = lesson.quiz_data.copy()
                                if len(questions) > 10:
                                    questions = random.sample(questions, 10)
                                else:
                                    random.shuffle(questions)
                                for q in questions:
                                    random.shuffle(q["Options"])
                                st.session_state[state_key] = {
                                    "questions": questions,
                                    "answers": {},
                                    "submitted": False,
                                    "score": 0,
                                    "passed": False
                                }
                            
                            attempt = st.session_state[state_key]
                            
                            if attempt["submitted"]:
                                if attempt["passed"]:
                                    st.success(f"🎉 **Congratulations!** You passed with a score of {attempt['score']}/{len(attempt['questions'])} ({(attempt['score']/len(attempt['questions']))*100:.0f}%)! [PREVIEW]")
                                    st.balloons()
                                    st.markdown("---")
                                else:
                                    st.error(f"Keep trying! You scored {attempt['score']}/{len(attempt['questions'])}. You need 70% to pass.")
                                    if st.button("🔄 Retake Quiz", key=f"prev_retake_{lesson.id}", type="primary"):
                                        del st.session_state[state_key]
                                        st.rerun()
                                    st.markdown("---")
                                    
                                if attempt["score"] < len(attempt["questions"]):
                                    with st.expander("🔍 Review Incorrect Answers", expanded=False):
                                        for idx, q in enumerate(attempt["questions"]):
                                            user_ans = attempt["answers"].get(q["UniqueID"])
                                            if user_ans != q["Right_Answer"]:
                                                st.markdown(f"**Q{idx+1}. {q['Question']}**")
                                                st.markdown(f"<span style='color:#d9534f;'>❌ Your Answer: {user_ans if user_ans else 'No answer provided'}</span>", unsafe_allow_html=True)
                                                st.markdown(f"<span style='color:#28a745;'>✅ Correct Answer: {q['Right_Answer']}</span>", unsafe_allow_html=True)
                                                st.markdown("---")
                                                
                                if attempt["passed"]:
                                    _render_mock_lesson_actions()
                                else:
                                    nav1, nav2 = st.columns(2)
                                    with nav1:
                                        if current_idx > 0:
                                            if st.button("⬅️ Prev", key="prev_quiz_fail_prev", use_container_width=True):
                                                st.session_state['preview_selected_lesson_id'] = all_lessons[current_idx - 1].id
                                                st.rerun()
                                    with nav2:
                                        if current_idx >= 0 and current_idx < len(all_lessons) - 1:
                                            if st.button("Next ➡️", key="prev_quiz_fail_next", use_container_width=True):
                                                st.session_state['preview_selected_lesson_id'] = all_lessons[current_idx + 1].id
                                                st.rerun()
                            else:
                                with st.form(f"prev_quiz_form_{lesson.id}"):
                                    for idx, q in enumerate(attempt["questions"]):
                                        st.markdown(f"**Q{idx+1}. {q['Question']}**")
                                        ans = st.radio("Select an answer:", q["Options"], key=f"prev_q_{lesson.id}_{q['UniqueID']}", index=None)
                                        attempt["answers"][q["UniqueID"]] = ans
                                        st.markdown("---")
                                        
                                    if st.form_submit_button("Submit Quiz", type="primary", use_container_width=True):
                                        score = 0
                                        for q in attempt["questions"]:
                                            if attempt["answers"].get(q["UniqueID"]) == q["Right_Answer"]:
                                                score += 1
                                        attempt["score"] = score
                                        pass_mark = int(len(attempt["questions"]) * 0.7)
                                        attempt["passed"] = score >= pass_mark
                                        attempt["submitted"] = True
                                        
                                        if attempt["passed"]:
                                            st.toast("✅ Quiz Passed! [PREVIEW]")
                                        st.rerun()
                else:
                    st.info("Select a lesson from the left to start previewing.")
    finally:
        db.close()


def show_course_explorer(user):
    """Standalone Course Explorer for Parents/Teachers to assign courses."""
    from database.models import Institute, Enrollment, UserRelation, User
    db = SessionLocal()
    try:
        st.markdown("### 🌐 Course Explorer")
        st.info("Browse available courses and assign them to your learners.")
        
        # Filter logic: if Admin, see all. If Institute admin/teacher/parent, see Open + their Institute's Restricted
        query = db.query(Course).filter(Course.is_published == True)
        if user.role != 'admin':
            active_inst = st.session_state.get('active_institute_id')
            from sqlalchemy import or_
            query = query.filter(or_(Course.access_type == 'Open', Course.institute_id == active_inst))
            
        courses = query.order_by(Course.created_at.desc()).all()
        if not courses:
            st.info("No courses found.")
            return
            
        # Draw Tiles
        cols = st.columns(3)
        for idx, course in enumerate(courses):
            with cols[idx % 3]:
                inst = db.query(Institute).get(course.institute_id) if course.institute_id else None
                inst_name = inst.name if inst else "Global"
                
                with st.container(border=True):
                    st.markdown(f"#### {course.title}")
                    st.markdown(f"**Institute:** {inst_name}")
                    st.markdown(f"**Access:** {course.access_type}")
                    st.markdown(f"**Duration:** {course.estimated_hours} hrs")
                    st.markdown(f"**Category:** {course.category.capitalize()}")
                    
                    if user.role in ['parent', 'teacher']:
                        if st.button("Assign Course", key=f"assign_course_{course.id}", use_container_width=True):
                            st.session_state['assigning_course_id'] = course.id
                            
        # Handle assignment popup/logic
        assign_cid = st.session_state.get('assigning_course_id')
        if assign_cid:
            course_to_assign = db.query(Course).get(assign_cid)
            st.markdown("---")
            st.markdown(f"### Assign '{course_to_assign.title}'")
            
            # get children/students
            if user.role == 'parent':
                relations = db.query(UserRelation).filter_by(guardian_id=user.id).all()
                child_ids = [r.child_id for r in relations]
                students = db.query(User).filter(User.id.in_(child_ids)).all()
            else:
                # Teacher can assign to any child in their institute
                active_inst = st.session_state.get('active_institute_id')
                from database.models import UserInstitute
                uis = db.query(UserInstitute).filter_by(institute_id=active_inst).all()
                uids = [ui.user_id for ui in uis]
                students = db.query(User).filter(User.id.in_(uids), User.role == 'child').all()
                
            if not students:
                st.warning("No learners available to assign.")
            else:
                student_options = {f"{s.full_name or s.username} ({s.username})": s.id for s in students}
                selected_student_name = st.selectbox("Select Learner", list(student_options.keys()))
                assign_type = st.selectbox("Assignment Type", ["Mandatory", "Optional"])
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Confirm Assignment", use_container_width=True, type="primary"):
                        sid = student_options[selected_student_name]
                        existing = db.query(Enrollment).filter_by(child_id=sid, course_id=course_to_assign.id).first()
                        if existing:
                            st.warning("Learner is already enrolled in this course.")
                        else:
                            new_enc = Enrollment(
                                child_id=sid,
                                course_id=course_to_assign.id,
                                assignment_type=assign_type,
                                status='not_started'
                            )
                            db.add(new_enc)
                            db.commit()
                            st.success(f"Assigned {course_to_assign.title} successfully!")
                            st.session_state['assigning_course_id'] = None
                            st.rerun()
                with c2:
                    if st.button("Cancel", use_container_width=True):
                        st.session_state['assigning_course_id'] = None
                        st.rerun()

    finally:
        db.close()
