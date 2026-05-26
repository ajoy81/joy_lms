# Ajoy Academy LMS Development Log

## Phase 1 — Foundation
* Timestamp: 2026-05-23T11:05:00+05:30
* Created `config.py` with database and app configurations.
* Created `database/__init__.py`.
* Created `database/engine.py` for SQLAlchemy database engine initialization.
* Created `database/models.py` defining 21 database models required for the LMS.
* Created `database/seed.py` for seeding default users, badges, course, and relationships.

## Phase 2 — Auth
* Timestamp: 2026-05-23T11:08:00+05:30
* Created `auth/__init__.py`.
* Created `auth/session.py` to handle Streamlit session states, login, logout, and activity logging.
* Created `auth/permissions.py` for role-based access decorators and data access helpers.
* Created `auth/login.py` to build the login form with `bcrypt` verification.
* Created `auth/register.py` with role selection, validations, and guardian linking for child accounts.

## Phase 3 — Components
* Timestamp: 2026-05-23T11:12:00+05:30
* Created `components/__init__.py`.
* Created `components/navbar.py` with the top navigation bar component.
* Created `components/sidebar.py` with the role-based navigation sidebar.
* Created `components/cards.py` with reusable UI components for courses, users, badges, and timeline posts.

## Phase 4 — Core Modules
* Timestamp: 2026-05-23T11:12:30+05:30
* Created `modules/__init__.py`.
* Created `modules/videos.py` to handle YouTube video embedding and ID extraction.
* Created `modules/activity_tracker.py` to log user activities natively in the database.
* Created `modules/courses.py` including `show_course_catalog`, `show_course_player`, and `show_course_builder` (incorporating module and lesson management).

## Phase 5 — Assessments
* Timestamp: 2026-05-23T11:13:30+05:30
* Created `modules/quizzes.py` with custom and Google Form quiz builder and player.
* Created `modules/homework.py` with homework assignment creation, student submission interfaces, and a grading queue for teachers.

## Phase 6 — Gamification
* Timestamp: 2026-05-23T11:15:30+05:30
* Created `modules/rewards.py` to handle point calculation, badge awards, and streak tracking.
* Created `modules/leaderboard.py` featuring Weekly and All-Time Hall of Fame views.
* Created `modules/certificates.py` and `utils/pdf_generator.py` for issuing and rendering PDF certificates with reportlab.

## Phase 7 — Timeline
* Timestamp: 2026-05-23T11:16:30+05:30
* Created `components/post_composer.py` providing a child-friendly interface for mixed media posts.
* Created `modules/timeline.py` integrating the feed view, auto-generated achievements, reactions, and guardian moderation.

## Phase 8 — Analytics
* Timestamp: 2026-05-23T11:17:30+05:30
* Created `modules/analytics.py` using Plotly to visualize study hours, points earned, quiz performance, and activity breakdowns.
* Created `utils/gsheets.py` to securely fetch and display external Google Sheets responses within the app.

## Phase 9 — Dashboards
* Timestamp: 2026-05-23T11:18:30+05:30
* Created `dashboard/__init__.py`.
* Created `dashboard/child_dashboard.py` offering a single-column, gamified learning hub for children.
* Created `dashboard/teacher_dashboard.py` with overview metrics, user linking, course management, and homework grading.
* Created `dashboard/parent_dashboard.py` focusing on child supervision, activity logs, and timeline moderation.

## Phase 10 — Integration
* Timestamp: 2026-05-23T11:19:00+05:30
* Created `app.py` as the main router handling session initialization and dynamic dashboard rendering based on role.
* Created `assets/styles.css` applying mobile-first, kid-friendly typography and card layouts.
* Created `.streamlit/config.toml` configuring the app theme and server settings.
* Created `requirements.txt` listing all necessary dependencies for deployment.

