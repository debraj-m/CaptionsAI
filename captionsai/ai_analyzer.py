"""
Core AI analyzer using OpenAI Vision API
"""

import base64
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image
import io

from openai import OpenAI
from .config import AIConfig


logger = logging.getLogger(__name__)


class AIAnalyzer:
    """Core AI analyzer for image analysis and content generation"""
    
    def __init__(self, config: AIConfig):
        """Initialize the AI analyzer with configuration"""
        self.config = config
        self.client = OpenAI(api_key=config.openai_api_key)
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        try:
            # Open and potentially resize image to reduce API costs
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for efficiency)
                max_size = 1024
                if max(img.size) > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
                
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze image using OpenAI Vision API
        
        Args:
            image_path: Path to the image file
            prompt: Analysis prompt for the AI
            
        Returns:
            Dict containing the AI response
        """
        try:
            # Validate image file exists
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Encode image
            base64_image = self._encode_image(image_path)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image {image_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
    
    def generate_text(self, prompt: str) -> Dict[str, Any]:
        """
        Generate text using OpenAI API (no image)
        
        Args:
            prompt: Text prompt for generation
            
        Returns:
            Dict containing the AI response
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",  # Use text model for non-image tasks
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            return {
                "success": True,
                "content": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
