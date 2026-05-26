# 🎓 AJOY ACADEMY — Complete LMS Build Prompt for AI Code Agent
# ================================================================
# Copy this ENTIRE prompt into Gemini / Claude / GPT Agent
# Build instruction: Generate ALL files, one-by-one, production-ready
# ================================================================

---

## 0. PROJECT IDENTITY

- **App Name**: Ajoy Academy
- **Tagline**: "Where Learning Meets Fun! 🚀"
- **Target Audience**: Kids aged 5–16, their Parents, and Teachers
- **Deployment**: Streamlit Community Cloud (initial), scalable to PostgreSQL + cloud VMs later

---

## 1. TECH STACK (MANDATORY — Do not substitute)

| Layer           | Technology                                    |
|-----------------|-----------------------------------------------|
| Frontend        | Streamlit 1.35+ (with custom CSS for mobile)  |
| Backend/Logic   | Python 3.11+                                  |
| ORM             | SQLAlchemy 2.0+ (declarative models)          |
| Database        | SQLite (dev), PostgreSQL-ready (prod)          |
| Auth            | bcrypt for password hashing                    |
| Charts          | Plotly Express + Plotly Graph Objects           |
| Data            | Pandas                                         |
| Google Sheets   | gspread + oauth2client                         |
| PDF Generation  | reportlab (for certificates)                   |
| File Handling   | Streamlit file_uploader + local storage        |
| Date/Time       | Python datetime + pytz                         |

---

## 2. ROLE-PERMISSION MATRIX (CRITICAL — Follow exactly)

| Feature/Action               | 👨‍🏫 Teacher | 👪 Parent | 👧 Child |
|------------------------------|:--------:|:------:|:-----:|
| Register / Login / Logout    |    ✅    |   ✅   |  ✅   |
| **Manage Users** (CRUD)      |    ✅    |   ✅   |  ❌   |
| **Link Children** to self    |    ✅    |   ✅   |  ❌   |
| **Create/Edit Courses**      |    ✅    |   ✅   |  ❌   |
| Create Modules inside Course |    ✅    |   ✅   |  ❌   |
| Add Lessons (video/text)     |    ✅    |   ✅   |  ❌   |
| Create Quizzes (custom+GForm)|    ✅    |   ✅   |  ❌   |
| Create Homework (PDF/GForm)  |    ✅    |   ✅   |  ❌   |
| Upload PDF Worksheets        |    ✅    |   ✅   |  ❌   |
| View Analytics Dashboard     |    ✅    |   ✅   |  ❌   |
| Issue Certificates           |    ✅    |   ✅   |  ❌   |
| Moderate Timeline Posts      |    ✅    |   ✅   |  ❌   |
| React/Comment on Timeline    |    ✅    |   ✅   |  ❌   |
| Award Manual Bonus Points    |    ✅    |   ✅   |  ❌   |
| **Browse/Enroll in Courses** |    ❌    |   ❌   |  ✅   |
| **Watch Videos/Do Lessons**  |    ❌    |   ❌   |  ✅   |
| **Take Quizzes**             |    ❌    |   ❌   |  ✅   |
| **Submit Homework**          |    ❌    |   ❌   |  ✅   |
| **Post to Timeline**         |    ❌    |   ❌   |  ✅   |
| **Earn Points/Badges/Streaks**|   ❌    |   ❌   |  ✅   |
| **View Own Certificates**    |    ❌    |   ❌   |  ✅   |
| View Leaderboard             |    ✅    |   ✅   |  ✅   |

---

## 3. PROJECT STRUCTURE (Create every file)

