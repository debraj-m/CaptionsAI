"""
Enhanced main module for CaptionsAI with personalized captions and trending hashtags
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from .ai_analyzer import AIAnalyzer
from .content_categorizer import ContentCategorizer
from .enhanced_caption_generator import (
    EnhancedCaptionGenerator, 
    EnhancedCaptionRequest, 
    PersonalizationData, 
    CaptionContext
)
from .hashtag_generator import EnhancedHashtagGenerator, HashtagRequest
from .platform_adapters import PlatformAdapterFactory
from .config import AIConfig


logger = logging.getLogger(__name__)


@dataclass
class EnhancedContentRequest:
    """Enhanced request for complete content generation"""
    image_path: str
    platform: str = "instagram"
    style: str = "casual"
    personalization: Optional[PersonalizationData] = None
    context: Optional[CaptionContext] = None
    max_hashtags: int = 15
    include_trending_hashtags: bool = True
    include_emojis: bool = True
    caption_variants: int = 1
    brand_name: Optional[str] = None


@dataclass
class EnhancedContentResult:
    """Enhanced result with personalized content and trending data"""
    caption: str
    alternative_captions: List[str]
    hashtags: List[str]
    trending_hashtags: List[str]
    category: str
    platform: str
    performance_metrics: Dict[str, float]
    personalization_summary: List[str]
    trending_insights: Dict[str, any]
    success: bool
    error: Optional[str] = None


class EnhancedCaptionsAI:
    """Enhanced CaptionsAI with personalization and real trending data"""
    
    def __init__(self, api_key: str):
        """Initialize with OpenAI API key"""
        # Create AIConfig from the api_key
        ai_config = AIConfig(openai_api_key=api_key)
        self.ai_analyzer = AIAnalyzer(ai_config)
        self.content_categorizer = ContentCategorizer(self.ai_analyzer)
        self.enhanced_caption_generator = EnhancedCaptionGenerator(self.ai_analyzer)
        self.enhanced_hashtag_generator = EnhancedHashtagGenerator(self.ai_analyzer)
        # Platform adapter will be created per request
    
    def generate_enhanced_content(self, request: EnhancedContentRequest) -> EnhancedContentResult:
        """
        Generate enhanced personalized content with trending hashtags
        
        Args:
            request: EnhancedContentRequest with all parameters
            
        Returns:
            EnhancedContentResult with personalized content and insights
        """
        try:
            logger.info(f"Starting enhanced content generation for {request.platform}")
            
            # Step 1: Categorize content
            logger.info("Categorizing content...")
            category_result = self.content_categorizer.categorize_content(request.image_path)
            
            if not category_result.success:
                return EnhancedContentResult(
                    caption="",
                    alternative_captions=[],
                    hashtags=[],
                    trending_hashtags=[],
                    category="unknown",
                    platform=request.platform,
                    performance_metrics={},
                    personalization_summary=[],
                    trending_insights={},
                    success=False,
                    error=f"Content categorization failed: {category_result.error}"
                )
            
            category = category_result.primary_category
            logger.info(f"Content categorized as: {category}")
            
            # Step 2: Generate enhanced captions
            logger.info("Generating enhanced personalized captions...")
            
            caption_request = EnhancedCaptionRequest(
                image_path=request.image_path,
                style=request.style,
                platform=request.platform,
                personalization=request.personalization,
                context=request.context,
                category_result=category_result,
                include_call_to_action=True,
                include_questions=True,
                include_emojis=request.include_emojis
            )
            
            # Generate primary caption
            primary_caption_result = self.enhanced_caption_generator.generate_enhanced_caption(caption_request)
            
            if not primary_caption_result.success:
                return EnhancedContentResult(
                    caption="",
                    alternative_captions=[],
                    hashtags=[],
                    trending_hashtags=[],
                    category=category,
                    platform=request.platform,
                    performance_metrics={},
                    personalization_summary=[],
                    trending_insights={},
                    success=False,
                    error=f"Caption generation failed: {primary_caption_result.error}"
                )
            
            # Generate alternative captions if requested
            alternative_captions = []
            if request.caption_variants > 1:
                logger.info(f"Generating {request.caption_variants - 1} alternative captions...")
                alt_results = self.enhanced_caption_generator.generate_multiple_variants(
                    caption_request, 
                    request.caption_variants - 1
                )
                alternative_captions = [result.caption for result in alt_results if result.success]
            
            # Step 3: Generate enhanced hashtags with trending data
            logger.info("Generating enhanced hashtags with trending data...")
            
            hashtag_request = HashtagRequest(
                image_path=request.image_path,
                category_result=category_result,
                platform=request.platform,
                max_hashtags=request.max_hashtags,
                include_trending=request.include_trending_hashtags,
                include_niche=True,
                include_branded=bool(request.brand_name),
                brand_name=request.brand_name
            )
            
            hashtag_result = self.enhanced_hashtag_generator.generate_enhanced_hashtags(hashtag_request)
            
            if not hashtag_result.success:
                logger.warning(f"Hashtag generation failed: {hashtag_result.error}")
                # Continue with caption only
                hashtags = []
                trending_hashtags = []
                trending_insights = {}
            else:
                hashtags = hashtag_result.hashtags
                trending_hashtags = hashtag_result.trending_hashtags
                trending_insights = {
                    "engagement_potential": hashtag_result.engagement_potential,
                    "trending_score": hashtag_result.trending_score,
                    "real_trending_count": len(hashtag_result.real_trending_hashtags),
                    "trending_sources": [th.hashtag for th in hashtag_result.real_trending_hashtags[:5]]
                }
            
            # Step 4: Calculate performance metrics
            logger.info("Calculating performance metrics...")
            
            caption_performance = self.enhanced_caption_generator.analyze_caption_performance(
                primary_caption_result.caption, 
                request.platform
            )
            
            performance_metrics = {
                "caption_engagement_score": primary_caption_result.engagement_score or 5.0,
                "hashtag_engagement_potential": hashtag_result.engagement_potential or 5.0,
                "trending_score": hashtag_result.trending_score or 3.0,
                "overall_score": (
                    (primary_caption_result.engagement_score or 5.0) * 0.4 +
                    (hashtag_result.engagement_potential or 5.0) * 0.4 +
                    (hashtag_result.trending_score or 3.0) * 0.2
                )
            }
            performance_metrics.update(caption_performance)
            
            # Step 5: Prepare personalization summary
            personalization_summary = primary_caption_result.personalization_elements or []
            if request.personalization:
                if request.personalization.brand_name:
                    personalization_summary.append(f"Brand voice: {request.personalization.brand_name}")
                if request.personalization.target_audience:
                    personalization_summary.append(f"Audience: {request.personalization.target_audience}")
                if request.personalization.industry:
                    personalization_summary.append(f"Industry: {request.personalization.industry}")
            
            logger.info(f"Enhanced content generation completed successfully")
            logger.info(f"Performance metrics - Overall: {performance_metrics['overall_score']:.1f}/10")
            
            return EnhancedContentResult(
                caption=primary_caption_result.caption,
                alternative_captions=alternative_captions,
                hashtags=hashtags,
                trending_hashtags=trending_hashtags,
                category=category,
                platform=request.platform,
                performance_metrics=performance_metrics,
                personalization_summary=personalization_summary,
                trending_insights=trending_insights,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced content generation: {e}")
            return EnhancedContentResult(
                caption="",
                alternative_captions=[],
                hashtags=[],
                trending_hashtags=[],
                category="unknown",
                platform=request.platform,
                performance_metrics={},
                personalization_summary=[],
                trending_insights={},
                success=False,
                error=str(e)
            )
    
    def analyze_content_performance(self, caption: str, hashtags: List[str], platform: str = "instagram") -> Dict[str, float]:
        """Analyze potential performance of content"""
        
        caption_metrics = self.enhanced_caption_generator.analyze_caption_performance(caption, platform)
        
        # Basic hashtag analysis
        hashtag_score = min(10.0, len(hashtags) / 1.5)  # Optimal around 15 hashtags
        
        return {
            "caption_score": caption_metrics.get("engagement_score", 5.0),
            "hashtag_score": hashtag_score,
            "readability_score": caption_metrics.get("readability_score", 7.0),
            "shareability_score": caption_metrics.get("shareability_score", 6.0),
            "platform_optimization": caption_metrics.get("platform_optimization", 7.0),
            "overall_score": (
                caption_metrics.get("engagement_score", 5.0) * 0.4 +
                hashtag_score * 0.3 +
                caption_metrics.get("readability_score", 7.0) * 0.3
            )
        }
    
    def get_trending_insights(self, category: str, platform: str = "instagram") -> Dict[str, any]:
        """Get trending insights for a category"""
        
        try:
            trending_result = self.enhanced_hashtag_generator.trending_fetcher.get_trending_hashtags(
                category=category,
                platform=platform,
                max_count=20
            )
            
            if trending_result.success:
                return {
                    "trending_hashtags": [th.hashtag for th in trending_result.hashtags],
                    "category": category,
                    "platform": platform,
                    "source": trending_result.source,
                    "engagement_scores": [th.engagement_score for th in trending_result.hashtags if th.engagement_score],
                    "growth_rates": [th.growth_rate for th in trending_result.hashtags if th.growth_rate],
                    "last_updated": trending_result.hashtags[0].last_updated if trending_result.hashtags else None
                }
            else:
                return {
                    "error": trending_result.error,
                    "category": category,
                    "platform": platform
                }
                
        except Exception as e:
            logger.error(f"Error getting trending insights: {e}")
            return {
                "error": str(e),
                "category": category,
                "platform": platform
            }
    
    def create_personalization_profile(
        self,
        brand_name: Optional[str] = None,
        target_audience: Optional[str] = None,
        industry: Optional[str] = None,
        brand_voice: str = "casual",
        interests: List[str] = None,
        brand_keywords: List[str] = None
    ) -> PersonalizationData:
        """Create a personalization profile for consistent content generation"""
        
        return PersonalizationData(
            brand_name=brand_name,
            target_audience=target_audience,
            industry=industry,
            brand_voice=brand_voice,
            interests=interests or [],
            brand_keywords=brand_keywords or []
        )
