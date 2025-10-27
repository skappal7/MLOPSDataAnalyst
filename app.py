"""
Streamlit Data Analyzer - Main Application
==========================================
Automated statistical analysis and insight generation for large datasets.

Author: Data Analysis System
Version: 1.0.0
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from core.data_processor import DataProcessor
from core.profiler import DataProfiler
from core.context_collector import ContextCollector
from analyzers.statistical import StatisticalAnalyzer
from analyzers.time_series import TimeSeriesAnalyzer
from analyzers.categorical import CategoricalAnalyzer
from analyzers.anomaly import AnomalyDetector
from insights.scorer import InsightScorer
from insights.generator import NarrativeGenerator
from exports.pdf_generator import PDFGenerator
from exports.excel_generator import ExcelGenerator
from exports.markdown_generator import MarkdownGenerator
from utils.helpers import format_bytes, format_number


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Data Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

if 'stage' not in st.session_state:
    st.session_state.stage = 'upload'  # upload -> questions -> analysis -> results

if 'data_processor' not in st.session_state:
    st.session_state.data_processor = None

if 'analysis_config' not in st.session_state:
    st.session_state.analysis_config = None

if 'insights' not in st.session_state:
    st.session_state.insights = None


# ============================================================================
# HEADER
# ============================================================================

st.title("📊 Intelligent Data Analyzer")
st.markdown("""
Automated statistical analysis powered by **Polars**, **DuckDB**, and advanced ML.  
Upload your dataset, answer 5 questions, and get actionable insights in seconds.
""")

st.divider()


# ============================================================================
# STAGE 1: DATA UPLOAD
# ============================================================================

if st.session_state.stage == 'upload':
    st.header("Step 1: Upload Your Dataset")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file (up to 200MB recommended)",
            type=['csv', 'xlsx', 'xls'],
            help="Supports CSV and Excel formats with up to 50+ columns"
        )
    
    with col2:
        st.info("""
        **Supported:**
        - CSV files
        - Excel (.xlsx, .xls)
        - Up to 200MB
        - 50+ columns
        - Mixed data types
        """)
    
    if uploaded_file is not None:
        # Display file info
        file_size = uploaded_file.size
        st.success(f"✅ File uploaded: **{uploaded_file.name}** ({format_bytes(file_size)})")
        
        # Process button
        if st.button("🚀 Process Data", type="primary", use_container_width=True):
            with st.spinner("Processing data... This may take 10-30 seconds for large files."):
                try:
                    # Initialize processor
                    processor = DataProcessor()
                    
                    # Load and convert to Parquet
                    parquet_path = processor.load_file(uploaded_file)
                    
                    # Get schema and profile
                    schema = processor.get_schema()
                    profile = DataProfiler.generate_profile(parquet_path)
                    
                    # Store in session state
                    st.session_state.data_processor = processor
                    st.session_state.profile = profile
                    st.session_state.parquet_path = parquet_path
                    
                    # Move to next stage
                    st.session_state.stage = 'questions'
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
                    st.exception(e)


# ============================================================================
# STAGE 2: CONTEXT QUESTIONS
# ============================================================================

elif st.session_state.stage == 'questions':
    st.header("Step 2: Provide Context")
    st.markdown("Answer these questions to guide the analysis:")
    
    # Display data preview
    with st.expander("📋 Data Preview", expanded=False):
        profile = st.session_state.profile
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows", format_number(profile['total_rows']))
        col2.metric("Total Columns", profile['total_columns'])
        col3.metric("Numeric Columns", len(profile['numeric_columns']))
        col4.metric("Categorical Columns", len(profile['categorical_columns']))
        
        st.dataframe(
            st.session_state.data_processor.get_preview(),
            use_container_width=True,
            height=200
        )
    
    # Collect context
    collector = ContextCollector(st.session_state.profile)
    analysis_config = collector.collect_context()
    
    # Generate insights button
    if st.button("🔍 Generate Insights", type="primary", use_container_width=True):
        st.session_state.analysis_config = analysis_config
        st.session_state.stage = 'analysis'
        st.rerun()


# ============================================================================
# STAGE 3: ANALYSIS (Background)
# ============================================================================

elif st.session_state.stage == 'analysis':
    st.header("Step 3: Analyzing Data...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Get data
        parquet_path = st.session_state.parquet_path
        config = st.session_state.analysis_config
        
        all_insights = []
        
        # Statistical Analysis
        status_text.text("Running statistical analysis...")
        progress_bar.progress(20)
        stat_analyzer = StatisticalAnalyzer(parquet_path, config)
        all_insights.extend(stat_analyzer.analyze())
        
        # Time Series Analysis (if applicable)
        if config.get('time_column'):
            status_text.text("Analyzing time series patterns...")
            progress_bar.progress(40)
            ts_analyzer = TimeSeriesAnalyzer(parquet_path, config)
            all_insights.extend(ts_analyzer.analyze())
        
        # Categorical Analysis
        status_text.text("Analyzing categorical segments...")
        progress_bar.progress(60)
        config['profile'] = st.session_state.profile  # Add profile to config
        cat_analyzer = CategoricalAnalyzer(parquet_path, config)
        all_insights.extend(cat_analyzer.analyze())
        
        # Anomaly Detection
        status_text.text("Detecting anomalies...")
        progress_bar.progress(80)
        anomaly_detector = AnomalyDetector(parquet_path, config)
        all_insights.extend(anomaly_detector.detect())
        
        # Score and rank insights
        status_text.text("Scoring and ranking insights...")
        progress_bar.progress(90)
        scorer = InsightScorer(config)
        scored_insights = scorer.score_all(all_insights)
        
        # Generate narratives
        status_text.text("Generating narratives...")
        progress_bar.progress(95)
        generator = NarrativeGenerator()
        final_insights = generator.generate_narratives(scored_insights)
        
        # Store results
        st.session_state.insights = final_insights
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        # Move to results
        st.session_state.stage = 'results'
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        st.exception(e)
        if st.button("← Back to Questions"):
            st.session_state.stage = 'questions'
            st.rerun()


# ============================================================================
# STAGE 4: RESULTS
# ============================================================================

elif st.session_state.stage == 'results':
    st.header("📈 Analysis Results")
    
    insights = st.session_state.insights
    config = st.session_state.analysis_config
    
    # Summary metrics
    high_priority = [i for i in insights if i['score'] >= 8]
    medium_priority = [i for i in insights if 6 <= i['score'] < 8]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🔴 High Priority", len(high_priority))
    col2.metric("🟡 Medium Priority", len(medium_priority))
    col3.metric("📊 Total Insights", len(insights))
    
    st.divider()
    
    # Display insights
    st.subheader("🎯 Key Findings")
    
    for idx, insight in enumerate(insights[:10], 1):  # Top 10
        score = insight['score']
        
        # Color coding
        if score >= 8:
            color = "🔴"
            badge = "HIGH PRIORITY"
        elif score >= 6:
            color = "🟡"
            badge = "MEDIUM"
        else:
            color = "🔵"
            badge = "LOW"
        
        with st.expander(f"{color} **Finding #{idx}** - {insight['title']} (Score: {score:.1f}/10)", expanded=(idx <= 3)):
            st.markdown(f"**{badge}**")
            st.markdown(insight['narrative'])
            
            # Display chart if available
            if 'chart' in insight:
                st.plotly_chart(insight['chart'], use_container_width=True)
            
            # Display supporting data
            if 'data' in insight:
                st.dataframe(insight['data'], use_container_width=True)
    
    st.divider()
    
    # Export options
    st.subheader("📥 Export Reports")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 Download PDF", use_container_width=True):
            with st.spinner("Generating PDF..."):
                pdf_gen = PDFGenerator()
                pdf_bytes = pdf_gen.generate(insights, config)
                st.download_button(
                    label="💾 Save PDF",
                    data=pdf_bytes,
                    file_name="analysis_report.pdf",
                    mime="application/pdf"
                )
    
    with col2:
        if st.button("📊 Download Excel", use_container_width=True):
            with st.spinner("Generating Excel..."):
                excel_gen = ExcelGenerator()
                excel_bytes = excel_gen.generate(insights, config)
                st.download_button(
                    label="💾 Save Excel",
                    data=excel_bytes,
                    file_name="analysis_report.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    with col3:
        if st.button("📝 Download Markdown", use_container_width=True):
            md_gen = MarkdownGenerator()
            md_content = md_gen.generate(insights, config)
            st.download_button(
                label="💾 Save Markdown",
                data=md_content,
                file_name="analysis_report.md",
                mime="text/markdown"
            )
    
    with col4:
        if st.button("🔄 New Analysis", use_container_width=True, type="primary"):
            # Reset session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ============================================================================
# SIDEBAR
# ============================================================================

with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    **Intelligent Data Analyzer v1.0**
    
    Automated statistical analysis using:
    - 🚀 Polars (fast data processing)
    - 🗄️ DuckDB (SQL analytics)
    - 📈 scipy/statsmodels (statistics)
    - 🤖 scikit-learn (ML insights)
    
    **No LLMs required** - pure statistical methods.
    """)
    
    st.divider()
    
    st.header("📋 Current Stage")
    stages = {
        'upload': '1️⃣ Upload Data',
        'questions': '2️⃣ Answer Questions',
        'analysis': '3️⃣ Analyzing...',
        'results': '4️⃣ View Results'
    }
    st.info(stages.get(st.session_state.stage, 'Unknown'))
    
    if st.session_state.stage != 'upload':
        if st.button("🔙 Start Over"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
