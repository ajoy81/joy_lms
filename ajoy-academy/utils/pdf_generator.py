import os
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor

def generate_certificate_pdf(child_name, course_name, cert_number, date_str, issuer_name, filepath):
    """Generates a beautiful PDF certificate using ReportLab."""
    c = canvas.Canvas(filepath, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Border
    c.setStrokeColor(HexColor("#FFD93D"))
    c.setLineWidth(10)
    c.rect(20, 20, width - 40, height - 40)
    
    c.setStrokeColor(HexColor("#FF6B6B"))
    c.setLineWidth(3)
    c.rect(30, 30, width - 60, height - 60)
    
    # Content
    c.setFont("Helvetica-Bold", 36)
    c.setFillColor(HexColor("#FF6B6B"))
    c.drawCentredString(width / 2, height - 100, "🎓 Joy LMS")
    
    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(HexColor("#2C3333"))
    c.drawCentredString(width / 2, height - 170, "Certificate of Completion")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2, height - 230, "This is to certify that")
    
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(HexColor("#4ECDC4"))
    c.drawCentredString(width / 2, height - 280, child_name)
    
    c.setFont("Helvetica", 18)
    c.setFillColor(HexColor("#2C3333"))
    c.drawCentredString(width / 2, height - 330, "has successfully completed the course")
    
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(HexColor("#FF6B6B"))
    c.drawCentredString(width / 2, height - 380, course_name)
    
    # Footer details
    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#555555"))
    c.drawString(100, 100, f"Date: {date_str}")
    c.drawString(100, 70, f"Certificate ID: {cert_number}")
    
    c.drawString(width - 250, 100, f"Issued by: {issuer_name}")
    
    c.save()
    return filepath
