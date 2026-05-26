# Ajoy Academy LMS - Test Credentials

This file contains the test users and system access credentials for the Ajoy Academy LMS development environment.

## 📱 Web Application Accounts
All accounts currently share the same password for testing convenience.

| Role | Username | Password | Linked To |
| :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `1234` | - |
| **System Admin/Teacher** | `teacher1` | `teacher123` | kid1 |
| **System Admin/Parent** | `parent1` | `parent123` | kid1 |
| **System Demo Child** | `kid1` | `kid123` | - |
| **Teacher (Custom)** | `rashi` | `1234` | pablo |
| **Parent (Custom)** | `monali` | `1234` | pablo |
| **Child (Custom)** | `pablo` | `1234` | - |
| **Institute admin** | `parental_admin` | `1234` | Parental |

> **Note:** The `monali`, `rashi`, and `pablo` accounts are actively linked. If `monali` (Parent) or `rashi` (Teacher) assign a course or homework, it will immediately appear on `pablo`'s dashboard.

---

## 🗄️ Database Access

The application uses a local SQLite database for development, which requires no active daemon or authentication to view.

* **Database Engine:** SQLite3
* **File Location:** `D:\A_LMS\ajoy-academy\lms.db`
* **Authentication:** None (Local file-based access)

### How to view the database:
You can view the raw database tables using any SQLite viewer tool:
1. Download [DB Browser for SQLite](https://sqlitebrowser.org/) or install a VS Code SQLite extension.
2. Open the file `lms.db` located in the `ajoy-academy` folder.
3. You will have full read/write access to all 21 tables (Users, Courses, Badges, Timeline, etc.).
