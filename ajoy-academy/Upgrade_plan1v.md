# Course Builder Overhaul — Tree Structure with Full CRUD

## Background

After thorough code review, the **database schema is already well-structured** with a proper Course → Module → Lesson hierarchy, PDF support, Quiz/QuizAttempt models, and LessonProgress tracking. The real problem is in the **Course Builder UI** ([courses.py](file:///d:/A_LMS/ajoy-academy/modules/courses.py) `show_course_builder()`, lines 411–669).

### Current Problems in Course Builder

| # | Problem | Where |
|---|---------|-------|
| 1 | **No tree view** — flat "My Courses" list with a separate "Manage Modules" button that opens below the tabs | L506–534, L536–669 |
| 2 | **Module editing is title-only** — can't edit description, order, lock status | L548–575 |
| 3 | **Lesson editing is title-only** — can't edit content, URL, type, or points after creation | L577–605 |
| 4 | **No course editing** — can't modify course metadata after creation | L506–534 |
| 5 | **No file upload** — PDFs and thumbnails use text URL input only | L644, L478 |
| 6 | **No order management** — `order_index` always defaults to 0, no UI to reorder | L611, L653 |
| 7 | **No publish/unpublish toggle** after course creation | L514 |
| 8 | **Quiz type missing from lesson builder** — quizzes exist as separate `Quiz` model but aren't integrated as a lesson type | L622 |
| 9 | **Indentation bug in course creation** — `try` block (L486) is outside the `if` check | L481–504 |
| 10 | **No confirmation on delete** — courses delete immediately via callback | L522–531 |

### What Already Works (No Changes Needed)

- ✅ Database models: `Course`, `Module`, `Lesson`, `Quiz`, `QuizAttempt`, `LessonProgress` — all properly defined
- ✅ Lesson types: `video`, `text`, `pdf`, `external_link` — all supported in schema
- ✅ `LessonProgress` with watch tracking, revision counting, completion tracking
- ✅ Course player (child view) — works well with YouTube tracker, PDF tracker, progress metrics
- ✅ Cascade deletes on Course → Module → Lesson via SQLAlchemy relationships
- ✅ Upload directory infrastructure (200MB max)

---

## User Review Required

> [!IMPORTANT]
> **Quiz as a Lesson Type**: Currently, Quizzes are a **separate model** (`Quiz` table) linked to modules/courses, not part of the `Lesson` table. This plan proposes adding `'quiz'` as a `lesson_type` option in the lesson builder, with a reference to the `Quiz` model. This means quizzes would appear **inline in the lesson tree** alongside videos, PDFs, and text. Should we:
> - **(A)** Add quiz as a lesson type (recommended — provides unified tree view)
> - **(B)** Keep quizzes separate and only improve the existing lesson types

> [!IMPORTANT]
> **File Upload for PDFs**: Currently PDFs use a text input for URL/path. This plan adds `st.file_uploader` for PDFs, saving files to `uploads/pdfs/`. Should we also add **video file upload** (currently URL-only), or keep videos as URL-based?

> [!WARNING]
> **No Database Migration Needed**: The schema already supports everything. Only the **UI code** needs changes. No data will be lost.

---

## Open Questions

1. **Quiz integration**: As a lesson type (unified tree) or keep separate?
2. **Video upload**: Add file upload for videos too, or keep URL-only?
3. **Module locking UI**: The `Module` model has `is_locked` and `unlock_after_module_id` fields. Should we expose these in the builder UI?
4. **Reordering approach**: Up/Down arrow buttons (▲▼) or drag numbers? (Streamlit doesn't support native drag-and-drop well, so arrow buttons are recommended)

---

## Proposed Changes

### Component 1: Course Builder — Tree View UI (Main Change)

Complete rewrite of `show_course_builder()` in [courses.py](file:///d:/A_LMS/ajoy-academy/modules/courses.py).

---

#### [MODIFY] [courses.py](file:///d:/A_LMS/ajoy-academy/modules/courses.py) — Lines 411–669

**Replace the current 3-tab layout with a unified tree-view interface:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  🏗️ Course Builder                                          [+ New Course] │
├──────────────────────────────┬──────────────────────────────────────────────┤
│  📚 COURSE TREE              │  📝 EDITOR PANEL                            │
│                              │                                              │
│  📕 Python Masterclass  ▼    │  ┌────────────────────────────────────────┐  │
│  │  ✏️ 🗑️  📊              │  │  📦 Edit Module: Python Basics         │  │
│  ├─ 📦 Module 1: Basics     │  │                                        │  │
│  │  ├─ 🎥 Lesson 1: Intro   │  │  Title: [Python Basics          ]     │  │
│  │  ├─ 📄 Lesson 2: Vars    │  │  Description: [Introduction to...]     │  │
│  │  ├─ 📑 Lesson 3: Guide   │  │  Order: [1]                            │  │
│  │  ├─ ❓ Lesson 4: Quiz    │  │  🔒 Locked: [ ] After Module: [—]     │  │
│  │  └─ [+ Add Lesson]       │  │                                        │  │
│  ├─ 📦 Module 2: Advanced   │  │  [💾 Save Changes]  [🗑️ Delete]       │  │
│  │  └─ [+ Add Lesson]       │  └────────────────────────────────────────┘  │
│  └─ [+ Add Module]          │                                              │
│                              │                                              │
│  📕 Web Development  ▶      │                                              │
│  │  ✏️ 🗑️  📊              │                                              │
│                              │                                              │
├──────────────────────────────┴──────────────────────────────────────────────┤
│  📊 Course Analytics (collapsible section at bottom)                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Detailed UI Behavior:**

**Left Panel — Course Tree (col ratio 2:5 with editor):**
1. **"+ New Course" button** at the top — opens the course creation form in the editor panel
2. **Course nodes** — each course shows as a collapsible block with:
   - Title + Published/Draft badge
   - Inline action buttons: ✏️ Edit, 🗑️ Delete (with confirmation), 📊 Analytics
   - Expand/collapse to show modules
3. **Module nodes** under each course:
   - Title with order number displayed
   - ▲▼ arrow buttons for reordering
   - Click to select for editing
   - "**+ Add Lesson**" button at the bottom of each module's lesson list
4. **Lesson nodes** under each module:
   - Content-type icon + title: 🎥 Video, 📄 Text, 📑 PDF, 🔗 Link, ❓ Quiz
   - ▲▼ arrow buttons for reordering
   - Click to select for editing
5. **"+ Add Module" button** at the bottom of each course's module list

**Right Panel — Context-Sensitive Editor:**

| Selection | Editor Content |
|---|---|
| **New Course** | Full creation form (title, description, category, difficulty, age group, hours, thumbnail upload, publish toggle) |
| **Edit Course** | Same form pre-populated + Update/Delete buttons |
| **New Module** | Module form (title, description, order auto-set, lock settings) |
| **Edit Module** | Module form pre-populated + Update/Delete buttons |
| **New Lesson** | Lesson type selector → type-specific form (see below) |
| **Edit Lesson** | Full lesson editing form with all fields editable |
| **Course Analytics** | Enrollment stats, student progress drill-down |

**Lesson Type-Specific Editor Fields:**

| Type | Fields |
|---|---|
| 🎥 **Video** | Title, YouTube/Video URL, Description (text area), Duration (minutes), Points |
| 📄 **Text** | Title, Content (large markdown text area), Duration (estimated), Points |
| 📑 **PDF** | Title, PDF file uploader (`st.file_uploader`), Description, Points |
| 🔗 **External Link** | Title, URL, Description, Points |
| ❓ **Quiz** | Title, link to existing Quiz or create inline quiz, Points |

**Session State for Tree Navigation:**
```python
# Track what's selected in the tree
st.session_state['cb_selected_type']     # 'course'|'module'|'lesson'|None
st.session_state['cb_selected_id']       # ID of selected entity
st.session_state['cb_creating']          # 'course'|'module'|'lesson'|None
st.session_state['cb_creating_parent']   # Parent ID (course_id for modules, module_id for lessons)
st.session_state['cb_expanded_courses']  # Set of expanded course IDs
st.session_state['cb_show_analytics']    # course_id if showing analytics, None otherwise
st.session_state['cb_confirm_delete']    # (type, id) tuple for delete confirmation
```

**Key Implementation Functions:**

```python
def show_course_builder(user):
    """Main entry — header + two-column layout"""

def _render_course_tree(user):
    """Left panel — all courses with expandable tree"""

def _render_course_node(course, user):
    """Single course expandable block with modules"""

def _render_module_node(module, course_id):
    """Single module with lessons, reorder buttons"""

def _render_lesson_node(lesson):
    """Single lesson with type icon, reorder buttons"""

def _render_editor_panel(user):
    """Right panel — routes to correct editor based on session state"""

def _render_course_form(user, course=None):
    """Course create/edit form (None = create mode)"""

def _render_module_form(course_id, module=None):
    """Module create/edit form"""

def _render_lesson_form(module_id, lesson=None):
    """Lesson create/edit form with type-specific sections"""

def _render_video_fields(lesson=None):
    """Video URL, description, preview"""

def _render_text_fields(lesson=None):
    """Markdown text editor"""

def _render_pdf_fields(lesson=None):
    """PDF file uploader + current file display"""

def _render_link_fields(lesson=None):
    """External link URL + description"""

def _render_quiz_fields(module_id, lesson=None):
    """Quiz selector/creator"""

def _render_course_analytics(course):
    """Analytics moved to right panel (from current tab3)"""

def _reorder_item(model_class, item_id, direction, parent_field, parent_id):
    """Generic reorder: swap order_index with adjacent item"""

def _handle_pdf_upload(uploaded_file, course_title):
    """Save PDF to uploads/pdfs/{course_title}/, return path"""

def _auto_order_index(model_class, parent_field, parent_id):
    """Return next order_index for new items (max + 1)"""

def _get_content_type_icon(lesson_type):
    """Return emoji icon for lesson type"""
```

**Bug Fixes Included:**
- Fix indentation bug in course creation (L486 `try` block)
- Auto-increment `order_index` for new modules/lessons
- Add delete confirmation dialog
- Proper session cleanup on delete

---

### Component 2: PDF Upload Support

---

#### [MODIFY] [config.py](file:///d:/A_LMS/ajoy-academy/config.py)

- Add `'pdfs'` to upload subdirectories
- Add `ALLOWED_PDF_EXTENSIONS = ['.pdf']`
- Add `MAX_PDF_SIZE_MB = 50`

---

#### [MODIFY] [courses.py](file:///d:/A_LMS/ajoy-academy/modules/courses.py) — `_handle_pdf_upload()`

New helper function:
- Uses `st.file_uploader(type=['pdf'])`
- Saves to `uploads/pdfs/{sanitized_course_title}/`
- Returns relative file path for storage in `Lesson.pdf_file_path`
- Shows current PDF filename if editing an existing PDF lesson

---

### Component 3: Minor Model Enhancement (Optional)

---

#### [MODIFY] [models.py](file:///d:/A_LMS/ajoy-academy/database/models.py)

**Optional — only if quiz-as-lesson-type is approved:**
- Add `quiz_id` column (FK → `quizzes.id`, nullable) to `Lesson` model
- Add relationship: `quiz = relationship("Quiz")`
- This links a lesson directly to a quiz, so quizzes appear in the lesson tree

---

## Summary of All Changes

| File | Action | Scope | Risk |
|---|---|---|---|
| [courses.py](file:///d:/A_LMS/ajoy-academy/modules/courses.py) | **REWRITE** `show_course_builder()` (L411–669) | ~260 lines replaced with ~500-600 lines of tree-view UI | Medium — core feature, well-scoped |
| [config.py](file:///d:/A_LMS/ajoy-academy/config.py) | MODIFY | Add PDF upload config (3 lines) | Low |
| [models.py](file:///d:/A_LMS/ajoy-academy/database/models.py) | MODIFY (optional) | Add `quiz_id` FK to Lesson (2 lines) | Low |

**Files NOT changed** (already working correctly):
- `database/engine.py` — no changes needed
- `database/models.py` — schema already supports everything (except optional quiz link)
- `dashboard/child_dashboard.py` — course player already works
- `dashboard/teacher_dashboard.py` — routes to `show_course_builder()`
- `dashboard/parent_dashboard.py` — routes to `show_course_builder()`
- `components/*` — all components work correctly
- `auth/*` — no changes needed

---

## Verification Plan

### Automated Testing
1. Run the app (`streamlit run app.py`) — verify no import errors
2. Login as teacher → navigate to Course Management
3. Test full CRUD cycle:
   - Create new course → verify it appears in tree
   - Add 2 modules → verify ordering and tree display
   - Add lessons of each type (Video, Text, PDF, Link) → verify type icons
   - Upload a PDF → verify file saved to `uploads/pdfs/`
   - Edit a module title/description → verify changes persist
   - Edit a lesson (change content, URL) → verify changes persist
   - Reorder modules (▲▼) → verify order changes
   - Reorder lessons (▲▼) → verify order changes
   - Delete a lesson → verify removed from tree
   - Delete a module → verify module and its lessons removed
   - Toggle course publish/unpublish → verify status changes
   - Delete a course (with confirmation) → verify cascade delete

### Manual Verification
1. Verify tree visually renders correctly with nested indentation
2. Verify smooth transitions between tree selection and editor panel
3. Verify PDF upload works and file persists across app restarts
4. Login as child → verify course player still works correctly with all lesson types
5. Test edge cases: course with 0 modules, module with 0 lessons, very long titles

---

## 📅 Recent UI & Layout Upgrades (Timestamp: 2026-05-24 21:00)

**1. Course Flow Flowchart Transformation**
- Converted the flat "My Courses" tree into a fully nested, flowchart-style directory structure.
- Implemented `st.columns` indentation and `↳` visual arrows to denote Course > Module > Lesson hierarchy.
- Replicated this exact nested flowchart structure across the Course Builder, Student Preview, and Student Player sidebars.

**2. Synchronized Student Preview**
- Upgraded the Parent's "Student Preview" mode to be a 100% pixel-perfect replica of the actual child Student Player.
- Injected the advanced YouTube thumbnail rendering and a mock progress tracking UI (100.0%, 5.0m, Revise, Mark Complete) directly into the preview mode.

**3. Advanced Duration & Progress Tracking**
- Engineered dynamic duration calculations that aggregate total course time from individual lesson times.
- Added a global, vibrant green (`#28a745`) progress bar above the Course header that tracks real-time completion percentage based on first-time completions.
- Appended right-aligned, minimized duration tags (e.g., `3 min`) lowered by `2px` for perfect vertical centering in the Course and Module headers.
- Replaced the active lesson indicator with a Green Tick (`✅`).

**4. Global UI Polishing & Typography**
- Adjusted sidebar column ratio to `[1.75, 2.25]` (1.75x wider Course Flow) to prevent awkward text wrapping.
- Stripped heavy Streamlit button boxes from action icons using `type="tertiary"`.
- Injected global CSS into `assets/styles.css` to tighten `.block-container` paddings, reduce vertical block gaps, zero out header padding, and standardize `Inter`/`Segoe UI` typography.

---

## 📋 Implement XLS-Based Interactive Quiz System
*This plan was approved on 2026-05-24 and outlines the steps to build a 10-question MCQ Quiz system featuring bulk XLS uploading for teachers and an interactive, randomized player for students.*

### Proposed Changes

#### 1. Database & Environment
- **requirements.txt**: Add `openpyxl` and `xlrd` for Excel parsing support via Pandas.
- **models.py**: Add a `quiz_data` (JSON) column to the `Lesson` model to cleanly store the array of questions, options, and right answers.

#### 2. Course Builder (Teacher/Parent View)
- **Template Download**: Add a button inside the Quiz lesson editor to download a pre-formatted `Quiz_Template.xlsx` containing the exact required columns: `Question`, `Option-1`, `Option-2`, `Option-3`, `Option-4`, `Right Answer`.
- **XLS Uploader**: Add `st.file_uploader` restricted to `.xls`, `.xlsx`, and `.csv`.
- **Parsing & Validation**: Read the file using Pandas, automatically generate the `UniqueID` (Random number) and `Question_ID` (System sequential). Verify that the `Right Answer` perfectly matches one of the 4 options. Render a "Preview" table of the uploaded questions before saving, and save the parsed array to the database upon clicking "Save Changes".

#### 3. Student Player (Child View)
- **Interactive Quiz UI**: When a student selects a Quiz lesson, hide the standard "Mark Complete" button and instead render an interactive quiz interface.
- **Randomization Algorithm**: Randomly select exactly 10 questions (if the pool is larger). Shuffle the display order of the questions. Shuffle the display order of the 4 options for each question so "Option-1" isn't always the first radio button.
- **Evaluation Engine**: Provide a "Submit Quiz" button at the bottom. Upon submission, compare the student's selections against the tagged `Question_ID` correct answers. Calculate percentage. If >= 70% (7/10), display a celebration, show results, award the full lesson points, and mark the lesson as `is_completed`. If < 70%, display a gentle "Try Again" message, reveal the score (but not the exact correct answers to prevent cheating), and provide a "Retake Quiz" button.