```
ajoy-academy/
├── app.py                           # Main entry, routing, page config
├── config.py                        # DB URL, app settings, constants
├── requirements.txt                 # All pip dependencies
├── .streamlit/
│   └── config.toml                  # Streamlit theme + server config
│
├── database/
│   ├── __init__.py
│   ├── engine.py                    # create_engine, SessionLocal, Base
│   ├── models.py                    # ALL SQLAlchemy ORM models (below)
│   └── seed.py                      # Seed default admin + demo data
│
├── auth/
│   ├── __init__.py
│   ├── login.py                     # Login page UI + bcrypt verify
│   ├── register.py                  # Registration with role selection
│   ├── session.py                   # st.session_state manager
│   └── permissions.py               # @require_role() decorator
│
├── dashboard/
│   ├── __init__.py
│   ├── teacher_dashboard.py         # Teacher analytics + management
│   ├── parent_dashboard.py          # Parent analytics + child mgmt
│   └── child_dashboard.py           # Student learning hub
│
├── modules/
│   ├── __init__.py
│   ├── courses.py                   # Moodle-style course builder
│   ├── videos.py                    # YouTube embed + watch tracking
│   ├── homework.py                  # HW: PDF upload, GForms, custom
│   ├── quizzes.py                   # Quiz engine: MCQ, T/F, custom
│   ├── rewards.py                   # Points, badges, streaks logic
│   ├── analytics.py                 # Plotly charts + data aggregation
│   ├── certificates.py              # PDF certificate generation
│   ├── timeline.py                  # 🆕 Facebook-style social feed
│   ├── leaderboard.py               # Rankings: weekly + all-time
│   └── activity_tracker.py          # Login/logout/session logging
│
├── components/
│   ├── __init__.py
│   ├── navbar.py                    # Top nav with logo + user info
│   ├── sidebar.py                   # Role-based sidebar menu
│   ├── cards.py                     # Reusable card components
│   ├── post_composer.py             # Timeline post creation widget
│   └── media_viewer.py              # Image/Video/PDF inline viewer
│
├── uploads/                         # gitignore this in production
│   ├── worksheets/
│   ├── homework_submissions/
│   ├── timeline_media/
│   └── certificates/
│
├── assets/
│   ├── logo.png                     # Ajoy Academy logo placeholder
│   ├── badges/                      # Badge icon images (use emojis if no images)
│   └── styles.css                   # Custom mobile-first CSS
│
└── utils/
    ├── __init__.py
    ├── helpers.py                   # Formatting, slugify, time utils
    ├── gsheets.py                   # gspread read/write integration
    └── pdf_generator.py             # reportlab certificate PDF builder
```

---

## 4. DATABASE MODELS (SQLAlchemy ORM — models.py)

Generate ALL the following models in `database/models.py` using SQLAlchemy 2.0 declarative style with `DeclarativeBase`. Every model must have `__tablename__`, proper types, relationships, foreign keys, and sensible defaults.

### 4.1 User
```
- id: Integer, primary_key, autoincrement
- username: String(50), unique, not null
- email: String(120), unique, not null
- password_hash: String(255), not null  # bcrypt hashed
- role: String(20), not null  # 'teacher', 'parent', 'child'
- full_name: String(100)
- avatar_emoji: String(10), default='👤'  # fun kid-friendly avatars
- date_of_birth: Date, nullable
- is_active: Boolean, default=True
- created_at: DateTime, default=utcnow
- last_login: DateTime, nullable
```

### 4.2 UserRelation (linking guardians to children)
```
- id: Integer, primary_key
- guardian_id: FK → User.id  (teacher or parent)
- child_id: FK → User.id
- relation_type: String(20)  # 'teacher', 'parent'
- created_at: DateTime
- UNIQUE constraint on (guardian_id, child_id)
```

### 4.3 Course
```
- id: Integer, primary_key
- title: String(200), not null
- description: Text
- thumbnail_url: String(500), nullable
- created_by: FK → User.id
- is_published: Boolean, default=False
- difficulty_level: String(20)  # 'beginner','intermediate','advanced'
- age_group: String(20)  # '5-7', '8-10', '11-13', '14-16'
- category: String(50)  # 'math','science','english','art','coding','other'
- estimated_hours: Float, nullable
- created_at: DateTime
- updated_at: DateTime
```

### 4.4 Module (sections inside a course)
```
- id: Integer, primary_key
- course_id: FK → Course.id, not null
- title: String(200)
- description: Text, nullable
- order_index: Integer, default=0
- is_locked: Boolean, default=False  # sequential unlock
- unlock_after_module_id: Integer, FK → Module.id, nullable
- created_at: DateTime
```

### 4.5 Lesson (content inside a module)
```
- id: Integer, primary_key
- module_id: FK → Module.id
- title: String(200)
- lesson_type: String(20)  # 'video', 'text', 'pdf', 'external_link'
- video_url: String(500), nullable  # YouTube URL
- content_text: Text, nullable  # Rich text content
- pdf_file_path: String(500), nullable
- external_url: String(500), nullable
- duration_minutes: Integer, nullable
- order_index: Integer, default=0
- points_reward: Integer, default=10
- created_at: DateTime
```

### 4.6 Quiz
```
- id: Integer, primary_key
- module_id: FK → Module.id, nullable
- course_id: FK → Course.id
- title: String(200)
- quiz_type: String(20)  # 'custom', 'google_form'
- google_form_url: String(500), nullable
- google_sheet_url: String(500), nullable
- questions: JSON  # List of {question, options[], correct_answer, points, question_type}
- time_limit_minutes: Integer, nullable
- pass_percentage: Integer, default=60
- max_attempts: Integer, default=3
- points_reward: Integer, default=50
- is_active: Boolean, default=True
- created_at: DateTime
```

**Quiz questions JSON structure:**
```json
[
  {
    "id": 1,
    "question_type": "mcq",  // mcq, true_false, fill_blank, short_answer
    "question_text": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "correct_answer": "4",
    "points": 10,
    "explanation": "2 + 2 = 4"  // shown after answering
  }
]
```

