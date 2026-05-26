from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, Text, Float, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from database.engine import Base

def utcnow():
    return datetime.now(pytz.utc)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False) # 'teacher', 'parent', 'child'
    full_name = Column(String(100))
    avatar_emoji = Column(String(10), default='👤')
    date_of_birth = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Profile Extensions
    profile_photo = Column(String(255), nullable=True)
    description = Column(String(100), nullable=True)
    contact_address = Column(String(255), nullable=True)
    mobile_no = Column(String(20), nullable=True)
    
    # Relationships
    institutes = relationship("UserInstitute", back_populates="user")
    created_courses = relationship("Course", back_populates="creator")
    created_homeworks = relationship("Homework", back_populates="creator")
    activity_logs = relationship("ActivityLog", back_populates="user")
    badges = relationship("UserBadge", back_populates="user")
    timeline_posts = relationship("TimelinePost", back_populates="author")
    timeline_reactions = relationship("TimelineReaction", back_populates="user")
    timeline_comments = relationship("TimelineComment", back_populates="user")
    rewards_received = relationship("Reward", foreign_keys='Reward.child_id', back_populates="child")
    rewards_awarded = relationship("Reward", foreign_keys='Reward.awarded_by', back_populates="awarded_by_user")
    certificates_received = relationship("Certificate", foreign_keys='Certificate.child_id', back_populates="child")
    certificates_issued = relationship("Certificate", foreign_keys='Certificate.issued_by', back_populates="issuer")

class UserRelation(Base):
    __tablename__ = 'user_relations'
    
    id = Column(Integer, primary_key=True)
    guardian_id = Column(Integer, ForeignKey('users.id'))
    child_id = Column(Integer, ForeignKey('users.id'))
    relation_type = Column(String(20)) # 'teacher', 'parent'
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (UniqueConstraint('guardian_id', 'child_id', name='uq_guardian_child'),)

class Institute(Base):
    __tablename__ = 'institutes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    users = relationship("UserInstitute", back_populates="institute", cascade="all, delete-orphan")

class UserInstitute(Base):
    __tablename__ = 'user_institutes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    institute_id = Column(Integer, ForeignKey('institutes.id'), nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (UniqueConstraint('user_id', 'institute_id', name='uq_user_institute'),)

    user = relationship("User", back_populates="institutes")
    institute = relationship("Institute", back_populates="users")

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    thumbnail_url = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    institute_id = Column(Integer, ForeignKey('institutes.id'), nullable=True)
    access_type = Column(String(20), default='Open') # 'Open', 'Restricted'
    is_published = Column(Boolean, default=False)
    difficulty_level = Column(String(20)) # 'beginner','intermediate','advanced'
    age_group = Column(String(20)) # '5-7', '8-10', '11-13', '14-16'
    category = Column(String(50)) # 'math','science','english','art','coding','other'
    estimated_hours = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    
    creator = relationship("User", back_populates="created_courses")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="course")
    homeworks = relationship("Homework", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")
    certificates = relationship("Certificate", back_populates="course")

class Module(Base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(200))
    description = Column(Text, nullable=True)
    order_index = Column(Integer, default=0)
    is_locked = Column(Boolean, default=False)
    unlock_after_module_id = Column(Integer, ForeignKey('modules.id'), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="module")
    homeworks = relationship("Homework", back_populates="module")
    unlock_after_module = relationship("Module", remote_side=[id])

class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('modules.id'))
    title = Column(String(200))
    lesson_type = Column(String(20)) # 'video', 'text', 'pdf', 'external_link'
    video_url = Column(String(500), nullable=True)
    video_file_path = Column(String(500), nullable=True)
    content_text = Column(Text, nullable=True)
    pdf_file_path = Column(String(500), nullable=True)
    external_url = Column(String(500), nullable=True)
    quiz_data = Column(JSON, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    order_index = Column(Integer, default=0)
    points_reward = Column(Integer, default=10)
    created_at = Column(DateTime, default=utcnow)
    
    module = relationship("Module", back_populates="lessons")
    progresses = relationship("LessonProgress", back_populates="lesson")

class Quiz(Base):
    __tablename__ = 'quizzes'

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(200))
    quiz_type = Column(String(20)) # 'custom', 'google_form'
    google_form_url = Column(String(500), nullable=True)
    google_sheet_url = Column(String(500), nullable=True)
    questions = Column(JSON)
    time_limit_minutes = Column(Integer, nullable=True)
    pass_percentage = Column(Integer, default=60)
    max_attempts = Column(Integer, default=3)
    points_reward = Column(Integer, default=50)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)
    
    module = relationship("Module", back_populates="quizzes")
    course = relationship("Course", back_populates="quizzes")
    attempts = relationship("QuizAttempt", back_populates="quiz")

