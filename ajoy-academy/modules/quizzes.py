import streamlit as st
import json
from database.engine import SessionLocal
from database.models import Quiz, QuizAttempt, Course, Module
from modules.activity_tracker import log_activity
from datetime import datetime
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def show_quiz_creator(user):
    st.markdown("## 🧠 Quiz Creator")
    
    db = SessionLocal()
    try:
        courses = db.query(Course).filter_by(created_by=user.id).all()
        if not courses:
            st.info("You need to create a course first before adding a quiz.")
            return
            
        course_id = st.selectbox("Select Course", [c.id for c in courses], format_func=lambda x: db.query(Course).get(x).title)
        modules = db.query(Module).filter_by(course_id=course_id).order_by(Module.order_index).all()
        module_id = st.selectbox("Select Module (optional)", [None] + [m.id for m in modules], format_func=lambda x: "None" if x is None else db.query(Module).get(x).title)
        
        quiz_type = st.radio("Quiz Type", ["custom", "google_form"])
        
        with st.form("quiz_creation_form"):
            title = st.text_input("Quiz Title")
            points_reward = st.number_input("Max Points Reward", value=50)
            
            if quiz_type == "google_form":
                gform_url = st.text_input("Google Form URL")
                gsheet_url = st.text_input("Google Sheet URL (for responses)")
                
                if st.form_submit_button("Save Google Form Quiz"):
                    new_quiz = Quiz(
                        course_id=course_id,
                        module_id=module_id,
                        title=title,
                        quiz_type="google_form",
                        google_form_url=gform_url,
                        google_sheet_url=gsheet_url,
                        points_reward=points_reward,
                        created_at=utcnow()
                    )
                    db.add(new_quiz)
                    db.commit()
                    st.success("Google Form Quiz saved!")
                    st.rerun()
            else:
                pass_pct = st.slider("Pass Percentage", 10, 100, 60)
                max_attempts = st.number_input("Max Attempts", value=3)
                time_limit = st.number_input("Time Limit (minutes, 0 for no limit)", value=0)
                
                # Simplified representation of JSON questions builder. 
                # In Streamlit, dynamic forms inside a st.form are tricky, 
                # but we'll accept a JSON array directly for simplicity in this prototype.
                st.markdown("### Questions JSON")
                st.info('Example: [{"question_type": "mcq", "question_text": "2+2?", "options": ["3","4"], "correct_answer": "4", "points": 10, "explanation": "2+2=4"}]')
                questions_json_str = st.text_area("Questions JSON Array", "[]")
                
                if st.form_submit_button("Save Custom Quiz"):
                    try:
                        questions = json.loads(questions_json_str)
                        new_quiz = Quiz(
                            course_id=course_id,
                            module_id=module_id,
                            title=title,
                            quiz_type="custom",
                            questions=questions,
                            pass_percentage=pass_pct,
                            max_attempts=max_attempts,
                            time_limit_minutes=time_limit if time_limit > 0 else None,
                            points_reward=points_reward,
                            created_at=utcnow()
                        )
                        db.add(new_quiz)
                        db.commit()
                        st.success("Custom Quiz saved!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error parsing questions JSON: {e}")
    finally:
        db.close()

def show_quiz_player(user, quiz_id):
    db = SessionLocal()
    try:
        quiz = db.query(Quiz).get(quiz_id)
        if not quiz:
            st.error("Quiz not found.")
            return
            
        st.markdown(f"## {quiz.title}")
        
        attempts = db.query(QuizAttempt).filter_by(child_id=user.id, quiz_id=quiz.id).count()
        if quiz.max_attempts and attempts >= quiz.max_attempts:
            st.warning("You have reached the maximum number of attempts for this quiz.")
            return
            
        if quiz.quiz_type == "google_form":
            st.markdown(f"[📝 Open Google Form Quiz]({quiz.google_form_url})")
            if st.button("I completed it!"):
                # Mock grading for gform
                attempt = QuizAttempt(
                    child_id=user.id, quiz_id=quiz.id, score=quiz.points_reward, max_score=quiz.points_reward,
                    percentage=100.0, passed=True, answers={}, time_taken_seconds=0, attempted_at=utcnow()
                )
                db.add(attempt)
                db.commit()
                log_activity(user.id, "quiz_complete", metadata={"quiz_id": quiz.id, "score": quiz.points_reward})
                st.success("Great job! Assuming completion for Google Form.")
                st.rerun()
        else:
            st.markdown(f"**Instructions:** Pass mark: {quiz.pass_percentage}%. Max Attempts: {quiz.max_attempts}")
            
            if not quiz.questions:
                st.info("This quiz has no questions.")
                return
                
            with st.form(f"quiz_form_{quiz.id}"):
                user_answers = {}
                max_score = 0
                for idx, q in enumerate(quiz.questions):
                    st.markdown(f"**Q{idx+1}: {q.get('question_text')}**")
                    if q.get('question_type') == 'mcq' or q.get('question_type') == 'true_false':
                        user_answers[str(idx)] = st.radio(f"Select answer", q.get('options', []), key=f"q_{idx}")
                    else:
                        user_answers[str(idx)] = st.text_input(f"Your answer", key=f"q_{idx}")
                    max_score += q.get('points', 10)
                    
                if st.form_submit_button("Submit Quiz"):
                    score = 0
                    for idx, q in enumerate(quiz.questions):
                        if str(user_answers[str(idx)]).strip().lower() == str(q.get('correct_answer')).strip().lower():
                            score += q.get('points', 10)
                            
                    percentage = (score / max_score) * 100 if max_score > 0 else 0
                    passed = percentage >= quiz.pass_percentage
                    
                    attempt = QuizAttempt(
                        child_id=user.id, quiz_id=quiz.id, score=score, max_score=max_score,
                        percentage=percentage, passed=passed, answers=user_answers, 
                        time_taken_seconds=0, attempted_at=utcnow()
                    )
                    db.add(attempt)
                    db.commit()
                    log_activity(user.id, "quiz_complete", metadata={"quiz_id": quiz.id, "score": score, "passed": passed})
                    
                    if passed:
                        st.success(f"🎉 You passed! Score: {score}/{max_score} ({percentage:.1f}%)")
                    else:
                        st.error(f"You scored {score}/{max_score} ({percentage:.1f}%). Keep trying!")
    finally:
        db.close()
