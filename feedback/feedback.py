import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

class FeedbackManager:
    def __init__(self):
        self.db_path = "feedback/feedback.db"
        self.setup_database()

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rating INTEGER, usability_score INTEGER, feature_satisfaction INTEGER,
            missing_features TEXT, improvement_suggestions TEXT, user_experience TEXT, timestamp DATETIME)''')
        conn.commit()
        conn.close()

    def save_feedback(self, feedback_data):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''INSERT INTO feedback (rating, usability_score, feature_satisfaction,
            missing_features, improvement_suggestions, user_experience, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)''',
            (*feedback_data.values(), datetime.now()))
        conn.commit()
        conn.close()

    def get_feedback_stats(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM feedback", conn)
        conn.close()
        return df.mean().to_dict() if not df.empty else {}

    def render_feedback_form(self):
        st.title("📝 Share Your Feedback")
        feedback_data = {
            'rating': st.slider("Overall Experience", 1, 5, 5),
            'usability_score': st.slider("Usability Score", 1, 5, 5),
            'feature_satisfaction': st.slider("Feature Satisfaction", 1, 5, 5),
            'missing_features': st.text_area("Missing Features"),
            'improvement_suggestions': st.text_area("Suggestions"),
            'user_experience': st.text_area("Your Experience")
        }
        if st.button("Submit Feedback"):
            for i in range(100):
                st.progress(i + 1)
                time.sleep(0.01)
            self.save_feedback(feedback_data)
            st.success("🎉 Thank you for your feedback!")
            st.balloons()

    def render_feedback_stats(self):
        stats = self.get_feedback_stats()
        st.title("📊 Feedback Overview")
        if stats:
            st.metric("Avg Rating", f"{stats.get('rating', 0):.1f}/5")
            st.metric("Usability", f"{stats.get('usability_score', 0):.1f}/5")
            st.metric("Satisfaction", f"{stats.get('feature_satisfaction', 0):.1f}/5")
        else:
            st.write("No feedback yet.")
