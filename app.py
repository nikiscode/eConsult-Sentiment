
"""
eConsultation Sentiment Analysis Platform
Main Streamlit application for analyzing stakeholder feedback.
"""

import os
import signal
import threading
import warnings

# Fix signal handling issues for Streamlit
if threading.current_thread() is threading.main_thread():
    # Only set signal handlers in main thread
    try:
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        signal.signal(signal.SIGTERM, signal.SIG_DFL)
    except ValueError:
        # Signal already set, ignore
        pass

# Suppress warnings that can cause signal issues
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

# Set environment variables to prevent signal issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

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
        
        # Main Document Input
        st.subheader("📄 Main Document/Legislation")
        document_input_method = st.radio(
            "Document input method:",
            ["Upload Document", "Manual Entry", "Skip Document"]
        )
        
        if document_input_method == "Upload Document":
            uploaded_doc = st.file_uploader(
                "Upload main document (PDF, TXT, DOCX)",
                type=['pdf', 'txt', 'docx'],
                help="Upload the main legislation/amendment document"
            )
            
            if uploaded_doc is not None:
                try:
                    if uploaded_doc.name.endswith('.txt'):
                        document_text = str(uploaded_doc.read(), "utf-8")
                    else:
                        st.warning("PDF and DOCX support coming soon. Please use TXT format for now.")
                        document_text = None
                    
                    if document_text:
                        st.session_state.main_document = document_text
                        st.session_state.document_analyzer.set_main_document(
                            document_text, uploaded_doc.name
                        )
                        st.success("Document loaded successfully!")
                        
                except Exception as e:
                    st.error(f"Error loading document: {str(e)}")
        
        elif document_input_method == "Manual Entry":
            document_text = st.text_area(
                "Enter main document content:",
                height=200,
                placeholder="Paste the main legislation/amendment text here..."
            )
            
            if st.button("Load Document"):
                if document_text.strip():
                    st.session_state.main_document = document_text
                    st.session_state.document_analyzer.set_main_document(
                        document_text, "Manual Entry Document"
                    )
                    st.success("Document loaded successfully!")
                else:
                    st.warning("Please enter document content.")
        
        else:  # Skip Document
            if st.button("Load Sample Legislation"):
                try:
                    with open("sample_legislation.txt", "r", encoding="utf-8") as f:
                        sample_document = f.read()
                    
                    st.session_state.main_document = sample_document
                    st.session_state.document_analyzer.set_main_document(
                        sample_document, "Sample Companies Amendment Act 2024"
                    )
                    st.success("Sample legislation loaded successfully!")
                    
                except Exception as e:
                    st.error(f"Error loading sample legislation: {str(e)}")
        
        st.markdown("---")
        
        # Data input options
        st.subheader("💬 Stakeholder Comments")
        input_method = st.radio(
            "Choose input method:",
            ["Upload CSV/Excel", "Manual Entry", "Sample Data"]
        )
        
        if input_method == "Upload CSV/Excel":
            uploaded_file = st.file_uploader(
                "Upload your data file",
                type=['csv', 'xlsx', 'xls'],
                help="Upload a CSV or Excel file with stakeholder comments"
            )
            
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.endswith('.csv'):
                        df = pd.read_csv(uploaded_file)
                    else:
                        df = pd.read_excel(uploaded_file)
                    
                    st.session_state.data = df
                    st.success(f"Data loaded successfully! {len(df)} records found.")
                    
                except Exception as e:
                    st.error(f"Error loading file: {str(e)}")
        
        elif input_method == "Manual Entry":
            st.subheader("Enter Comments")
            comments_text = st.text_area(
                "Enter stakeholder comments (one per line):",
                height=200,
                placeholder="Enter each comment on a new line..."
            )
            
            if st.button("Process Comments"):
                if comments_text.strip():
                    comments = [line.strip() for line in comments_text.split('\n') if line.strip()]
                    df = pd.DataFrame({'comments': comments})
                    st.session_state.data = df
                    st.success(f"Processed {len(comments)} comments!")
                else:
                    st.warning("Please enter some comments.")
        
        else:  # Sample Data
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Load Sample Data"):
                    sample_comments = [
                        "The proposed amendment is excellent and will greatly benefit small businesses.",
                        "I have serious concerns about the implementation timeline. It seems rushed.",
                        "The draft legislation needs more clarity on compliance requirements.",
                        "This is a positive step towards digital transformation in governance.",
                        "The penalties mentioned are too harsh and will discourage innovation.",
                        "Good initiative, but more stakeholder consultation is needed.",
                        "The proposed changes will create unnecessary bureaucratic burden.",
                        "I support this amendment as it addresses current market gaps effectively.",
                        "The language used in the draft is too technical for common understanding.",
                        "This legislation will help improve transparency in the sector."
                    ]
                    df = pd.DataFrame({'comments': sample_comments})
                    st.session_state.data = df
                    st.success("Sample data loaded successfully!")
            
            with col2:
                if st.button("Load Sample Legislation Comments"):
                    try:
                        df = pd.read_csv("sample_legislation_comments.csv")
                        st.session_state.data = df
                        st.success("Sample legislation comments loaded successfully!")
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
        st.info("👈 Please select a data input method from the sidebar to begin analysis.")
        
        # Features overview
        st.subheader("🎯 Key Features")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            ### 📊 Sentiment Analysis
            - Individual comment sentiment classification
            - Overall sentiment distribution
            - Confidence score analysis
            - Polarity and subjectivity metrics
            """)
        
        with col2:
            st.markdown("""
            ### 📝 Summary Generation
            - AI-powered text summarization
            - Key insights extraction
            - Multiple summarization algorithms
            - Configurable summary length
            """)
        
        with col3:
            st.markdown("""
            ### ☁️ Word Cloud Visualization
            - Keyword frequency analysis
            - Visual word density representation
            - Customizable word cloud parameters
            - Export capabilities
            """)

def run_analysis(df, analyze_sentiment, document_aware_analysis, generate_summary, create_wordcloud):
    """Run the selected analysis on the data."""
    
    analyzer = st.session_state.analyzer
    
    # Get comments column
    if 'comments' in df.columns:
        comments = df['comments'].dropna().tolist()
    elif 'comment' in df.columns:
        comments = df['comment'].dropna().tolist()
    elif 'text' in df.columns:
        comments = df['text'].dropna().tolist()
    else:
        # Use first text column
        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            comments = df[text_columns[0]].dropna().tolist()
        else:
            st.error("No text column found in the data!")
            return
    
    if not comments:
        st.error("No comments found in the data!")
        return
    
    # Create tabs for different analysis results
    tabs = []
    if analyze_sentiment:
        tabs.append("Basic Sentiment")
    if document_aware_analysis:
        tabs.append("Document-Aware Analysis")
    if generate_summary:
        tabs.append("Summary")
    if create_wordcloud:
        tabs.append("Word Cloud")
    
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
                    positive_count = sum(1 for r in sentiment_results if r.get('label') == 'POSITIVE')
                    st.metric("Positive Comments", positive_count)
                
                with col2:
                    negative_count = sum(1 for r in sentiment_results if r.get('label') == 'NEGATIVE')
                    st.metric("Negative Comments", negative_count)
                
                with col3:
                    neutral_count = sum(1 for r in sentiment_results if r.get('label') == 'NEUTRAL')
                    st.metric("Neutral Comments", neutral_count)
                
                with col4:
                    avg_confidence = np.mean([r.get('confidence', 0) for r in sentiment_results])
                    st.metric("Avg Confidence", f"{avg_confidence:.2f}")
                    
            except Exception as e:
                st.error(f"Error calculating metrics: {str(e)}")
                # Show debug info
                st.write("Debug - First sentiment result:", sentiment_results[0] if sentiment_results else "No results")
            
            # Visualizations
            col1, col2 = st.columns(2)
            
            with col1:
                sentiment_chart = analyzer.create_sentiment_distribution_chart(sentiment_results)
                if sentiment_chart:
                    st.plotly_chart(sentiment_chart, use_container_width=True)
            
            with col2:
                confidence_chart = analyzer.create_confidence_distribution(sentiment_results)
                if confidence_chart:
                    st.plotly_chart(confidence_chart, use_container_width=True)
            
            # Detailed sentiment breakdown
            st.subheader("📈 Detailed Sentiment Breakdown")
            
            # Create detailed analysis
            detailed_df = results_df.copy()
            
            # Fix the confidence categorization to avoid array comparison issues
            def categorize_confidence(conf):
                if conf <= 0.6:
                    return 'Low'
                elif conf <= 0.8:
                    return 'Medium'
                else:
                    return 'High'
            
            detailed_df['confidence_category'] = detailed_df['confidence'].apply(categorize_confidence)
            
            # Group by sentiment and confidence
            sentiment_summary = detailed_df.groupby(['label', 'confidence_category']).size().unstack(fill_value=0)
            
            fig = px.bar(
                sentiment_summary,
                title="Sentiment Distribution by Confidence Level",
                labels={'value': 'Count', 'index': 'Sentiment'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        tab_index += 1
    
    # Document-Aware Analysis Tab
    if document_aware_analysis:
        with tab_objects[tab_index]:
            st.subheader("📄 Document-Aware Analysis")
            
            if not st.session_state.main_document:
                st.warning("⚠️ No main document loaded. Please load a document first to enable document-aware analysis.")
            else:
                st.info(f"📋 Analyzing comments in relation to: **{st.session_state.document_analyzer.document_title}**")
                
                with st.spinner("Performing document-aware analysis..."):
                    document_analyzer = st.session_state.document_analyzer
                    doc_results = document_analyzer.analyze_batch_document_aware(comments)
                
                # Create results DataFrame
                doc_results_df = pd.DataFrame([
                    {
                        'comment_id': r['comment_id'],
                        'comment': r['comment'],
                        'sentiment': r['adjusted_sentiment']['label'],
                        'confidence': r['adjusted_sentiment']['score'],
                        'relevance_score': r['relevance']['relevance_score'],
                        'relevance_category': r['relevance']['relevance_category'],
                        'comment_type': r['comment_type']['primary_type'],
                        'target_section': r['document_context']['target_section'],
                        'is_relevant': r['document_context']['is_relevant'],
                        'is_constructive': r['document_context']['constructive_feedback']
                    }
                    for r in doc_results
                ])
                
                # Display results
                st.dataframe(doc_results_df, use_container_width=True)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    relevant_count = sum(1 for r in doc_results if r['relevance']['relevance_score'] > 0.3)
                    st.metric("Relevant Comments", f"{relevant_count}/{len(comments)}")
                
                with col2:
                    avg_relevance = np.mean([r['relevance']['relevance_score'] for r in doc_results])
                    st.metric("Avg Relevance", f"{avg_relevance:.3f}")
                
                with col3:
                    constructive_count = sum(1 for r in doc_results if r['comment_type']['is_constructive'])
                    st.metric("Constructive Feedback", f"{constructive_count}/{len(comments)}")
                
                with col4:
                    positive_relevant = sum(1 for r in doc_results 
                                         if r['relevance']['relevance_score'] > 0.3 and 
                                         r['adjusted_sentiment']['label'] == 'POSITIVE')
                    st.metric("Positive & Relevant", positive_relevant)
                
                # Visualizations
                st.subheader("📊 Document-Aware Visualizations")
                
                try:
                    visualizations = document_analyzer.create_document_aware_visualizations(doc_results)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if 'relevance_distribution' in visualizations:
                            st.plotly_chart(visualizations['relevance_distribution'], use_container_width=True)
                    
                    with col2:
                        if 'relevance_categories' in visualizations:
                            st.plotly_chart(visualizations['relevance_categories'], use_container_width=True)
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        if 'sentiment_vs_relevance' in visualizations:
                            st.plotly_chart(visualizations['sentiment_vs_relevance'], use_container_width=True)
                    
                    with col4:
                        if 'comment_types' in visualizations:
                            st.plotly_chart(visualizations['comment_types'], use_container_width=True)
                
                except Exception as e:
                    st.error(f"Error creating visualizations: {str(e)}")
                
                # Document Summary
                st.subheader("📝 Document-Focused Summary")
                
                try:
                    doc_summary = document_analyzer.generate_document_summary(doc_results)
                    
                    if doc_summary:
                        st.write(doc_summary['summary'])
                        
                        # Show detailed stats
                        with st.expander("Detailed Statistics"):
                            st.json(doc_summary)
                
                except Exception as e:
                    st.error(f"Error generating document summary: {str(e)}")
                
                # Section-wise Analysis
                st.subheader("📋 Section-wise Analysis")
                
                try:
                    section_feedback = defaultdict(list)
                    for result in doc_results:
                        section = result['relevance']['most_relevant_section']
                        if section and result['relevance']['relevance_score'] > 0.3:
                            section_feedback[section['title']].append(result)
                    
                    if section_feedback:
                        for section_title, feedback in section_feedback.items():
                            with st.expander(f"📄 {section_title} ({len(feedback)} comments)"):
                                sentiment_dist = Counter([f['adjusted_sentiment']['label'] for f in feedback])
                                st.write(f"**Sentiment Distribution:** {dict(sentiment_dist)}")
                                
                                # Show sample comments
                                st.write("**Sample Comments:**")
                                for i, f in enumerate(feedback[:3]):  # Show first 3 comments
                                    st.write(f"{i+1}. {f['comment'][:200]}...")
                    else:
                        st.info("No section-specific feedback found.")
                
                except Exception as e:
                    st.error(f"Error in section-wise analysis: {str(e)}")
        
        tab_index += 1
    
    # Summary Tab
    if generate_summary:
        with tab_objects[tab_index]:
            st.subheader("📝 Summary Generation")
            
            # Individual summaries
            st.subheader("Individual Comment Summaries")
            
            summary_results = []
            # Process all comments, not just first 10
            for i, comment in enumerate(comments):
                if i % 5 == 0:  # Update progress every 5 comments
                    st.progress((i + 1) / len(comments))
                summary = analyzer.generate_summary(comment)
                summary_results.append({
                    'comment_id': i + 1,
                    'original_comment': comment,
                    'summary': summary
                })
            
            # Display summaries
            for result in summary_results:
                with st.expander(f"Comment {result['comment_id']}"):
                    st.write("**Original:**")
                    st.write(result['original_comment'])
                    st.write("**Summary:**")
                    st.write(result['summary'])
            
            # Overall summary
            st.subheader("Overall Summary")
            st.info("Generating overall summary from all comments...")
            
            # Create a comprehensive summary from all comments
            all_comments_text = ' '.join(comments)
            
            # Generate summary with appropriate length based on number of comments
            if len(comments) > 50:
                max_len, min_len = 300, 150
            elif len(comments) > 20:
                max_len, min_len = 250, 120
            else:
                max_len, min_len = 200, 100
            
            overall_summary = analyzer.generate_summary(all_comments_text, max_length=max_len, min_length=min_len)
            st.write(overall_summary)
            
            # Additional insights
            st.subheader("Summary Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Comments", len(comments))
            with col2:
                avg_words = np.mean([len(comment.split()) for comment in comments])
                st.metric("Avg Words/Comment", f"{avg_words:.1f}")
            with col3:
                total_words = sum(len(comment.split()) for comment in comments)
                st.metric("Total Words", total_words)
        
        tab_index += 1
    
    # Word Cloud Tab
    if create_wordcloud:
        with tab_objects[tab_index]:
            st.subheader("☁️ Word Cloud Analysis")
            
            # Word cloud parameters
            col1, col2 = st.columns(2)
            
            with col1:
                max_words = st.slider("Maximum Words", 50, 200, 100)
            
            with col2:
                colormap = st.selectbox(
                    "Color Scheme",
                    ['viridis', 'plasma', 'inferno', 'magma', 'Blues', 'Reds', 'Greens']
                )
            
            # Generate word cloud
            with st.spinner("Generating word cloud..."):
                wordcloud = analyzer.create_word_cloud(comments, max_words=max_words)
                
                if wordcloud:
                    # Display word cloud
                    fig, ax = plt.subplots(figsize=(12, 6))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    ax.set_title('Word Cloud - Stakeholder Comments', fontsize=16, pad=20)
                    
                    st.pyplot(fig)
                    
                    # Keyword frequency
                    st.subheader("📊 Keyword Frequency Analysis")
                    keywords = analyzer.get_keyword_frequency(comments, top_n=20)
                    
                    if keywords:
                        # Create keyword frequency chart
                        keyword_df = pd.DataFrame(list(keywords.items()), columns=['Word', 'Frequency'])
                        
                        fig = px.bar(
                            keyword_df,
                            x='Frequency',
                            y='Word',
                            orientation='h',
                            title="Top 20 Keywords",
                            labels={'Frequency': 'Frequency', 'Word': 'Keywords'}
                        )
                        fig.update_layout(height=500, yaxis={'categoryorder': 'total ascending'})
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Display keyword table
                        st.dataframe(keyword_df, use_container_width=True)
        
        tab_index += 1
    
    # Export functionality
    st.subheader("📤 Export Results")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Export to CSV"):
            if analyze_sentiment and 'results_df' in locals():
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
    
    with col2:
        if st.button("Export Summary Report"):
            report = generate_report(comments, sentiment_results if analyze_sentiment else None)
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    with col3:
        if st.button("Export Word Cloud"):
            if create_wordcloud and wordcloud:
                # Save word cloud as image
                wordcloud.to_file("wordcloud.png")
                with open("wordcloud.png", "rb") as file:
                    st.download_button(
                        label="Download Word Cloud",
                        data=file.read(),
                        file_name=f"wordcloud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png"
                    )

def generate_report(comments, sentiment_results):
    """Generate a comprehensive analysis report."""
    report = []
    report.append("eConsultation Sentiment Analysis Report")
    report.append("=" * 50)
    report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Total Comments Analyzed: {len(comments)}")
    report.append("")
    
    if sentiment_results:
        report.append("SENTIMENT ANALYSIS SUMMARY")
        report.append("-" * 30)
        
        positive_count = sum(1 for r in sentiment_results if r['label'] == 'POSITIVE')
        negative_count = sum(1 for r in sentiment_results if r['label'] == 'NEGATIVE')
        neutral_count = sum(1 for r in sentiment_results if r['label'] == 'NEUTRAL')
        
        report.append(f"Positive Comments: {positive_count} ({positive_count/len(sentiment_results)*100:.1f}%)")
        report.append(f"Negative Comments: {negative_count} ({negative_count/len(sentiment_results)*100:.1f}%)")
        report.append(f"Neutral Comments: {neutral_count} ({neutral_count/len(sentiment_results)*100:.1f}%)")
        report.append("")
        
        avg_confidence = np.mean([r['confidence'] for r in sentiment_results])
        report.append(f"Average Confidence Score: {avg_confidence:.3f}")
        report.append("")
    
    report.append("DETAILED ANALYSIS")
    report.append("-" * 20)
    report.append("This report provides insights into stakeholder feedback sentiment,")
    report.append("helping identify key themes and overall reception of proposed amendments.")
    report.append("")
    report.append("Recommendations:")
    report.append("1. Focus on addressing concerns raised in negative feedback")
    report.append("2. Leverage positive feedback for communication strategies")
    report.append("3. Use neutral feedback for clarification and improvement")
    
    return "\n".join(report)

if __name__ == "__main__":
    main()
