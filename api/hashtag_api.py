"""
FastAPI server for CaptionsAI Hashtag Generation
"""

import os
import logging
import sys
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import tempfile
import uvicorn
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from captionsai.ai_analyzer import AIAnalyzer
from captionsai.content_categorizer import ContentCategorizer
from captionsai.hashtag_generator import EnhancedHashtagGenerator, HashtagRequest
from captionsai.config import AIConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CaptionsAI Hashtag API",
    description="AI-powered hashtag generation for social media content",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for AI components
ai_analyzer = None
content_categorizer = None
hashtag_generator = None


class HashtagGenerationRequest(BaseModel):
    """Request model for hashtag generation"""
    platform: str = "instagram"
    max_hashtags: int = 15
    include_trending: bool = True
    include_niche: bool = True
    include_branded: bool = False
    brand_name: Optional[str] = None


class HashtagGenerationResponse(BaseModel):
    """Response model for hashtag generation"""
    hashtags: List[str]
    trending_hashtags: List[str]
    niche_hashtags: List[str]
    branded_hashtags: List[str]
    ai_generated_hashtags: List[str]
    platform: str
    total_count: int
    engagement_potential: Optional[float] = None
    trending_score: Optional[float] = None
    success: bool
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize AI components on startup"""
    global ai_analyzer, content_categorizer, hashtag_generator
    
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize AI components
        ai_config = AIConfig(openai_api_key=api_key)
        ai_analyzer = AIAnalyzer(ai_config)
        content_categorizer = ContentCategorizer(ai_analyzer)
        hashtag_generator = EnhancedHashtagGenerator(ai_analyzer)
        
        logger.info("AI components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI components: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CaptionsAI Hashtag API",
        "version": "1.0.0",
        "description": "AI-powered hashtag generation for social media content",
        "endpoints": {
            "generate_hashtags": "/hashtags/generate",
            "health": "/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_components": {
            "ai_analyzer": ai_analyzer is not None,
            "content_categorizer": content_categorizer is not None,
            "hashtag_generator": hashtag_generator is not None
        }
    }


@app.post("/hashtags/generate", response_model=HashtagGenerationResponse)
async def generate_hashtags(
    image: UploadFile = File(...),
    platform: str = Form("instagram"),
    max_hashtags: int = Form(15),
    include_trending: bool = Form(True),
    include_niche: bool = Form(True),
    include_branded: bool = Form(False),
    brand_name: Optional[str] = Form(None)
):
    """
    Generate hashtags for an uploaded image
    
    Args:
        image: The image file to analyze
        platform: Social media platform (instagram, facebook, twitter, linkedin)
        max_hashtags: Maximum number of hashtags to generate
        include_trending: Include trending hashtags
        include_niche: Include niche-specific hashtags
        include_branded: Include branded hashtags
        brand_name: Brand name for branded hashtags
    
    Returns:
        HashtagGenerationResponse with generated hashtags and metadata
    """
    if not ai_analyzer or not content_categorizer or not hashtag_generator:
        raise HTTPException(
            status_code=500,
            detail="AI components not initialized"
        )
    
    # Validate file type
    if not image.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400,
            detail="File must be an image"
        )
    
    # Save uploaded file temporarily
    temp_file = None
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(image.filename).suffix) as temp_file:
            content = await image.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        logger.info(f"Processing image: {image.filename}")
        
        # Step 1: Categorize content
        category_result = content_categorizer.categorize_content(temp_file_path)
        
        if not category_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Content categorization failed: {category_result.error}"
            )
        
        # Step 2: Create hashtag request
        hashtag_request = HashtagRequest(
            image_path=temp_file_path,
            category_result=category_result,
            platform=platform,
            max_hashtags=max_hashtags,
            include_trending=include_trending,
            include_niche=include_niche,
            include_branded=include_branded,
            brand_name=brand_name
        )
        
        # Step 3: Generate hashtags
        hashtag_result = hashtag_generator.generate_enhanced_hashtags(hashtag_request)
        
        if not hashtag_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Hashtag generation failed: {hashtag_result.error}"
            )
        
        # Return response
        return HashtagGenerationResponse(
            hashtags=hashtag_result.hashtags,
            trending_hashtags=hashtag_result.trending_hashtags,
            niche_hashtags=hashtag_result.niche_hashtags,
            branded_hashtags=hashtag_result.branded_hashtags,
            ai_generated_hashtags=hashtag_result.ai_generated_hashtags,
            platform=hashtag_result.platform,
            total_count=hashtag_result.total_count,
            engagement_potential=hashtag_result.engagement_potential,
            trending_score=hashtag_result.trending_score,
            success=hashtag_result.success,
            error=hashtag_result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating hashtags: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "hashtag_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
