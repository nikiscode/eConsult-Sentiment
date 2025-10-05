 # E-consultation Sentiment Analysis Platform - User Guide

## 📖 Table of Contents
1. [Getting Started](#getting-started)
2. [Data Input Methods](#data-input-methods)
3. [Analysis Features](#analysis-features)
4. [Understanding Results](#understanding-results)
5. [Export Options](#export-options)
6. [Best Practices](#best-practices)
7. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### First Launch
1. **Install the Platform**: Follow the installation instructions in README.md
2. **Start the Application**: Run `streamlit run app.py`
3. **Open Browser**: Navigate to `http://localhost:8501`
4. **Wait for Models**: The AI models will load automatically (first time may take 5-10 minutes)

### Interface Overview
- **Left Sidebar**: Data input options and configuration
- **Main Area**: Analysis results and visualizations
- **Top Navigation**: Application title and status

## 📊 Data Input Methods

### Method 1: Upload CSV/Excel File
**Best for**: Large datasets with structured data

1. Click "Upload CSV/Excel" in the sidebar
2. Select your file (CSV, XLSX, or XLS format)
3. Ensure your file has a column containing stakeholder comments
4. Supported column names: `comments`, `comment`, `text`, or any text column

**File Format Example**:
```csv
comments,stakeholder_id,date
"The proposed amendment is excellent",ST001,2024-01-15
"I have concerns about implementation",ST002,2024-01-16
```

### Method 2: Manual Entry
**Best for**: Small datasets or testing

1. Click "Manual Entry" in the sidebar
2. Type each comment on a separate line
3. Click "Process Comments" when done
4. Each line becomes a separate comment for analysis

### Method 3: Sample Data
**Best for**: Testing and demonstration

1. Click "Load Sample Data" in the sidebar
2. Pre-loaded sample comments will be used
3. Perfect for exploring features without your own data

## 🔧 Analysis Features

### Sentiment Analysis
**Purpose**: Classify each comment as Positive, Negative, or Neutral

**What it provides**:
- **Label**: POSITIVE, NEGATIVE, or NEUTRAL
- **Confidence**: How certain the model is (0-1 scale)
- **Polarity**: Sentiment strength (-1 to +1)
- **Subjectivity**: How subjective vs objective the text is (0-1)

**Understanding Results**:
- **POSITIVE**: Supportive, favorable comments
- **NEGATIVE**: Critical, unfavorable comments  
- **NEUTRAL**: Factual, balanced comments
- **High Confidence (>0.8)**: Very certain prediction
- **Low Confidence (<0.6)**: Uncertain prediction

### Summary Generation
**Purpose**: Create concise summaries of comments

**Features**:
- **Individual Summaries**: Summary for each comment
- **Overall Summary**: Combined summary of all comments
- **Configurable Length**: Adjust summary length
- **Multiple Algorithms**: Uses BART model with TextRank fallback

**Best Practices**:
- Use for comments longer than 50 words
- Adjust length based on your needs
- Review summaries for accuracy

### Word Cloud Visualization
**Purpose**: Visual representation of frequently used terms

**Features**:
- **Keyword Extraction**: Identifies most common words
- **Visual Density**: Word size indicates frequency
- **Customizable**: Adjust colors, word count, styling
- **Frequency Analysis**: Detailed keyword statistics

**Understanding Word Clouds**:
- **Larger words**: More frequently used
- **Color intensity**: Visual emphasis
- **Word positioning**: Random placement for visual appeal

## 📈 Understanding Results

### Sentiment Distribution Chart
- **Pie Chart**: Shows proportion of each sentiment
- **Color Coding**: Green (Positive), Red (Negative), Yellow (Neutral)
- **Percentages**: Exact distribution of sentiments

### Confidence Distribution
- **Histogram**: Shows confidence score distribution
- **X-axis**: Confidence scores (0-1)
- **Y-axis**: Number of comments
- **Interpretation**: Higher bars indicate more confident predictions

### Keyword Frequency Chart
- **Bar Chart**: Horizontal bars showing word frequency
- **Top 20**: Most frequently used terms
- **Sorted**: Highest frequency at top
- **Excludes**: Common stop words (the, and, or, etc.)

### Detailed Breakdown
- **Sentiment by Confidence**: Cross-analysis of sentiment and confidence
- **Grouped Bars**: Shows distribution across confidence levels
- **Insights**: Identify patterns in prediction certainty

## 📤 Export Options

### CSV Export
**Contains**: All sentiment analysis results
**Columns**: comment_id, comment, label, confidence, polarity, subjectivity, sentiment_score
**Use Case**: Further analysis in Excel or other tools

### Summary Report
**Format**: Plain text file
**Contains**: 
- Analysis summary statistics
- Key findings
- Recommendations
- Timestamp and metadata

### Word Cloud Image
**Format**: PNG image file
**Contains**: High-resolution word cloud
**Use Case**: Presentations, reports, documentation

## 💡 Best Practices

### Data Preparation
1. **Clean Data**: Remove duplicates and irrelevant comments
2. **Consistent Format**: Use consistent column names
3. **Reasonable Size**: Start with 100-1000 comments for testing
4. **Quality Check**: Review data before analysis

### Analysis Configuration
1. **Start Simple**: Begin with default settings
2. **Adjust Gradually**: Modify parameters based on results
3. **Test First**: Use sample data to understand features
4. **Save Settings**: Note successful configurations

### Result Interpretation
1. **Consider Context**: Sentiment analysis is a guide, not absolute truth
2. **Review Edge Cases**: Check low-confidence predictions manually
3. **Look for Patterns**: Identify common themes in results
4. **Validate Findings**: Cross-check with manual review

### Performance Optimization
1. **Batch Processing**: Process large datasets in chunks
2. **GPU Usage**: Enable GPU if available for faster processing
3. **Memory Management**: Close other applications for large datasets
4. **Caching**: Results are cached for repeated analysis

## 🛠️ Troubleshooting

### Common Issues

#### "No text column found"
**Cause**: Data file doesn't have recognizable text column
**Solution**: 
- Rename your text column to `comments`, `comment`, or `text`
- Ensure the column contains text data, not numbers

#### "Models failed to load"
**Cause**: Internet connection issues or insufficient disk space
**Solution**:
- Check internet connection
- Ensure 2GB+ free disk space
- Restart the application
- Check firewall settings

#### "CUDA out of memory"
**Cause**: GPU memory insufficient for large datasets
**Solution**:
- Reduce batch size in configuration
- Process data in smaller chunks
- Use CPU processing instead

#### "Slow processing"
**Cause**: Large dataset or CPU-only processing
**Solution**:
- Enable GPU if available
- Reduce dataset size for testing
- Close other applications
- Increase system RAM

### Error Messages

#### Import Errors
```
ModuleNotFoundError: No module named 'transformers'
```
**Solution**: Run `pip install -r requirements.txt`

#### Memory Errors
```
RuntimeError: CUDA out of memory
```
**Solution**: Use CPU processing or reduce batch size

#### File Errors
```
FileNotFoundError: [Errno 2] No such file or directory
```
**Solution**: Check file path and permissions

### Performance Tips

#### For Large Datasets (>1000 comments)
1. Process in batches of 500-1000 comments
2. Use GPU acceleration if available
3. Monitor system memory usage
4. Consider data preprocessing

#### For Better Accuracy
1. Clean and preprocess text data
2. Remove irrelevant comments
3. Use consistent language in comments
4. Review and validate results manually

#### For Faster Processing
1. Enable GPU support
2. Close unnecessary applications
3. Use SSD storage
4. Increase system RAM

## 📞 Getting Help

### Self-Help Resources
1. **README.md**: Installation and setup instructions
2. **This User Guide**: Detailed usage instructions
3. **Sample Data**: Test with provided sample data
4. **Test Script**: Run `python test_installation.py`

### Support Channels
1. **Documentation**: Check all documentation files
2. **Issue Tracker**: Report bugs and request features
3. **Community**: Join user community discussions
4. **Technical Support**: Contact development team

### Reporting Issues
When reporting issues, include:
1. **Error Message**: Exact error text
2. **Steps to Reproduce**: What you did before the error
3. **Data Information**: Size and format of your data
4. **System Information**: OS, Python version, hardware specs
5. **Screenshots**: Visual evidence of the issue

---

**Remember**: This platform is designed to assist in analysis, not replace human judgment. Always review and validate results before making important decisions based on the analysis.
