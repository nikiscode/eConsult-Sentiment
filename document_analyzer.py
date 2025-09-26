"""
Document-Aware Sentiment Analysis Module
This module provides sentiment analysis and classification based on the main document/legislation content.
"""

import os
import warnings

# Set environment variables to prevent threading issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

# Suppress warnings
warnings.filterwarnings('ignore')

import pandas as pd
import numpy as np
import streamlit as st
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re
from collections import Counter, defaultdict
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

class DocumentAwareAnalyzer:
    """
    Document-aware sentiment analysis class that analyzes comments in relation to specific legislation.
    """
    
    def __init__(self):
        """Initialize the document-aware analyzer."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_models()
        self.main_document = None
        self.document_sections = None
        self.document_embeddings = None
        
    def _load_models(self):
        """Load pre-trained models for document analysis."""
        try:
            # Load sentiment analysis model
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Initialize TF-IDF vectorizer for semantic similarity with better parameters
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=2000,
                stop_words='english',
                ngram_range=(1, 3),  # Include trigrams for better context
                min_df=1,  # Include all terms
                max_df=0.95,  # Exclude very common terms
                sublinear_tf=True  # Use sublinear TF scaling
            )
            
            # Load summarization model
            self.summarizer_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            st.success("Document-aware models loaded successfully!")
            
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            # Fallback models
            self.sentiment_pipeline = pipeline("sentiment-analysis")
            self.tfidf_vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            self.summarizer_pipeline = pipeline("summarization")
    
    def set_main_document(self, document_text, document_title="Main Document"):
        """
        Set the main document/legislation for analysis.
        
        Args:
            document_text (str): The main document content
            document_title (str): Title of the document
        """
        self.main_document = document_text
        self.document_title = document_title
        
        # Extract sections from the document
        self.document_sections = self._extract_document_sections(document_text)
        
        # Create TF-IDF embeddings for document sections
        if self.document_sections:
            section_texts = [section['content'] for section in self.document_sections]
            self.document_embeddings = self.tfidf_vectorizer.fit_transform(section_texts)
        
        st.success(f"Main document '{document_title}' loaded with {len(self.document_sections)} sections")
    
    def _extract_document_sections(self, document_text):
        """
        Extract sections from the document based on common patterns.
        
        Args:
            document_text (str): Document content
            
        Returns:
            list: List of document sections
        """
        sections = []
        
        # Enhanced section patterns for legal documents
        section_patterns = [
            # Pattern 1: Section/Clause/Article with numbers
            r'(?:Section|Clause|Article|Chapter|Part)\s+(\d+(?:\.\d+)*)[:\.]?\s*(.*?)(?=(?:Section|Clause|Article|Chapter|Part)\s+\d+|$)',
            # Pattern 2: Numbered sections
            r'(\d+(?:\.\d+)*)[:\.]\s*(.*?)(?=\d+(?:\.\d+)*[:\.]|$)',
            # Pattern 3: Amendment patterns
            r'Amendment of section (\d+)[:\.]?\s*(.*?)(?=Amendment of section \d+|$)',
            # Pattern 4: Subsection patterns
            r'In section (\d+)[:\.]?\s*(.*?)(?=In section \d+|$)',
            # Pattern 5: Capitalized headings
            r'([A-Z][A-Z\s]+)[:\.]\s*(.*?)(?=[A-Z][A-Z\s]+[:\.]|$)'
        ]
        
        for pattern in section_patterns:
            matches = re.finditer(pattern, document_text, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    section_id = match.group(1).strip()
                    section_content = match.group(2).strip()
                    
                    if len(section_content) > 50:  # Only include substantial sections
                        sections.append({
                            'id': section_id,
                            'title': f"Section {section_id}",
                            'content': section_content,
                            'word_count': len(section_content.split())
                        })
        
        # If no sections found, create artificial sections
        if not sections:
            sentences = sent_tokenize(document_text)
            chunk_size = max(5, len(sentences) // 10)  # Create ~10 sections
            
            for i in range(0, len(sentences), chunk_size):
                chunk = sentences[i:i + chunk_size]
                if len(chunk) > 0:
                    sections.append({
                        'id': f"Part_{i//chunk_size + 1}",
                        'title': f"Part {i//chunk_size + 1}",
                        'content': ' '.join(chunk),
                        'word_count': len(' '.join(chunk).split())
                    })
        
        return sections
    
    def analyze_comment_relevance(self, comment):
        """
        Analyze how relevant a comment is to the main document.
        
        Args:
            comment (str): Comment text
            
        Returns:
            dict: Relevance analysis results
        """
        if self.document_embeddings is None or self.document_sections is None or len(self.document_sections) == 0:
            return {
                'relevance_score': 0.0,
                'most_relevant_section': None,
                'relevance_category': 'Unknown'
            }
        
        # Get comment embedding using TF-IDF
        comment_embedding = self.tfidf_vectorizer.transform([comment])
        
        # Calculate similarity with document sections
        similarities = cosine_similarity(comment_embedding, self.document_embeddings)[0]
        
        # Enhanced relevance scoring with keyword matching
        comment_lower = comment.lower()
        keyword_boost = 0.0
        
        # Check for legal/legislation keywords
        legal_keywords = ['section', 'clause', 'article', 'amendment', 'act', 'law', 'regulation', 
                         'provision', 'requirement', 'compliance', 'penalty', 'fine', 'director', 
                         'company', 'board', 'shareholder', 'csr', 'remuneration', 'disqualification']
        
        for keyword in legal_keywords:
            if keyword in comment_lower:
                keyword_boost += 0.1
        
        # Check for section numbers mentioned in comments
        import re
        section_matches = re.findall(r'section\s+(\d+)', comment_lower)
        if section_matches:
            keyword_boost += 0.2 * len(section_matches)
        
        # Apply keyword boost to similarity scores
        similarities = similarities + keyword_boost
        
        # Find most relevant section
        max_similarity_idx = np.argmax(similarities)
        max_similarity = similarities[max_similarity_idx]
        most_relevant_section = self.document_sections[max_similarity_idx]
        
        # Categorize relevance
        if max_similarity > 0.7:
            relevance_category = 'Highly Relevant'
        elif max_similarity > 0.5:
            relevance_category = 'Moderately Relevant'
        elif max_similarity > 0.3:
            relevance_category = 'Somewhat Relevant'
        else:
            relevance_category = 'Low Relevance'
        
        return {
            'relevance_score': float(max_similarity),
            'most_relevant_section': most_relevant_section,
            'relevance_category': relevance_category,
            'all_similarities': similarities.tolist()
        }
    
    def classify_comment_type(self, comment):
        """
        Classify the type of comment based on content analysis.
        
        Args:
            comment (str): Comment text
            
        Returns:
            dict: Comment classification results
        """
        comment_lower = comment.lower()
        
        # Define classification patterns with more comprehensive keywords
        classifications = {
            'Support': [
                'support', 'agree', 'approve', 'endorse', 'favor', 'good', 'excellent',
                'beneficial', 'positive', 'welcome', 'appreciate', 'commend', 'excellent',
                'great', 'wonderful', 'fantastic', 'outstanding', 'praise', 'laud',
                'commendable', 'admirable', 'valuable', 'useful', 'helpful'
            ],
            'Opposition': [
                'oppose', 'disagree', 'against', 'object', 'concern', 'problem', 'issue',
                'negative', 'harmful', 'damaging', 'unacceptable', 'reject', 'criticize',
                'criticism', 'flawed', 'inadequate', 'insufficient', 'worried', 'worrisome',
                'problematic', 'troubling', 'serious concern', 'major issue'
            ],
            'Suggestion': [
                'suggest', 'recommend', 'propose', 'recommendation', 'improvement',
                'modify', 'change', 'amend', 'revise', 'clarify', 'should', 'could',
                'might', 'consider', 'alternative', 'better', 'enhance', 'strengthen',
                'improve', 'refine', 'adjust', 'update'
            ],
            'Question': [
                'question', 'ask', 'wonder', 'unclear', 'confused', 'explain',
                'how', 'what', 'why', 'when', 'where', '?', 'unclear', 'confusion',
                'understand', 'comprehension', 'clarification needed', 'please explain'
            ],
            'Clarification': [
                'clarify', 'explain', 'define', 'specify', 'detail', 'elaborate',
                'understand', 'comprehension', 'meaning', 'interpretation', 'scope',
                'extent', 'coverage', 'application', 'implementation'
            ],
            'Implementation': [
                'implement', 'execute', 'apply', 'enforce', 'timeline', 'schedule',
                'process', 'procedure', 'mechanism', 'rollout', 'deployment', 'phasing',
                'stages', 'steps', 'approach', 'methodology', 'framework'
            ]
        }
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in classifications.items():
            score = sum(1 for keyword in keywords if keyword in comment_lower)
            category_scores[category] = score
        
        # Find primary classification
        primary_category = max(category_scores, key=category_scores.get)
        primary_score = category_scores[primary_category]
        
        # Determine confidence
        total_keywords = sum(category_scores.values())
        confidence = primary_score / total_keywords if total_keywords > 0 else 0
        
        return {
            'primary_type': primary_category,
            'confidence': confidence,
            'all_scores': category_scores,
            'is_constructive': primary_category in ['Suggestion', 'Question', 'Clarification']
        }
    
    def analyze_document_aware_sentiment(self, comment):
        """
        Analyze sentiment with awareness of the main document context.
        
        Args:
            comment (str): Comment text
            
        Returns:
            dict: Document-aware sentiment analysis results
        """
        # Basic sentiment analysis
        sentiment_result = self.sentiment_pipeline(comment)
        
        # Normalize label names to ensure consistency
        label = sentiment_result[0]['label']
        if label in ['LABEL_2', 'POSITIVE']:
            normalized_label = 'POSITIVE'
        elif label in ['LABEL_0', 'NEGATIVE']:
            normalized_label = 'NEGATIVE'
        elif label in ['LABEL_1', 'NEUTRAL']:
            normalized_label = 'NEUTRAL'
        else:
            normalized_label = label  # Keep original if not recognized
        
        # Update the sentiment result with normalized label
        sentiment_result[0]['label'] = normalized_label
        
        # Relevance analysis
        relevance = self.analyze_comment_relevance(comment)
        
        # Comment type classification
        comment_type = self.classify_comment_type(comment)
        
        # Context-aware sentiment adjustment
        base_sentiment = sentiment_result[0]
        adjusted_sentiment = self._adjust_sentiment_for_context(
            base_sentiment, relevance, comment_type
        )
        
        return {
            'base_sentiment': base_sentiment,
            'adjusted_sentiment': adjusted_sentiment,
            'relevance': relevance,
            'comment_type': comment_type,
            'document_context': {
                'is_relevant': relevance['relevance_score'] > 0.3,
                'target_section': relevance['most_relevant_section']['title'] if relevance['most_relevant_section'] else None,
                'constructive_feedback': comment_type['is_constructive']
            }
        }
    
    def _adjust_sentiment_for_context(self, base_sentiment, relevance, comment_type):
        """
        Adjust sentiment based on document context and comment type.
        
        Args:
            base_sentiment (dict): Base sentiment result
            relevance (dict): Relevance analysis
            comment_type (dict): Comment type classification
            
        Returns:
            dict: Adjusted sentiment result
        """
        label = base_sentiment['label']
        confidence = base_sentiment['score']
        
        # Adjust confidence based on relevance
        relevance_factor = relevance['relevance_score']
        adjusted_confidence = confidence * (0.5 + 0.5 * relevance_factor)
        
        # Adjust sentiment based on comment type
        if comment_type['primary_type'] == 'Support' and label == 'POSITIVE':
            adjusted_confidence = min(1.0, adjusted_confidence * 1.2)
        elif comment_type['primary_type'] == 'Opposition' and label == 'NEGATIVE':
            adjusted_confidence = min(1.0, adjusted_confidence * 1.2)
        elif comment_type['primary_type'] in ['Question', 'Clarification']:
            # Questions and clarifications are often neutral regardless of sentiment
            if label != 'NEUTRAL':
                adjusted_confidence = adjusted_confidence * 0.8
        
        return {
            'label': label,
            'score': adjusted_confidence,
            'original_score': confidence,
            'adjustment_factor': adjusted_confidence / confidence if confidence > 0 else 1.0
        }
    
    def analyze_batch_document_aware(self, comments):
        """
        Analyze a batch of comments with document awareness.
        
        Args:
            comments (list): List of comments
            
        Returns:
            list: List of document-aware analysis results
        """
        results = []
        
        for i, comment in enumerate(comments):
            if i % 10 == 0:
                st.progress((i + 1) / len(comments))
            
            result = self.analyze_document_aware_sentiment(comment)
            result['comment_id'] = i + 1
            result['comment'] = comment
            results.append(result)
        
        return results
    
    def generate_document_summary(self, comments_results):
        """
        Generate a summary focused on the main document aspects.
        
        Args:
            comments_results (list): Results from document-aware analysis
            
        Returns:
            dict: Document-focused summary
        """
        if not comments_results:
            return {}
        
        # Group comments by relevance and sentiment
        highly_relevant = [r for r in comments_results if r['relevance']['relevance_score'] > 0.7]
        moderately_relevant = [r for r in comments_results if 0.5 < r['relevance']['relevance_score'] <= 0.7]
        
        # Analyze sentiment distribution for relevant comments
        relevant_comments = [r for r in comments_results if r['relevance']['relevance_score'] > 0.3]
        
        if not relevant_comments:
            return {
                'summary': "No highly relevant comments found for the main document.",
                'relevance_stats': {'total_comments': len(comments_results), 'relevant_comments': 0}
            }
        
        # Sentiment analysis for relevant comments
        sentiment_counts = Counter([r['adjusted_sentiment']['label'] for r in relevant_comments])
        
        # Comment type analysis
        type_counts = Counter([r['comment_type']['primary_type'] for r in relevant_comments])
        
        # Section-wise analysis
        section_feedback = defaultdict(list)
        for result in relevant_comments:
            section = result['relevance']['most_relevant_section']
            if section:
                section_feedback[section['title']].append(result)
        
        # Generate summary text
        summary_parts = []
        
        summary_parts.append(f"Analysis of {len(comments_results)} comments regarding '{self.document_title}':")
        summary_parts.append(f"- {len(relevant_comments)} comments ({len(relevant_comments)/len(comments_results)*100:.1f}%) are relevant to the document")
        
        if sentiment_counts:
            summary_parts.append(f"- Sentiment distribution: {dict(sentiment_counts)}")
        
        if type_counts:
            summary_parts.append(f"- Comment types: {dict(type_counts)}")
        
        if section_feedback:
            summary_parts.append(f"- Most discussed sections: {list(section_feedback.keys())[:5]}")
        
        return {
            'summary': '\n'.join(summary_parts),
            'relevance_stats': {
                'total_comments': len(comments_results),
                'relevant_comments': len(relevant_comments),
                'highly_relevant': len(highly_relevant),
                'moderately_relevant': len(moderately_relevant)
            },
            'sentiment_distribution': dict(sentiment_counts),
            'comment_types': dict(type_counts),
            'section_feedback': dict(section_feedback)
        }
    
    def create_document_aware_visualizations(self, results):
        """
        Create visualizations specific to document-aware analysis.
        
        Args:
            results (list): Document-aware analysis results
            
        Returns:
            dict: Visualization objects
        """
        import plotly.express as px
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        visualizations = {}
        
        # Relevance distribution
        relevance_scores = [r['relevance']['relevance_score'] for r in results]
        relevance_categories = [r['relevance']['relevance_category'] for r in results]
        
        fig_relevance = px.histogram(
            x=relevance_scores,
            nbins=20,
            title="Comment Relevance to Main Document",
            labels={'x': 'Relevance Score', 'y': 'Count'}
        )
        visualizations['relevance_distribution'] = fig_relevance
        
        # Relevance categories pie chart
        category_counts = Counter(relevance_categories)
        fig_categories = px.pie(
            values=list(category_counts.values()),
            names=list(category_counts.keys()),
            title="Relevance Categories Distribution"
        )
        visualizations['relevance_categories'] = fig_categories
        
        # Sentiment vs Relevance scatter plot
        sentiments = [r['adjusted_sentiment']['label'] for r in results]
        fig_scatter = px.scatter(
            x=relevance_scores,
            y=[r['adjusted_sentiment']['score'] for r in results],
            color=sentiments,
            title="Sentiment vs Relevance",
            labels={'x': 'Relevance Score', 'y': 'Sentiment Confidence'}
        )
        visualizations['sentiment_vs_relevance'] = fig_scatter
        
        # Comment types distribution
        comment_types = [r['comment_type']['primary_type'] for r in results]
        type_counts = Counter(comment_types)
        fig_types = px.bar(
            x=list(type_counts.keys()),
            y=list(type_counts.values()),
            title="Comment Types Distribution"
        )
        visualizations['comment_types'] = fig_types
        
        return visualizations
