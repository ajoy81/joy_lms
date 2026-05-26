import os
from database.engine import SessionLocal
from database.models import Reward, UserBadge, Badge, ActivityLog, Streak
from datetime import datetime, date, timedelta
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def award_points(user_id, points, reason, reference_type=None, reference_id=None, awarded_by=None):
    """Awards points to a user and checks for any new badges to unlock."""
    db = SessionLocal()
    try:
        reward = Reward(
            child_id=user_id,
            points=points,
            reason=reason,
            reference_type=reference_type,
            reference_id=reference_id,
            awarded_by=awarded_by,
            awarded_at=utcnow()
        )
        db.add(reward)
        db.commit()
        
        # Log activity
        log = ActivityLog(user_id=user_id, action_type="points_earned", metadata={"points": points, "reason": reason}, timestamp=utcnow())
        db.add(log)
        db.commit()
        
        # Check badge criteria (simplified version for prototype)
        # Check total points badge
        total_points = sum([r.points for r in db.query(Reward).filter_by(child_id=user_id).all()])
        if total_points >= 1000:
            badge = db.query(Badge).filter_by(name="Point Collector").first()
            if badge:
                award_badge(db, user_id, badge.id)
                
    finally:
        db.close()

def award_badge(db, user_id, badge_id):
    """Awards a badge to a user if they don't already have it."""
    existing = db.query(UserBadge).filter_by(user_id=user_id, badge_id=badge_id).first()
    if not existing:
        user_badge = UserBadge(user_id=user_id, badge_id=badge_id, earned_at=utcnow())
        db.add(user_badge)
        
        badge = db.query(Badge).get(badge_id)
        # Create timeline post auto
        from database.models import TimelinePost
        post = TimelinePost(
            author_id=user_id,
            post_type="text",
            text_content=f"🎉 I earned the {badge.name} badge!",
            is_auto_generated=True,
            auto_post_type="badge_earned",
            created_at=utcnow(),
            updated_at=utcnow()
        )
        db.add(post)
        db.commit()
        
def update_streak(user_id):
    """Updates user's streak based on login activity."""
    db = SessionLocal()
    try:
        today = utcnow().date()
        yesterday = today - timedelta(days=1)
        
        streak = db.query(Streak).filter_by(child_id=user_id).first()
        if not streak:
            streak = Streak(child_id=user_id, current_streak=1, longest_streak=1, last_active_date=today)
            db.add(streak)
            db.commit()
            award_points(user_id, 5, "Daily login")
            return
            
        if streak.last_active_date == today:
            # Already updated today
            return
            
        if streak.last_active_date == yesterday:
            streak.current_streak += 1
            if streak.current_streak > streak.longest_streak:
                streak.longest_streak = streak.current_streak
            streak.last_active_date = today
            db.commit()
            award_points(user_id, 5, "Daily login")
            
            # Check streak badges
            if streak.current_streak == 3:
                b = db.query(Badge).filter_by(name="Streak Starter").first()
                if b: award_badge(db, user_id, b.id)
            elif streak.current_streak == 7:
                b = db.query(Badge).filter_by(name="Streak Master").first()
                if b: 
                    award_badge(db, user_id, b.id)
                    award_points(user_id, 50, "7-day streak bonus")
        elif streak.last_active_date < yesterday:
            # Streak broken
            streak.current_streak = 1
            streak.last_active_date = today
            db.commit()
            award_points(user_id, 5, "Daily login")
            
    finally:
        db.close()
