"""
Configuration file for eConsultation Sentiment Analysis Platform
"""

# Model Configuration
MODEL_CONFIG = {
    'sentiment_model': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
    'summarization_model': 'facebook/bart-large-cnn',
    'device': 'auto',  # 'auto', 'cpu', 'cuda'
    'batch_size': 8,
    'max_length': 512
}

# Analysis Configuration
ANALYSIS_CONFIG = {
    'default_max_words': 100,
    'default_summary_length': 150,
    'default_min_summary_length': 50,
    'confidence_threshold': 0.6,
    'max_comments_for_summary': 1000
}

# UI Configuration
UI_CONFIG = {
    'page_title': 'eConsultation Sentiment Analysis',
    'page_icon': '📊',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'theme': 'light'
}

# Export Configuration
EXPORT_CONFIG = {
    'supported_formats': ['csv', 'txt', 'png'],
    'default_filename_prefix': 'econsultation_analysis',
    'include_timestamp': True
}

# Word Cloud Configuration
WORDCLOUD_CONFIG = {
    'width': 800,
    'height': 400,
    'background_color': 'white',
    'colormap': 'viridis',
    'relative_scaling': 0.5,
    'random_state': 42,
    'max_font_size': 100,
    'min_font_size': 10
}

# Color Schemes for Visualizations
COLOR_SCHEMES = {
    'sentiment': {
        'POSITIVE': '#2E8B57',
        'NEGATIVE': '#DC143C',
        'NEUTRAL': '#FFD700'
    },
    'confidence': {
        'high': '#2E8B57',
        'medium': '#FFD700',
        'low': '#DC143C'
    }
}

# Stop Words (can be extended)
STOP_WORDS = [
    'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did',
    'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that',
    'these', 'those', 'a', 'an', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me',
    'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their'
]

# File Upload Configuration
UPLOAD_CONFIG = {
    'max_file_size': 50,  # MB
    'allowed_extensions': ['csv', 'xlsx', 'xls'],
    'encoding': 'utf-8'
}

# Performance Configuration
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 3600,  # seconds
    'max_workers': 4,
    'chunk_size': 100
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'app.log'
}
