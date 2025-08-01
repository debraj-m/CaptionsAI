"""
Social media platform adapters
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .enhanced_caption_generator import EnhancedCaptionResult
from .hashtag_generator import EnhancedHashtagResult
from .content_categorizer import CategoryResult


logger = logging.getLogger(__name__)


@dataclass
class SocialMediaPost:
    """Structured social media post data"""
    caption: str
    hashtags: List[str]
    platform: str
    category: str
    character_count: int
    hashtag_count: int
    engagement_tips: List[str]
    best_posting_times: List[str]
    content_warnings: List[str]


class PlatformAdapter(ABC):
    """Abstract base class for platform-specific adapters"""
    
    @abstractmethod
    def format_post(
        self,
        caption_result: EnhancedCaptionResult,
        hashtag_result: EnhancedHashtagResult,
        category_result: Optional[CategoryResult] = None
    ) -> SocialMediaPost:
        """Format content for the specific platform"""
        pass
    
    @abstractmethod
    def get_platform_guidelines(self) -> Dict[str, Any]:
        """Get platform-specific guidelines and limits"""
        pass
    
    @abstractmethod
    def validate_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Validate content against platform rules"""
        pass


class InstagramAdapter(PlatformAdapter):
    """Instagram-specific content adapter"""
    
    def __init__(self):
        self.platform = "instagram"
        self.guidelines = {
            "caption_max_length": 2200,
            "caption_optimal_length": 125,
            "max_hashtags": 30,
            "optimal_hashtags": 11,
            "supports_line_breaks": True,
            "supports_emojis": True,
            "supports_mentions": True,
            "algorithm_favors": ["engagement", "saves", "shares", "comments"]
        }
    
    def format_post(
        self,
        caption_result: EnhancedCaptionResult,
        hashtag_result: EnhancedHashtagResult,
        category_result: Optional[CategoryResult] = None
    ) -> SocialMediaPost:
        """Format content for Instagram"""
        
        # Format caption with proper line breaks
        caption = self._format_instagram_caption(caption_result.caption)
        
        # Select optimal number of hashtags
        hashtags = hashtag_result.hashtags[:self.guidelines["optimal_hashtags"]]
        
        # Add hashtags to caption or as separate section
        if len(caption) + len(" ".join(hashtags)) < self.guidelines["caption_max_length"]:
            # Add hashtags to caption with spacing
            full_caption = f"{caption}\n\n{'·' * 20}\n{' '.join(hashtags)}"
        else:
            # Keep hashtags separate if caption would be too long
            full_caption = caption
        
        # Generate engagement tips
        engagement_tips = self._get_instagram_engagement_tips(category_result)
        
        # Best posting times for Instagram
        best_times = [
            "6 AM - 9 AM (morning commute)",
            "12 PM - 2 PM (lunch break)",
            "5 PM - 7 PM (evening commute)",
            "7 PM - 9 PM (evening leisure)"
        ]
        
        # Content warnings
        warnings = self._check_instagram_content_warnings(full_caption, hashtags)
        
        return SocialMediaPost(
            caption=full_caption,
            hashtags=hashtags,
            platform=self.platform,
            category=category_result.primary_category if category_result else "unknown",
            character_count=len(full_caption),
            hashtag_count=len(hashtags),
            engagement_tips=engagement_tips,
            best_posting_times=best_times,
            content_warnings=warnings
        )
    
    def get_platform_guidelines(self) -> Dict[str, Any]:
        """Get Instagram-specific guidelines"""
        return self.guidelines.copy()
    
    def validate_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Validate Instagram content"""
        issues = []
        suggestions = []
        
        # Check caption length
        if post.character_count > self.guidelines["caption_max_length"]:
            issues.append(f"Caption too long ({post.character_count} chars, max {self.guidelines['caption_max_length']})")
            suggestions.append("Shorten the caption or move some content to comments")
        
        # Check hashtag count
        if post.hashtag_count > self.guidelines["max_hashtags"]:
            issues.append(f"Too many hashtags ({post.hashtag_count}, max {self.guidelines['max_hashtags']})")
            suggestions.append("Reduce hashtag count for better engagement")
        
        # Check for optimal engagement
        if post.hashtag_count < 5:
            suggestions.append("Consider adding more hashtags (5-11 is optimal)")
        
        if post.character_count < 50:
            suggestions.append("Caption might be too short - consider adding more context")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _format_instagram_caption(self, caption: str) -> str:
        """Format caption with Instagram-specific styling"""
        # Instagram-specific formatting
        lines = caption.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():
                # Add some Instagram-style formatting
                formatted_lines.append(line.strip())
            else:
                formatted_lines.append("")
        
        return '\n'.join(formatted_lines)
    
    def _get_instagram_engagement_tips(
        self, 
        category_result: Optional[CategoryResult]
    ) -> List[str]:
        """Get Instagram-specific engagement tips"""
        tips = [
            "Ask a question to encourage comments",
            "Use relevant Instagram Story stickers",
            "Post when your audience is most active",
            "Use a mix of popular and niche hashtags"
        ]
        
        if category_result:
            category_tips = {
                "food": ["Tag the location", "Share the recipe in comments"],
                "travel": ["Use location tags", "Share travel tips"],
                "fashion": ["Tag brands and stores", "Create outfit details"],
                "fitness": ["Share your workout routine", "Motivate with transformation stories"],
                "business": ["Share valuable insights", "Use professional hashtags"]
            }
            
            if category_result.primary_category in category_tips:
                tips.extend(category_tips[category_result.primary_category])
        
        return tips[:5]  # Limit to top 5 tips
    
    def _check_instagram_content_warnings(
        self, 
        caption: str, 
        hashtags: List[str]
    ) -> List[str]:
        """Check for potential Instagram content issues"""
        warnings = []
        
        # Check for potentially problematic content
        sensitive_terms = ["sale", "buy now", "discount", "promo"]
        caption_lower = caption.lower()
        
        for term in sensitive_terms:
            if term in caption_lower:
                warnings.append(f"Promotional content detected - may affect reach")
                break
        
        # Check hashtag quality
        hashtag_text = " ".join(hashtags).lower()
        if "#follow" in hashtag_text or "#like" in hashtag_text:
            warnings.append("Avoid engagement-baiting hashtags like #follow #like")
        
        return warnings


class FacebookAdapter(PlatformAdapter):
    """Facebook-specific content adapter"""
    
    def __init__(self):
        self.platform = "facebook"
        self.guidelines = {
            "caption_max_length": 63206,
            "caption_optimal_length": 40,
            "max_hashtags": 10,
            "optimal_hashtags": 3,
            "supports_line_breaks": True,
            "supports_emojis": True,
            "supports_links": True,
            "algorithm_favors": ["meaningful_conversations", "time_spent", "shares"]
        }
    
    def format_post(
        self,
        caption_result: EnhancedCaptionResult,
        hashtag_result: EnhancedHashtagResult,
        category_result: Optional[CategoryResult] = None
    ) -> SocialMediaPost:
        """Format content for Facebook"""
        
        # Facebook prefers shorter captions that encourage conversation
        caption = self._format_facebook_caption(caption_result.caption)
        
        # Use fewer hashtags on Facebook
        hashtags = hashtag_result.hashtags[:self.guidelines["optimal_hashtags"]]
        
        # Facebook hashtags can be integrated into the caption more naturally
        full_caption = f"{caption}\n\n{' '.join(hashtags)}"
        
        # Generate engagement tips
        engagement_tips = self._get_facebook_engagement_tips(category_result)
        
        # Best posting times for Facebook
        best_times = [
            "9 AM - 10 AM (morning check-in)",
            "1 PM - 3 PM (lunch and afternoon)",
            "7 PM - 9 PM (evening leisure)"
        ]
        
        # Content warnings
        warnings = self._check_facebook_content_warnings(full_caption, hashtags)
        
        return SocialMediaPost(
            caption=full_caption,
            hashtags=hashtags,
            platform=self.platform,
            category=category_result.primary_category if category_result else "unknown",
            character_count=len(full_caption),
            hashtag_count=len(hashtags),
            engagement_tips=engagement_tips,
            best_posting_times=best_times,
            content_warnings=warnings
        )
    
    def get_platform_guidelines(self) -> Dict[str, Any]:
        """Get Facebook-specific guidelines"""
        return self.guidelines.copy()
    
    def validate_content(self, post: SocialMediaPost) -> Dict[str, Any]:
        """Validate Facebook content"""
        issues = []
        suggestions = []
        
        # Facebook is more lenient on caption length
        if post.character_count > self.guidelines["caption_max_length"]:
            issues.append(f"Caption extremely long ({post.character_count} chars)")
        
        # Check hashtag usage
        if post.hashtag_count > self.guidelines["max_hashtags"]:
            suggestions.append(f"Consider fewer hashtags ({post.hashtag_count} used, {self.guidelines['optimal_hashtags']} optimal)")
        
        # Facebook-specific suggestions
        if post.character_count > 200:
            suggestions.append("Consider shorter caption for better Facebook engagement")
        
        if "?" not in post.caption:
            suggestions.append("Consider adding a question to encourage comments")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions
        }
    
    def _format_facebook_caption(self, caption: str) -> str:
        """Format caption for Facebook's conversational style"""
        # Facebook prefers more conversational, shorter content
        # If caption is too long, suggest shortening
        if len(caption) > 200:
            # Take first sentence or paragraph
            sentences = caption.split('. ')
            if len(sentences) > 1:
                shortened = sentences[0] + '.'
                return f"{shortened}\n\n[Full story in comments]"
        
        return caption
    
    def _get_facebook_engagement_tips(
        self, 
        category_result: Optional[CategoryResult]
    ) -> List[str]:
        """Get Facebook-specific engagement tips"""
        tips = [
            "Ask questions to start conversations",
            "Share personal stories and experiences",
            "Use Facebook Groups for niche communities",
            "Post at times when your friends are online",
            "Encourage shares and meaningful reactions"
        ]
        
        if category_result:
            category_tips = {
                "business": ["Join relevant Facebook Groups", "Share valuable industry insights"],
                "family": ["Tag family members", "Share memories and stories"],
                "events": ["Create Facebook Events", "Encourage RSVPs and shares"],
                "travel": ["Check in to locations", "Share travel experiences"],
                "food": ["Share recipes and cooking tips", "Tag restaurants"]
            }
            
            if category_result.primary_category in category_tips:
                tips.extend(category_tips[category_result.primary_category])
        
        return tips[:5]
    
    def _check_facebook_content_warnings(
        self, 
        caption: str, 
        hashtags: List[str]
    ) -> List[str]:
        """Check for Facebook content issues"""
        warnings = []
        
        # Facebook is stricter about promotional content
        promotional_terms = ["buy", "sale", "discount", "offer", "deal"]
        caption_lower = caption.lower()
        
        promo_count = sum(1 for term in promotional_terms if term in caption_lower)
        if promo_count > 2:
            warnings.append("High promotional content may reduce organic reach")
        
        # Check for external links (Facebook prefers native content)
        if "http" in caption_lower or "www." in caption_lower:
            warnings.append("External links may reduce organic reach - consider native content")
        
        return warnings


class PlatformAdapterFactory:
    """Factory class for creating platform adapters"""
    
    _adapters = {
        "instagram": InstagramAdapter,
        "facebook": FacebookAdapter
    }
    
    @classmethod
    def create_adapter(cls, platform: str) -> PlatformAdapter:
        """Create adapter for specified platform"""
        if platform.lower() not in cls._adapters:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return cls._adapters[platform.lower()]()
    
    @classmethod
    def get_supported_platforms(cls) -> List[str]:
        """Get list of supported platforms"""
        return list(cls._adapters.keys())