## UI/UX Enhancements
* Timestamp: 2026-05-23T11:43:00+05:30
* Updated `app.py` to include a global `Laptop/Mobile` toggle in the sidebar. This injects custom CSS to restrict the container width, simulating a mobile device layout to help both users and developers test responsive designs natively in the browser.
* Updated `components/sidebar.py` to include a persistent hyperlink for the Online Dictionary 'Xobdo' (https://www.xobdo.org/) across all user roles.

## Phase 11 — Child Activity Tracking & Drill-down Dashboards
* Timestamp: 2026-05-23T17:49:00+05:30
* Modified `database/models.py` to add `watch_percentage` and `last_accessed_at` to the `LessonProgress` schema.
* Created `database/migrate.py` to execute table migrations on the SQLite database.
* Created custom Streamlit component `components/youtube_tracker/index.html` using the YouTube Iframe Player API to track play progress, active watch percentage, and playing session duration.
* Created custom Streamlit component `components/pdf_tracker/index.html` to embed PDFs in a scroll-sensing container and track reading percentage, automatically marking completion at 90% scroll depth.
* Modified `modules/courses.py` to:
  * Integrate active study time tracking (updating `watch_duration_seconds` every 5 seconds) and flushing when changing lessons or logging out.
  * Integrate custom YouTube and PDF progress trackers.
  * Add **Previous Lesson** and **Next Lesson** navigation buttons.
  * Add a manual **Mark as Complete ✅** backup override.
  * Automatically recalculate course completion progress (`Enrollment.progress_percentage`) upon lesson completion.
* Modified `auth/session.py` to flush the active lesson study time when logging out.
* Modified `modules/analytics.py` to add a **Detailed Progress** drill-down tab for parent/teacher dashboards, visualizing Course -> Module -> Lesson hierarchies with completion statuses, watch/scroll percentages, and total duration minutes.

## Phase 12 — Course Builder Analytics & Edits
* Timestamp: 2026-05-23T18:00:00+05:30
* Removed duplicate lesson entries from the database.
* Modified modules/courses.py to add inline Edit (Rename) and Delete capabilities for Modules and Lessons within the Course Builder.
* Modified modules/courses.py to introduce a Course Analytics tab, displaying enrollment numbers, average completion progress, and a drill-down view of student-level engagement statistics per course.

## Phase 13 — Course Builder Tree UI & Global Polish
* Timestamp: 2026-05-24T21:00:00+05:30
* Modified `modules/courses.py` to completely rewrite the Course Builder UI into a nested, flowchart-style directory tree using indented `st.columns` and visual `↳` arrows.
* Modified `modules/courses.py` to strip bulky Streamlit buttons from action icons, using tertiary transparent buttons instead.
* Modified `modules/courses.py` to replicate the new Course Flowchart tree navigation structure to the Student Player and the Teacher/Parent Student Preview.
* Modified `modules/courses.py` to inject the advanced YouTube thumbnail rendering and full progress tracking controls (100.0%, 5.0m, Revise, Mark Complete) directly into the Student Preview mode, ensuring a 100% pixel-perfect replica of the child interface.
* Engineered dynamic duration tracking to aggregate total course time from individual lesson times, and added a global green `st.progress` bar above the Course header.
* Adjusted the Course Flow sidebar ratio to 1.75x wider (`[1.75, 2.25]`) to prevent text wrapping.
* Modified `assets/styles.css` to inject global typography UI polishing: tightening `.block-container` paddings, reducing `stVerticalBlock` gaps, zeroing header paddings, and standardizing an `Inter/Segoe UI` type scale.
* Generated comprehensive User Manual `user_manual.md`.

## Phase 14 — XLS-Based Interactive Quiz System
* Timestamp: 2026-05-24T21:49:00+05:30
* Modified `requirements.txt` to include `openpyxl` and `xlrd` for Pandas Excel parsing.
* Modified `database/models.py` by adding a new `quiz_data` JSON column to the `Lesson` table to store questions array cleanly.
* Executed SQLite `ALTER TABLE lessons ADD COLUMN quiz_data JSON;` via `alter_db.py`.
* Modified `modules/courses.py` (Course Builder) to generate and provide a dynamic `Quiz_Template.xlsx` download for Teachers/Parents.
* Modified `modules/courses.py` (Course Builder) to include `st.file_uploader` for `.csv/.xls/.xlsx`. Implemented Pandas parsing, validation against required columns, UUID generation for questions, and direct JSON saving into `lesson.quiz_data`.
* Modified `modules/courses.py` (Student Player & Preview) to completely overhaul the Quiz lesson UI. It now pulls the JSON data, automatically randomizes the 10 questions and randomizes the order of the 4 options per question.
* Engineered a client-side (session_state) grading engine that evaluates submitted answers against the tagged `Question_ID`, requiring a 70% pass mark to unlock lesson completion and automatically update the `LessonProgress` tracking table.

## Phase 15 — Quiz Locking & Gamification Rewards
* Timestamp: 2026-05-24T22:00:00+05:30
* Modified `database/models.py` to add a new `quiz_results` JSON column to the `LessonProgress` table to permanently store passing quiz attempts.
* Created and executed `alter_db2.py` to run SQLite `ALTER TABLE lesson_progresses ADD COLUMN quiz_results JSON;`.
* Initialized two new Badges: "Quiz Master" and "Halfway There" via an initialization script.
* Modified `modules/courses.py` Quiz Player UI: If a student scores >= 70%, the interactive quiz form is permanently locked and hidden. The UI instead retrieves `quiz_results` from the database and allows the student to revisit only their incorrect answers anytime they want.
* Integrated the LMS `award_points` system. Completing a quiz now rewards the student with points (default 10) directly to their Kid Dashboard.
* Integrated the LMS `award_badge` system. Passing a quiz instantly unlocks the "Quiz Master" badge.
* Engineered dynamic course progression logic upon quiz completion: When a quiz marks a lesson as completed, the system calculates `completed_lessons / total_lessons` and automatically awards the "Halfway There" badge once 50% coursework is achieved.

## Phase 16 — Persistent Login & Sidebar Home Icon
* Timestamp: 2026-05-25T10:30:00+05:30
* Modified `requirements.txt` to include `streamlit-cookies-controller>=0.0.3` to handle client-side persistent cookies.
* Modified `auth/login.py` to add a "Keep me logged in" checkbox. When checked, successful login now stores the user's ID in an `ajoy_auth_token` browser cookie with a 30-day expiration.
* Modified `auth/session.py` to seamlessly auto-login the user: `init_session()` now checks `st.context.cookies` on app load. If `ajoy_auth_token` is present but `st.session_state` is cleared (e.g., from a browser refresh), it instantly reconstructs the session without requiring a manual re-login.
* Modified `auth/session.py` to purge the `ajoy_auth_token` cookie when the user clicks Logout.
* Modified `components/sidebar.py` to inject a `🏠 Home` button just below the main logo. Clicking it resets the `sidebar_nav` back to the default dashboard for the user's role without triggering a hard browser reload, preventing accidental logouts for users who don't use persistent cookies.
