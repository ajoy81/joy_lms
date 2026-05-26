import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'ajoy_academy.db')}")

# App Settings
APP_NAME = "Joy LMS"
APP_TAGLINE = "Where Learning Meets Fun! 🚀"

# Upload directories
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
WORKSHEETS_DIR = os.path.join(UPLOAD_DIR, "worksheets")
HOMEWORK_DIR = os.path.join(UPLOAD_DIR, "homework_submissions")
TIMELINE_MEDIA_DIR = os.path.join(UPLOAD_DIR, "timeline_media")
CERTIFICATES_DIR = os.path.join(UPLOAD_DIR, "certificates")
PDFS_DIR = os.path.join(UPLOAD_DIR, "pdfs")

VIDEOS_DIR = os.path.join(UPLOAD_DIR, "videos")
NOTES_DIR = os.path.join(UPLOAD_DIR, "notes")

# PDF upload settings
ALLOWED_PDF_EXTENSIONS = ['.pdf']
MAX_PDF_SIZE_MB = 50

# Lesson content types
CONTENT_TYPES = ['video', 'text', 'pdf', 'external_link', 'quiz']

# Ensure upload directories exist
for directory in [WORKSHEETS_DIR, HOMEWORK_DIR, TIMELINE_MEDIA_DIR, CERTIFICATES_DIR, PDFS_DIR, VIDEOS_DIR, NOTES_DIR]:
    os.makedirs(directory, exist_ok=True)
