import streamlit as st
import pandas as pd
from database.engine import SessionLocal
from database.models import Reward, User
from datetime import datetime, timedelta
import pytz

def utcnow():
    return datetime.now(pytz.utc)

def show_leaderboard(user):
    st.markdown("## 🏅 Leaderboard")
    
    tab1, tab2 = st.tabs(["Weekly Leaderboard", "All-Time Leaderboard"])
    
    db = SessionLocal()
    try:
        query = db.query(User).filter_by(role="child")
        
        active_inst = st.session_state.get('active_institute_id')
        if active_inst:
            from database.models import UserInstitute
            query = query.join(UserInstitute).filter(UserInstitute.institute_id == active_inst)
            
        children = query.all()
        child_dict = {c.id: f"{c.avatar_emoji} {c.username}" for c in children}
        
        with tab1:
            st.markdown("### This Week's Top Learners")
            start_of_week = utcnow() - timedelta(days=utcnow().weekday())
            rewards_this_week = db.query(Reward).filter(Reward.awarded_at >= start_of_week).all()
            
            weekly_scores = {}
            for r in rewards_this_week:
                if r.child_id in child_dict:
                    weekly_scores[r.child_id] = weekly_scores.get(r.child_id, 0) + r.points
                    
            if not weekly_scores:
                st.info("No points earned yet this week. Be the first!")
            else:
                sorted_weekly = sorted(weekly_scores.items(), key=lambda x: x[1], reverse=True)[:10]
                for idx, (cid, pts) in enumerate(sorted_weekly):
                    rank_icon = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"
                    highlight = "background-color: #FFF3E0; border: 2px solid #FF9800;" if cid == user.id else "background-color: #FFFFFF;"
                    st.markdown(f"""
                    <div style="padding: 10px; margin-bottom: 5px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); {highlight}">
                        <h4 style="margin: 0;">{rank_icon} {child_dict[cid]} <span style="float: right; color: #FF6B6B;">{pts} pts</span></h4>
                    </div>
                    """, unsafe_allow_html=True)

        with tab2:
            st.markdown("### All-Time Hall of Fame")
            all_rewards = db.query(Reward).all()
            
            all_time_scores = {}
            for r in all_rewards:
                if r.child_id in child_dict:
                    all_time_scores[r.child_id] = all_time_scores.get(r.child_id, 0) + r.points
                    
            if not all_time_scores:
                st.info("No points recorded yet.")
            else:
                sorted_all = sorted(all_time_scores.items(), key=lambda x: x[1], reverse=True)[:10]
                for idx, (cid, pts) in enumerate(sorted_all):
                    rank_icon = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"#{idx+1}"
                    highlight = "background-color: #FFF3E0; border: 2px solid #FF9800;" if cid == user.id else "background-color: #FFFFFF;"
                    st.markdown(f"""
                    <div style="padding: 10px; margin-bottom: 5px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); {highlight}">
                        <h4 style="margin: 0;">{rank_icon} {child_dict[cid]} <span style="float: right; color: #FF6B6B;">{pts} pts</span></h4>
                    </div>
                    """, unsafe_allow_html=True)

    finally:
        db.close()
