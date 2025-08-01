"""
Configuration management for CaptionsAI
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from decouple import config


@dataclass
class AIConfig:
    """Configuration for AI services"""
    openai_api_key: str
    max_tokens: int = 500
    temperature: float = 0.7
    model: str = "gpt-4o-mini"


@dataclass
class PlatformConfig:
    """Configuration for social media platforms"""
    supported_platforms: List[str]
    max_hashtags: int = 15
    default_caption_style: str = "casual"


@dataclass
class AppConfig:
    """Main application configuration"""
    ai: AIConfig
    platforms: PlatformConfig
    debug: bool = False


def load_config() -> AppConfig:
    """Load configuration from environment variables"""
    
    # Load API key (required)
    openai_api_key = config('OPENAI_API_KEY', default=None)
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # AI Configuration
    ai_config = AIConfig(
        openai_api_key=openai_api_key,
        max_tokens=config('MAX_TOKENS', default=500, cast=int),
        temperature=config('TEMPERATURE', default=0.7, cast=float),
        model=config('AI_MODEL', default='gpt-4o')
    )
    
    # Platform Configuration
    supported_platforms_str = config('SUPPORTED_PLATFORMS', default='instagram,facebook')
    supported_platforms = [p.strip() for p in supported_platforms_str.split(',')]
    
    platform_config = PlatformConfig(
        supported_platforms=supported_platforms,
        max_hashtags=config('MAX_HASHTAGS', default=15, cast=int),
        default_caption_style=config('DEFAULT_CAPTION_STYLE', default='casual')
    )
    
    return AppConfig(
        ai=ai_config,
        platforms=platform_config,
        debug=config('DEBUG', default=False, cast=bool)
    )
