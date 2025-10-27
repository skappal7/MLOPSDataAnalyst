"""
Context Collector
=================
Collects user context through 5 strategic questions.
"""

import streamlit as st
from typing import Dict, Any, List


class ContextCollector:
    """
    Interactive context collection system.
    
    Asks 5 questions to understand:
    1. Domain/data type
    2. Key metrics
    3. Time dimension
    4. Comparison needs
    5. Alert thresholds
    """
    
    def __init__(self, profile: Dict[str, Any]):
        """
        Initialize with data profile.
        
        Args:
            profile: Data profile from profiler
        """
        self.profile = profile
    
    def collect_context(self) -> Dict[str, Any]:
        """
        Collect analysis context through UI.
        
        Returns:
            Configuration dictionary
        """
        config = {}
        
        # ========================================
        # QUESTION 1: Domain/Data Type
        # ========================================
        st.subheader("1️⃣ What type of data is this?")
        config['domain'] = st.selectbox(
            "Select the category that best describes your data:",
            options=[
                'Sales/Revenue',
                'Customer Behavior',
                'Operations/Supply Chain',
                'Marketing/Campaigns',
                'Financial/Accounting',
                'Other'
            ],
            help="This helps prioritize relevant analyses"
        )
        
        st.divider()
        
        # ========================================
        # QUESTION 2: Key Metrics
        # ========================================
        st.subheader("2️⃣ What are your key metrics?")
        st.caption("Select up to 3 most important numeric columns")
        
        numeric_cols = self.profile['numeric_columns']
        config['key_metrics'] = st.multiselect(
            "Choose key metrics to analyze:",
            options=numeric_cols,
            max_selections=3,
            help="These will be prioritized in correlation and anomaly detection"
        )
        
        st.divider()
        
        # ========================================
        # QUESTION 3: Time Dimension
        # ========================================
        st.subheader("3️⃣ Time dimension (optional)")
        
        date_cols = self.profile['date_columns']
        
        if date_cols:
            config['time_column'] = st.selectbox(
                "Select date/time column:",
                options=[None] + date_cols,
                help="Required for trend and seasonality analysis"
            )
            
            if config['time_column']:
                config['time_granularity'] = st.radio(
                    "Analysis granularity:",
                    options=['Daily', 'Weekly', 'Monthly', 'Quarterly'],
                    horizontal=True
                )
        else:
            st.info("⚠️ No date columns detected. Time-series analysis will be skipped.")
            config['time_column'] = None
        
        st.divider()
        
        # ========================================
        # QUESTION 4: Comparison Type
        # ========================================
        st.subheader("4️⃣ What comparisons matter?")
        
        comparison_options = ['Period-over-period (MoM, YoY)', 
                             'Segment comparisons (by category)',
                             'Against target/benchmark']
        
        config['comparisons'] = st.multiselect(
            "Select comparison types:",
            options=comparison_options,
            default=[comparison_options[0]],
            help="Defines how insights are framed"
        )
        
        # Target input if selected
        if 'Against target/benchmark' in config['comparisons']:
            if config['key_metrics']:
                targets = {}
                st.caption("Enter target values for key metrics:")
                cols = st.columns(len(config['key_metrics']))
                for idx, metric in enumerate(config['key_metrics']):
                    with cols[idx]:
                        targets[metric] = st.number_input(
                            f"Target {metric}:",
                            value=0.0,
                            step=0.1
                        )
                config['targets'] = targets
        
        st.divider()
        
        # ========================================
        # QUESTION 5: Alert Thresholds
        # ========================================
        st.subheader("5️⃣ What's unusual in your domain?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            config['change_threshold'] = st.slider(
                "Alert if % change exceeds:",
                min_value=5,
                max_value=50,
                value=15,
                step=5,
                help="Percentage change that warrants attention"
            ) / 100  # Convert to decimal
        
        with col2:
            config['outlier_threshold'] = st.slider(
                "Outlier sensitivity (std deviations):",
                min_value=2.0,
                max_value=4.0,
                value=3.0,
                step=0.5,
                help="Lower = more sensitive to outliers"
            )
        
        # Optional: Known patterns
        with st.expander("🔧 Advanced: Known patterns (optional)"):
            config['known_seasonality'] = st.text_input(
                "Describe known seasonal patterns:",
                placeholder="e.g., 'Q4 typically 40% higher', 'Monday peaks'"
            )
        
        return config
