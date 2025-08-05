# CaptionsAI

An AI-powered tool that generates engaging social media captions, categorizes content, and suggests relevant hashtags for Instagram and Facebook using OpenAI's vision and language models.

## 🚀 New: REST APIs Available!

CaptionsAI now provides **two separate REST APIs** for easy integration:

- **Caption API** (Port 8000): Generate personalized captions
- **Hashtag API** (Port 8001): Generate relevant hashtags

👉 See [api/README.md](api/README.md) for detailed API documentation and usage examples.

## Features

- **🤖 AI-Powered Analysis**: OpenAI Vision API for intelligent image analysis
- **✍️ Caption Generation**: Create engaging captions in multiple styles (casual, professional, funny, inspirational, etc.)
- **🏷️ Smart Hashtag Generation**: Generate platform-optimized hashtags with trending insights
- **📊 Content Categorization**: Automatically categorize content into relevant topics
- **🎯 Personalization**: Customize captions based on brand voice, audience, and context
- **📱 Multi-Platform Support**: Optimized for Instagram, Facebook, Twitter, and LinkedIn
- **🔄 Multiple Variations**: Generate multiple caption options to choose from
- **🔧 Modular Architecture**: Easy to extend and customize
- **🌐 REST APIs**: Easy integration into web applications and services

## 📋 Requirements

- Python 3.8 or higher
- OpenAI API key
- Internet connection for API calls
- Supported image formats: JPG, PNG, GIF, BMP, WebP

## 🛠️ Installation

1. Clone or download this repository:
```bash
cd CaptionsAI
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
.venv\Scripts\activate  # On Windows
# source .venv/bin/activate  # On macOS/Linux
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root (copy from `.env.example` if available)

2. Add your OpenAI API key to the `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

3. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)

## 📖 Usage

### 🌐 REST APIs (Recommended)

**Quick Start:**
```bash
# Start both APIs
python api/run_apis.py

# Or start individually
python api/caption_api.py    # Caption API on port 8000
python api/hashtag_api.py    # Hashtag API on port 8001
```

**Test the APIs:**
```bash
python api/demo_apis.py      # Interactive demo
python api/test_apis.py      # API tests
```