### 4.7 Homework
```
- id: Integer, primary_key
- module_id: FK → Module.id, nullable
- course_id: FK → Course.id
- title: String(200)
- description: Text
- hw_type: String(20)  # 'pdf_worksheet', 'google_form', 'custom_text', 'file_upload'
- pdf_file_path: String(500), nullable  # uploaded worksheet PDF
- google_form_url: String(500), nullable
- google_sheet_url: String(500), nullable
- due_date: DateTime, nullable
- max_points: Integer, default=100
- is_active: Boolean, default=True
- created_by: FK → User.id
- created_at: DateTime
```

### 4.8 HomeworkSubmission
```
- id: Integer, primary_key
- homework_id: FK → Homework.id
- child_id: FK → User.id
- submission_type: String(20)  # 'file', 'text', 'link'
- file_path: String(500), nullable
- text_content: Text, nullable
- submitted_at: DateTime
- score: Integer, nullable  # graded by teacher/parent
- feedback: Text, nullable
- graded_by: FK → User.id, nullable
- graded_at: DateTime, nullable
```

### 4.9 Enrollment
```
- id: Integer, primary_key
- child_id: FK → User.id
- course_id: FK → Course.id
- progress_percentage: Float, default=0.0
- enrolled_at: DateTime
- completed_at: DateTime, nullable
- certificate_issued: Boolean, default=False
- UNIQUE constraint on (child_id, course_id)
```

### 4.10 LessonProgress
```
- id: Integer, primary_key
- child_id: FK → User.id
- lesson_id: FK → Lesson.id
- is_completed: Boolean, default=False
- watch_duration_seconds: Integer, default=0
- completed_at: DateTime, nullable
- UNIQUE constraint on (child_id, lesson_id)
```

### 4.11 QuizAttempt
```
- id: Integer, primary_key
- child_id: FK → User.id
- quiz_id: FK → Quiz.id
- score: Integer
- max_score: Integer
- percentage: Float
- passed: Boolean
- answers: JSON  # {question_id: selected_answer}
- time_taken_seconds: Integer
- attempted_at: DateTime
```

### 4.12 ActivityLog
```
- id: Integer, primary_key
- user_id: FK → User.id
- action_type: String(50)  # 'login','logout','video_start','video_complete',
                           # 'quiz_start','quiz_complete','homework_submit',
                           # 'badge_earned','course_complete','timeline_post'
- metadata: JSON, nullable  # extra details
- session_duration_minutes: Float, nullable
- ip_address: String(45), nullable
- timestamp: DateTime, default=utcnow
```

### 4.13 Reward (points ledger)
```
- id: Integer, primary_key
- child_id: FK → User.id
- points: Integer
- reason: String(200)  # 'lesson_complete', 'quiz_perfect', 'daily_login', 'streak_7', etc.
- reference_type: String(50), nullable  # 'lesson','quiz','badge','manual'
- reference_id: Integer, nullable
- awarded_by: FK → User.id, nullable  # null = system, else teacher/parent
- awarded_at: DateTime
```

### 4.14 Badge
```
- id: Integer, primary_key
- name: String(100), unique
- emoji_icon: String(10)  # 🏆🌟🔥📚💡🎯🦄🚀
- description: String(500)
- criteria_type: String(50)  # 'lessons_completed','quizzes_passed','streak_days',
                              # 'points_total','courses_completed','perfect_quiz'
- criteria_value: Integer  # e.g., 10 lessons, 7-day streak
- points_value: Integer, default=100
- tier: String(20)  # 'bronze','silver','gold','platinum','diamond'
- created_at: DateTime
```

### 4.15 UserBadge
```
- id: Integer, primary_key
- user_id: FK → User.id
- badge_id: FK → Badge.id
- earned_at: DateTime
- UNIQUE constraint on (user_id, badge_id)
```

### 4.16 Streak
```
- id: Integer, primary_key
- child_id: FK → User.id, unique
- current_streak: Integer, default=0
- longest_streak: Integer, default=0
- last_active_date: Date
- streak_freeze_count: Integer, default=0  # fun: earn freezes!
```

### 4.17 WeeklyGoal
```
- id: Integer, primary_key
- child_id: FK → User.id
- week_start_date: Date
- target_study_minutes: Integer, default=120
- target_lessons: Integer, default=5
- target_quizzes: Integer, default=2
- actual_study_minutes: Integer, default=0
- actual_lessons: Integer, default=0
- actual_quizzes: Integer, default=0
- achieved_percentage: Float, default=0.0
- UNIQUE constraint on (child_id, week_start_date)
```

