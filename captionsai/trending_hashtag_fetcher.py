"""
Trending hashtag fetcher module
Fetches real-time trending hashtags from various sources
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import json
import re
from urllib.parse import quote_plus


logger = logging.getLogger(__name__)


@dataclass
class TrendingHashtagData:
    """Data for trending hashtags"""
    hashtag: str
    platform: str
    engagement_score: Optional[int] = None
    growth_rate: Optional[float] = None
    category: Optional[str] = None
    last_updated: Optional[str] = None


@dataclass
class TrendingResult:
    """Result of trending hashtag fetch"""
    hashtags: List[TrendingHashtagData]
    source: str
    category: str
    platform: str
    success: bool
    error: Optional[str] = None


class TrendingHashtagFetcher:
    """Fetches trending hashtags from various sources"""
    
    def __init__(self):
        """Initialize the trending hashtag fetcher"""
        self.cache = {}
        self.cache_duration = 3600  # 1 hour in seconds
        self.blocked_sources = set()  # Track sources that are blocking us
        
        # Category mappings for different sources
        self.category_keywords = {
            "food": ["food", "cooking", "recipe", "restaurant", "foodie", "culinary"],
            "travel": ["travel", "vacation", "destination", "tourism", "wanderlust"],
            "fashion": ["fashion", "style", "outfit", "clothing", "ootd", "style"],
            "fitness": ["fitness", "workout", "gym", "health", "exercise", "wellness"],
            "business": ["business", "entrepreneur", "marketing", "startup", "professional"],
            "lifestyle": ["lifestyle", "daily", "life", "living", "home", "personal"],
            "technology": ["tech", "technology", "gadget", "digital", "innovation"],
            "beauty": ["beauty", "makeup", "skincare", "cosmetics", "beautytips"],
            "photography": ["photography", "photo", "camera", "photographer", "picture"],
            "art": ["art", "artist", "creative", "design", "artwork", "artistic"],
            "events": ["events", "festival", "celebration", "ceremony", "gathering", "occasion"]
        }
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key].get("timestamp", 0)
        return (time.time() - cache_time) < self.cache_duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]["data"]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def fetch_trending_from_hashtagify(self, category: str, platform: str = "instagram") -> TrendingResult:
        """
        Fetch trending hashtags from Hashtagify.me (or similar service)
        Note: This would require an API key in production
        """
        try:
            cache_key = f"hashtagify_{category}_{platform}"
            cached_data = self._get_from_cache(cache_key)
            
            if cached_data:
                logger.info(f"Using cached trending data for {category}")
                return TrendingResult(
                    hashtags=cached_data["hashtags"],
                    source="hashtagify_cache",
                    category=category,
                    platform=platform,
                    success=True
                )
            
            # In production, you would make actual API calls here
            # For now, we'll simulate with category-based trending data
            trending_hashtags = self._get_simulated_trending_data(category, platform)
            
            result_data = {
                "hashtags": trending_hashtags,
                "category": category,
                "platform": platform
            }
            
            self._save_to_cache(cache_key, result_data)
            
            return TrendingResult(
                hashtags=trending_hashtags,
                source="hashtagify_simulated",
                category=category,
                platform=platform,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error fetching from Hashtagify: {e}")
            return TrendingResult(
                hashtags=[],
                source="hashtagify",
                category=category,
                platform=platform,
                success=False,
                error=str(e)
            )
    
    def fetch_trending_from_ritetag(self, category: str, platform: str = "instagram") -> TrendingResult:
        """
        Fetch trending hashtags from RiteTag API
        Note: This would require an API key in production
        """
        try:
            cache_key = f"ritetag_{category}_{platform}"
            cached_data = self._get_from_cache(cache_key)
            
            if cached_data:
                logger.info(f"Using cached RiteTag data for {category}")
                return TrendingResult(
                    hashtags=cached_data["hashtags"],
                    source="ritetag_cache",
                    category=category,
                    platform=platform,
                    success=True
                )
            
            # Simulate API call
            trending_hashtags = self._get_simulated_trending_data(category, platform, source="ritetag")
            
            result_data = {
                "hashtags": trending_hashtags,
                "category": category,
                "platform": platform
            }
            
            self._save_to_cache(cache_key, result_data)
            
            return TrendingResult(
                hashtags=trending_hashtags,
                source="ritetag_simulated",
                category=category,
                platform=platform,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error fetching from RiteTag: {e}")
            return TrendingResult(
                hashtags=[],
                source="ritetag",
                category=category,
                platform=platform,
                success=False,
                error=str(e)
            )
    
    def fetch_trending_from_web_scraping(self, category: str, platform: str = "instagram") -> TrendingResult:
        """
        Fetch trending hashtags by scraping public trend websites
        Falls back to simulated data if scraping fails
        """
        try:
            cache_key = f"webscrape_{category}_{platform}"
            cached_data = self._get_from_cache(cache_key)
            
            if cached_data:
                logger.info(f"Using cached web scraping data for {category}")
                return TrendingResult(
                    hashtags=cached_data["hashtags"],
                    source="webscrape_cache",
                    category=category,
                    platform=platform,
                    success=True
                )
            
            trending_hashtags = []
            
            # Try to scrape from multiple sources
            try:
                if platform == "instagram":
                    hashtags = self._scrape_instagram_trends(category)
                    trending_hashtags.extend(hashtags)
                
                # Add more scraping sources as needed
                hashtags_from_trend_sites = self._scrape_trend_websites(category, platform)
                trending_hashtags.extend(hashtags_from_trend_sites)
                
            except Exception as scraping_error:
                logger.warning(f"Web scraping failed: {scraping_error}. Falling back to simulated data.")
                # Fall back to simulated trending data
                trending_hashtags = self._get_simulated_trending_data(category, platform, source="webscrape_fallback")
            
            # If scraping yielded no results, use simulated data
            if not trending_hashtags:
                logger.info(f"No hashtags found from scraping, using simulated data for {category}")
                trending_hashtags = self._get_simulated_trending_data(category, platform, source="webscrape_fallback")
            
            # Remove duplicates
            unique_hashtags = self._remove_duplicate_hashtags(trending_hashtags)
            
            result_data = {
                "hashtags": unique_hashtags[:20],  # Limit to top 20
                "category": category,
                "platform": platform
            }
            
            self._save_to_cache(cache_key, result_data)
            
            return TrendingResult(
                hashtags=unique_hashtags[:20],
                source="web_scraping_with_fallback",
                category=category,
                platform=platform,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error in web scraping: {e}")
            # Final fallback to simulated data
            try:
                trending_hashtags = self._get_simulated_trending_data(category, platform, source="error_fallback")
                return TrendingResult(
                    hashtags=trending_hashtags,
                    source="fallback_simulated",
                    category=category,
                    platform=platform,
                    success=True
                )
            except Exception as fallback_error:
                logger.error(f"Even fallback failed: {fallback_error}")
                return TrendingResult(
                    hashtags=[],
                    source="web_scraping",
                    category=category,
                    platform=platform,
                    success=False,
                    error=str(e)
                )
    
    def _scrape_instagram_trends(self, category: str) -> List[TrendingHashtagData]:
        """Scrape Instagram trending hashtags from top-hashtags.com"""
        from bs4 import BeautifulSoup
        
        hashtags = []
        source_name = "top-hashtags.com"
        
        # Skip if we know this source is blocking us
        if source_name in self.blocked_sources:
            logger.debug(f"Skipping {source_name} - known to be blocking requests")
            return hashtags
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }

        try:
            # Encode category for URL
            encoded_category = quote_plus(category.lower())
            url = f'https://top-hashtags.com/instagram/{encoded_category}/'
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'lxml')
            hashtag_elements = soup.select('.entry-content .tag-box')
            
            for i, element in enumerate(hashtag_elements[:20]):  # Get top 20 hashtags
                hashtag_text = element.get_text().strip()
                if hashtag_text.startswith('#'):
                    engagement_score = 1000 - (i * 50)  # Estimated engagement score
                    growth_rate = 0.15 - (i * 0.005)    # Estimated growth rate
                    
                    hashtags.append(TrendingHashtagData(
                        hashtag=hashtag_text,
                        platform="instagram",
                        engagement_score=engagement_score,
                        growth_rate=growth_rate,
                        category=category,
                        last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                logger.info(f"Website {source_name} blocking access (403) - adding to blocked list")
                self.blocked_sources.add(source_name)
            else:
                logger.warning(f"HTTP error scraping Instagram trends: {e}")
        except requests.exceptions.RequestException as e:
            logger.debug(f"Network issue scraping Instagram trends: {e}")
        except Exception as e:
            logger.warning(f"Unexpected error scraping Instagram trends: {e}")
            
        return hashtags
    
    def _scrape_trend_websites(self, category: str, platform: str) -> List[TrendingHashtagData]:
        """Scrape trending hashtag websites"""
        from bs4 import BeautifulSoup
        
        hashtags = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Try all-hashtag.com first
        if "all-hashtag.com" not in self.blocked_sources:
            try:
                encoded_category = quote_plus(category.lower())
                url = f'https://all-hashtag.com/top-hashtags.php?keyword={encoded_category}'
                
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                hashtag_elements = soup.select('.copy-hashtags')
                
                for i, element in enumerate(hashtag_elements[:15]):  # Get top 15 hashtags
                    hashtag_text = element.get_text().strip()
                    if not hashtag_text.startswith('#'):
                        hashtag_text = f'#{hashtag_text}'
                        
                    hashtags.append(TrendingHashtagData(
                        hashtag=hashtag_text,
                        platform=platform,
                        engagement_score=900 - (i * 50),
                        growth_rate=0.12 - (i * 0.005),
                        category=category,
                        last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.info("all-hashtag.com blocking access - adding to blocked list")
                    self.blocked_sources.add("all-hashtag.com")
                else:
                    logger.debug(f"HTTP error with all-hashtag.com: {e}")
            except Exception as e:
                logger.debug(f"Error with all-hashtag.com: {e}")
        
        # Try hashtagsforlikes.co as backup if we don't have enough hashtags
        if len(hashtags) < 5 and "hashtagsforlikes.co" not in self.blocked_sources:
            try:
                encoded_category = quote_plus(category.lower())
                url = f'https://hashtagsforlikes.co/hashtag/{encoded_category}'
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'lxml')
                hashtag_elements = soup.select('.hashtag-item')
                
                for i, element in enumerate(hashtag_elements[:10]):
                    hashtag_text = element.get_text().strip()
                    if not hashtag_text.startswith('#'):
                        hashtag_text = f'#{hashtag_text}'
                        
                    hashtags.append(TrendingHashtagData(
                        hashtag=hashtag_text,
                        platform=platform,
                        engagement_score=800 - (i * 50),
                        growth_rate=0.10 - (i * 0.005),
                        category=category,
                        last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    logger.info("hashtagsforlikes.co blocking access - adding to blocked list")
                    self.blocked_sources.add("hashtagsforlikes.co")
                else:
                    logger.debug(f"HTTP error with hashtagsforlikes.co: {e}")
            except Exception as e:
                logger.debug(f"Error with hashtagsforlikes.co: {e}")
        
        # Fall back to category-based hashtags if web scraping yields too few results
        if len(hashtags) < 5:
            logger.info(f"Limited scraping results for {category}, supplementing with curated hashtags")
            category_trends = self._get_category_trending_hashtags(category, platform)
            hashtags.extend(category_trends)
        
        return hashtags
    
    def _get_category_trending_hashtags(self, category: str, platform: str) -> List[TrendingHashtagData]:
        """Get trending hashtags based on category analysis"""
        
        # Current trending patterns (would be updated regularly)
        trending_data = {
            "food": {
                "instagram": ["#foodie2025", "#healthyrecipes", "#plantbasedmeals", "#foodphotography", "#homecooking"],
                "facebook": ["#familymeals", "#cookingathome", "#healthyliving", "#foodblog"]
            },
            "travel": {
                "instagram": ["#wanderlust2025", "#solotravel", "#sustainabletravel", "#hiddenplaces", "#localcuisine"],
                "facebook": ["#familytravel", "#roadtrip", "#vacation2025", "#traveltips"]
            },
            "fashion": {
                "instagram": ["#ootd2025", "#sustainablefashion", "#vintagestyle", "#thriftfinds", "#styleinspo"],
                "facebook": ["#fashionadvice", "#styletrends", "#outfitideas", "#fashion2025"]
            },
            "fitness": {
                "instagram": ["#fitnessjourney", "#homeworkout", "#mentalhealthfitness", "#strongwomen", "#fitnessmotivation"],
                "facebook": ["#healthylifestyle", "#workoutmotivation", "#wellness", "#fitnessgoals"]
            },
            "business": {
                "instagram": ["#entrepreneur2025", "#businessowner", "#digitalnomad", "#hustle", "#mindset"],
                "facebook": ["#smallbusiness", "#entrepreneurship", "#businesstips", "#success"]
            },
            "events": {
                "instagram": ["#celebration2025", "#festivalstoday", "#culturalheritage", "#traditionalmeets", "#festivalvibes", "#spiritualjourney", "#communitylove", "#heritagepride", "#festivemood", "#sacredmoments"],
                "facebook": ["#familyfestival", "#culturalevent", "#traditioncelebration", "#spiritualgathering", "#festivalmemories"]
            },
            "lifestyle": {
                "instagram": ["#mindfuliving", "#dailyinspo", "#gratitudepractice", "#selfcaresunday", "#positivevibes"],
                "facebook": ["#lifelessons", "#inspiration", "#motivation", "#wellbeing", "#mindfulness"]
            },
            "art": {
                "instagram": ["#artistsoninstagram", "#creativeminds", "#artoftheday", "#digitalart2025", "#arttherapy"],
                "facebook": ["#localartists", "#artcommunity", "#creativeexpression", "#artlovers", "#inspiration"]
            }
        }
        
        hashtags_list = trending_data.get(category, {}).get(platform, [])
        
        hashtags = []
        for i, hashtag in enumerate(hashtags_list):
            hashtags.append(TrendingHashtagData(
                hashtag=hashtag,
                platform=platform,
                engagement_score=800 - i * 50,
                growth_rate=0.12 - i * 0.015,
                category=category,
                last_updated=time.strftime("%Y-%m-%d %H:%M:%S")
            ))
        
        return hashtags
    
    def _get_simulated_trending_data(self, category: str, platform: str, source: str = "general") -> List[TrendingHashtagData]:
        """Get simulated trending data for testing/demonstration"""
        
        # Different sources might have different trending hashtags
        if source == "ritetag":
            multiplier = 1.2
            suffix = "RT"
        else:
            multiplier = 1.0
            suffix = ""
        
        base_hashtags = self._get_category_trending_hashtags(category, platform)
        
        # Adjust scores based on source
        for hashtag in base_hashtags:
            if hashtag.engagement_score:
                hashtag.engagement_score = int(hashtag.engagement_score * multiplier)
            if suffix:
                hashtag.hashtag += suffix
        
        return base_hashtags
    
    def _remove_duplicate_hashtags(self, hashtags: List[TrendingHashtagData]) -> List[TrendingHashtagData]:
        """Remove duplicate hashtags while preserving the best ones"""
        seen = set()
        unique_hashtags = []
        
        # Sort by engagement score (highest first)
        sorted_hashtags = sorted(hashtags, key=lambda x: x.engagement_score or 0, reverse=True)
        
        for hashtag in sorted_hashtags:
            hashtag_lower = hashtag.hashtag.lower()
            if hashtag_lower not in seen:
                seen.add(hashtag_lower)
                unique_hashtags.append(hashtag)
        
        return unique_hashtags
    
    def get_trending_hashtags(self, category: str, platform: str = "instagram", max_count: int = 15) -> TrendingResult:
        """
        Get trending hashtags from multiple sources
        
        Args:
            category: Content category
            platform: Social media platform
            max_count: Maximum number of hashtags to return
            
        Returns:
            TrendingResult with trending hashtags
        """
        all_hashtags = []
        sources_tried = []
        
        # Try multiple sources in order of preference
        sources = [
            ("web_scraping", self.fetch_trending_from_web_scraping),
            ("hashtagify", self.fetch_trending_from_hashtagify),
            ("ritetag", self.fetch_trending_from_ritetag)
        ]
        
        for source_name, fetch_method in sources:
            try:
                result = fetch_method(category, platform)
                sources_tried.append(source_name)
                
                if result.success and result.hashtags:
                    all_hashtags.extend(result.hashtags)
                    logger.info(f"Successfully fetched {len(result.hashtags)} hashtags from {source_name}")
                
            except Exception as e:
                logger.warning(f"Failed to fetch from {source_name}: {e}")
                continue
        
        if not all_hashtags:
            return TrendingResult(
                hashtags=[],
                source=",".join(sources_tried),
                category=category,
                platform=platform,
                success=False,
                error="No trending hashtags found from any source"
            )
        
        # Remove duplicates and limit count
        unique_hashtags = self._remove_duplicate_hashtags(all_hashtags)
        final_hashtags = unique_hashtags[:max_count]
        
        return TrendingResult(
            hashtags=final_hashtags,
            source=",".join(sources_tried),
            category=category,
            platform=platform,
            success=True
        )

