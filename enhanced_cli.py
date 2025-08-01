#!/usr/bin/env python3
"""
Enhanced CLI for CaptionsAI with personalization and trending hashtags
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

# Add the package to the path
sys.path.insert(0, str(Path(__file__).parent))

from captionsai.enhanced_main import (
    EnhancedCaptionsAI, 
    EnhancedContentRequest, 
    PersonalizationData, 
    CaptionContext
)
from captionsai.config import load_config


def setup_logging(verbose: bool = False):
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def print_separator(title: str = ""):
    """Print a nice separator"""
    if title:
        print(f"\n{'='*60}")
        print(f" {title}")
        print(f"{'='*60}")
    else:
        print("-" * 60)


def print_performance_metrics(metrics: dict):
    """Print performance metrics in a nice format"""
    print_separator("📊 PERFORMANCE METRICS")
    
    print(f"Overall Score:           {metrics.get('overall_score', 0):.1f}/10")
    print(f"Caption Engagement:      {metrics.get('caption_engagement_score', 0):.1f}/10")
    print(f"Hashtag Potential:       {metrics.get('hashtag_engagement_potential', 0):.1f}/10")
    print(f"Trending Score:          {metrics.get('trending_score', 0):.1f}/10")
    print(f"Readability:             {metrics.get('readability_score', 0):.1f}/10")
    print(f"Platform Optimization:   {metrics.get('platform_optimization', 0):.1f}/10")


def print_trending_insights(insights: dict):
    """Print trending insights"""
    if not insights:
        return
        
    print_separator("📈 TRENDING INSIGHTS")
    
    print(f"Engagement Potential:    {insights.get('engagement_potential', 'N/A')}")
    print(f"Trending Score:          {insights.get('trending_score', 'N/A')}")
    print(f"Real Trending Hashtags:  {insights.get('real_trending_count', 0)}")
    
    if insights.get('trending_sources'):
        print(f"Top Trending Sources:    {', '.join(insights['trending_sources'][:3])}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced CaptionsAI - Generate personalized captions and trending hashtags",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python enhanced_cli.py image.jpg
  
  # With personalization
  python enhanced_cli.py image.jpg --brand "MyBrand" --audience "young adults" --industry "fitness"
  
  # Multiple caption variants
  python enhanced_cli.py image.jpg --variants 3 --style inspirational
  
  # Business content
  python enhanced_cli.py image.jpg --brand "TechStartup" --style professional --platform facebook
        """
    )
    
    # Required arguments
    parser.add_argument(
        "image_path",
        help="Path to the image file to analyze"
    )
    
    # Platform and style
    parser.add_argument(
        "--platform",
        choices=["instagram", "facebook"],
        default="instagram",
        help="Target social media platform (default: instagram)"
    )
    
    parser.add_argument(
        "--style",
        choices=["casual", "professional", "funny", "inspirational", "storytelling", "educational"],
        default="casual",
        help="Caption style (default: casual)"
    )
    
    # Personalization options
    parser.add_argument(
        "--brand",
        help="Brand name for personalized content"
    )
    
    parser.add_argument(
        "--audience",
        help="Target audience description (e.g., 'young professionals', 'fitness enthusiasts')"
    )
    
    parser.add_argument(
        "--industry",
        help="Industry or niche (e.g., 'fitness', 'technology', 'food')"
    )
    
    parser.add_argument(
        "--voice",
        choices=["casual", "professional", "friendly", "authoritative", "playful"],
        default="casual",
        help="Brand voice tone (default: casual)"
    )
    
    parser.add_argument(
        "--interests",
        nargs="+",
        help="User/brand interests (space-separated list)"
    )
    
    parser.add_argument(
        "--keywords",
        nargs="+",
        help="Brand keywords to include (space-separated list)"
    )
    
    # Content options
    parser.add_argument(
        "--variants",
        type=int,
        default=1,
        help="Number of caption variants to generate (default: 1)"
    )
    
    parser.add_argument(
        "--max-hashtags",
        type=int,
        default=15,
        help="Maximum number of hashtags (default: 15)"
    )
    
    parser.add_argument(
        "--no-trending",
        action="store_true",
        help="Disable trending hashtag fetching"
    )
    
    parser.add_argument(
        "--no-emojis",
        action="store_true",
        help="Disable emojis in caption generation"
    )
    
    # Context options
    parser.add_argument(
        "--occasion",
        help="Special occasion or event context"
    )
    
    parser.add_argument(
        "--goal",
        choices=["engagement", "awareness", "sales", "education"],
        help="Content goal"
    )
    
    parser.add_argument(
        "--mood",
        help="Desired mood for the content"
    )
    
    # Output options
    parser.add_argument(
        "--output",
        help="Output file to save results"
    )
    
    parser.add_argument(
        "--show-insights",
        action="store_true",
        help="Show detailed trending insights"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # Validate image path
    if not os.path.exists(args.image_path):
        print(f"❌ Error: Image file '{args.image_path}' not found")
        sys.exit(1)
    
    try:
        # Load configuration
        try:
            config = load_config()
        except ValueError as e:
            print(f"❌ Configuration Error: {e}")
            print("💡 Please set your OpenAI API key as an environment variable:")
            print("   $env:OPENAI_API_KEY = 'your-api-key-here'")
            print("   Or create a .env file with OPENAI_API_KEY=your-api-key-here")
            sys.exit(1)
        
        print(f"🚀 Enhanced CaptionsAI - Analyzing {args.image_path}")
        
        # Initialize the enhanced AI
        captions_ai = EnhancedCaptionsAI(config.ai.openai_api_key)
        
        # Create personalization data
        personalization = None
        if any([args.brand, args.audience, args.industry, args.interests, args.keywords]):
            personalization = PersonalizationData(
                brand_name=args.brand,
                target_audience=args.audience,
                industry=args.industry,
                brand_voice=args.voice,
                interests=args.interests or [],
                brand_keywords=args.keywords or []
            )
        
        # Create context data
        context = None
        if any([args.occasion, args.goal, args.mood]):
            context = CaptionContext(
                occasion=args.occasion,
                content_goal=args.goal,
                mood=args.mood
            )
        
        # Create request
        request = EnhancedContentRequest(
            image_path=args.image_path,
            platform=args.platform,
            style=args.style,
            personalization=personalization,
            context=context,
            max_hashtags=args.max_hashtags,
            include_trending_hashtags=not args.no_trending,
            include_emojis=not args.no_emojis,
            caption_variants=args.variants,
            brand_name=args.brand
        )
        
        # Generate content
        print("🔍 Analyzing image and generating personalized content...")
        result = captions_ai.generate_enhanced_content(request)
        
        if not result.success:
            print(f"❌ Error: {result.error}")
            sys.exit(1)
        
        # Display results
        print_separator("✨ ENHANCED CONTENT RESULTS")
        
        print(f"📂 Category: {result.category.title()}")
        print(f"📱 Platform: {result.platform.title()}")
        
        if result.personalization_summary:
            print(f"👤 Personalization: {', '.join(result.personalization_summary)}")
        
        print_separator("📝 PRIMARY CAPTION")
        print(result.caption)
        
        # Show alternative captions
        if result.alternative_captions:
            for i, alt_caption in enumerate(result.alternative_captions, 1):
                print_separator(f"📝 ALTERNATIVE CAPTION {i}")
                print(alt_caption)
        
        # Show hashtags
        print_separator("🏷️ HASHTAGS")
        if result.hashtags:
            hashtag_text = " ".join(result.hashtags)
            print(hashtag_text)
            print(f"\nTotal: {len(result.hashtags)} hashtags")
        else:
            print("No hashtags generated")
        
        # Show trending hashtags separately
        if result.trending_hashtags:
            print_separator("🔥 TRENDING HASHTAGS")
            trending_text = " ".join(result.trending_hashtags)
            print(trending_text)
            print(f"\nTrending: {len(result.trending_hashtags)} hashtags")
        
        # Show performance metrics
        if result.performance_metrics:
            print_performance_metrics(result.performance_metrics)
        
        # Show trending insights
        if args.show_insights and result.trending_insights:
            print_trending_insights(result.trending_insights)
        
        # Show additional insights
        if args.show_insights:
            print_separator("🎯 ADDITIONAL INSIGHTS")
            insights = captions_ai.get_trending_insights(result.category, args.platform)
            
            if "error" not in insights:
                print(f"Category: {insights.get('category', 'Unknown')}")
                print(f"Source: {insights.get('source', 'Unknown')}")
                
                if insights.get('trending_hashtags'):
                    print(f"Top trending for {result.category}: {', '.join(insights['trending_hashtags'][:5])}")
            else:
                print(f"Could not fetch additional insights: {insights['error']}")
        
        # Save to file if requested
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(f"Enhanced CaptionsAI Results\n")
                    f.write(f"Platform: {result.platform}\n")
                    f.write(f"Category: {result.category}\n")
                    f.write(f"Style: {args.style}\n\n")
                    
                    f.write(f"Primary Caption:\n{result.caption}\n\n")
                    
                    if result.alternative_captions:
                        for i, alt in enumerate(result.alternative_captions, 1):
                            f.write(f"Alternative Caption {i}:\n{alt}\n\n")
                    
                    if result.hashtags:
                        f.write(f"Hashtags:\n{' '.join(result.hashtags)}\n\n")
                    
                    if result.trending_hashtags:
                        f.write(f"Trending Hashtags:\n{' '.join(result.trending_hashtags)}\n\n")
                    
                    if result.performance_metrics:
                        f.write("Performance Metrics:\n")
                        for key, value in result.performance_metrics.items():
                            f.write(f"  {key}: {value}\n")
                
                print(f"\n💾 Results saved to: {args.output}")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not save to file: {e}")
        
        print_separator()
        print("✅ Enhanced content generation completed successfully!")
        
        # Show tips
        overall_score = result.performance_metrics.get('overall_score', 0)
        if overall_score < 6:
            print("\n💡 Tips to improve:")
            print("   - Try adding more personalization details")
            print("   - Use trending hashtags for better reach")
            print("   - Consider different caption styles")
        elif overall_score >= 8:
            print("\n🎉 Excellent content! This should perform well on social media.")
        
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