### 4.18 Certificate
```
- id: Integer, primary_key
- child_id: FK → User.id
- course_id: FK → Course.id
- issued_by: FK → User.id
- certificate_number: String(50), unique  # e.g., "AJOY-2026-00001"
- child_name_on_cert: String(100)
- course_name_on_cert: String(200)
- completion_date: Date
- pdf_file_path: String(500)
- issued_at: DateTime
- UNIQUE constraint on (child_id, course_id)
```

### 4.19 TimelinePost 🆕
```
- id: Integer, primary_key
- author_id: FK → User.id  # ONLY children can author
- post_type: String(20)  # 'text', 'image', 'video', 'mixed'
- text_content: Text, nullable
- media_paths: JSON  # list of file paths ["uploads/timeline_media/img1.jpg"]
- video_url: String(500), nullable  # YouTube or external
- visibility: String(20), default='guardians'  # 'private','guardians'
- is_approved: Boolean, default=True  # moderation flag
- is_auto_generated: Boolean, default=False  # system achievement posts
- auto_post_type: String(50), nullable  # 'badge_earned','quiz_aced','streak_milestone'
- created_at: DateTime
- updated_at: DateTime, nullable
```

### 4.20 TimelineReaction 🆕
```
- id: Integer, primary_key
- post_id: FK → TimelinePost.id, on_delete CASCADE
- user_id: FK → User.id  # teacher or parent
- reaction_type: String(10)  # '⭐','👏','❤️','🎉','💡'
- created_at: DateTime
- UNIQUE constraint on (post_id, user_id)  # one reaction per user per post
```

### 4.21 TimelineComment 🆕
```
- id: Integer, primary_key
- post_id: FK → TimelinePost.id, on_delete CASCADE
- user_id: FK → User.id  # teacher, parent, OR the child (own posts)
- comment_text: Text, not null
- created_at: DateTime
```

---

## 5. FEATURE SPECIFICATIONS (Build each completely)

### 5.1 AUTH MODULE (`auth/`)

**Login Page (`auth/login.py`):**
- Ajoy Academy logo at top (use emoji 🎓 if no image)
- Username + Password fields
- "Login" button → bcrypt.checkpw()
- On success: set session_state (user_id, username, role, login_time)
- Log ActivityLog(action_type='login')
- Redirect to appropriate dashboard based on role
- "Don't have an account? Register here" link
- Show fun welcome message: "Welcome back, {name}! 🎉"

**Register Page (`auth/register.py`):**
- Fields: Full Name, Username, Email, Password, Confirm Password, Role dropdown, DOB (optional), Avatar emoji picker
- Password strength indicator
- bcrypt.hashpw() before storing
- Role selection: Teacher 👨‍🏫 / Parent 👪 / Child 👧
- For child registration: must enter a parent/teacher invite code OR be created by a parent/teacher
- Validation: unique username, valid email format, password min 6 chars

**Session Manager (`auth/session.py`):**
- Functions: init_session(), login_user(), logout_user(), get_current_user(), is_logged_in()
- Track session start time for duration calculation
- On logout: calculate session_duration, log ActivityLog(action_type='logout')

**Permissions (`auth/permissions.py`):**
- Decorator: @require_role('teacher', 'parent') — redirects to login if unauthorized
- Function: can_manage_child(user_id, child_id) — checks UserRelation
- Function: is_course_creator(user_id, course_id)
- Helper: get_linked_children(user_id) → list of child User objects
- Helper: get_linked_guardians(child_id) → list of teacher/parent User objects

---

### 5.2 COURSE BUILDER MODULE (`modules/courses.py`) — Moodle-style

**For Teachers & Parents:**

1. **Course Creation Form:**
   - Title, Description (text area), Category (dropdown), Difficulty Level, Age Group
   - Thumbnail URL (optional)
   - Estimated hours
   - "Save as Draft" or "Publish" buttons

2. **Module Manager (inside a course):**
   - Add/Edit/Delete/Reorder modules
   - Each module: Title, Description, Lock settings
   - Drag-like reorder using order_index (up/down buttons)

3. **Lesson Manager (inside a module):**
   - Add lessons of types:
     a) **Video Lesson**: Title + YouTube URL (auto-extract embed) + duration
     b) **Text Lesson**: Title + rich text content (Markdown supported)
     c) **PDF Lesson**: Title + PDF file upload (stored in uploads/worksheets/)
     d) **External Link**: Title + URL
   - Set points reward per lesson
   - Reorder lessons within module

4. **Quiz Attachment** (per module — see section 5.6)
5. **Homework Attachment** (per module — see section 5.7)

6. **Course Preview**: View course as a student would see it
7. **Course Analytics**: Enrollments, avg completion, avg quiz scores

**For Children (Course Catalog & Learning):**

