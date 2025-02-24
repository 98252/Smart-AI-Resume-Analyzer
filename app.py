import streamlit as st
import json
import pandas as pd
from utils.resume_analyzer import ResumeAnalyzer
from utils.resume_builder import ResumeBuilder
from config.database import get_database_connection, save_resume_data, save_analysis_data, init_database
from config.job_roles import JOB_ROLES
from config.courses import COURSES_BY_CATEGORY, get_courses_for_role, get_category_for_role
from dashboard.dashboard import DashboardManager
from feedback.feedback import FeedbackManager
from ui_components import apply_modern_styles

class ResumeApp:
    def __init__(self):
        """Initialize the application"""
        if 'form_data' not in st.session_state:
            st.session_state.form_data = {
                'personal_info': {'full_name': '', 'email': '', 'phone': '', 'location': '', 'linkedin': '', 'portfolio': ''},
                'summary': '', 'experiences': [], 'education': [], 'projects': [], 'skills_categories': {'technical': [], 'soft': [], 'languages': [], 'tools': []}
            }
        if 'page' not in st.session_state:
            st.session_state.page = 'home'
        if 'is_admin' not in st.session_state:
            st.session_state.is_admin = False

        self.pages = {
            "🏠 HOME": self.render_home,
            "🔍 RESUME ANALYZER": self.render_analyzer,
            "📝 RESUME BUILDER": self.render_builder,
            "📊 DASHBOARD": self.render_dashboard,
            "💬 FEEDBACK": self.render_feedback_page,
            "ℹ️ ABOUT": self.render_about
        }

        self.dashboard_manager = DashboardManager()
        self.analyzer = ResumeAnalyzer()
        self.builder = ResumeBuilder()
        self.job_roles = JOB_ROLES

        if 'user_id' not in st.session_state:
            st.session_state.user_id = 'default_user'
        if 'selected_role' not in st.session_state:
            st.session_state.selected_role = None

        init_database()
        apply_modern_styles()

    def render_home(self):
        """Render the home page"""
        st.title("Smart Resume AI 🚀")
        st.write("Transform your career with AI-powered resume analysis and building.")
        if st.button("Get Started"):
            st.session_state.page = 'resume_analyzer'
            st.rerun()

    def render_analyzer(self):
        """Render the resume analyzer page"""
        st.title("Resume Analyzer 🔍")
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'docx'])
        if uploaded_file:
            with st.spinner("Analyzing..."):
                text = self.analyzer.extract_text(uploaded_file)
                analysis = self.analyzer.analyze_resume(text)
                st.write("Analysis Results:")
                st.json(analysis)

    def render_builder(self):
        """Render the resume builder page"""
        st.title("Resume Builder 📝")
        full_name = st.text_input("Full Name", value=st.session_state.form_data['personal_info']['full_name'])
        email = st.text_input("Email", value=st.session_state.form_data['personal_info']['email'])
        if st.button("Generate Resume"):
            st.success("Resume generated successfully!")

    def render_dashboard(self):
        """Render the dashboard page"""
        self.dashboard_manager.render_dashboard()

    def render_feedback_page(self):
        """Render the feedback page"""
        feedback_manager = FeedbackManager()
        feedback_manager.render_feedback_form()

    def render_about(self):
        """Render the about page"""
        st.title("About ℹ️")
        st.write("Smart Resume AI is designed to help job seekers optimize their resumes using AI.")

    def main(self):
        """Main application entry point"""
        with st.sidebar:
            st.title("Navigation")
            for page_name, page_func in self.pages.items():
                if st.button(page_name):
                    st.session_state.page = page_name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("💬", "").replace("ℹ️", "").strip()
                    st.rerun()

        if 'initial_load' not in st.session_state:
            st.session_state.initial_load = True
            st.session_state.page = 'home'
            st.rerun()

        current_page = st.session_state.get('page', 'home')
        page_mapping = {name.lower().replace(" ", "_").replace("🏠", "").replace("🔍", "").replace("📝", "").replace("📊", "").replace("💬", "").replace("ℹ️", "").strip(): name 
                       for name in self.pages.keys()}
        
        if current_page in page_mapping:
            self.pages[page_mapping[current_page]]()
        else:
            self.render_home()

if __name__ == "__main__":
    app = ResumeApp()
    app.main()