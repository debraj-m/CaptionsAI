"""
Content categorization module
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .ai_analyzer import AIAnalyzer


logger = logging.getLogger(__name__)


@dataclass
class CategoryResult:
    """Result of content categorization"""
    primary_category: str
    secondary_categories: List[str]
    confidence_score: float
    description: str
    success: bool
    error: Optional[str] = None


class ContentCategorizer:
    """Categorizes content based on image analysis"""
    
    def __init__(self, ai_analyzer: AIAnalyzer):
        """Initialize with AI analyzer"""
        self.ai_analyzer = ai_analyzer
        
        # Predefined categories for social media content
        self.categories = {
            # Lifestyle
            "food": ["cooking", "dining", "recipes", "restaurants", "beverages"],
            "travel": ["destinations", "adventures", "culture", "landmarks", "transportation"],
            "fashion": ["outfits", "style", "accessories", "trends", "clothing"],
            "fitness": ["workout", "health", "sports", "yoga", "nutrition"],
            "beauty": ["skincare", "makeup", "haircare", "cosmetics", "self-care"],
            
            # Professional
            "business": ["corporate", "meetings", "office", "networking", "productivity"],
            "technology": ["gadgets", "software", "innovation", "digital", "ai"],
            "education": ["learning", "teaching", "books", "courses", "knowledge"],
            
            # Creative
            "art": ["painting", "drawing", "sculpture", "design", "creativity"],
            "photography": ["portraits", "landscape", "street", "macro", "abstract"],
            "music": ["instruments", "concerts", "recording", "performance", "audio"],
            
            # Personal
            "family": ["children", "parents", "relatives", "gatherings", "memories"],
            "pets": ["dogs", "cats", "animals", "pet care", "cute pets"],
            "home": ["interior", "decoration", "diy", "gardening", "organization"],
            
            # Entertainment
            "events": ["parties", "celebrations", "festivals", "concerts", "gatherings"],
            "hobbies": ["crafts", "collections", "games", "reading", "recreation"],
            "nature": ["outdoors", "wildlife", "plants", "environment", "seasons"],
            
            # Commercial
            "products": ["reviews", "unboxing", "recommendations", "shopping", "deals"],
            "services": ["consulting", "tutorials", "demonstrations", "support"],
            "brand": ["marketing", "promotion", "company", "identity", "awareness"]
        }
    
    def _build_categorization_prompt(self) -> str:
        """Build the AI prompt for content categorization"""
        
        categories_list = list(self.categories.keys())
        
        prompt = f"""
        Analyze this image and categorize the content for social media purposes.
        
        Available categories: {', '.join(categories_list)}
        
        Please provide your response in the following JSON format:
        {{
            "primary_category": "most_relevant_category",
            "secondary_categories": ["relevant_category_1", "relevant_category_2"],
            "confidence_score": 0.85,
            "description": "Brief description of what you see and why you chose these categories"
        }}
        
        GUIDELINES:
        - Choose the most accurate primary category from the list above
        - Include 1-3 secondary categories that also apply
        - Confidence score should be between 0.0 and 1.0
        - Base categorization only on what's actually visible in the image
        - If the content doesn't clearly fit any category, use the closest match and lower confidence
        
        Return only the JSON response, nothing else.
        """
        
        return prompt
    
    def categorize_content(self, image_path: str) -> CategoryResult:
        """
        Categorize content based on image analysis
        
        Args:
            image_path: Path to the image file
            
        Returns:
            CategoryResult with categorization data
        """
        try:
            # Build the prompt
            prompt = self._build_categorization_prompt()
            
            # Analyze image
            result = self.ai_analyzer.analyze_image(image_path, prompt)
            
            if not result["success"]:
                return CategoryResult(
                    primary_category="unknown",
                    secondary_categories=[],
                    confidence_score=0.0,
                    description="",
                    success=False,
                    error=result.get("error", "Unknown error occurred")
                )
            
            # Parse the JSON response
            response_text = result["content"].strip()
            
            # Remove any markdown formatting if present
            if response_text.startswith("```json"):
                response_text = response_text.replace("```json", "").replace("```", "").strip()
            elif response_text.startswith("```"):
                response_text = response_text.replace("```", "").strip()
            
            try:
                import json
                data = json.loads(response_text)
                
                primary_category = data.get("primary_category", "unknown")
                secondary_categories = data.get("secondary_categories", [])
                confidence_score = float(data.get("confidence_score", 0.0))
                description = data.get("description", "")
                
                # Validate categories exist in our predefined list
                valid_categories = list(self.categories.keys())
                
                if primary_category not in valid_categories:
                    primary_category = "unknown"
                    confidence_score *= 0.5  # Reduce confidence for unknown category
                
                # Filter valid secondary categories
                secondary_categories = [
                    cat for cat in secondary_categories 
                    if cat in valid_categories and cat != primary_category
                ]
                
                logger.info(f"Categorized as: {primary_category} (confidence: {confidence_score})")
                
                return CategoryResult(
                    primary_category=primary_category,
                    secondary_categories=secondary_categories,
                    confidence_score=confidence_score,
                    description=description,
                    success=True
                )
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                
                # Fallback: try to extract category from text
                response_lower = response_text.lower()
                best_match = "unknown"
                best_score = 0.0
                
                for category in self.categories.keys():
                    if category in response_lower:
                        best_match = category
                        best_score = 0.6  # Lower confidence for fallback
                        break
                
                return CategoryResult(
                    primary_category=best_match,
                    secondary_categories=[],
                    confidence_score=best_score,
                    description=response_text,
                    success=True
                )
                
        except Exception as e:
            logger.error(f"Error categorizing content: {e}")
            return CategoryResult(
                primary_category="unknown",
                secondary_categories=[],
                confidence_score=0.0,
                description="",
                success=False,
                error=str(e)
            )
    
    def get_category_subcategories(self, category: str) -> List[str]:
        """Get subcategories for a given category"""
        return self.categories.get(category, [])
    
    def get_all_categories(self) -> Dict[str, List[str]]:
        """Get all available categories and their subcategories"""
        return self.categories.copy()