1. **Course Catalog**: Grid of published courses with thumbnail, title, category, difficulty, age group
2. **Filter/Search**: By category, difficulty, age group
3. **Enrollment**: "Enroll Now 🚀" button → creates Enrollment record
4. **Course Player**:
   - Left sidebar: Module list with checkmarks ✅ for completed
   - Main area: Current lesson content
   - For video: embedded YouTube player (use st.video or iframe)
   - For text: rendered Markdown
   - For PDF: download button + embedded viewer
   - "Mark as Complete ✅" button → updates LessonProgress, awards points
   - Auto-advance to next lesson
   - Progress bar at top showing % complete
5. **Sequential Unlock**: Module N+1 unlocks only after Module N is 100% complete (if is_locked=True)

---

### 5.3 STUDENT DASHBOARD (`dashboard/child_dashboard.py`)

Layout (mobile-first, single column):

```
┌─────────────────────────────────┐
│  👋 Hi {name}! Welcome back!    │
│  🌟 {total_points} pts  🔥 {streak} day streak │
├─────────────────────────────────┤
│  📊 DAILY PROGRESS              │
│  ████████░░ 72% of today's goal │
│  Lessons: 3/5  Quizzes: 1/2     │
├─────────────────────────────────┤
│  🎬 CONTINUE LEARNING           │
│  [Course Card - Resume Button]  │
│  [Course Card - Resume Button]  │
├─────────────────────────────────┤
│  📝 PENDING HOMEWORK            │
│  HW 1: Math Worksheet (Due Fri) │
│  HW 2: Science Quiz (Due Mon)   │
├─────────────────────────────────┤
│  🏆 MY BADGES                   │
│  🌟 🔥 📚 💡 🦄 (+3 more)     │
├─────────────────────────────────┤
│  📢 MY TIMELINE                 │
│  [Mini timeline feed - last 3]  │
│  [See all →]                    │
├─────────────────────────────────┤
│  🏅 LEADERBOARD (Top 5)         │
│  1. Aman - 1250 pts             │
│  2. You - 1100 pts  ← 🎯       │
│  3. Priya - 980 pts             │
└─────────────────────────────────┘
```

**Daily Reward System:**
- First login of the day awards 5 bonus points
- Check if `last_active_date` != today → award + update streak
- Show "🎁 Daily Reward Claimed! +5 pts" celebration

---

### 5.4 TEACHER DASHBOARD (`dashboard/teacher_dashboard.py`)

Sections:
1. **Overview Cards**: Total students, Total courses, Active today, Avg quiz score
2. **Manage Users**: Table of linked children with status, last active, progress
3. **Link Children**: Search by username → create UserRelation
4. **Course Management**: List of created courses with edit/publish/analytics
5. **Analytics** (Plotly charts):
   - Login frequency heatmap (per child per day)
   - Total study hours per child (bar chart)
   - Video completion rates (donut chart)
   - Quiz performance trends (line chart)
   - Reward history (timeline)
6. **Activity Feed**: Recent activities of linked children
7. **Homework Grading Queue**: Pending submissions to grade

---

### 5.5 PARENT DASHBOARD (`dashboard/parent_dashboard.py`)

Similar to Teacher Dashboard but focused on own children:
1. **My Children**: Cards with avatar, name, streak, points, last active
2. **Create Courses for My Kids**: Quick course builder
3. **Analytics per Child**: Same Plotly charts as teacher
4. **Recent Activity Log**: Timestamped list of child's actions
5. **Reward History**: Points earned/spent, badges timeline
6. **Timeline Moderation**: View & manage child's posts

---

### 5.6 QUIZ ENGINE (`modules/quizzes.py`)

**Quiz Creator (Teacher/Parent):**
1. Choose quiz type: **Custom** or **Google Form**
2. **Google Form**: Paste Google Form URL + Google Sheet URL for responses
3. **Custom Quiz Builder**:
   - Add questions one-by-one
   - Question types: Multiple Choice (MCQ), True/False, Fill in the Blank
   - For MCQ: Add 2–6 options, mark correct answer
   - Set points per question
   - Add explanation (shown after answer)
   - Set time limit (optional)
   - Set pass percentage
   - Set max attempts
4. Preview quiz before saving
5. Attach to a module in a course

**Quiz Player (Child):**
1. Show instructions + time limit + max attempts
2. One question at a time or all-at-once mode
3. Timer countdown (if time limit set)
4. Submit → auto-grade → show results
5. Show correct/incorrect with explanations
6. Award points based on score
7. Log QuizAttempt + ActivityLog
8. If score >= pass_percentage → mark quiz as passed

---

### 5.7 HOMEWORK MODULE (`modules/homework.py`)

**Homework Creator (Teacher/Parent):**
1. **PDF Worksheet**: Upload PDF file → stored in uploads/worksheets/ → students can download
2. **Google Form**: Paste Google Form URL
3. **Custom Text Assignment**: Title + description + due date
4. **File Upload Assignment**: Students upload their work
5. Set max points, due date, attach to module