class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('modules.id'), nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    title = Column(String(200))
    description = Column(Text)
    hw_type = Column(String(20)) # 'pdf_worksheet', 'google_form', 'custom_text', 'file_upload'
    pdf_file_path = Column(String(500), nullable=True)
    google_form_url = Column(String(500), nullable=True)
    google_sheet_url = Column(String(500), nullable=True)
    due_date = Column(DateTime, nullable=True)
    max_points = Column(Integer, default=100)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=utcnow)
    
    module = relationship("Module", back_populates="homeworks")
    course = relationship("Course", back_populates="homeworks")
    creator = relationship("User", back_populates="created_homeworks")
    submissions = relationship("HomeworkSubmission", back_populates="homework")

class HomeworkSubmission(Base):
    __tablename__ = 'homework_submissions'

    id = Column(Integer, primary_key=True)
    homework_id = Column(Integer, ForeignKey('homeworks.id'))
    child_id = Column(Integer, ForeignKey('users.id'))
    submission_type = Column(String(20)) # 'file', 'text', 'link'
    file_path = Column(String(500), nullable=True)
    text_content = Column(Text, nullable=True)
    submitted_at = Column(DateTime, default=utcnow)
    score = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    graded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    homework = relationship("Homework", back_populates="submissions")
    child = relationship("User", foreign_keys=[child_id])
    grader = relationship("User", foreign_keys=[graded_by])

class Enrollment(Base):
    __tablename__ = 'enrollments'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    progress_percentage = Column(Float, default=0.0)
    enrolled_at = Column(DateTime, default=utcnow)
    completed_at = Column(DateTime, nullable=True)
    certificate_issued = Column(Boolean, default=False)
    assignment_type = Column(String(20), default='Suggested')
    
    __table_args__ = (UniqueConstraint('child_id', 'course_id', name='uq_child_course'),)
    
    child = relationship("User", foreign_keys=[child_id])
    course = relationship("Course", back_populates="enrollments")

class LessonProgress(Base):
    __tablename__ = 'lesson_progresses'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    lesson_id = Column(Integer, ForeignKey('lessons.id'))
    is_completed = Column(Boolean, default=False)
    watch_duration_seconds = Column(Integer, default=0)
    watch_percentage = Column(Float, default=0.0)
    revise_count = Column(Integer, default=0)
    completion_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, default=utcnow, onupdate=utcnow)
    completed_at = Column(DateTime, nullable=True)
    quiz_results = Column(JSON, nullable=True)
    
    __table_args__ = (UniqueConstraint('child_id', 'lesson_id', name='uq_child_lesson'),)
    
    child = relationship("User", foreign_keys=[child_id])
    lesson = relationship("Lesson", back_populates="progresses")

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempts'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    quiz_id = Column(Integer, ForeignKey('quizzes.id'))
    score = Column(Integer)
    max_score = Column(Integer)
    percentage = Column(Float)
    passed = Column(Boolean)
    answers = Column(JSON)
    time_taken_seconds = Column(Integer)
    attempted_at = Column(DateTime, default=utcnow)
    
    child = relationship("User", foreign_keys=[child_id])
    quiz = relationship("Quiz", back_populates="attempts")

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    action_type = Column(String(50))
    metadata_info = Column('metadata', JSON, nullable=True)
    session_duration_minutes = Column(Float, nullable=True)
    ip_address = Column(String(45), nullable=True)
    timestamp = Column(DateTime, default=utcnow)
    
    user = relationship("User", back_populates="activity_logs")

