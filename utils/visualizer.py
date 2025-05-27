import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import streamlit as st
import pandas as pd
import numpy as np

class ResumeVisualizer:
    """Create visualizations for resume analysis"""
    
    def __init__(self):
        pass
    
    def plot_skills(self, skills_dict):
        """Create a horizontal bar chart of skills
        
        Args:
            skills_dict: Dictionary of skills and their frequencies
            
        Returns:
            Plotly figure object
        """
        if not skills_dict:
            return None
            
        # Sort skills by frequency
        sorted_skills = dict(sorted(skills_dict.items(), key=lambda x: x[1], reverse=True))
        
        # Create dataframe
        df = pd.DataFrame({
            'Skill': list(sorted_skills.keys()),
            'Count': list(sorted_skills.values())
        })
        
        # Create horizontal bar chart
        fig = px.bar(
            df, 
            y='Skill', 
            x='Count',
            orientation='h',
            title='Skills Identified in Resume',
            color='Count',
            color_continuous_scale=px.colors.sequential.Blues
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=10, r=10, t=50, b=10),
            height=min(100 + len(sorted_skills) * 20, 600)  # Dynamic height based on number of skills
        )
        
        return fig
    
    def plot_word_cloud(self, word_freq):
        """Generate a word cloud from word frequencies
        
        Args:
            word_freq: Dictionary of words and their frequencies
            
        Returns:
            WordCloud object
        """
        if not word_freq:
            return None
            
        wordcloud = WordCloud(
            width=800, 
            height=400,
            background_color='white',
            colormap='viridis',
            max_words=100
        ).generate_from_frequencies(word_freq)
        
        return wordcloud
    
    def plot_job_match(self, comparison_results):
        """Create a visualization for job description match
        
        Args:
            comparison_results: Results from the job comparison analysis
            
        Returns:
            Plotly figure object
        """
        if not comparison_results or 'match_percentage' not in comparison_results:
            return None
        
        match_percentage = comparison_results['match_percentage']
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=match_percentage,
            title={'text': "Resume Match with Job Description"},
            gauge={
                'axis': {'range': [0, 100]},
                'bar': {'color': "royalblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgray"},
                    {'range': [30, 70], 'color': "gray"},
                    {'range': [70, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        return fig
    
    def plot_keyword_comparison(self, comparison_results):
        """Create a visual comparison of matching vs missing keywords
        
        Args:
            comparison_results: Results from the job comparison analysis
            
        Returns:
            Plotly figure object
        """
        if not comparison_results or 'matching_keywords' not in comparison_results:
            return None
            
        matching = len(comparison_results['matching_keywords'])
        missing = len(comparison_results['missing_keywords'])
        
        labels = ['Matching Keywords', 'Missing Keywords']
        values = [matching, missing]
        colors = ['rgb(82, 192, 128)', 'rgb(207, 85, 85)']
        
        fig = px.pie(
            names=labels, 
            values=values, 
            title='Keyword Comparison',
            color_discrete_sequence=colors
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        return fig
    
    def plot_readability(self, readability_scores):
        """Create radar chart for readability metrics
        
        Args:
            readability_scores: Dictionary of readability scores
            
        Returns:
            Plotly figure object
        """
        if not readability_scores:
            return None
            
        # Select relevant metrics for visualization
        metrics = [
            'flesch_reading_ease', 
            'flesch_kincaid_grade',
            'coleman_liau_index',
            'automated_readability_index',
            'dale_chall_readability_score'
        ]
        
        # Create nice labels for the metrics
        labels = [
            'Flesch Reading Ease', 
            'Flesch-Kincaid Grade',
            'Coleman-Liau Index',
            'Automated Readability',
            'Dale-Chall Score'
        ]
        
        values = [readability_scores.get(metric, 0) for metric in metrics]
        
        # Normalize values to 0-10 scale for consistent visualization
        # Note: Flesch Reading Ease is 0-100 scale where higher is better
        # Most other metrics are grade levels (lower is more readable)
        normalized_values = [
            values[0] / 10,  # Flesch Reading Ease/10 (0-10 scale)
            min(10, values[1]),  # Grade level capped at 10
            min(10, values[2]),  # Grade level capped at 10
            min(10, values[3]),  # Grade level capped at 10
            min(10, values[4])   # Score capped at 10
        ]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=labels,
            fill='toself',
            name='Readability Metrics'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10]
                )),
            title='Resume Readability Assessment',
            height=350,
            margin=dict(l=10, r=10, t=50, b=10),
        )
        
        return fig
