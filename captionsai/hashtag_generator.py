"""
Enhanced hashtag generation module with trending data
"""

import logging
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
from .ai_analyzer import AIAnalyzer
from .content_categorizer import CategoryResult
from .trending_hashtag_fetcher import TrendingHashtagFetcher, TrendingHashtagData


logger = logging.getLogger(__name__)


@dataclass
class HashtagRequest:
    """Request data for hashtag generation"""
    image_path: str
    category_result: Optional[CategoryResult] = None
    platform: str = "instagram"
    max_hashtags: int = 15
    include_trending: bool = True
    include_niche: bool = True
    include_branded: bool = False
    brand_name: Optional[str] = None


@dataclass
class EnhancedHashtagResult:
    """Enhanced result of hashtag generation with trending data"""
    hashtags: List[str]
    trending_hashtags: List[str]
    niche_hashtags: List[str]
    branded_hashtags: List[str]
    ai_generated_hashtags: List[str]
    real_trending_hashtags: List[TrendingHashtagData]
    platform: str
    total_count: int
    engagement_potential: Optional[float] = None
    trending_score: Optional[float] = None
    success: bool = True
    error: Optional[str] = None


class EnhancedHashtagGenerator:
    """Enhanced hashtag generator with trending data and real-time insights"""
    
    def __init__(self, ai_analyzer: AIAnalyzer):
        """Initialize with AI analyzer and trending fetcher"""
        self.ai_analyzer = ai_analyzer
        self.trending_fetcher = TrendingHashtagFetcher()
        
        # Platform-specific hashtag guidelines
        self.platform_guidelines = {
            "instagram": {
                "max_hashtags": 30,
                "optimal_range": (8, 15),
                "character_limit": 100,  # per hashtag
                "style": "mix of popular and niche",
                "trending_weight": 0.4
            },
            "facebook": {
                "max_hashtags": 10,
                "optimal_range": (3, 7),
                "character_limit": 100,
                "style": "fewer, more targeted",
                "trending_weight": 0.3
            }
        }
        
        # Category-specific hashtag templates (baseline/fallback)
        self.category_hashtags = {
            "food": {
                "popular": ["#food", "#foodie", "#delicious", "#yummy", "#foodstagram"],
                "niche": ["#homecooking", "#foodphotography", "#recipe", "#foodlover", "#tasty"],
                "trending": ["#foodgasm", "#instafood", "#eats", "#feast", "#cooking"]
            },
            "travel": {
                "popular": ["#travel", "#wanderlust", "#adventure", "#explore", "#vacation"],
                "niche": ["#travelgram", "#backpacking", "#solotravel", "#roadtrip", "#nature"],
                "trending": ["#wanderer", "#explore", "#getaway", "#bucketlist", "#discovery"]
            },
            "fashion": {
                "popular": ["#fashion", "#style", "#ootd", "#outfit", "#trendy"],
                "niche": ["#fashionista", "#styleinspo", "#lookbook", "#fashionblogger", "#styling"],
                "trending": ["#outfitoftheday", "#fashionstyle", "#streetstyle", "#fashionpost", "#stylish"]
            },
            "fitness": {
                "popular": ["#fitness", "#workout", "#gym", "#health", "#fit"],
                "niche": ["#fitnessjourney", "#training", "#exercise", "#motivation", "#strength"],
                "trending": ["#fitlife", "#gymlife", "#healthy", "#wellness", "#strong"]
            },
            "business": {
                "popular": ["#business", "#entrepreneur", "#success", "#motivation", "#work"],
                "niche": ["#startup", "#leadership", "#productivity", "#innovation", "#growth"],
                "trending": ["#hustle", "#mindset", "#goals", "#businessowner", "#professional"]
            }
        }
    
    def _get_real_trending_hashtags(self, category: str, platform: str, max_count: int = 10) -> List[TrendingHashtagData]:
        """Get real trending hashtags from external sources"""
        try:
            trending_result = self.trending_fetcher.get_trending_hashtags(
                category=category,
                platform=platform,
                max_count=max_count
            )
            
            if trending_result.success:
                logger.info(f"Found {len(trending_result.hashtags)} real trending hashtags for {category}")
                return trending_result.hashtags
            else:
                logger.warning(f"Failed to get trending hashtags: {trending_result.error}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching real trending hashtags: {e}")
            return []
    
    def _combine_hashtag_sources(
        self, 
        ai_hashtags: Dict[str, List[str]], 
        trending_hashtags: List[TrendingHashtagData],
        request: HashtagRequest
    ) -> Dict[str, List[str]]:
        """Combine AI-generated hashtags with real trending data"""
        
        combined = {
            "trending": [],
            "niche": ai_hashtags.get("niche_hashtags", []),
            "popular": ai_hashtags.get("popular_hashtags", []),
            "branded": ai_hashtags.get("branded_hashtags", [])
        }
        
        # Add real trending hashtags
        trending_tags = [th.hashtag for th in trending_hashtags]
        combined["trending"] = trending_tags
        
        # If we don't have enough AI hashtags, supplement with trending
        if len(combined["popular"]) < 5:
            # Add some trending hashtags to popular category
            for hashtag in trending_tags[:3]:
                if hashtag not in combined["popular"]:
                    combined["popular"].append(hashtag)
        
        return combined
    
    def _calculate_engagement_potential(
        self, 
        hashtags: List[str], 
        trending_data: List[TrendingHashtagData]
    ) -> float:
        """Calculate potential engagement score for hashtag combination"""
        
        score = 5.0  # Base score
        
        # Boost for trending hashtags
        trending_hashtag_set = {th.hashtag.lower() for th in trending_data}
        trending_matches = sum(1 for h in hashtags if h.lower() in trending_hashtag_set)
        score += trending_matches * 0.5
        
        # Boost for hashtag diversity
        if len(hashtags) >= 8:
            score += 1.0
        
        # Boost for optimal count
        if 10 <= len(hashtags) <= 15:
            score += 0.5
        
        # Penalty for too many or too few
        if len(hashtags) < 5:
            score -= 1.0
        elif len(hashtags) > 25:
            score -= 0.5
        
        return min(10.0, max(1.0, score))
    
    def _calculate_trending_score(self, trending_data: List[TrendingHashtagData]) -> float:
        """Calculate trending score based on real data"""
        
        if not trending_data:
            return 3.0
        
        # Average engagement scores
        engagement_scores = [th.engagement_score or 500 for th in trending_data]
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        
        # Normalize to 1-10 scale
        # Assuming 1000+ engagement is excellent (score 10)
        score = min(10.0, max(1.0, (avg_engagement / 1000) * 10))
        
        return score
    
    def generate_enhanced_hashtags(self, request: HashtagRequest) -> EnhancedHashtagResult:
        """
        Generate enhanced hashtags with real trending data
        
        Args:
            request: HashtagRequest with image path and preferences
            
        Returns:
            EnhancedHashtagResult with generated hashtags and trending data
        """
        try:
            # Get category for trending hashtag fetching
            category = "general"
            if request.category_result and request.category_result.primary_category:
                category = request.category_result.primary_category
            
            # Get real trending hashtags first
            logger.info(f"Fetching real trending hashtags for category: {category}")
            real_trending_hashtags = self._get_real_trending_hashtags(
                category=category,
                platform=request.platform,
                max_count=8
            )
            
            # Get image description for AI hashtag generation
            description_prompt = "Describe this image focusing on key subjects, activities, style, and mood for hashtag generation."
            description_result = self.ai_analyzer.analyze_image(request.image_path, description_prompt)
            
            image_description = ""
            if description_result["success"]:
                image_description = description_result["content"]
            
            # Build hashtag generation prompt
            prompt = self._build_enhanced_hashtag_prompt(request, image_description, real_trending_hashtags)
            
            # Generate AI hashtags
            result = self.ai_analyzer.analyze_image(request.image_path, prompt)
            
            if not result["success"]:
                return EnhancedHashtagResult(
                    hashtags=[],
                    trending_hashtags=[],
                    niche_hashtags=[],
                    branded_hashtags=[],
                    ai_generated_hashtags=[],
                    real_trending_hashtags=real_trending_hashtags,
                    platform=request.platform,
                    total_count=0,
                    success=False,
                    error=result.get("error", "Unknown error occurred")
                )
            
            # Parse AI response
            ai_hashtags = self._parse_ai_hashtag_response(result["content"])
            
            # Combine AI hashtags with real trending data
            combined_hashtags = self._combine_hashtag_sources(ai_hashtags, real_trending_hashtags, request)
            
            # Build final hashtag list
            final_hashtags = []
            
            # Add trending hashtags first (high priority)
            if request.include_trending:
                final_hashtags.extend(combined_hashtags["trending"][:5])
            
            # Add niche hashtags
            if request.include_niche:
                final_hashtags.extend(combined_hashtags["niche"][:5])
            
            # Add popular hashtags
            final_hashtags.extend(combined_hashtags["popular"][:5])
            
            # Add branded hashtags
            if request.include_branded:
                final_hashtags.extend(combined_hashtags["branded"][:3])
            
            # Remove duplicates while preserving order
            seen = set()
            unique_hashtags = []
            for hashtag in final_hashtags:
                if hashtag.lower() not in seen:
                    seen.add(hashtag.lower())
                    unique_hashtags.append(hashtag)
            
            # Limit to max hashtags
            final_hashtags = unique_hashtags[:request.max_hashtags]
            
            # Calculate performance metrics
            engagement_potential = self._calculate_engagement_potential(final_hashtags, real_trending_hashtags)
            trending_score = self._calculate_trending_score(real_trending_hashtags)
            
            logger.info(f"Generated {len(final_hashtags)} enhanced hashtags with {len(real_trending_hashtags)} real trending hashtags")
            
            return EnhancedHashtagResult(
                hashtags=final_hashtags,
                trending_hashtags=combined_hashtags["trending"],
                niche_hashtags=combined_hashtags["niche"],
                branded_hashtags=combined_hashtags["branded"],
                ai_generated_hashtags=list(ai_hashtags.values()),
                real_trending_hashtags=real_trending_hashtags,
                platform=request.platform,
                total_count=len(final_hashtags),
                engagement_potential=engagement_potential,
                trending_score=trending_score,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating enhanced hashtags: {e}")
            return EnhancedHashtagResult(
                hashtags=[],
                trending_hashtags=[],
                niche_hashtags=[],
                branded_hashtags=[],
                ai_generated_hashtags=[],
                real_trending_hashtags=[],
                platform=request.platform,
                total_count=0,
                success=False,
                error=str(e)
            )
    
    def _build_enhanced_hashtag_prompt(
        self, 
        request: HashtagRequest, 
        image_description: str,
        trending_hashtags: List[TrendingHashtagData]
    ) -> str:
        """Build enhanced prompt incorporating real trending data"""
        
        platform_info = self.platform_guidelines.get(request.platform, {})
        optimal_range = platform_info.get("optimal_range", (8, 15))
        
        # Get trending hashtag strings
        trending_tags = [th.hashtag for th in trending_hashtags]
        
        prompt = f"""
        Generate relevant hashtags for this social media image using AI analysis combined with real trending data.
        
        IMAGE ANALYSIS: {image_description}
        
        REAL TRENDING HASHTAGS FOR THIS CATEGORY: {', '.join(trending_tags) if trending_tags else 'None available'}
        
        REQUIREMENTS:
        - Platform: {request.platform.title()}
        - Number of hashtags: {optimal_range[0]}-{optimal_range[1]} (max {request.max_hashtags})
        - Incorporate trending hashtags when relevant
        - Mix of popular, niche, and trending hashtags
        """
        
        if request.category_result:
            prompt += f"- Primary category: {request.category_result.primary_category}\n"
            if request.category_result.secondary_categories:
                prompt += f"- Secondary categories: {', '.join(request.category_result.secondary_categories)}\n"
        
        if request.brand_name:
            prompt += f"- Brand: {request.brand_name}\n"
        
        prompt += f"""
        HASHTAG STRATEGY:
        1. TRENDING: Use {len(trending_tags)} real trending hashtags from the list above when relevant
        2. POPULAR: High-volume hashtags for broad reach
        3. NICHE: Specific, targeted hashtags for your content type
        4. BRANDED: Brand-specific hashtags (if applicable)
        
        GUIDELINES:
        - Prioritize real trending hashtags that match the image content
        - Base all hashtags on what's actually visible in the image
        - Include a mix of different popularity levels
        - Avoid banned or shadowbanned hashtags
        - Use proper hashtag format (# followed by text, no spaces)
        - Consider current trends and seasonality
        - Make hashtags specific and relevant, not generic
        
        Return hashtags in this JSON format:
        {{
            "trending_hashtags": ["trending hashtags that match the image"],
            "popular_hashtags": ["#hashtag1", "#hashtag2"],
            "niche_hashtags": ["#hashtag3", "#hashtag4"],
            "branded_hashtags": ["#hashtag5", "#hashtag6"]
        }}
        
        Return only the JSON response, nothing else.
        """
        
        return prompt
    
    def _parse_ai_hashtag_response(self, response_text: str) -> Dict[str, List[str]]:
        """Parse AI hashtag response"""
        
        response_text = response_text.strip()
        
        # Remove markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        try:
            import json
            data = json.loads(response_text)
            
            # Clean hashtags
            for key in data:
                if isinstance(data[key], list):
                    data[key] = self._clean_hashtags(data[key])
            
            return data
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            
            # Fallback: extract hashtags from text
            hashtags = self._extract_hashtags_from_text(response_text)
            
            return {
                "trending_hashtags": hashtags[:3],
                "popular_hashtags": hashtags[3:8],
                "niche_hashtags": hashtags[8:12],
                "branded_hashtags": hashtags[12:15]
            }
    
    def _clean_hashtags(self, hashtags: List[str]) -> List[str]:
        """Clean and validate hashtags"""
        cleaned = []
        for hashtag in hashtags:
            # Ensure hashtag starts with #
            if not hashtag.startswith('#'):
                hashtag = '#' + hashtag
            
            # Remove spaces and special characters except #
            hashtag = ''.join(c for c in hashtag if c.isalnum() or c == '#')
            
            # Validate length and format
            if len(hashtag) > 2 and len(hashtag) <= 100:
                cleaned.append(hashtag)
        
        return cleaned
    
    def _extract_hashtags_from_text(self, text: str) -> List[str]:
        """Extract hashtags from free text as fallback"""
        import re
        
        # Find all hashtags in text
        hashtag_pattern = r'#[A-Za-z0-9_]+'
        hashtags = re.findall(hashtag_pattern, text)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_hashtags = []
        for hashtag in hashtags:
            if hashtag.lower() not in seen:
                seen.add(hashtag.lower())
                unique_hashtags.append(hashtag)
        
        return unique_hashtags
    
    def get_category_suggestions(self, category: str, platform: str = "instagram") -> List[str]:
        """Get suggested hashtags for a specific category"""
        category_data = self.category_hashtags.get(category, {})
        
        suggestions = []
        suggestions.extend(category_data.get("popular", []))
        suggestions.extend(category_data.get("niche", []))
        suggestions.extend(category_data.get("trending", []))
        
        # Limit based on platform
        platform_info = self.platform_guidelines.get(platform, {})
        max_suggestions = platform_info.get("optimal_range", (8, 15))[1]
        
        return suggestions[:max_suggestions]
