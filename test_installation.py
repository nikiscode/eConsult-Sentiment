"""
Test script to verify installation and functionality of eConsultation Sentiment Analysis Platform
"""

import sys
import importlib
import traceback

def test_imports():
    """Test if all required packages can be imported."""
    print("🧪 Testing package imports...")
    
    required_packages = [
        'streamlit',
        'transformers',
        'torch',
        'pandas',
        'numpy',
        'wordcloud',
        'matplotlib',
        'seaborn',
        'plotly',
        'scikit-learn',
        'nltk',
        'textblob',
        'sumy',
        'spacy'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package}")
        except ImportError as e:
            print(f"❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n⚠️ Failed to import: {', '.join(failed_imports)}")
        return False
    else:
        print("\n✅ All packages imported successfully!")
        return True

def test_models():
    """Test if AI models can be loaded."""
    print("\n🤖 Testing AI model loading...")
    
    try:
        from transformers import pipeline
        
        # Test sentiment analysis model
        print("Loading sentiment analysis model...")
        sentiment_pipeline = pipeline("sentiment-analysis")
        print("✅ Sentiment analysis model loaded")
        
        # Test summarization model
        print("Loading summarization model...")
        summarizer_pipeline = pipeline("summarization")
        print("✅ Summarization model loaded")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality with sample data."""
    print("\n🔧 Testing basic functionality...")
    
    try:
        from sentiment_analyzer import SentimentAnalyzer
        
        # Initialize analyzer
        print("Initializing SentimentAnalyzer...")
        analyzer = SentimentAnalyzer()
        
        # Test sentiment analysis
        test_text = "This is a positive comment about the proposed legislation."
        print("Testing sentiment analysis...")
        result = analyzer.analyze_sentiment(test_text)
        print(f"✅ Sentiment analysis result: {result['label']} (confidence: {result['confidence']:.3f})")
        
        # Test summarization
        test_long_text = """
        The proposed amendment to the Companies Act is a significant step towards modernizing 
        corporate governance in India. This legislation aims to streamline compliance requirements 
        for small and medium enterprises while maintaining transparency and accountability. 
        The key provisions include simplified reporting mechanisms, digital filing systems, 
        and reduced penalties for minor violations. However, there are concerns about the 
        implementation timeline and the need for adequate training of regulatory officials.
        """
        print("Testing summarization...")
        summary = analyzer.generate_summary(test_long_text)
        print(f"✅ Summary generated: {summary[:100]}...")
        
        # Test word cloud
        print("Testing word cloud generation...")
        test_texts = [test_long_text]
        wordcloud = analyzer.create_word_cloud(test_texts)
        if wordcloud:
            print("✅ Word cloud generated successfully")
        else:
            print("⚠️ Word cloud generation had issues")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        traceback.print_exc()
        return False

def test_nltk_data():
    """Test if NLTK data is available."""
    print("\n📚 Testing NLTK data...")
    
    try:
        import nltk
        
        # Test required NLTK data
        required_data = ['punkt', 'stopwords', 'vader_lexicon']
        
        for data_name in required_data:
            try:
                nltk.data.find(f'tokenizers/{data_name}')
                print(f"✅ {data_name}")
            except LookupError:
                print(f"❌ {data_name} not found")
                return False
        
        print("✅ All NLTK data available")
        return True
        
    except Exception as e:
        print(f"❌ NLTK data test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 eConsultation Sentiment Analysis Platform - Installation Test")
    print("=" * 70)
    
    tests = [
        ("Package Imports", test_imports),
        ("NLTK Data", test_nltk_data),
        ("AI Models", test_models),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! The installation is successful.")
        print("🚀 You can now run: streamlit run app.py")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please check the errors above.")
        print("💡 Try running the installation script again or check the requirements.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