**API Endpoints:**
- Caption API: `http://localhost:8000` ([Docs](http://localhost:8000/docs))
- Hashtag API: `http://localhost:8001` ([Docs](http://localhost:8001/docs))

See [api/README.md](api/README.md) for complete API documentation.

### 🖥️ Command Line Interface

Basic usage:
```bash
python enhanced_cli.py your_image.jpg
```

Advanced options:
```bash
# Specify platform and style
python enhanced_cli.py your_image.jpg --platform instagram --style casual

# Generate for multiple platforms
python enhanced_cli.py your_image.jpg --platforms instagram facebook

# Generate multiple caption variations
python enhanced_cli.py your_image.jpg --multiple-captions 3

# Include brand information
python enhanced_cli.py your_image.jpg --brand "YourBrand" --audience "young adults"

# Save results to file
python enhanced_cli.py your_image.jpg --output results.json --format json
```

### Python API

```python
from captionsai.enhanced_main import CaptionsAI, ContentRequest

# Initialize
ai = CaptionsAI()

# Create request
request = ContentRequest(
    image_path="your_image.jpg",
    platform="instagram",
    style="casual",
    brand_name="YourBrand",
    max_hashtags=15
)

# Generate content
result = ai.generate_content(request)

if result.success:
    print("Caption:", result.post.caption)
    print("Hashtags:", result.post.hashtags)
    print("Category:", result.post.category)
```

## Project Structure

```
CaptionsAI/
├── api/                               # REST API Components
│   ├── caption_api.py                 # Caption generation API
│   ├── hashtag_api.py                 # Hashtag generation API
│   ├── run_apis.py                    # Run both APIs
│   ├── test_apis.py                   # API test suite
│   ├── demo_apis.py                   # API demo script
│   └── README.md                      # API documentation
├── captionsai/                        # Core Library
│   ├── __init__.py                    # Package initialization
│   ├── config.py                      # Configuration management
│   ├── ai_analyzer.py                 # OpenAI API integration
│   ├── enhanced_caption_generator.py  # Caption generation logic
│   ├── content_categorizer.py         # Content categorization
│   ├── hashtag_generator.py           # Hashtag generation
│   ├── platform_adapters.py           # Platform-specific formatting
│   ├── trending_hashtag_fetcher.py    # Trending hashtags
│   └── enhanced_main.py               # Main orchestrator class
├── enhanced_cli.py                    # Command line interface
├── enhanced_example.py                # Usage examples
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
└── README.md                          # This file
```

## Supported Platforms

### Instagram
- Caption Length: Up to 2,200 characters (optimal: ~125)
- Hashtags: Up to 30 (optimal: 8-15)
- Features: Stories, Reels, hashtag strategy
- Algorithm: Favors engagement, saves, shares

### Facebook
- Caption Length: Up to 63,206 characters (optimal: ~40)
- Hashtags: Up to 10 (optimal: 3-7)
- Features: Links, events, longer content
- Algorithm: Favors meaningful conversations

## Content Categories

The AI automatically categorizes content into relevant topics:

- **Lifestyle**: food, travel, fashion, fitness, beauty
- **Professional**: business, technology, education
- **Creative**: art, photography, music
- **Personal**: family, pets, home
- **Entertainment**: events, hobbies, nature
- **Commercial**: products, services, brand

## Caption Styles

Choose from multiple caption styles:

- **Casual**: Friendly, conversational tone
- **Professional**: Polished, business-appropriate
- **Funny**: Humorous, witty content
- **Inspirational**: Motivational, uplifting
- **Storytelling**: Narrative, experience-sharing
- **Educational**: Informative, teaching-focused

## API Reference

### CaptionsAI Class

```python
class CaptionsAI:
    def __init__(self, config_path: Optional[str] = None)
    def generate_content(self, request: ContentRequest) -> ContentResult
    def generate_for_multiple_platforms(self, request: ContentRequest, platforms: List[str]) -> Dict[str, ContentResult]
    def analyze_image_only(self, image_path: str) -> Dict[str, Any]
    def get_supported_platforms(self) -> List[str]
    def get_available_styles(self) -> List[str]
```

### ContentRequest

```python
@dataclass
class ContentRequest:
    image_path: str
    platform: str = "instagram"
    style: str = "casual"
    target_audience: Optional[str] = None
    brand_name: Optional[str] = None
    brand_voice: Optional[str] = None
    max_hashtags: int = 15
    include_call_to_action: bool = True
    generate_multiple_captions: bool = False
    caption_count: int = 3
```

## Configuration Options

Environment variables in `.env` file:

```env
# Required
OPENAI_API_KEY=your_api_key

# Optional customization
DEFAULT_CAPTION_STYLE=casual
MAX_HASHTAGS=15
SUPPORTED_PLATFORMS=instagram,facebook
AI_MODEL=gpt-4-vision-preview
MAX_TOKENS=500
TEMPERATURE=0.7
DEBUG=false
```

## Examples

### Example 1: Food Photo for Instagram

```python
request = ContentRequest(
    image_path="food_photo.jpg",
    platform="instagram",
    style="casual",
    max_hashtags=12
)

result = ai.generate_content(request)
# Output: Engaging food caption with relevant hashtags
```

### Example 2: Business Content for Multiple Platforms

```python
request = ContentRequest(
    image_path="office_meeting.jpg",
    style="professional",
    brand_name="TechCorp",
    target_audience="business professionals"
)

results = ai.generate_for_multiple_platforms(request, ["instagram", "facebook"])
# Output: Platform-optimized professional content
```

### Example 3: Travel Photo with Multiple Captions

```python
request = ContentRequest(
    image_path="beach_sunset.jpg",
    platform="instagram",
    style="inspirational",
    generate_multiple_captions=True,
    caption_count=3
)

result = ai.generate_content(request)
# Output: 3 different inspirational captions + hashtags
```

## Testing the Setup

Run the test script to verify everything is working:

```bash
python test_setup.py
```

## Error Handling

The system includes comprehensive error handling:

- **API Failures**: Graceful handling of OpenAI API errors
- **Invalid Images**: File format and existence validation
- **Configuration Issues**: Clear error messages for setup problems
- **Rate Limiting**: Proper handling of API rate limits

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the coding guidelines in `.github/copilot-instructions.md`
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: Report bugs via GitHub Issues
- **Documentation**: Check the code comments and docstrings
- **Examples**: See `enhanced_example.py` for usage patterns

## Roadmap

- [ ] Support for more platforms (Twitter, LinkedIn, TikTok)
- [ ] Video content analysis
- [ ] Bulk processing capabilities
- [ ] Analytics and performance tracking
- [ ] Custom AI model fine-tuning
- [ ] Web interface
- [ ] Browser extension

---

**Built for social media creators and marketers**
