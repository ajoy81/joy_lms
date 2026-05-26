import streamlit as st
import os
from database.engine import SessionLocal
from database.models import Certificate, Course, User, Enrollment
from utils.pdf_generator import generate_certificate_pdf
from modules.activity_tracker import log_activity
from datetime import datetime
import pytz
import uuid

def utcnow():
    return datetime.now(pytz.utc)

def issue_certificate(child_id, course_id, issuer_id):
    """Issues a certificate if one doesn't already exist."""
    db = SessionLocal()
    try:
        existing = db.query(Certificate).filter_by(child_id=child_id, course_id=course_id).first()
        if existing:
            return existing
            
        child = db.query(User).get(child_id)
        course = db.query(Course).get(course_id)
        issuer = db.query(User).get(issuer_id)
        
        cert_number = f"AJOY-{utcnow().year}-{str(uuid.uuid4())[:8].upper()}"
        filename = f"{cert_number}.pdf"
        
        # Ensure directory exists
        cert_dir = os.path.join(os.getcwd(), "uploads", "certificates")
        os.makedirs(cert_dir, exist_ok=True)
        filepath = os.path.join(cert_dir, filename)
        
        # Generate PDF
        generate_certificate_pdf(
            child_name=child.full_name or child.username,
            course_name=course.title,
            cert_number=cert_number,
            date_str=utcnow().strftime("%B %d, %Y"),
            issuer_name=issuer.full_name or issuer.username,
            filepath=filepath
        )
        
        # Save to DB
        cert = Certificate(
            child_id=child_id,
            course_id=course_id,
            issued_by=issuer_id,
            certificate_number=cert_number,
            child_name_on_cert=child.full_name or child.username,
            course_name_on_cert=course.title,
            completion_date=utcnow().date(),
            pdf_file_path=filepath,
            issued_at=utcnow()
        )
        db.add(cert)
        
        # Update Enrollment
        enrollment = db.query(Enrollment).filter_by(child_id=child_id, course_id=course_id).first()
        if enrollment:
            enrollment.certificate_issued = True
            
        # Post to timeline auto
        from database.models import TimelinePost
        post = TimelinePost(
            author_id=child_id,
            post_type="text",
            text_content=f"🎉 I earned a certificate for {course.title}!",
            is_auto_generated=True,
            auto_post_type="course_complete",
            created_at=utcnow(),
            updated_at=utcnow()
        )
        db.add(post)
        db.commit()
        
        log_activity(child_id, "certificate_earned", metadata={"course_id": course_id})
        return cert
    finally:
        db.close()

def show_certificates(user):
    st.markdown("## 🎓 My Certificates")
    
    db = SessionLocal()
    try:
        certs = db.query(Certificate).filter_by(child_id=user.id).all()
        if not certs:
            st.info("You haven't earned any certificates yet. Keep learning!")
            return
            
        for cert in certs:
            with st.expander(f"{cert.course_name_on_cert} - {cert.completion_date}"):
                st.write(f"Certificate ID: {cert.certificate_number}")
                st.write(f"Issued by: {db.query(User).get(cert.issued_by).username if cert.issued_by else 'System'}")
                if os.path.exists(cert.pdf_file_path):
                    with open(cert.pdf_file_path, "rb") as f:
                        st.download_button("📥 Download Certificate", f, file_name=os.path.basename(cert.pdf_file_path), mime="application/pdf", key=f"cert_{cert.id}")
                else:
                    st.error("Certificate file not found on server.")
    finally:
        db.close()
