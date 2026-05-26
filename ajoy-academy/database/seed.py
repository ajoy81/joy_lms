import bcrypt
from datetime import date
from database.engine import SessionLocal, init_db
from database.models import User, Badge, Course, Module, Lesson, UserRelation

def seed_db():
    init_db()
    db = SessionLocal()

    try:
        # Check if already seeded
        if db.query(User).first() is not None:
            print("Database already seeded.")
            return

        print("Seeding database...")

        # 1-3. Users
        teacher = User(
            username="teacher1",
            email="teacher1@example.com",
            password_hash=bcrypt.hashpw("teacher123".encode(), bcrypt.gensalt()).decode(),
            role="teacher",
            full_name="Admin Teacher",
            avatar_emoji="👨‍🏫"
        )
        parent = User(
            username="parent1",
            email="parent1@example.com",
            password_hash=bcrypt.hashpw("parent123".encode(), bcrypt.gensalt()).decode(),
            role="parent",
            full_name="Admin Parent",
            avatar_emoji="👪"
        )
        child = User(
            username="kid1",
            email="kid1@example.com",
            password_hash=bcrypt.hashpw("kid123".encode(), bcrypt.gensalt()).decode(),
            role="child",
            full_name="Demo Kid",
            avatar_emoji="👧"
        )
        db.add_all([teacher, parent, child])
        db.commit()

        # 4. Badges
        badges = [
            Badge(name="First Steps", emoji_icon="🐣", description="Complete 1 lesson", criteria_type="lessons_completed", criteria_value=1, points_value=100, tier="Bronze"),
            Badge(name="Bookworm", emoji_icon="📚", description="Complete 10 lessons", criteria_type="lessons_completed", criteria_value=10, points_value=100, tier="Silver"),
            Badge(name="Scholar", emoji_icon="🎓", description="Complete 25 lessons", criteria_type="lessons_completed", criteria_value=25, points_value=100, tier="Gold"),
            Badge(name="Quiz Whiz", emoji_icon="🧠", description="Pass 5 quizzes", criteria_type="quizzes_passed", criteria_value=5, points_value=100, tier="Silver"),
            Badge(name="Perfect Score", emoji_icon="💯", description="Get 100% on any quiz", criteria_type="perfect_quiz", criteria_value=1, points_value=100, tier="Gold"),
            Badge(name="Streak Starter", emoji_icon="🔥", description="3-day streak", criteria_type="streak_days", criteria_value=3, points_value=100, tier="Bronze"),
            Badge(name="Streak Master", emoji_icon="⚡", description="7-day streak", criteria_type="streak_days", criteria_value=7, points_value=100, tier="Silver"),
            Badge(name="Unstoppable", emoji_icon="🌟", description="30-day streak", criteria_type="streak_days", criteria_value=30, points_value=100, tier="Platinum"),
            Badge(name="Course Completer", emoji_icon="🏆", description="Complete 1 course", criteria_type="courses_completed", criteria_value=1, points_value=100, tier="Gold"),
            Badge(name="Social Butterfly", emoji_icon="🦋", description="10 timeline posts", criteria_type="timeline_posts", criteria_value=10, points_value=100, tier="Silver"),
            Badge(name="Point Collector", emoji_icon="💎", description="Earn 1000 total points", criteria_type="points_total", criteria_value=1000, points_value=100, tier="Gold"),
            Badge(name="Super Learner", emoji_icon="🦄", description="Complete 5 courses", criteria_type="courses_completed", criteria_value=5, points_value=100, tier="Diamond"),
        ]
        db.add_all(badges)

        # 5. Sample course
        course = Course(
            title="Fun with Numbers 🔢",
            description="A fun introduction to basic math concepts.",
            created_by=teacher.id,
            is_published=True,
            difficulty_level="beginner",
            age_group="5-7",
            category="math"
        )
        db.add(course)
        db.commit()

        module1 = Module(course_id=course.id, title="Module 1: Counting", order_index=1)
        module2 = Module(course_id=course.id, title="Module 2: Addition", order_index=2, is_locked=True)
        db.add_all([module1, module2])
        db.commit()

        lessons = [
            Lesson(module_id=module1.id, title="Counting to 10", lesson_type="text", content_text="Let's count! 1, 2, 3, 4, 5, 6, 7, 8, 9, 10.", order_index=1),
            Lesson(module_id=module1.id, title="Counting backwards", lesson_type="text", content_text="10, 9, 8, 7, 6, 5, 4, 3, 2, 1.", order_index=2),
            Lesson(module_id=module1.id, title="Counting song", lesson_type="video", video_url="https://www.youtube.com/watch?v=85M1yxIcHpw", order_index=3),
            Lesson(module_id=module2.id, title="Adding 1", lesson_type="text", content_text="What is 1 + 1? It is 2!", order_index=1),
            Lesson(module_id=module2.id, title="Adding 2", lesson_type="text", content_text="What is 2 + 2? It is 4!", order_index=2),
            Lesson(module_id=module2.id, title="Addition practice", lesson_type="text", content_text="Try these: 3+1, 4+2", order_index=3),
        ]
        db.add_all(lessons)

        # 6. Links
        link1 = UserRelation(guardian_id=teacher.id, child_id=child.id, relation_type="teacher")
        link2 = UserRelation(guardian_id=parent.id, child_id=child.id, relation_type="parent")
        db.add_all([link1, link2])

        db.commit()
        print("Database seeded successfully.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
