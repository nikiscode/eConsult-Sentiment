"""
Sentiment Analysis Module for eConsultation Platform
This module provides comprehensive sentiment analysis, summarization, and visualization capabilities.
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
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import nltk
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.text_rank import TextRankSummarizer
from sumy.summarizers.lsa import LsaSummarizer
import re
from collections import Counter

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('vader_lexicon', quiet=True)
except:
    pass

class SentimentAnalyzer:
    """
    Comprehensive sentiment analysis class for eConsultation feedback analysis.
    """
    
    def __init__(self):
        """Initialize the sentiment analyzer with pre-trained models."""
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_models()
        
    def _load_models(self):
        """Load pre-trained models for sentiment analysis and summarization."""
        try:
            # Load sentiment analysis model
            model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model_name,
                tokenizer=model_name,
                device=0 if torch.cuda.is_available() else -1
            )
            
            # Load summarization model
            self.summarizer_pipeline = pipeline(
                "summarization",
                model="facebook/bart-large-cnn",
                device=0 if torch.cuda.is_available() else -1
            )
            
            st.success("Models loaded successfully!")
            
        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            # Fallback to simpler models
            self.sentiment_pipeline = pipeline("sentiment-analysis")
            self.summarizer_pipeline = pipeline("summarization")
    
    def analyze_sentiment(self, text):
        """
        Analyze sentiment of a single text.
        
        Args:
            text (str): Input text to analyze
            
        Returns:
            dict: Sentiment analysis results
        """
        try:
            # Use transformer model
            result = self.sentiment_pipeline(text)
            
            # Also use TextBlob for additional insights
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Normalize label names to ensure consistency
            label = result[0]['label']
            if label in ['LABEL_2', 'POSITIVE']:
                normalized_label = 'POSITIVE'
            elif label in ['LABEL_0', 'NEGATIVE']:
                normalized_label = 'NEGATIVE'
            elif label in ['LABEL_1', 'NEUTRAL']:
                normalized_label = 'NEUTRAL'
            else:
                normalized_label = label  # Keep original if not recognized
            
            return {
                'label': normalized_label,
                'confidence': result[0]['score'],
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment_score': polarity  # Normalized score
            }
        except Exception as e:
            st.error(f"Error in sentiment analysis: {str(e)}")
            return {
                'label': 'NEUTRAL',
                'confidence': 0.5,
                'polarity': 0.0,
                'subjectivity': 0.5,
                'sentiment_score': 0.0
            }
    
    def analyze_batch_sentiments(self, texts):
        """
        Analyze sentiments for a batch of texts.
        
        Args:
            texts (list): List of texts to analyze
            
        Returns:
            list: List of sentiment analysis results
        """
        results = []
        for i, text in enumerate(texts):
            if i % 10 == 0:
                st.progress((i + 1) / len(texts))
            results.append(self.analyze_sentiment(text))
        return results
    
    def generate_summary(self, text, max_length=150, min_length=50):
        """
        Generate summary of the text.
        
        Args:
            text (str): Input text to summarize
            max_length (int): Maximum length of summary
            min_length (int): Minimum length of summary
            
        Returns:
            str: Generated summary
        """
        try:
            # Clean and prepare text
            cleaned_text = self._clean_text(text)
            
            if len(cleaned_text.split()) < 50:
                return cleaned_text  # Return original if too short
            
            # Use transformer model for summarization
            summary = self.summarizer_pipeline(
                cleaned_text,
                max_length=max_length,
                min_length=min_length,
                do_sample=False
            )
            
            return summary[0]['summary_text']
            
        except Exception as e:
            st.error(f"Error in summarization: {str(e)}")
            # Fallback to extractive summarization
            return self._extractive_summary(text)
    
    def _extractive_summary(self, text, sentences_count=3):
        """
        Generate extractive summary using TextRank.
        
        Args:
            text (str): Input text
            sentences_count (int): Number of sentences in summary
            
        Returns:
            str: Extractive summary
        """
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summarizer = TextRankSummarizer()
            summary_sentences = summarizer(parser.document, sentences_count)
            return ' '.join([str(sentence) for sentence in summary_sentences])
        except:
            # Simple fallback - return first few sentences
            sentences = text.split('.')
            return '. '.join(sentences[:sentences_count]) + '.'
    
    def _clean_text(self, text):
        """
        Clean and preprocess text.
        
        Args:
            text (str): Input text
            
        Returns:
            str: Cleaned text
        """
        # Remove extra whitespaces
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?;:]', '', text)
        return text.strip()
    
    def create_word_cloud(self, texts, max_words=100):
        """
        Create word cloud from texts.
        
        Args:
            texts (list): List of texts
            max_words (int): Maximum number of words in word cloud
            
        Returns:
            WordCloud: Word cloud object
        """
        try:
            # Combine all texts
            combined_text = ' '.join(texts)
            
            # Clean text
            cleaned_text = self._clean_text(combined_text)
            
            # Create word cloud
            wordcloud = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=max_words,
                colormap='viridis',
                relative_scaling=0.5,
                random_state=42
            ).generate(cleaned_text)
            
            return wordcloud
            
        except Exception as e:
            st.error(f"Error creating word cloud: {str(e)}")
            return None
    
    def get_keyword_frequency(self, texts, top_n=20):
        """
        Get keyword frequency analysis.
        
        Args:
            texts (list): List of texts
            top_n (int): Number of top keywords to return
            
        Returns:
            dict: Keyword frequency dictionary
        """
        try:
            # Combine and clean texts
            combined_text = ' '.join(texts)
            cleaned_text = self._clean_text(combined_text).lower()
            
            # Simple word frequency (can be enhanced with POS tagging)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text)
            
            # Remove common stop words
            stop_words = set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'])
            words = [word for word in words if word not in stop_words]
            
            # Count frequencies
            word_freq = Counter(words)
            
            return dict(word_freq.most_common(top_n))
            
        except Exception as e:
            st.error(f"Error in keyword analysis: {str(e)}")
            return {}
    
    def create_sentiment_distribution_chart(self, sentiment_results):
        """
        Create sentiment distribution visualization.
        
        Args:
            sentiment_results (list): List of sentiment analysis results
            
        Returns:
            plotly.graph_objects.Figure: Sentiment distribution chart
        """
        try:
            # Extract labels and create counts
            labels = [result['label'] for result in sentiment_results]
            label_counts = Counter(labels)
            
            # Create pie chart
            fig = px.pie(
                values=list(label_counts.values()),
                names=list(label_counts.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'POSITIVE': '#2E8B57',
                    'NEGATIVE': '#DC143C',
                    'NEUTRAL': '#FFD700',
                    'LABEL_2': '#2E8B57',  # Handle original labels
                    'LABEL_0': '#DC143C',
                    'LABEL_1': '#FFD700'
                }
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400)
            
            return fig
            
        except Exception as e:
            st.error(f"Error creating sentiment chart: {str(e)}")
            return None
    
    def create_confidence_distribution(self, sentiment_results):
        """
        Create confidence score distribution chart.
        
        Args:
            sentiment_results (list): List of sentiment analysis results
            
        Returns:
            plotly.graph_objects.Figure: Confidence distribution chart
        """
        try:
            confidences = [result['confidence'] for result in sentiment_results]
            
            fig = px.histogram(
                x=confidences,
                nbins=20,
                title="Confidence Score Distribution",
                labels={'x': 'Confidence Score', 'y': 'Count'}
            )
            
            fig.update_layout(height=400)
            return fig
            
        except Exception as e:
            st.error(f"Error creating confidence chart: {str(e)}")
            return None
