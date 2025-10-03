 # e-Consultation Sentiment Analysis Platform

A comprehensive AI-powered sentiment analysis platform designed for analyzing stakeholder feedback in the eConsultation module of MCA21 portal. This solution helps government officials efficiently analyze large volumes of comments and suggestions on proposed amendments and draft legislations.

## 🎯 Problem Statement

The eConsultation module allows stakeholders to submit comments on proposed amendments/draft legislations through the MCA21 portal. When substantial volumes of comments are received, there's a risk of certain observations being inadvertently overlooked or inadequately analyzed. This platform leverages AI-assisted tools to ensure all remarks are duly considered and systematically analyzed.

## ✨ Key Features

### 📊 Document-Aware Sentiment Analysis
- **Context-Aware Analysis**: Analyze comments in relation to specific legislation/amendments
- **Relevance Scoring**: Measure how relevant each comment is to the main document
- **Section Mapping**: Identify which sections of the legislation comments relate to
- **Comment Classification**: Categorize comments as Support, Opposition, Suggestion, Question, etc.
- **Adjusted Sentiment**: Sentiment analysis adjusted for document context and relevance

### 📊 Basic Sentiment Analysis
- **Individual Comment Analysis**: Classify each comment as Positive, Negative, or Neutral
- **Confidence Scoring**: Provide confidence levels for sentiment predictions
- **Polarity & Subjectivity**: Advanced sentiment metrics using TextBlob
- **Batch Processing**: Analyze multiple comments simultaneously
- **Visual Distribution**: Interactive charts showing sentiment distribution

### 📝 Summary Generation
- **AI-Powered Summarization**: Using Facebook's BART model for accurate summaries
- **Individual Summaries**: Generate concise summaries for each comment
- **Overall Summary**: Create comprehensive summary of all feedback
- **Configurable Length**: Adjustable summary length parameters
- **Fallback Algorithms**: Multiple summarization methods for reliability

### ☁️ Word Cloud Visualization
- **Keyword Extraction**: Identify most frequently used terms
- **Visual Representation**: Create beautiful word clouds showing term density
- **Customizable Parameters**: Adjust word count, color schemes, and styling
- **Frequency Analysis**: Detailed keyword frequency charts
- **Export Capabilities**: Download word clouds as images

### 📈 Advanced Analytics
- **Confidence Distribution**: Analyze prediction confidence across comments
- **Sentiment Trends**: Identify patterns in stakeholder feedback
- **Keyword Insights**: Understand common themes and concerns
- **Export Options**: CSV, reports, and image downloads

## 🚀 Technology Stack

### Core AI Models
- **Sentiment Analysis**: `cardiffnlp/twitter-roberta-base-sentiment-latest`
- **Text Summarization**: `facebook/bart-large-cnn`
- **Additional Libraries**: TextBlob, NLTK, spaCy

### Framework & Visualization
- **Web Framework**: Streamlit
- **Visualization**: Plotly, Matplotlib, Seaborn
- **Word Cloud**: WordCloud library
- **Data Processing**: Pandas, NumPy

### Performance & Scalability
- **GPU Support**: Automatic CUDA detection for faster processing
- **Batch Processing**: Efficient handling of large comment volumes
- **Memory Optimization**: Optimized for large datasets

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional, for cloning)

### Setup Instructions

1. **Clone or Download the Repository**
   ```bash
   git clone <repository-url>
   cd sentAna
   ```

