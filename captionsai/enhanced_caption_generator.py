"""
Enhanced caption generation module with personalization and specificity
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .ai_analyzer import AIAnalyzer
from .content_categorizer import CategoryResult
import json
import re


logger = logging.getLogger(__name__)


@dataclass
class PersonalizationData:
    """User personalization data for better captions"""
    user_name: Optional[str] = None
    brand_name: Optional[str] = None
    brand_voice: Optional[str] = None  # casual, professional, funny, inspirational
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    interests: List[str] = None
    previous_captions: List[str] = None  # For learning user style
    brand_keywords: List[str] = None
    avoid_keywords: List[str] = None


@dataclass
class CaptionContext:
    """Additional context for caption generation"""
    time_of_day: Optional[str] = None
    season: Optional[str] = None
    event_type: Optional[str] = None
    mood: Optional[str] = None
    occasion: Optional[str] = None
    content_goal: Optional[str] = None  # engagement, awareness, sales, education


@dataclass
class EnhancedCaptionRequest:
    """Enhanced request data for caption generation"""
    image_path: str
    style: str = "casual"
    platform: str = "instagram"
    personalization: Optional[PersonalizationData] = None
    context: Optional[CaptionContext] = None
    category_result: Optional[CategoryResult] = None
    include_call_to_action: bool = True
    include_questions: bool = True
    include_emojis: bool = True
    caption_length: str = "medium"  # short, medium, long
    tone_modifiers: List[str] = None  # authentic, trendy, educational, storytelling


@dataclass
class EnhancedCaptionResult:
    """Enhanced result of caption generation"""
    caption: str
    style: str
    platform: str
    word_count: int
    character_count: int
    engagement_score: Optional[float] = None
    personalization_elements: List[str] = None
    call_to_action: Optional[str] = None
    hook: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


class EnhancedCaptionGenerator:
    """Enhanced caption generator with personalization and specificity"""
    
    def __init__(self, ai_analyzer: AIAnalyzer):
        """Initialize with AI analyzer"""
        self.ai_analyzer = ai_analyzer
        
        # Enhanced style prompts with personality
        self.enhanced_style_prompts = {
            "casual": {
                "base": "Write a relaxed, conversational caption that feels like talking to a friend",
                "elements": ["contractions", "casual language", "relatable tone"],
                "avoid": ["overly formal language", "corporate speak"]
            },
            "professional": {
                "base": "Write a polished, business-appropriate caption that establishes authority",
                "elements": ["industry expertise", "professional insights", "valuable information"],
                "avoid": ["casual slang", "overly personal details"]
            },
            "funny": {
                "base": "Write a humorous caption that entertains and brings joy",
                "elements": ["witty observations", "playful language", "light humor"],
                "avoid": ["offensive content", "inside jokes", "forced humor"]
            },
            "inspirational": {
                "base": "Write an uplifting caption that motivates and inspires action",
                "elements": ["positive messaging", "motivational quotes", "empowering language"],
                "avoid": ["negative language", "discouraging content"]
            },
            "storytelling": {
                "base": "Write a narrative caption that tells a compelling story",
                "elements": ["personal anecdotes", "narrative structure", "emotional connection"],
                "avoid": ["dry facts", "impersonal content"]
            },
            "educational": {
                "base": "Write an informative caption that teaches something valuable",
                "elements": ["useful tips", "how-to information", "educational value"],
                "avoid": ["overwhelming detail", "boring presentation"]
            }
        }
        
        # Platform-specific optimization
        self.platform_optimization = {
            "instagram": {
                "max_length": 2200,
                "optimal_length": 125,
                "engagement_tactics": ["questions", "emojis", "line_breaks", "hashtags"],
                "best_practices": ["hook_first_line", "visual_focus", "story_format"]
            },
            "facebook": {
                "max_length": 63206,
                "optimal_length": 80,
                "engagement_tactics": ["conversation_starters", "polls", "shares"],
                "best_practices": ["community_focus", "longer_form", "links_ok"]
            }
        }
        
        # Caption structure templates
        self.caption_structures = {
            "hook_story_cta": {
                "parts": ["hook", "story", "call_to_action"],
                "description": "Attention-grabbing opening, personal story, clear CTA"
            },
            "question_answer_engage": {
                "parts": ["question", "answer", "engagement"],
                "description": "Pose question, provide answer, encourage interaction"
            },
            "tip_explanation_example": {
                "parts": ["tip", "explanation", "example"],
                "description": "Share tip, explain why it works, give example"
            },
            "story_lesson_question": {
                "parts": ["story", "lesson", "question"],
                "description": "Tell story, extract lesson, ask audience question"
            }
        }
    
    def _analyze_image_in_detail(self, image_path: str) -> Dict[str, str]:
        """Get detailed image analysis for more specific captions"""
        
        analysis_prompts = {
            "visual_elements": """
            Analyze the visual elements in this image:
            - Main subjects (people, objects, animals)
            - Colors and lighting
            - Composition and framing
            - Background and setting
            - Mood and atmosphere
            - Any text or branding visible
            Keep it concise but comprehensive.
            """,
            
            "emotion_mood": """
            Analyze the emotional content and mood of this image:
            - What emotions does it evoke?
            - What's the overall mood or feeling?
            - What story might this image tell?
            - What might the viewer feel when seeing this?
            """,
            
            "context_situation": """
            Analyze the context and situation in this image:
            - What activity or event is happening?
            - What time of day or season might it be?
            - What location or setting is this?
            - What might have happened before or after this moment?
            """
        }
        
        analysis_results = {}
        
        for analysis_type, prompt in analysis_prompts.items():
            try:
                result = self.ai_analyzer.analyze_image(image_path, prompt)
                if result["success"]:
                    analysis_results[analysis_type] = result["content"]
                else:
                    analysis_results[analysis_type] = "Analysis not available"
            except Exception as e:
                logger.warning(f"Failed {analysis_type} analysis: {e}")
                analysis_results[analysis_type] = "Analysis not available"
        
        return analysis_results
    
    def _build_personalized_prompt(self, request: EnhancedCaptionRequest, image_analysis: Dict[str, str]) -> str:
        """Build a highly personalized prompt for caption generation"""
        
        style_info = self.enhanced_style_prompts.get(request.style, self.enhanced_style_prompts["casual"])
        platform_info = self.platform_optimization.get(request.platform, {})
        
        # Determine caption length
        length_guidelines = {
            "short": "Keep it concise, 1-2 sentences max",
            "medium": "Use 2-4 sentences for good engagement",
            "long": "Write a longer caption with multiple paragraphs if needed"
        }
        
        length_guide = length_guidelines.get(request.caption_length, length_guidelines["medium"])
        
        prompt = f"""
        Create an engaging, personalized social media caption based on this image analysis:
        
        IMAGE ANALYSIS:
        Visual Elements: {image_analysis.get('visual_elements', 'Not available')}
        Emotion/Mood: {image_analysis.get('emotion_mood', 'Not available')}
        Context: {image_analysis.get('context_situation', 'Not available')}
        
        STYLE REQUIREMENTS:
        - Style: {style_info['base']}
        - Include: {', '.join(style_info['elements'])}
        - Avoid: {', '.join(style_info['avoid'])}
        - Platform: {request.platform.title()}
        - Length: {length_guide}
        """
        
        # Add personalization
        if request.personalization:
            p = request.personalization
            
            if p.brand_name:
                prompt += f"- Brand: {p.brand_name}\n"
            
            if p.target_audience:
                prompt += f"- Target Audience: {p.target_audience}\n"
            
            if p.industry:
                prompt += f"- Industry: {p.industry}\n"
            
            if p.brand_voice:
                prompt += f"- Brand Voice: {p.brand_voice}\n"
            
            if p.interests:
                prompt += f"- User Interests: {', '.join(p.interests)}\n"
            
            if p.brand_keywords:
                prompt += f"- Include Keywords: {', '.join(p.brand_keywords)}\n"
            
            if p.avoid_keywords:
                prompt += f"- Avoid Keywords: {', '.join(p.avoid_keywords)}\n"
        
        # Add context
        if request.context:
            c = request.context
            
            if c.occasion:
                prompt += f"- Occasion: {c.occasion}\n"
            
            if c.content_goal:
                prompt += f"- Goal: {c.content_goal}\n"
            
            if c.mood:
                prompt += f"- Desired Mood: {c.mood}\n"
        
        # Add category information
        if request.category_result:
            prompt += f"- Content Category: {request.category_result.primary_category}\n"
            if request.category_result.secondary_categories:
                prompt += f"- Secondary Categories: {', '.join(request.category_result.secondary_categories)}\n"
        
        # Add engagement elements
        engagement_elements = []
        if request.include_call_to_action:
            engagement_elements.append("subtle call-to-action")
        if request.include_questions:
            engagement_elements.append("engaging question")
        if request.include_emojis:
            engagement_elements.append("relevant emojis")
        
        if engagement_elements:
            prompt += f"- Include: {', '.join(engagement_elements)}\n"
        
        # Explicitly handle emoji exclusion
        if not request.include_emojis:
            prompt += "- IMPORTANT: Do NOT use any emojis in the caption. Write plain text only.\n"
        
        # Add tone modifiers
        if request.tone_modifiers:
            prompt += f"- Tone Modifiers: {', '.join(request.tone_modifiers)}\n"
        
        prompt += """
        
        CAPTION REQUIREMENTS:
        1. Start with a hook that's SPECIFIC to what's actually in the image
        2. Write like a real person, not a marketing bot
        3. Use natural, conversational language (like you're posting on your personal account)
        4. Be specific about visual details you can see
        5. Avoid generic phrases like "vibes are in the air", "look at this", "feeling blessed"
        6. Don't use cliché expressions or overly enthusiastic language
        7. Make it personal and relatable
        8. Use line breaks sparingly for readability
        9. Keep it authentic - write how real people actually post
        10. Focus on the specific moment, event, or feeling captured in the image
        
        WRITING STYLE:
        - Write in first person when appropriate
        - Use specific details from the image
        - Keep the tone natural and conversational
        - Avoid marketing language or generic captions
        - Make it sound like something a friend would post
        - Be genuine and authentic
        
        Return the caption as a JSON object with this structure:
        {
            "caption": "The complete caption text",
            "hook": "The attention-grabbing first line",
            "call_to_action": "The CTA or engagement element",
            "personalization_elements": ["element1", "element2"],
            "engagement_score": 8.5
        }
        
        Return only the JSON response, nothing else.
        """
        
        return prompt
    
    def _parse_caption_response(self, response_text: str) -> Dict:
        """Parse the AI response and extract caption components"""
        
        # Clean the response
        response_text = response_text.strip()
        
        # Remove markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        try:
            data = json.loads(response_text)
            return data
        
        except json.JSONDecodeError:
            # Fallback: treat entire response as caption
            logger.warning("Failed to parse JSON response, using entire text as caption")
            return {
                "caption": response_text,
                "hook": response_text.split('\n')[0] if '\n' in response_text else response_text[:50],
                "call_to_action": None,
                "personalization_elements": [],
                "engagement_score": 5.0
            }
    
    def generate_enhanced_caption(self, request: EnhancedCaptionRequest) -> EnhancedCaptionResult:
        """
        Generate an enhanced, personalized caption
        
        Args:
            request: EnhancedCaptionRequest with image path and personalization data
            
        Returns:
            EnhancedCaptionResult with generated caption and metadata
        """
        try:
            # Get detailed image analysis
            logger.info("Analyzing image for detailed caption generation")
            image_analysis = self._analyze_image_in_detail(request.image_path)
            
            # Build personalized prompt
            prompt = self._build_personalized_prompt(request, image_analysis)
            
            # Generate caption
            result = self.ai_analyzer.analyze_image(request.image_path, prompt)
            
            if not result["success"]:
                return EnhancedCaptionResult(
                    caption="",
                    style=request.style,
                    platform=request.platform,
                    word_count=0,
                    character_count=0,
                    success=False,
                    error=result.get("error", "Unknown error occurred")
                )
            
            # Parse the response
            caption_data = self._parse_caption_response(result["content"])
            
            caption = caption_data.get("caption", "").strip()
            hook = caption_data.get("hook", "")
            call_to_action = caption_data.get("call_to_action", "")
            personalization_elements = caption_data.get("personalization_elements", [])
            engagement_score = caption_data.get("engagement_score", 5.0)
            
            # Calculate metrics
            word_count = len(caption.split())
            character_count = len(caption)
            
            logger.info(f"Generated enhanced caption: {character_count} chars, {word_count} words, score: {engagement_score}")
            
            return EnhancedCaptionResult(
                caption=caption,
                style=request.style,
                platform=request.platform,
                word_count=word_count,
                character_count=character_count,
                engagement_score=engagement_score,
                personalization_elements=personalization_elements,
                call_to_action=call_to_action,
                hook=hook,
                success=True
            )
            
        except Exception as e:
            logger.error(f"Error generating enhanced caption: {e}")
            return EnhancedCaptionResult(
                caption="",
                style=request.style,
                platform=request.platform,
                word_count=0,
                character_count=0,
                success=False,
                error=str(e)
            )
    
    def generate_multiple_variants(
        self, 
        request: EnhancedCaptionRequest, 
        count: int = 3
    ) -> List[EnhancedCaptionResult]:
        """
        Generate multiple caption variants with different approaches
        
        Args:
            request: EnhancedCaptionRequest with base requirements
            count: Number of variants to generate
            
        Returns:
            List of EnhancedCaptionResult objects
        """
        variants = []
        
        # Different approaches for variants
        variant_approaches = [
            {"tone_modifiers": ["authentic", "conversational"]},
            {"tone_modifiers": ["educational", "informative"]},
            {"tone_modifiers": ["storytelling", "personal"]},
            {"tone_modifiers": ["trendy", "current"]},
            {"tone_modifiers": ["inspirational", "motivational"]}
        ]
        
        for i in range(min(count, len(variant_approaches))):
            # Create variant request
            variant_request = EnhancedCaptionRequest(
                image_path=request.image_path,
                style=request.style,
                platform=request.platform,
                personalization=request.personalization,
                context=request.context,
                category_result=request.category_result,
                include_call_to_action=request.include_call_to_action,
                include_questions=request.include_questions,
                include_emojis=request.include_emojis,
                caption_length=request.caption_length,
                tone_modifiers=variant_approaches[i]["tone_modifiers"]
            )
            
            result = self.generate_enhanced_caption(variant_request)
            variants.append(result)
        
        return variants
    
    def analyze_caption_performance(self, caption: str, platform: str = "instagram") -> Dict[str, float]:
        """
        Analyze a caption for potential performance metrics
        
        Args:
            caption: The caption text to analyze
            platform: Social media platform
            
        Returns:
            Dictionary with performance predictions
        """
        
        # Basic metrics
        word_count = len(caption.split())
        character_count = len(caption)
        sentence_count = len([s for s in caption.split('.') if s.strip()])
        
        # Engagement elements
        has_question = '?' in caption
        has_emoji = any(ord(char) > 127 for char in caption)  # Basic emoji detection
        has_hashtag = '#' in caption
        has_mention = '@' in caption
        line_breaks = caption.count('\n')
        
        # Calculate engagement score
        engagement_score = 5.0  # Base score
        
        # Adjust based on elements
        if has_question:
            engagement_score += 1.5
        if has_emoji:
            engagement_score += 1.0
        if line_breaks > 0:
            engagement_score += 0.5
        if 50 <= character_count <= 150:  # Optimal length
            engagement_score += 1.0
        elif character_count > 300:
            engagement_score -= 0.5
        
        # Platform-specific adjustments
        if platform == "instagram":
            if has_hashtag:
                engagement_score += 0.5
            if word_count > 50:
                engagement_score -= 0.5
        elif platform == "facebook":
            if 20 <= word_count <= 80:
                engagement_score += 0.5
        
        # Cap the score
        engagement_score = min(10.0, max(1.0, engagement_score))
        
        return {
            "engagement_score": engagement_score,
            "readability_score": 8.0 if line_breaks > 0 else 6.0,
            "shareability_score": 7.5 if has_question or has_emoji else 5.0,
            "platform_optimization": 8.0 if character_count <= 150 else 6.0
        }
