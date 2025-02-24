import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from config.database import get_database_connection
from io import BytesIO

class DashboardManager:
    def __init__(self):
        self.conn = get_database_connection()
        self.colors = {
            'primary': '#4CAF50',
            'secondary': '#2196F3',
            'info': '#00BCD4',
            'success': '#66BB6A',
            'purple': '#9C27B0',
            'background': '#1E1E1E',
            'card': '#2D2D2D',
            'text': '#FFFFFF',
            'subtext': '#B0B0B0'
        }

    def apply_dashboard_style(self):
        """Apply custom styling for dashboard"""
        st.markdown("""
            <style>
                .dashboard-title { font-size: 2.5rem; font-weight: bold; margin-bottom: 2rem; color: white; text-align: center; }
                .metric-card { background-color: #2D2D2D; border-radius: 15px; padding: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
                .metric-value { font-size: 2.5rem; font-weight: bold; color: #4CAF50; margin: 0.5rem 0; }
                .metric-label { font-size: 1rem; color: #B0B0B0; }
                .chart-container { background-color: #2D2D2D; border-radius: 15px; padding: 1.5rem; margin: 1rem 0; }
                .section-title { font-size: 1.5rem; color: white; margin: 2rem 0 1rem 0; }
            </style>
        """, unsafe_allow_html=True)

    def get_resume_metrics(self):
        """Get resume-related metrics from database"""
        cursor = self.conn.cursor()
        now = datetime.now()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_week = now - timedelta(days=now.weekday())
        start_of_month = now.replace(day=1)

        metrics = {}
        for period, start_date in [
            ('Today', start_of_day),
            ('This Week', start_of_week),
            ('This Month', start_of_month),
            ('All Time', datetime(2000, 1, 1))
        ]:
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT rd.id) as total_resumes,
                    ROUND(AVG(ra.ats_score), 1) as avg_ats_score,
                    ROUND(AVG(ra.keyword_match_score), 1) as avg_keyword_score,
                    COUNT(DISTINCT CASE WHEN ra.ats_score >= 70 THEN rd.id END) as high_scoring
                FROM resume_data rd
                LEFT JOIN resume_analysis ra ON rd.id = ra.resume_id
                WHERE rd.created_at >= ?
            """, (start_date.strftime('%Y-%m-%d %H:%M:%S'),))
            
            row = cursor.fetchone()
            metrics[period] = {
                'total': row[0] or 0,
                'ats_score': row[1] or 0,
                'keyword_score': row[2] or 0,
                'high_scoring': row[3] or 0
            }
        
        return metrics

    def get_skill_distribution(self):
        """Get skill distribution data"""
        cursor = self.conn.cursor()
        cursor.execute("""
            WITH RECURSIVE split(skill, rest) AS (
                SELECT '', skills || ',' FROM resume_data
                UNION ALL
                SELECT substr(rest, 0, instr(rest, ',')), substr(rest, instr(rest, ',') + 1)
                FROM split WHERE rest <> ''
            )
            SELECT skill, COUNT(*) as count
            FROM split WHERE skill <> ''
            GROUP BY skill
            ORDER BY count DESC
            LIMIT 10
        """)
        
        skills, counts = [], []
        for row in cursor.fetchall():
            skills.append(row[0])
            counts.append(row[1])
            
        return skills, counts

    def get_weekly_trends(self):
        """Get weekly submission trends"""
        cursor = self.conn.cursor()
        now = datetime.now()
        dates = [(now - timedelta(days=x)).strftime('%Y-%m-%d') for x in range(6, -1, -1)]
        
        submissions = []
        for date in dates:
            cursor.execute("SELECT COUNT(*) FROM resume_data WHERE DATE(created_at) = DATE(?)", (date,))
            submissions.append(cursor.fetchone()[0])
            
        return [d[-3:] for d in dates], submissions

    def render_dashboard(self):
        """Main dashboard rendering function"""
        self.apply_dashboard_style()

        # Dashboard Header
        st.markdown("""
            <div class="dashboard-container">
                <div class="dashboard-title">Resume Analytics Dashboard</div>
            </div>
        """, unsafe_allow_html=True)

        # Quick Stats
        metrics = self.get_resume_metrics()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['All Time']['total']}</div><div class='metric-label'>Total Resumes</div></div>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['All Time']['ats_score']}</div><div class='metric-label'>Avg ATS Score</div></div>", unsafe_allow_html=True)
        with col3:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['All Time']['high_scoring']}</div><div class='metric-label'>High Scoring</div></div>", unsafe_allow_html=True)
        with col4:
            st.markdown(f"<div class='metric-card'><div class='metric-value'>{metrics['All Time']['keyword_score']}</div><div class='metric-label'>Avg Keyword Score</div></div>", unsafe_allow_html=True)

        # Charts
        st.markdown('<div class="section-title">📈 Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_skill_distribution_chart()
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = self.create_submission_trends_chart()
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    def create_skill_distribution_chart(self):
        """Create a skill distribution chart"""
        skills, counts = self.get_skill_distribution()
        fig = go.Figure(data=[
            go.Bar(x=skills, y=counts, marker_color=self.colors['info'])
        ])
        fig.update_layout(
            title="Top Skills",
            paper_bgcolor=self.colors['card'],
            plot_bgcolor=self.colors['card'],
            font={'color': self.colors['text']},
            height=300
        )
        return fig

    def create_submission_trends_chart(self):
        """Create a weekly submission trend chart"""
        dates, submissions = self.get_weekly_trends()
        fig = go.Figure(data=[
            go.Scatter(x=dates, y=submissions, mode='lines+markers', line=dict(color=self.colors['info'], width=3))
        ])
        fig.update_layout(
            title="Weekly Submissions",
            paper_bgcolor=self.colors['card'],
            plot_bgcolor=self.colors['card'],
            font={'color': self.colors['text']},
            height=300
        )
        return fig