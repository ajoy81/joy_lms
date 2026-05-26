from database.engine import SessionLocal
from database.models import Badge

def init_badges():
    db = SessionLocal()
    try:
        b1 = db.query(Badge).filter_by(name="Quiz Master").first()
        if not b1:
            b1 = Badge(name="Quiz Master", description="Successfully passed a Quiz!", emoji_icon="🎓", criteria_type="quiz_passed", criteria_value=1, points_value=50, tier="Silver")
            db.add(b1)
            
        b2 = db.query(Badge).filter_by(name="Halfway There").first()
        if not b2:
            b2 = Badge(name="Halfway There", description="Completed 50% of a course!", emoji_icon="🚀", criteria_type="course_50", criteria_value=1, points_value=100, tier="Gold")
            db.add(b2)
            
        db.commit()
        print("Badges initialized.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_badges()
