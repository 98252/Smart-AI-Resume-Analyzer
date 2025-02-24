import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class DashboardComponents:
    def __init__(self, colors):
        self.colors = colors

    def render_metric_card(self, title, value, subtitle=None, trend=None, trend_value=None):
        trend_html = f"""
            <div style="color: {self.colors['success' if trend == 'up' else 'danger']}; font-size: 0.9rem; margin-top: 5px;">
                {'↑' if trend == 'up' else '↓'} {trend_value}%
            </div>
        """ if trend and trend_value else ""
        
        st.markdown(f"""
            <div class="metric-card">
                <div style="color: {self.colors['subtext']}; font-size: 0.9rem;">{title}</div>
                <div style="color: {self.colors['text']}; font-size: 2rem; font-weight: bold; margin: 10px 0;">{value}</div>
                {f'<div style="color: {self.colors["subtext"]}; font-size: 0.8rem;">{subtitle}</div>' if subtitle else ''}
                {trend_html}
            </div>
        """, unsafe_allow_html=True)

    def create_gauge_chart(self, value, title):
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=value,
            title={'text': title, 'font': {'size': 24, 'color': self.colors['text']}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': self.colors['text']},
                'bar': {'color': self.colors['primary']},
                'steps': [
                    {'range': [0, 40], 'color': self.colors['danger']},
                    {'range': [40, 70], 'color': self.colors['warning']},
                    {'range': [70, 100], 'color': self.colors['success']}
                ],
            }
        ))
        fig.update_layout(paper_bgcolor=self.colors['card'], plot_bgcolor=self.colors['card'], font={'color': self.colors['text']}, height=300, margin=dict(l=20, r=20, t=50, b=20))
        return fig

    def create_trend_chart(self, dates, values, title):
        fig = go.Figure(go.Scatter(x=dates, y=values, mode='lines+markers', line=dict(color=self.colors['info'], width=3), marker=dict(size=8, color=self.colors['info'])))
        fig.update_layout(title=title, paper_bgcolor=self.colors['card'], plot_bgcolor=self.colors['card'], font={'color': self.colors['text']}, height=300, margin=dict(l=20, r=20, t=50, b=20), xaxis=dict(showgrid=True, gridcolor=self.colors['background']), yaxis=dict(showgrid=True, gridcolor=self.colors['background']))
        return fig

    def create_bar_chart(self, categories, values, title):
        fig = go.Figure(go.Bar(x=categories, y=values, marker_color=self.colors['primary'], text=values, textposition='auto'))
        fig.update_layout(title=title, paper_bgcolor=self.colors['card'], plot_bgcolor=self.colors['card'], font={'color': self.colors['text']}, height=300, margin=dict(l=20, r=20, t=50, b=20), xaxis=dict(showgrid=False, color=self.colors['text']), yaxis=dict(showgrid=True, gridcolor=self.colors['background'], color=self.colors['text']))
        return fig

    def create_dual_axis_chart(self, categories, values1, values2, title):
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=categories, y=values1, name="Count", marker_color=self.colors['secondary']), secondary_y=False)
        fig.add_trace(go.Scatter(x=categories, y=values2, name="Score", line=dict(color=self.colors['warning'], width=3), mode='lines+markers'), secondary_y=True)
        fig.update_layout(title=title, paper_bgcolor=self.colors['card'], plot_bgcolor=self.colors['card'], font={'color': self.colors['text']}, height=300, margin=dict(l=20, r=20, t=50, b=20), showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig.update_xaxes(title_text="Categories", color=self.colors['text'])
        fig.update_yaxes(title_text="Count", color=self.colors['text'], secondary_y=False)
        fig.update_yaxes(title_text="Score", color=self.colors['text'], secondary_y=True)
        return fig