2. **Create Virtual Environment (Recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download Additional NLTK Data**
   ```bash
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

## 🏃‍♂️ Quick Start

### Installation

**For Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

**For Windows:**
```cmd
install.bat
```

### Running the Application

**For Windows (Signal Fix Required):**
```cmd
# Method 1: Use Windows batch file (recommended)
 

# Method 2: Use Windows Python script
python start_windows.py

# Method 3: Use Windows-optimized app
streamlit run app_windows.py

# Method 4: Direct run (may have signal issues)
streamlit run app.py
```

**For Linux/macOS:**
```bash
streamlit run app.py
```

### Access the Application
- Open your browser and navigate to `http://localhost:8501`
- The application will automatically load AI models (may take a few minutes on first run)

### 🔧 Windows Signal Fix

If you encounter "signal only works in main thread" error on Windows:

1. **Use the Windows batch file** (recommended):
   ```cmd
   start_windows.bat
   ```

2. **Use the Windows Python script**:
   ```cmd
   python start_windows.py
   ```

3. **Use the Windows-optimized app**:
   ```cmd
   streamlit run app_windows.py
   ```

These methods automatically set the required environment variables to prevent threading and signal issues on Windows.

### Using the Platform

1. **Data Input Options**:
   - **Upload CSV/Excel**: Upload files with stakeholder comments
   - **Manual Entry**: Type comments directly into the interface
   - **Sample Data**: Use built-in sample data for testing

2. **Analysis Configuration**:
   - Select analysis options (Sentiment, Summary, Word Cloud)
   - Configure parameters as needed
   - Click "Run Analysis"

3. **Review Results**:
   - Navigate through different tabs for various analyses
   - Export results in multiple formats
   - Download comprehensive reports

## 📊 Data Format Requirements

### CSV/Excel File Format
Your data file should contain at least one column with stakeholder comments. Supported column names:
- `comments`
- `comment`
- `text`
- Any text column (first text column will be used automatically)

### Example Data Structure
```csv
comments
"The proposed amendment is excellent and will benefit small businesses."
"I have concerns about the implementation timeline."
"This legislation needs more clarity on compliance requirements."
```

## 🔧 Configuration Options

### Sentiment Analysis Parameters
- **Model**: Uses RoBERTa-based sentiment analysis model
- **Confidence Thresholds**: Configurable confidence levels
- **Batch Size**: Adjustable for performance optimization

### Summary Generation Settings
- **Max Length**: Maximum words in summary (default: 150)
- **Min Length**: Minimum words in summary (default: 50)
- **Algorithm**: BART transformer model with TextRank fallback

### Word Cloud Customization
- **Max Words**: Number of words to display (default: 100)
- **Color Schemes**: Multiple color palettes available
- **Size**: Customizable dimensions and styling

## 📈 Performance Considerations

### Hardware Requirements
- **Minimum**: 4GB RAM, CPU-only processing
- **Recommended**: 8GB+ RAM, GPU support for faster processing
- **Storage**: 2GB+ free space for model downloads

### Optimization Tips
- Use GPU if available for faster processing
- Process comments in batches for large datasets
- Monitor memory usage with very large datasets
- Consider data preprocessing for better results

## 🛠️ Troubleshooting

### Common Issues

1. **Model Loading Errors**
   - Ensure stable internet connection for model downloads
   - Check available disk space
   - Restart application if models fail to load

2. **Memory Issues**
   - Reduce batch size for large datasets
   - Close other applications to free memory
   - Consider processing data in smaller chunks

3. **Performance Issues**
   - Enable GPU support if available
   - Reduce word cloud complexity
   - Limit summary generation for very long texts

### Error Messages
- **"No text column found"**: Ensure your data has a text column
- **"Models failed to load"**: Check internet connection and disk space
- **"CUDA out of memory"**: Reduce batch size or use CPU processing

## 📋 API Reference

### SentimentAnalyzer Class

#### Methods

**`analyze_sentiment(text)`**
- Analyzes sentiment of a single text
- Returns: Dictionary with label, confidence, polarity, subjectivity

**`analyze_batch_sentiments(texts)`**
- Analyzes sentiments for multiple texts
- Returns: List of sentiment analysis results

**`generate_summary(text, max_length=150, min_length=50)`**
- Generates summary of input text
- Returns: Summarized text string

**`create_word_cloud(texts, max_words=100)`**
- Creates word cloud from list of texts
- Returns: WordCloud object

**`get_keyword_frequency(texts, top_n=20)`**
- Extracts keyword frequency from texts
- Returns: Dictionary of word frequencies

## 🔒 Security & Privacy

### Data Handling
- All processing is done locally on your machine
- No data is sent to external servers
- Comments are processed in memory only
- Temporary files are cleaned up automatically

### Model Security
- Uses open-source, well-vetted models
- Models are downloaded from official Hugging Face repositories
- No custom data is used for model training

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include type hints where appropriate
- Write tests for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help
- Check the troubleshooting section above
- Review the documentation
- Open an issue for bugs or feature requests
- Contact the development team for enterprise support

### Feature Requests
We welcome feature requests! Please open an issue with:
- Detailed description of the feature
- Use case and benefits
- Any implementation suggestions

## 🗺️ Roadmap

### Upcoming Features
- **Multi-language Support**: Analysis in Hindi and other Indian languages
- **Advanced Analytics**: Trend analysis and time-series sentiment tracking
- **Integration APIs**: REST API for integration with existing systems
- **Custom Models**: Fine-tuned models for government document analysis
- **Real-time Processing**: Live comment analysis capabilities

### Version History
- **v1.0.0**: Initial release with core sentiment analysis features
- **v1.1.0**: Added word cloud and summary generation
- **v1.2.0**: Enhanced UI and export capabilities

## 📞 Contact

For questions, support, or collaboration opportunities:
- **Email**: [contact-email]
- **Project Repository**: [repository-url]
- **Documentation**: [documentation-url]

---

**Note**: This platform is designed specifically for the eConsultation module requirements and can be customized further based on specific organizational needs.
