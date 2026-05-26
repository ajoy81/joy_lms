import streamlit as st
import os
from database.engine import SessionLocal
from database.models import Homework, HomeworkSubmission, Course, Module
from modules.activity_tracker import log_activity
from datetime import datetime
import pytz
import uuid

def utcnow():
    return datetime.now(pytz.utc)

def show_homework_creator(user):
    st.markdown("## 📝 Homework Creator")
    
    db = SessionLocal()
    try:
        courses = db.query(Course).filter_by(created_by=user.id).all()
        if not courses:
            st.info("You need to create a course first before adding homework.")
            return
            
        course_id = st.selectbox("Select Course", [c.id for c in courses], format_func=lambda x: db.query(Course).get(x).title, key="hw_course_sel")
        modules = db.query(Module).filter_by(course_id=course_id).order_by(Module.order_index).all()
        module_id = st.selectbox("Select Module (optional)", [None] + [m.id for m in modules], format_func=lambda x: "None" if x is None else db.query(Module).get(x).title, key="hw_mod_sel")
        
        hw_type = st.radio("Homework Type", ["pdf_worksheet", "google_form", "custom_text", "file_upload"], key="hw_type")
        
        with st.form("hw_creation_form"):
            title = st.text_input("Homework Title")
            description = st.text_area("Description / Instructions")
            max_points = st.number_input("Max Points", value=100)
            
            pdf_path = None
            gform_url = None
            gsheet_url = None
            
            if hw_type == "pdf_worksheet":
                st.info("For PDF worksheets, please provide instructions. Uploading files via form is handled later in this prototype.")
            elif hw_type == "google_form":
                gform_url = st.text_input("Google Form URL")
                gsheet_url = st.text_input("Google Sheet URL (for responses)")
                
            due_date = st.date_input("Due Date")
            
            if st.form_submit_button("Save Homework"):
                due_datetime = datetime.combine(due_date, datetime.min.time()).replace(tzinfo=pytz.utc)
                new_hw = Homework(
                    course_id=course_id,
                    module_id=module_id,
                    title=title,
                    description=description,
                    hw_type=hw_type,
                    pdf_file_path=pdf_path,
                    google_form_url=gform_url,
                    google_sheet_url=gsheet_url,
                    due_date=due_datetime,
                    max_points=max_points,
                    created_by=user.id,
                    created_at=utcnow()
                )
                db.add(new_hw)
                db.commit()
                st.success("Homework assignment created!")
                st.rerun()
    finally:
        db.close()

def show_homework_grading(user):
    st.markdown("## 📋 Homework Grading Queue")
    db = SessionLocal()
    try:
        hw_ids = [hw.id for hw in db.query(Homework).filter_by(created_by=user.id).all()]
        submissions = db.query(HomeworkSubmission).filter(HomeworkSubmission.homework_id.in_(hw_ids), HomeworkSubmission.graded_at == None).all()
        
        if not submissions:
            st.info("No pending submissions to grade.")
            return
            
        for sub in submissions:
            hw = db.query(Homework).get(sub.homework_id)
            with st.expander(f"Submission for: {hw.title} (Child ID: {sub.child_id})"):
                st.write(f"Submitted on: {sub.submitted_at}")
                if sub.submission_type == 'text':
                    st.write("**Answer:**")
                    st.write(sub.text_content)
                elif sub.submission_type == 'file':
                    st.write(f"[📥 Download File]({sub.file_path})")
                
                with st.form(f"grade_form_{sub.id}"):
                    score = st.number_input("Score", min_value=0, max_value=hw.max_points, value=hw.max_points)
                    feedback = st.text_area("Feedback")
                    if st.form_submit_button("Submit Grade"):
                        sub.score = score
                        sub.feedback = feedback
                        sub.graded_by = user.id
                        sub.graded_at = utcnow()
                        db.commit()
                        st.success("Graded!")
                        st.rerun()
    finally:
        db.close()

def show_child_homework(user):
    st.markdown("## 📝 My Homework")
    db = SessionLocal()
    try:
        from database.models import Enrollment
        enrolled_course_ids = [e.course_id for e in db.query(Enrollment).filter_by(child_id=user.id).all()]
        homeworks = db.query(Homework).filter(Homework.course_id.in_(enrolled_course_ids), Homework.is_active == True).all()
        
        if not homeworks:
            st.info("You don't have any homework right now.")
            return
            
        for hw in homeworks:
            sub = db.query(HomeworkSubmission).filter_by(homework_id=hw.id, child_id=user.id).first()
            status = "Completed" if sub else "Pending"
            
            with st.expander(f"[{status}] {hw.title} (Due: {hw.due_date.strftime('%Y-%m-%d') if hw.due_date else 'No Due Date'})"):
                st.write(hw.description)
                
                if sub:
                    st.success("You have submitted this homework.")
                    if sub.graded_at:
                        st.info(f"Grade: {sub.score}/{hw.max_points} | Feedback: {sub.feedback}")
                    else:
                        st.info("Waiting for grade.")
                else:
                    if hw.hw_type == "google_form":
                        st.markdown(f"[📝 Open Google Form]({hw.google_form_url})")
                        if st.button("Mark as Submitted", key=f"mark_{hw.id}"):
                            new_sub = HomeworkSubmission(homework_id=hw.id, child_id=user.id, submission_type='link', submitted_at=utcnow())
                            db.add(new_sub)
                            db.commit()
                            log_activity(user.id, "homework_submit", metadata={"homework_id": hw.id})
                            st.rerun()
                    elif hw.hw_type == "custom_text":
                        with st.form(f"submit_text_{hw.id}"):
                            answer = st.text_area("Your Answer")
                            if st.form_submit_button("Submit Work"):
                                new_sub = HomeworkSubmission(homework_id=hw.id, child_id=user.id, submission_type='text', text_content=answer, submitted_at=utcnow())
                                db.add(new_sub)
                                db.commit()
                                log_activity(user.id, "homework_submit", metadata={"homework_id": hw.id})
                                st.rerun()
                    else:
                        st.info(f"Submission type: {hw.hw_type}. Currently handled outside Streamlit prototype or placeholder.")
                        if st.button("Mark as Done", key=f"mark_done_{hw.id}"):
                            new_sub = HomeworkSubmission(homework_id=hw.id, child_id=user.id, submission_type='link', submitted_at=utcnow())
                            db.add(new_sub)
                            db.commit()
                            log_activity(user.id, "homework_submit", metadata={"homework_id": hw.id})
                            st.rerun()
    finally:
        db.close()
