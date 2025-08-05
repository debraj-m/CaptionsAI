"""
FastAPI server for CaptionsAI Caption Generation
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
import json

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from captionsai.ai_analyzer import AIAnalyzer
from captionsai.content_categorizer import ContentCategorizer
from captionsai.enhanced_caption_generator import (
    EnhancedCaptionGenerator, 
    EnhancedCaptionRequest,
    PersonalizationData,
    CaptionContext
)
from captionsai.config import AIConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CaptionsAI Caption API",
    description="AI-powered caption generation for social media content",
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
caption_generator = None


class PersonalizationDataModel(BaseModel):
    """Pydantic model for personalization data"""
    user_name: Optional[str] = None
    brand_name: Optional[str] = None
    brand_voice: Optional[str] = None
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    interests: List[str] = []
    previous_captions: List[str] = []
    brand_keywords: List[str] = []
    avoid_keywords: List[str] = []


class CaptionContextModel(BaseModel):
    """Pydantic model for caption context"""
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    event_type: Optional[str] = None
    mood: Optional[str] = None
    occasion: Optional[str] = None
    content_goal: Optional[str] = None


class CaptionGenerationRequest(BaseModel):
    """Request model for caption generation"""
    style: str = "casual"
    platform: str = "instagram"
    personalization: Optional[PersonalizationDataModel] = None
    context: Optional[CaptionContextModel] = None
    include_emojis: bool = True
    include_hashtags: bool = False
    max_length: Optional[int] = None
    caption_variants: int = 1


class CaptionGenerationResponse(BaseModel):
    """Response model for caption generation"""
    caption: str
    alternative_captions: List[str]
    platform: str
    style: str
    word_count: int
    character_count: int
    personalization_applied: List[str]
    success: bool
    error: Optional[str] = None


@app.on_event("startup")
async def startup_event():
    """Initialize AI components on startup"""
    global ai_analyzer, content_categorizer, caption_generator
    
    try:
        # Get OpenAI API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize AI components
        ai_config = AIConfig(openai_api_key=api_key)
        ai_analyzer = AIAnalyzer(ai_config)
        content_categorizer = ContentCategorizer(ai_analyzer)
        caption_generator = EnhancedCaptionGenerator(ai_analyzer)
        
        logger.info("AI components initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize AI components: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CaptionsAI Caption API",
        "version": "1.0.0",
        "description": "AI-powered caption generation for social media content",
        "endpoints": {
            "generate_caption": "/captions/generate",
            "health": "/health"
        },
        "supported_platforms": ["instagram", "facebook", "twitter", "linkedin"],
        "supported_styles": ["casual", "professional", "funny", "inspirational", "promotional"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ai_components": {
            "ai_analyzer": ai_analyzer is not None,
            "content_categorizer": content_categorizer is not None,
            "caption_generator": caption_generator is not None
        }
    }


@app.post("/captions/generate", response_model=CaptionGenerationResponse)
async def generate_caption(
    image: UploadFile = File(...),
    style: str = Form("casual"),
    platform: str = Form("instagram"),
    include_emojis: bool = Form(True),
    include_hashtags: bool = Form(False),
    max_length: Optional[int] = Form(None),
    caption_variants: int = Form(1),
    personalization: Optional[str] = Form(None),  # JSON string
    context: Optional[str] = Form(None)  # JSON string
):
    """
    Generate captions for an uploaded image
    
    Args:
        image: The image file to analyze
        style: Caption style (casual, professional, funny, inspirational, promotional)
        platform: Social media platform (instagram, facebook, twitter, linkedin)
        include_emojis: Include emojis in the caption
        include_hashtags: Include hashtags in the caption
        max_length: Maximum caption length
        caption_variants: Number of caption variants to generate
        personalization: JSON string with personalization data
        context: JSON string with caption context
    
    Returns:
        CaptionGenerationResponse with generated captions and metadata
    """
    if not ai_analyzer or not content_categorizer or not caption_generator:
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
    
    # Parse personalization and context JSON strings
    personalization_data = None
    caption_context = None
    
    try:
        if personalization:
            personalization_dict = json.loads(personalization)
            personalization_data = PersonalizationData(**personalization_dict)
        
        if context:
            context_dict = json.loads(context)
            caption_context = CaptionContext(**context_dict)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON in personalization or context: {e}"
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
        
        # Step 2: Create caption request
        caption_request = EnhancedCaptionRequest(
            image_path=temp_file_path,
            style=style,
            platform=platform,
            personalization=personalization_data,
            context=caption_context,
            include_emojis=include_emojis,
            include_hashtags=include_hashtags,
            max_length=max_length,
            caption_variants=caption_variants,
            category_result=category_result
        )
        
        # Step 3: Generate captions
        caption_result = caption_generator.generate_enhanced_caption(caption_request)
        
        if not caption_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Caption generation failed: {caption_result.error}"
            )
        
        # Return response
        return CaptionGenerationResponse(
            caption=caption_result.caption,
            alternative_captions=caption_result.alternative_captions,
            platform=caption_result.platform,
            style=caption_result.style,
            word_count=caption_result.word_count,
            character_count=caption_result.character_count,
            personalization_applied=caption_result.personalization_applied,
            success=caption_result.success,
            error=caption_result.error
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating caption: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


@app.post("/captions/batch", response_model=List[CaptionGenerationResponse])
async def generate_captions_batch(
    request: CaptionGenerationRequest,
    images: List[UploadFile] = File(...)
):
    """
    Generate captions for multiple images in batch
    
    Args:
        request: Caption generation request parameters
        images: List of image files to analyze
    
    Returns:
        List of CaptionGenerationResponse for each image
    """
    if len(images) > 10:  # Limit batch size
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 images allowed per batch request"
        )
    
    results = []
    for image in images:
        try:
            # Process each image using the single generation endpoint logic
            # This is a simplified version - in production, you'd want to optimize this
            result = await generate_caption(
                image=image,
                style=request.style,
                platform=request.platform,
                include_emojis=request.include_emojis,
                include_hashtags=request.include_hashtags,
                max_length=request.max_length,
                caption_variants=request.caption_variants,
                personalization=json.dumps(request.personalization.dict()) if request.personalization else None,
                context=json.dumps(request.context.dict()) if request.context else None
            )
            results.append(result)
        except Exception as e:
            # Add error result for failed images
            results.append(CaptionGenerationResponse(
                caption="",
                alternative_captions=[],
                platform=request.platform,
                style=request.style,
                word_count=0,
                character_count=0,
                personalization_applied=[],
                success=False,
                error=str(e)
            ))
    
    return results


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the server
    uvicorn.run(
        "caption_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