class Reward(Base):
    __tablename__ = 'rewards'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    points = Column(Integer)
    reason = Column(String(200))
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(Integer, nullable=True)
    awarded_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    awarded_at = Column(DateTime, default=utcnow)
    
    child = relationship("User", foreign_keys=[child_id], back_populates="rewards_received")
    awarded_by_user = relationship("User", foreign_keys=[awarded_by], back_populates="rewards_awarded")

class Badge(Base):
    __tablename__ = 'badges'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True)
    emoji_icon = Column(String(10))
    description = Column(String(500))
    criteria_type = Column(String(50))
    criteria_value = Column(Integer)
    points_value = Column(Integer, default=100)
    tier = Column(String(20))
    created_at = Column(DateTime, default=utcnow)

class UserBadge(Base):
    __tablename__ = 'user_badges'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    badge_id = Column(Integer, ForeignKey('badges.id'))
    earned_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),)
    
    user = relationship("User", back_populates="badges")
    badge = relationship("Badge")

class Streak(Base):
    __tablename__ = 'streaks'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'), unique=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(Date)
    streak_freeze_count = Column(Integer, default=0)
    
    child = relationship("User", foreign_keys=[child_id])

class WeeklyGoal(Base):
    __tablename__ = 'weekly_goals'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    week_start_date = Column(Date)
    target_study_minutes = Column(Integer, default=120)
    target_lessons = Column(Integer, default=5)
    target_quizzes = Column(Integer, default=2)
    actual_study_minutes = Column(Integer, default=0)
    actual_lessons = Column(Integer, default=0)
    actual_quizzes = Column(Integer, default=0)
    achieved_percentage = Column(Float, default=0.0)
    
    __table_args__ = (UniqueConstraint('child_id', 'week_start_date', name='uq_child_week'),)
    
    child = relationship("User", foreign_keys=[child_id])

class Certificate(Base):
    __tablename__ = 'certificates'

    id = Column(Integer, primary_key=True)
    child_id = Column(Integer, ForeignKey('users.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    issued_by = Column(Integer, ForeignKey('users.id'))
    certificate_number = Column(String(50), unique=True)
    child_name_on_cert = Column(String(100))
    course_name_on_cert = Column(String(200))
    completion_date = Column(Date)
    pdf_file_path = Column(String(500))
    issued_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (UniqueConstraint('child_id', 'course_id', name='uq_child_course_cert'),)
    
    child = relationship("User", foreign_keys=[child_id], back_populates="certificates_received")
    course = relationship("Course", back_populates="certificates")
    issuer = relationship("User", foreign_keys=[issued_by], back_populates="certificates_issued")

class TimelinePost(Base):
    __tablename__ = 'timeline_posts'

    id = Column(Integer, primary_key=True)
    author_id = Column(Integer, ForeignKey('users.id'))
    post_type = Column(String(20))
    text_content = Column(Text, nullable=True)
    media_paths = Column(JSON, nullable=True)
    video_url = Column(String(500), nullable=True)
    visibility = Column(String(20), default='guardians')
    is_approved = Column(Boolean, default=True)
    is_auto_generated = Column(Boolean, default=False)
    auto_post_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=utcnow)
    
    author = relationship("User", back_populates="timeline_posts")
    reactions = relationship("TimelineReaction", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("TimelineComment", back_populates="post", cascade="all, delete-orphan")

class TimelineReaction(Base):
    __tablename__ = 'timeline_reactions'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('timeline_posts.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id'))
    reaction_type = Column(String(10))
    created_at = Column(DateTime, default=utcnow)
    
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='uq_post_user_reaction'),)
    
    post = relationship("TimelinePost", back_populates="reactions")
    user = relationship("User", back_populates="timeline_reactions")

class TimelineComment(Base):
    __tablename__ = 'timeline_comments'

    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey('timeline_posts.id', ondelete='CASCADE'))
    user_id = Column(Integer, ForeignKey('users.id'))
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)
    
    post = relationship("TimelinePost", back_populates="comments")
    user = relationship("User", back_populates="timeline_comments")