**Homework View (Child):**
1. List of pending/completed homework with due dates
2. **PDF Worksheet**: View + Download button (📥)
3. **Google Form**: "Open in Google Forms" button
4. **Submit Work**: Text input or file upload
5. View grade + feedback after grading

**Grading (Teacher/Parent):**
1. Queue of ungraded submissions
2. View submission content
3. Enter score (0 to max_points) + feedback text
4. Save grade → award points to child

---

### 5.8 GAMIFICATION SYSTEM (`modules/rewards.py`)

**Points System:**
- Lesson completed: +10 pts
- Quiz passed: +50 pts
- Quiz perfect score: +100 pts (bonus)
- Homework submitted: +20 pts
- Daily login: +5 pts
- 7-day streak: +50 pts bonus
- 30-day streak: +200 pts bonus
- Timeline post: +5 pts
- Course completed: +200 pts

**Badges (Pre-seed these in seed.py):**
| Badge Name        | Emoji | Criteria                  | Tier     |
|-------------------|-------|---------------------------|----------|
| First Steps       | 🐣    | Complete 1 lesson         | Bronze   |
| Bookworm          | 📚    | Complete 10 lessons       | Silver   |
| Scholar            | 🎓    | Complete 25 lessons       | Gold     |
| Quiz Whiz         | 🧠    | Pass 5 quizzes            | Silver   |
| Perfect Score     | 💯    | Get 100% on any quiz      | Gold     |
| Streak Starter    | 🔥    | 3-day streak              | Bronze   |
| Streak Master     | ⚡    | 7-day streak              | Silver   |
| Unstoppable       | 🌟    | 30-day streak             | Platinum |
| Course Completer  | 🏆    | Complete 1 course         | Gold     |
| Social Butterfly  | 🦋    | 10 timeline posts         | Silver   |
| Point Collector   | 💎    | Earn 1000 total points    | Gold     |
| Super Learner     | 🦄    | Complete 5 courses        | Diamond  |

**Badge Award Logic:**
- After each action (lesson complete, quiz pass, etc.), check if any new badge criteria is met
- If yes: create UserBadge, create Reward points, auto-post to Timeline, show celebration 🎉

**Streaks:**
- Update on each daily first login
- If `last_active_date` == yesterday → current_streak += 1
- If `last_active_date` < yesterday → current_streak = 1 (unless streak freeze)
- Update longest_streak if current > longest

**Weekly Goals:**
- Auto-created each Monday for each child
- Default targets: 120 min study, 5 lessons, 2 quizzes
- Teachers/Parents can customize targets
- Show progress ring in dashboard
- If achieved_pct >= 100%: bonus 50 points

---

### 5.9 LEADERBOARD (`modules/leaderboard.py`)

- **Weekly Leaderboard**: Points earned this week only
- **All-Time Leaderboard**: Total lifetime points
- Show top 10 with rank, avatar emoji, name, points
- Highlight current user's position
- Fun rank labels: 🥇 Champion, 🥈 Star, 🥉 Rising Star
- **Privacy**: Only show children linked to the same teachers/parents (same "academy")

---

### 5.10 CERTIFICATE MODULE (`modules/certificates.py`)

**Certificate Generation (auto or manual):**
1. Auto-trigger when course progress_percentage reaches 100%
2. Teacher/Parent can also manually issue
3. Generate PDF using reportlab:
   - Header: "🎓 Ajoy Academy"
   - "Certificate of Completion"
   - "This is to certify that **{child_name}** has successfully completed the course **{course_name}**"
   - Completion date
   - Unique certificate number: "AJOY-{YEAR}-{5-digit-sequence}"
   - Issued by: {teacher/parent name}
   - Decorative border (use reportlab drawing capabilities)
4. Save PDF to uploads/certificates/
5. Child can view and download from their profile
6. Auto-post to timeline: "🎉 I earned a certificate for {course_name}!"

---

### 5.11 TIMELINE / SOCIAL FEED (`modules/timeline.py`) 🆕

**This is a Facebook-style timeline for kids — CRITICAL FEATURE**

**Post Composer (`components/post_composer.py`):**
- Only visible to children
- Text area: "What did you learn today? 🌟"
- Media buttons: 📷 Photo | 🎥 Video | 📎 File
- Photo: st.file_uploader (JPG/PNG, max 5MB) → save to uploads/timeline_media/
- Video: Option to paste YouTube URL OR upload MP4 (max 25MB)
- Mixed: Text + one or more media
- "✨ Post It!" button
- On post: create TimelinePost + award 5 points + log ActivityLog

