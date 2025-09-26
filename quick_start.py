#!/usr/bin/env python3
"""
Quick Start Script for eConsultation Sentiment Analysis Platform
This script provides a command-line interface for quick analysis without the web UI.
"""

import argparse
import pandas as pd
import json
from datetime import datetime
from sentiment_analyzer import SentimentAnalyzer

def analyze_file(input_file, output_file=None, analysis_type='all'):
    """
    Analyze a CSV file with comments.
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to output file (optional)
        analysis_type (str): Type of analysis ('sentiment', 'summary', 'wordcloud', 'all')
    """
    print(f"🚀 Starting analysis of {input_file}...")
    
    # Load data
    try:
        df = pd.read_csv(input_file)
        print(f"✅ Loaded {len(df)} records from {input_file}")
    except Exception as e:
        print(f"❌ Error loading file: {e}")
        return
    
    # Get comments column
    if 'comments' in df.columns:
        comments = df['comments'].dropna().tolist()
    elif 'comment' in df.columns:
        comments = df['comment'].dropna().tolist()
    elif 'text' in df.columns:
        comments = df['text'].dropna().tolist()
    else:
        text_columns = df.select_dtypes(include=['object']).columns
        if len(text_columns) > 0:
            comments = df[text_columns[0]].dropna().tolist()
        else:
            print("❌ No text column found in the data!")
            return
    
    if not comments:
        print("❌ No comments found in the data!")
        return
    
    print(f"📝 Found {len(comments)} comments to analyze")
    
    # Initialize analyzer
    print("🤖 Loading AI models...")
    analyzer = SentimentAnalyzer()
    
    results = {}
    
    # Sentiment Analysis
    if analysis_type in ['sentiment', 'all']:
        print("📊 Analyzing sentiments...")
        sentiment_results = analyzer.analyze_batch_sentiments(comments)
        results['sentiment'] = sentiment_results
        
        # Summary statistics
        positive_count = sum(1 for r in sentiment_results if r['label'] == 'POSITIVE')
        negative_count = sum(1 for r in sentiment_results if r['label'] == 'NEGATIVE')
        neutral_count = sum(1 for r in sentiment_results if r['label'] == 'NEUTRAL')
        
        print(f"📈 Sentiment Summary:")
        print(f"   Positive: {positive_count} ({positive_count/len(sentiment_results)*100:.1f}%)")
        print(f"   Negative: {negative_count} ({negative_count/len(sentiment_results)*100:.1f}%)")
        print(f"   Neutral: {neutral_count} ({neutral_count/len(sentiment_results)*100:.1f}%)")
    
    # Summary Generation
    if analysis_type in ['summary', 'all']:
        print("📝 Generating summaries...")
        summaries = []
        for i, comment in enumerate(comments):  # Process all comments
            summary = analyzer.generate_summary(comment)
            summaries.append({
                'comment_id': i + 1,
                'original': comment,
                'summary': summary
            })
        results['summaries'] = summaries
        
        print(f"✅ Generated {len(summaries)} summaries")
    
    # Word Cloud Analysis
    if analysis_type in ['wordcloud', 'all']:
        print("☁️ Analyzing keywords...")
        keywords = analyzer.get_keyword_frequency(comments, top_n=20)
        results['keywords'] = keywords
        
        print("🔤 Top 10 Keywords:")
        for i, (word, freq) in enumerate(list(keywords.items())[:10]):
            print(f"   {i+1}. {word}: {freq}")
    
    # Save results
    if output_file:
        print(f"💾 Saving results to {output_file}...")
        
        if output_file.endswith('.json'):
            # Save as JSON
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        elif output_file.endswith('.csv'):
            # Save sentiment results as CSV
            if 'sentiment' in results:
                sentiment_df = pd.DataFrame(results['sentiment'])
                sentiment_df['comment'] = comments
                sentiment_df.to_csv(output_file, index=False)
        else:
            # Save as text report
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("eConsultation Sentiment Analysis Report\n")
                f.write("=" * 50 + "\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Input File: {input_file}\n")
                f.write(f"Total Comments: {len(comments)}\n\n")
                
                if 'sentiment' in results:
                    f.write("SENTIMENT ANALYSIS\n")
                    f.write("-" * 20 + "\n")
                    f.write(f"Positive: {positive_count} ({positive_count/len(sentiment_results)*100:.1f}%)\n")
                    f.write(f"Negative: {negative_count} ({negative_count/len(sentiment_results)*100:.1f}%)\n")
                    f.write(f"Neutral: {neutral_count} ({neutral_count/len(sentiment_results)*100:.1f}%)\n\n")
                
                if 'keywords' in results:
                    f.write("TOP KEYWORDS\n")
                    f.write("-" * 15 + "\n")
                    for word, freq in list(results['keywords'].items())[:10]:
                        f.write(f"{word}: {freq}\n")
        
        print(f"✅ Results saved to {output_file}")
    
    print("🎉 Analysis completed successfully!")

def main():
    """Main function for command-line interface."""
    parser = argparse.ArgumentParser(
        description="eConsultation Sentiment Analysis - Quick Start",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python quick_start.py sample_data.csv
  python quick_start.py data.csv -o results.json
  python quick_start.py data.csv -t sentiment -o sentiment_results.csv
  python quick_start.py data.csv -t wordcloud -o keywords.txt
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input CSV file containing stakeholder comments'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (optional)'
    )
    
    parser.add_argument(
        '-t', '--type',
        choices=['sentiment', 'summary', 'wordcloud', 'all'],
        default='all',
        help='Type of analysis to perform (default: all)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='eConsultation Sentiment Analysis v1.0.0'
    )
    
    args = parser.parse_args()
    
    # Run analysis
    analyze_file(args.input_file, args.output, args.type)

if __name__ == "__main__":
    main()
