import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.engine import SessionLocal
from database.models import User, ActivityLog, QuizAttempt, LessonProgress, Reward, Course, Enrollment, Lesson, Module
from utils.gsheets import render_google_sheet_view
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func

def utcnow():
    return datetime.now(pytz.utc)

def common_layout(fig):
    fig.update_layout(margin=dict(l=20, r=20, t=40, b=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def show_analytics(user, child_ids):
    """Shows analytics dashboards for given child_ids."""
    st.markdown("## 📈 Analytics Dashboard")
    
    if not child_ids:
        st.info("No children linked to generate analytics.")
        return
        
    db = SessionLocal()
    try:
        # Filter for selected child
        children = db.query(User).filter(User.id.in_(child_ids)).all()
        child_dict = {c.id: c.username for c in children}
        
        options = ["All"] + child_ids
        default_index = 0
        if 'selected_child_for_analytics' in st.session_state and st.session_state['selected_child_for_analytics'] in options:
            default_index = options.index(st.session_state['selected_child_for_analytics'])
            
        selected_child_id = st.selectbox("Select Child", options, index=default_index, format_func=lambda x: "All Children" if x == "All" else child_dict[x])
        target_ids = child_ids if selected_child_id == "All" else [selected_child_id]
        
        tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Performance", "Engagement", "Detailed Progress"])
        
        with tab1:
            # Study Hours (Mocking study hours based on session duration)
            logs = db.query(ActivityLog).filter(ActivityLog.user_id.in_(target_ids), ActivityLog.action_type == 'logout').all()
            if logs:
                df_logs = pd.DataFrame([{
                    "Date": log.timestamp.date(),
                    "Minutes": log.session_duration_minutes or 0,
                    "Child": child_dict[log.user_id]
                } for log in logs])
                
                df_grouped = df_logs.groupby(["Date", "Child"])["Minutes"].sum().reset_index()
                fig1 = px.bar(df_grouped, x="Date", y="Minutes", color="Child", title="Daily Study Minutes")
                st.plotly_chart(common_layout(fig1), use_container_width=True)
            else:
                st.info("Not enough session data for Study Hours chart.")
                
            # Points Earned Timeline
            rewards = db.query(Reward).filter(Reward.child_id.in_(target_ids)).all()
            if rewards:
                df_rew = pd.DataFrame([{
                    "Date": r.awarded_at.date(),
                    "Points": r.points,
                    "Child": child_dict[r.child_id]
                } for r in rewards])
                df_rew_group = df_rew.groupby(["Date", "Child"])["Points"].sum().reset_index()
                df_rew_group['Cumulative Points'] = df_rew_group.groupby('Child')['Points'].cumsum()
                
                fig2 = px.line(df_rew_group, x="Date", y="Cumulative Points", color="Child", title="Points Over Time")
                st.plotly_chart(common_layout(fig2), use_container_width=True)
                
        with tab2:
            # Quiz Performance Line Chart
            quizzes = db.query(QuizAttempt).filter(QuizAttempt.child_id.in_(target_ids)).order_by(QuizAttempt.attempted_at).all()
            if quizzes:
                df_quiz = pd.DataFrame([{
                    "Date": q.attempted_at,
                    "Score %": q.percentage,
                    "Child": child_dict[q.child_id],
                    "Quiz ID": q.quiz_id
                } for q in quizzes])
                fig3 = px.line(df_quiz, x="Date", y="Score %", color="Child", markers=True, title="Quiz Scores Over Time")
                fig3.update_yaxes(range=[0, 105])
                st.plotly_chart(common_layout(fig3), use_container_width=True)
            else:
                st.info("No quiz attempts recorded yet.")
                
            # Video Completion Donut
            if selected_child_id != "All":
                enrollments = db.query(Enrollment).filter_by(child_id=selected_child_id).all()
                valid_course = None
                for enr in enrollments:
                    c = db.query(Course).get(enr.course_id)
                    if c:
                        valid_course = c
                        break
                        
                if valid_course:
                    lessons = db.query(Lesson).join(Module).filter(Module.course_id == valid_course.id, Lesson.lesson_type == 'video').all()
                    if lessons:
                        total_videos = len(lessons)
                        completed = db.query(LessonProgress).filter(LessonProgress.child_id == selected_child_id, LessonProgress.lesson_id.in_([l.id for l in lessons]), LessonProgress.is_completed == True).count()
                        
                        fig4 = px.pie(names=["Completed", "Remaining"], values=[completed, total_videos - completed], hole=0.5, title=f"Video Completion: {valid_course.title}")
                        fig4.update_traces(marker=dict(colors=['#4ECDC4', '#E0E0E0']))
                        st.plotly_chart(common_layout(fig4), use_container_width=True)
            
        with tab3:
            # Activity Breakdown Pie
            all_logs = db.query(ActivityLog).filter(ActivityLog.user_id.in_(target_ids)).all()
            if all_logs:
                # Group by action_type
                df_act = pd.DataFrame([{"Action": log.action_type} for log in all_logs])
                act_counts = df_act["Action"].value_counts().reset_index()
                act_counts.columns = ["Action Type", "Count"]
                
                fig5 = px.pie(act_counts, names="Action Type", values="Count", title="Activity Breakdown")
                st.plotly_chart(common_layout(fig5), use_container_width=True)
            else:
                st.info("No activity logs to breakdown.")
                
            st.markdown("### 🎯 Weekly Goal Progress")
            # Mock progress ring using plotly gauge
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = 75,
                title = {'text': "Weekly Goal %"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#FF6B6B"},
                    'steps': [
                        {'range': [0, 50], 'color': "#F0F2F6"},
                        {'range': [50, 80], 'color': "#FFD93D"},
                        {'range': [80, 100], 'color': "#4ECDC4"}
                    ]
                }
            ))
            st.plotly_chart(common_layout(fig_gauge), use_container_width=True)
            
        with tab4:
            if selected_child_id == "All":
                st.info("ℹ️ Select a single child from the dropdown above to view detailed lesson-by-lesson progress.")
            else:
                enrollments = db.query(Enrollment).filter_by(child_id=selected_child_id).all()
                if not enrollments:
                    st.info("This child is not enrolled in any courses yet.")
                else:
                    for enroll in enrollments:
                        course = db.query(Course).get(enroll.course_id)
                        if not course:
                            continue
                        
                        # Calculate total time spent on this course
                        total_seconds = db.query(func.sum(LessonProgress.watch_duration_seconds)).\
                            join(Lesson, Lesson.id == LessonProgress.lesson_id).\
                            join(Module, Module.id == Lesson.module_id).\
                            filter(LessonProgress.child_id == selected_child_id, Module.course_id == course.id).\
                            scalar() or 0
                        total_mins = total_seconds / 60.0
                        
                        # Display course header card
                        st.markdown(f"""
                        <div style="background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%); padding: 15px; border-radius: 10px; color: white; margin-bottom: 10px;">
                            <h3 style="margin: 0; color: white;">📚 {course.title}</h3>
                            <p style="margin: 5px 0 0 0; font-size: 0.9em; opacity: 0.9;">
                                Category: <b>{course.category}</b> | Difficulty: <b>{course.difficulty_level}</b> | Total Time Spent: <b>{total_mins:.1f} mins</b>
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Progress Bar
                        total_lessons = db.query(Lesson).join(Module).filter(Module.course_id == course.id).count()
                        completed = 0
                        if total_lessons > 0:
                            completed = db.query(LessonProgress).join(Lesson).join(Module).filter(
                                Module.course_id == course.id,
                                LessonProgress.child_id == selected_child_id,
                                LessonProgress.is_completed == True
                            ).count()
                            actual_progress = int((completed / total_lessons) * 100)
                        else:
                            actual_progress = 0
                            
                        st.progress(min(actual_progress / 100.0, 1.0))
                        st.write(f"Course Progress: **{actual_progress}%**")
                        
                        # Modules
                        modules = db.query(Module).filter_by(course_id=course.id).order_by(Module.order_index).all()
                        for mod in modules:
                            lessons = db.query(Lesson).filter_by(module_id=mod.id).order_by(Lesson.order_index).all()
                            if not lessons:
                                continue
                                
                            # Calculate module progress
                            mod_lessons_count = len(lessons)
                            mod_completed_count = db.query(LessonProgress).filter(
                                LessonProgress.child_id == selected_child_id,
                                LessonProgress.lesson_id.in_([l.id for l in lessons]),
                                LessonProgress.is_completed == True
                            ).count()
                            
                            mod_title_text = f"📦 {mod.title} ({mod_completed_count}/{mod_lessons_count} completed)"
                            with st.expander(mod_title_text):
                                for les in lessons:
                                    prog = db.query(LessonProgress).filter_by(child_id=selected_child_id, lesson_id=les.id).first()
                                    
                                    # Status
                                    if prog and prog.is_completed:
                                        status_icon = "🟢"
                                        status_text = "Completed"
                                    elif prog and (prog.watch_duration_seconds > 0 or (prog.watch_percentage or 0.0) > 0):
                                        status_icon = "🟠"
                                        status_text = "In Progress"
                                    else:
                                        status_icon = "⚪"
                                        status_text = "Not Started"
                                        
                                    duration_mins = (prog.watch_duration_seconds or 0) / 60.0 if prog else 0.0
                                    progress_val = prog.watch_percentage if prog else 0.0
                                    
                                    c_icon, c_title, c_type, c_status, c_pct, c_time = st.columns([0.5, 3, 1.5, 2, 2, 2])
                                    with c_icon:
                                        st.write(status_icon)
                                    with c_title:
                                        st.markdown(f"**{les.title}**")
                                    with c_type:
                                        st.caption(les.lesson_type.upper())
                                    with c_status:
                                        st.write(status_text)
                                    with c_pct:
                                        if les.lesson_type == 'video':
                                            st.write(f"Watch: {progress_val:.1f}%")
                                        elif les.lesson_type == 'pdf':
                                            st.write(f"Scroll: {progress_val:.1f}%")
                                        else:
                                            st.write("-")
                                    with c_time:
                                        st.write(f"{duration_mins:.1f} mins")
            
    finally:
        db.close()