**Timeline Feed (Child View):**
- Infinite-scroll-like feed (load more button)
- Show own posts in chronological order (newest first)
- Each post card:
  ```
  ┌───────────────────────────────────┐
  │ 👧 {child_name} · {time_ago}      │
  │                                    │
  │  {text_content}                    │
  │                                    │
  │  [Image/Video if present]          │
  │                                    │
  │  ⭐ 3  👏 2  ❤️ 1   💬 2 comments │
  │  ─────────────────────────────     │
  │  👨‍🏫 Teacher: "Great job!"        │
  │  👪 Mama: "Love it! ❤️"           │
  │  [Write a comment...]             │
  └───────────────────────────────────┘
  ```
- Auto-generated achievement posts (badge earned, quiz aced, course complete, streak milestone) — marked with special styling ✨

**Timeline Feed (Teacher/Parent View):**
- See posts from ALL linked children
- Filter by child
- Can react: Click one of ⭐👏❤️🎉💡 (toggle on/off)
- Can comment: Text input below each post
- **Moderation**: 🚫 Hide Post button → sets is_approved=False (post hidden from child too)

**Auto-Generated Posts (system creates these):**
- 🏆 "{name} earned the {badge_name} badge!"
- 💯 "{name} scored a perfect 100% on {quiz_name}!"
- 🔥 "{name} is on a {streak} day learning streak!"
- 🎓 "{name} completed the course {course_name}!"
- These posts have `is_auto_generated=True` and special card styling

---

### 5.12 ANALYTICS MODULE (`modules/analytics.py`)

Generate these Plotly charts for Teacher/Parent dashboards:

1. **Login Heatmap**: Calendar heatmap showing login days (green intensity = hours studied)
2. **Study Hours Bar Chart**: Per child, daily/weekly/monthly study time
3. **Video Completion Donut**: % videos completed vs remaining per course
4. **Quiz Performance Line Chart**: Score trends over time per child
5. **Points Earned Timeline**: Cumulative points graph
6. **Leaderboard Bar Race**: Animated top 5 children points comparison
7. **Weekly Goal Progress Ring**: Circular progress indicator
8. **Activity Breakdown Pie**: Time spent on videos vs quizzes vs homework

Use Plotly Express for quick charts, Plotly Graph Objects for custom.
All charts must be mobile-responsive (use `fig.update_layout(margin=dict(l=20,r=20,t=40,b=20))`)

---

### 5.13 ACTIVITY TRACKER (`modules/activity_tracker.py`)

**Auto-logged events:**
- Login (with timestamp)
- Logout (with session duration)
- Video started (which video, course)
- Video completed (duration watched)
- Quiz started
- Quiz completed (score, time taken)
- Homework submitted
- Badge earned
- Course enrolled
- Course completed
- Timeline post created

**Session Duration Tracking:**
- On login: store `session_start` in session_state
- On logout (or on every page load with heartbeat): calculate duration
- Store in ActivityLog.session_duration_minutes

---

## 6. UI/UX REQUIREMENTS (Mobile-First)

### 6.1 Streamlit Config (`.streamlit/config.toml`)
```toml
[theme]
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
```

### 6.2 Custom CSS (`assets/styles.css`) — inject via st.markdown
```css
/* Mobile-first responsive */
.stApp { max-width: 100%; }
/* Fun, kid-friendly typography */
h1, h2, h3 { font-family: 'Comic Sans MS', 'Segoe UI', cursive, sans-serif; }
/* Card-like containers */
.stExpander, div[data-testid="stMetric"] { 
    border-radius: 15px; 
    border: 2px solid #FFD93D;
    padding: 10px;
}
/* Big, touch-friendly buttons */
.stButton > button {
    border-radius: 25px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: bold;
    min-height: 48px;  /* touch target */
}
/* Colorful badges container */
.badge-container { display: flex; flex-wrap: wrap; gap: 8px; }
/* Timeline post card */
.timeline-card {
    background: white;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

### 6.3 Color Palette
- Primary: #FF6B6B (Coral Red)
- Secondary: #4ECDC4 (Teal)
- Accent: #FFD93D (Golden Yellow)
- Success: #6BCB77 (Green)
- Background: #FFFFFF / #F0F2F6
- Dark text: #2C3333

### 6.4 Navigation
- Sidebar for menu (collapsed by default on mobile)
- Top bar: Logo + "Ajoy Academy" + User avatar emoji + Logout button
- Role-based menu items
- Breadcrumbs for course navigation

---

## 7. GOOGLE SHEETS INTEGRATION (`utils/gsheets.py`)

```python
# Structure for gspread integration
# Teacher/Parent pastes:
# 1. Google Form URL (for quiz/homework)
# 2. Google Sheet URL (for response viewing)
# On analytics page: fetch sheet data via gspread and display as DataFrame
# Requires service account JSON — store path in config.py
# For Streamlit Cloud: use st.secrets for credentials
```

---

## 8. SEED DATA (`database/seed.py`)

Pre-populate on first run:
1. Default admin teacher: username="teacher1", password="teacher123", role="teacher"
2. Default parent: username="parent1", password="parent123", role="parent"
3. Default child: username="kid1", password="kid123", role="child"
4. All 12 badges from the badge table above
5. Sample course: "Fun with Numbers 🔢" with 2 modules, 3 lessons each
6. Link teacher1→kid1, parent1→kid1

---

## 9. DEPLOYMENT (Streamlit Community Cloud)

### requirements.txt:
```
streamlit>=1.35.0
sqlalchemy>=2.0.0
bcrypt>=4.1.0
pandas>=2.0.0
plotly>=5.18.0
gspread>=5.12.0
oauth2client>=4.1.3
reportlab>=4.1.0
Pillow>=10.0.0
python-dateutil>=2.8.0
```

### Deployment Steps:
1. Push all code to GitHub repository
2. Go to share.streamlit.io
3. Connect GitHub repo
4. Set main file: `app.py`
5. Add secrets in Streamlit Cloud dashboard (for Google Sheets if needed)
6. Deploy!

### Database Note:
- SQLite file will be in the app directory (works on Streamlit Cloud but resets on reboot)
- For persistence: migrate to PostgreSQL (change only `config.py` DATABASE_URL)
- SQLAlchemy ORM makes this a one-line change

---

## 10. APP.PY MAIN ROUTER (Structure)

```python
import streamlit as st
from database.engine import init_db
from auth.session import init_session, is_logged_in, get_current_user
from auth.login import show_login_page
from auth.register import show_register_page

