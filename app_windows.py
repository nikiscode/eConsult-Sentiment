"""
eConsultation Sentiment Analysis Platform - Windows Version
Main Streamlit application for analyzing stakeholder feedback.
Windows-specific signal handling to prevent threading issues.
"""

import os
import platform
import warnings

# Windows-specific environment setup
if platform.system() == 'Windows':
    # Set environment variables to prevent threading issues on Windows
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["MKL_NUM_THREADS"] = "1"
    os.environ["NUMEXPR_NUM_THREADS"] = "1"
    os.environ["NUMBA_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    os.environ["NUMEXPR_MAX_THREADS"] = "1"
    os.environ["CUDA_VISIBLE_DEVICES"] = ""
    os.environ["PYTHONHASHSEED"] = "0"
    os.environ["PYTHONIOENCODING"] = "utf-8"
    os.environ["PYTHONUNBUFFERED"] = "1"
    
    # Windows-specific signal handling
    try:
        import signal
        # On Windows, signal handling is different
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
    except (ValueError, AttributeError):
        # Signal handling not available or already set
        pass
else:
    # Unix/Linux/macOS signal handling
    import signal
    import threading
    
    def setup_signal_handling():
        """Setup signal handling to prevent threading issues."""
        try:
            if threading.current_thread() is threading.main_thread():
                signal.signal(signal.SIGINT, signal.SIG_DFL)
                signal.signal(signal.SIGTERM, signal.SIG_DFL)
        except (ValueError, OSError):
            pass
    
    setup_signal_handling()

# Suppress warnings that can cause signal issues
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io
import base64
from datetime import datetime
import json
from collections import defaultdict, Counter

from sentiment_analyzer import SentimentAnalyzer
from document_analyzer import DocumentAwareAnalyzer

# Page configuration
st.set_page_config(
    page_title="eConsultation Sentiment Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">📊 eConsultation Sentiment Analysis Platform</h1>', unsafe_allow_html=True)
    
    # Show platform info
    if platform.system() == 'Windows':
        st.info("🪟 Running on Windows - Signal handling optimized for Windows compatibility")
    else:
        st.info(f"🖥️ Running on {platform.system()} - Signal handling optimized for Unix/Linux/macOS")
    
    st.markdown("---")
    
    # Initialize session state
    if 'analyzer' not in st.session_state:
        with st.spinner("Loading AI models..."):
            st.session_state.analyzer = SentimentAnalyzer()
    
    if 'document_analyzer' not in st.session_state:
        with st.spinner("Loading document-aware models..."):
            st.session_state.document_analyzer = DocumentAwareAnalyzer()
    
    if 'data' not in st.session_state:
        st.session_state.data = None
    
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    if 'main_document' not in st.session_state:
        st.session_state.main_document = None
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Data Input")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload a CSV file with stakeholder comments"
        )
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.session_state.data = df
                st.success(f"✅ Loaded {len(df)} comments")
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
        
        # Manual data entry
        st.subheader("Or enter data manually")
        manual_data = st.text_area(
            "Enter comments (one per line)",
            height=100,
            help="Enter comments separated by new lines"
        )
        
        if manual_data and st.button("Load Manual Data"):
            comments = [line.strip() for line in manual_data.split('\n') if line.strip()]
            if comments:
                df = pd.DataFrame({'comment': comments})
                st.session_state.data = df
                st.success(f"✅ Loaded {len(comments)} comments")
        
        # Sample data
        if st.button("Load Sample Data"):
            sample_data = [
                "This legislation is excellent and will help small businesses",
                "I have concerns about the implementation timeline",
                "The proposed changes are too restrictive",
                "This is a step in the right direction",
                "We need more clarity on the compliance requirements",
                "The penalties seem too harsh for minor violations",
                "Great initiative to modernize the regulatory framework",
                "The consultation period was too short",
                "This will create unnecessary bureaucracy",
                "The exemptions are well thought out"
            ]
            df = pd.DataFrame({'comment': sample_data})
            st.session_state.data = df
            st.success(f"✅ Loaded {len(sample_data)} sample comments")
        
        # Main document input
        st.header("📄 Main Document")
        
        # Document upload
        uploaded_doc = st.file_uploader(
            "Upload main document",
            type=['txt', 'pdf'],
            help="Upload the main legislation/document for context-aware analysis"
        )
        
        if uploaded_doc is not None:
            try:
                if uploaded_doc.type == "text/plain":
                    content = str(uploaded_doc.read(), "utf-8")
                else:
                    st.warning("PDF support coming soon. Please upload a .txt file.")
                    content = None
                
                if content:
                    st.session_state.main_document = content
                    st.success("✅ Main document loaded")
            except Exception as e:
                st.error(f"Error loading document: {str(e)}")
        
        # Manual document entry
        manual_doc = st.text_area(
            "Or enter document manually",
            height=150,
            help="Enter the main document text for context-aware analysis"
        )
        
        if manual_doc and st.button("Load Manual Document"):
            st.session_state.main_document = manual_doc
            st.success("✅ Main document loaded")
        
        # Sample legislation
        if st.button("Load Sample Legislation"):
            try:
                with open('sample_legislation.txt', 'r', encoding='utf-8') as f:
                    content = f.read()
                st.session_state.main_document = content
                st.success("✅ Sample legislation loaded")
            except Exception as e:
                st.error(f"Error loading sample legislation: {str(e)}")
        
        # Load sample legislation comments
        if st.button("Load Sample Legislation Comments"):
            try:
                df = pd.read_csv('sample_legislation_comments.csv')
                st.session_state.data = df
                st.success(f"✅ Loaded {len(df)} sample legislation comments")
            except Exception as e:
                st.error(f"Error loading sample legislation comments: {str(e)}")
    
    # Main content area
    if st.session_state.data is not None:
        df = st.session_state.data
        
        # Display data preview
        st.subheader("📄 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)
        
        # Analysis options
        st.subheader("🔧 Analysis Options")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            analyze_sentiment = st.checkbox("Basic Sentiment", value=True)
        with col2:
            document_aware_analysis = st.checkbox("Document-Aware Analysis", value=True)
        with col3:
            generate_summary = st.checkbox("Generate Summary", value=True)
        with col4:
            create_wordcloud = st.checkbox("Word Cloud", value=True)
        
        # Show document status
        if st.session_state.main_document:
            st.success("✅ Main document loaded - Document-aware analysis available")
        else:
            st.warning("⚠️ No main document loaded - Only basic analysis available")
        
        # Run analysis button
        if st.button("🚀 Run Analysis", type="primary"):
            if not any([analyze_sentiment, document_aware_analysis, generate_summary, create_wordcloud]):
                st.warning("Please select at least one analysis option.")
            else:
                run_analysis(df, analyze_sentiment, document_aware_analysis, generate_summary, create_wordcloud)
    
    else:
        # Welcome message
        st.info("👋 Welcome! Please upload your data or enter comments manually to get started.")
        
        # Show platform-specific instructions
        if platform.system() == 'Windows':
            st.markdown("""
            ### 🪟 Windows Users - Quick Start:
            1. **Double-click** `start_windows.bat` to start the application
            2. **Or run**: `python start_windows.py` in Command Prompt
            3. **Or run**: `python -m streamlit run app.py` directly
            """)
        else:
            st.markdown("""
            ### 🖥️ Unix/Linux/macOS Users - Quick Start:
            1. **Run**: `python3 -m streamlit run app.py`
            2. **Or run**: `python3 run_app.py`
            3. **Or use**: `./install.sh` for installation
            """)

def categorize_confidence(conf):
    """Custom confidence categorization to avoid pandas cut issues."""
    if conf <= 0.6:
        return 'Low'
    elif conf <= 0.8:
        return 'Medium'
    else:
        return 'High'

def run_analysis(df, analyze_sentiment, document_aware_analysis, generate_summary, create_wordcloud):
    """Run the selected analysis options."""
    
    analyzer = st.session_state.analyzer
    document_analyzer = st.session_state.document_analyzer
    
    # Extract comments
    if 'comment' in df.columns:
        comments = df['comment'].astype(str).tolist()
    else:
        st.error("No 'comment' column found in the data!")
        return
    
    # Set up document for document-aware analysis
    if document_aware_analysis and st.session_state.main_document:
        with st.spinner("Setting up document-aware analysis..."):
            document_analyzer.set_document(st.session_state.main_document)
    
    # Determine tabs to show
    tabs = []
    if analyze_sentiment:
        tabs.append("📊 Sentiment Analysis")
    if document_aware_analysis:
        tabs.append("📋 Document-Aware Analysis")
    if generate_summary:
        tabs.append("📝 Summary Generation")
    if create_wordcloud:
        tabs.append("☁️ Word Cloud")
    
    if not tabs:
        st.warning("No analysis options selected!")
        return
    
    tab_objects = st.tabs(tabs)
    tab_index = 0
    
    # Sentiment Analysis Tab
    if analyze_sentiment:
        with tab_objects[tab_index]:
            st.subheader("📊 Sentiment Analysis Results")
            
            with st.spinner("Analyzing sentiments..."):
                sentiment_results = analyzer.analyze_batch_sentiments(comments)
            
            # Debug: Check if sentiment_results is properly populated
            if not sentiment_results:
                st.error("No sentiment results generated!")
                return
            
            # Create results DataFrame
            results_df = pd.DataFrame(sentiment_results)
            results_df['comment'] = comments
            results_df['comment_id'] = range(1, len(comments) + 1)
            
            # Reorder columns
            results_df = results_df[['comment_id', 'comment', 'label', 'confidence', 'polarity', 'subjectivity', 'sentiment_score']]
            
            # Display results
            st.dataframe(results_df, use_container_width=True)
            
            # Metrics - with better error handling
            col1, col2, col3, col4 = st.columns(4)
            
            try:
                with col1:
                    positive_count = len([r for r in sentiment_results if r['label'] == 'POSITIVE'])
                    st.metric("Positive Comments", positive_count)
                
                with col2:
                    negative_count = len([r for r in sentiment_results if r['label'] == 'NEGATIVE'])
                    st.metric("Negative Comments", negative_count)
                
                with col3:
                    neutral_count = len([r for r in sentiment_results if r['label'] == 'NEUTRAL'])
                    st.metric("Neutral Comments", neutral_count)
                
                with col4:
                    avg_confidence = np.mean([r['confidence'] for r in sentiment_results])
                    st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                
            except Exception as e:
                st.error(f"Error calculating metrics: {str(e)}")
            
            # Sentiment distribution chart
            st.subheader("📈 Sentiment Distribution")
            sentiment_counts = Counter([r['label'] for r in sentiment_results])
            
            fig = px.pie(
                values=list(sentiment_counts.values()),
                names=list(sentiment_counts.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'POSITIVE': '#2E8B57',
                    'NEGATIVE': '#DC143C',
                    'NEUTRAL': '#4682B4'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Confidence analysis
            st.subheader("🎯 Confidence Analysis")
            detailed_df = results_df.copy()
            detailed_df['confidence_category'] = detailed_df['confidence'].apply(categorize_confidence)
            
            confidence_counts = detailed_df['confidence_category'].value_counts()
            fig_conf = px.bar(
                x=confidence_counts.index,
                y=confidence_counts.values,
                title="Confidence Level Distribution",
                color=confidence_counts.values,
                color_continuous_scale="Viridis"
            )
            st.plotly_chart(fig_conf, use_container_width=True)
            
            # Download results
            csv = results_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Results",
                data=csv,
                file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        tab_index += 1
    
    # Document-Aware Analysis Tab
    if document_aware_analysis:
        with tab_objects[tab_index]:
            st.subheader("📋 Document-Aware Analysis Results")
            
            if not st.session_state.main_document:
                st.warning("No main document loaded. Please load a document first.")
            else:
                with st.spinner("Performing document-aware analysis..."):
                    doc_results = document_analyzer.analyze_batch_document_aware(comments)
                
                if doc_results:
                    # Create document-aware results DataFrame
                    doc_df = pd.DataFrame(doc_results)
                    doc_df['comment'] = comments
                    doc_df['comment_id'] = range(1, len(comments) + 1)
                    
                    # Display results
                    st.dataframe(doc_df, use_container_width=True)
                    
                    # Document-aware metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        high_relevance = len([r for r in doc_results if r['relevance_category'] == 'High'])
                        st.metric("High Relevance", high_relevance)
                    
                    with col2:
                        medium_relevance = len([r for r in doc_results if r['relevance_category'] == 'Medium'])
                        st.metric("Medium Relevance", medium_relevance)
                    
                    with col3:
                        low_relevance = len([r for r in doc_results if r['relevance_category'] == 'Low'])
                        st.metric("Low Relevance", low_relevance)
                    
                    with col4:
                        avg_relevance = np.mean([r['relevance_score'] for r in doc_results])
                        st.metric("Avg Relevance", f"{avg_relevance:.2f}")
                    
                    # Comment type distribution
                    st.subheader("📊 Comment Type Distribution")
                    comment_types = Counter([r['comment_type'] for r in doc_results])
                    
                    fig_types = px.pie(
                        values=list(comment_types.values()),
                        names=list(comment_types.keys()),
                        title="Comment Type Distribution"
                    )
                    st.plotly_chart(fig_types, use_container_width=True)
                    
                    # Section-wise analysis
                    st.subheader("📑 Section-wise Analysis")
                    try:
                        section_analysis = defaultdict(list)
                        for result in doc_results:
                            if result['most_relevant_section']:
                                section_analysis[result['most_relevant_section']].append(result)
                        
                        if section_analysis:
                            section_stats = []
                            for section, results in section_analysis.items():
                                sentiment_counts = Counter([r['sentiment_label'] for r in results])
                                section_stats.append({
                                    'Section': section,
                                    'Comment Count': len(results),
                                    'Positive': sentiment_counts.get('POSITIVE', 0),
                                    'Negative': sentiment_counts.get('NEGATIVE', 0),
                                    'Neutral': sentiment_counts.get('NEUTRAL', 0),
                                    'Avg Relevance': np.mean([r['relevance_score'] for r in results])
                                })
                            
                            section_df = pd.DataFrame(section_stats)
                            st.dataframe(section_df, use_container_width=True)
                        else:
                            st.info("No section-specific analysis available")
                    except Exception as e:
                        st.error(f"Error in section-wise analysis: {str(e)}")
                    
                    # Download document-aware results
                    csv_doc = doc_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Document-Aware Results",
                        data=csv_doc,
                        file_name=f"document_aware_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                else:
                    st.error("No document-aware results generated!")
        
        tab_index += 1
    
    # Summary Generation Tab
    if generate_summary:
        with tab_objects[tab_index]:
            st.subheader("📝 Summary Generation")
            
            # Individual summaries
            st.subheader("Individual Comment Summaries")
            with st.spinner("Generating individual summaries..."):
                individual_summaries = []
                for i, comment in enumerate(comments):
                    try:
                        summary = analyzer.generate_summary(comment, max_length=100, min_length=30)
                        individual_summaries.append({
                            'Comment ID': i + 1,
                            'Original Comment': comment,
                            'Summary': summary
                        })
                    except Exception as e:
                        st.error(f"Error generating summary for comment {i+1}: {str(e)}")
                        individual_summaries.append({
                            'Comment ID': i + 1,
                            'Original Comment': comment,
                            'Summary': 'Error generating summary'
                        })
            
            if individual_summaries:
                summary_df = pd.DataFrame(individual_summaries)
                st.dataframe(summary_df, use_container_width=True)
                
                # Download individual summaries
                csv_summary = summary_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Individual Summaries",
                    data=csv_summary,
                    file_name=f"individual_summaries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            # Overall summary
            st.subheader("Overall Summary")
            st.info("Generating overall summary from all comments...")
            
            all_comments_text = ' '.join(comments)
            
            if len(comments) > 50:
                max_len, min_len = 300, 150
            elif len(comments) > 20:
                max_len, min_len = 250, 120
            else:
                max_len, min_len = 200, 100
            
            overall_summary = analyzer.generate_summary(all_comments_text, max_length=max_len, min_length=min_len)
            st.write(overall_summary)
            
            # Summary statistics
            st.subheader("📊 Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Comments", len(comments))
            with col2:
                avg_words = np.mean([len(comment.split()) for comment in comments])
                st.metric("Avg Words/Comment", f"{avg_words:.1f}")
            with col3:
                total_words = sum([len(comment.split()) for comment in comments])
                st.metric("Total Words", total_words)
        
        tab_index += 1
    
    # Word Cloud Tab
    if create_wordcloud:
        with tab_objects[tab_index]:
            st.subheader("☁️ Word Cloud Visualization")
            
            with st.spinner("Generating word cloud..."):
                wordcloud = analyzer.create_wordcloud(' '.join(comments))
            
            if wordcloud:
                st.image(wordcloud, caption="Word Cloud of Comments", use_container_width=True)
                
                # Download word cloud
                buffer = io.BytesIO()
                wordcloud.save(buffer, format='PNG')
                buffer.seek(0)
                
                st.download_button(
                    label="📥 Download Word Cloud",
                    data=buffer.getvalue(),
                    file_name=f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png"
                )
            else:
                st.error("Failed to generate word cloud!")

if __name__ == "__main__":
    main()