# Page config
st.set_page_config(
    page_title="🎓 Ajoy Academy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
with open("assets/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize database
init_db()

# Initialize session
init_session()

# Routing
if not is_logged_in():
    page = st.sidebar.radio("", ["Login", "Register"])
    if page == "Login":
        show_login_page()
    else:
        show_register_page()
else:
    user = get_current_user()
    if user.role == 'teacher':
        from dashboard.teacher_dashboard import show_teacher_dashboard
        show_teacher_dashboard(user)
    elif user.role == 'parent':
        from dashboard.parent_dashboard import show_parent_dashboard
        show_parent_dashboard(user)
    elif user.role == 'child':
        from dashboard.child_dashboard import show_child_dashboard
        show_child_dashboard(user)
```

---

## 11. BUILD SEQUENCE (Follow this order)

1. **Phase 1 — Foundation**: config.py → database/engine.py → database/models.py → database/seed.py
2. **Phase 2 — Auth**: auth/session.py → auth/permissions.py → auth/login.py → auth/register.py
3. **Phase 3 — Components**: components/navbar.py → components/sidebar.py → components/cards.py
4. **Phase 4 — Core Modules**: modules/courses.py → modules/videos.py → modules/activity_tracker.py
5. **Phase 5 — Assessments**: modules/quizzes.py → modules/homework.py
6. **Phase 6 — Gamification**: modules/rewards.py → modules/leaderboard.py → modules/certificates.py
7. **Phase 7 — Timeline**: components/post_composer.py → modules/timeline.py
8. **Phase 8 — Analytics**: modules/analytics.py → utils/gsheets.py
9. **Phase 9 — Dashboards**: dashboard/child_dashboard.py → dashboard/teacher_dashboard.py → dashboard/parent_dashboard.py
10. **Phase 10 — Integration**: app.py → assets/styles.css → .streamlit/config.toml → requirements.txt
11. **Phase 11 — Polish**: Testing, seed data, responsive fixes, deploy

---

## 12. CRITICAL REMINDERS FOR THE AI AGENT

- **EVERY file must be complete and runnable** — no placeholder `pass` or `TODO`
- **Import paths must be correct** relative to project root
- **SQLAlchemy relationships** must be defined with back_populates
- **bcrypt**: Use `bcrypt.hashpw(password.encode(), bcrypt.gensalt())` and `bcrypt.checkpw()`
- **Streamlit session_state**: Always check `if 'key' not in st.session_state` before setting
- **File uploads**: Use `st.file_uploader()` → save with unique filenames (use uuid)
- **YouTube embeds**: Extract video ID, use `st.markdown(iframe_html, unsafe_allow_html=True)`
- **Mobile responsive**: Test all layouts in single-column mode
- **JSON fields in SQLite**: Use `sqlalchemy.JSON` type (works with SQLite)
- **All dates**: Use `datetime.utcnow()` and display in local time
- **Error handling**: Wrap DB operations in try-except with user-friendly error messages
- **The app name "Ajoy Academy" must appear** in the header/logo of every page
- Generate ALL files in the build sequence order. Do not skip any file.
