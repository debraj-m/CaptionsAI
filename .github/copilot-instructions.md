<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# CaptionsAI Project Instructions

This is a modular AI-powered social media content generation tool that:

1. Analyzes media files using OpenAI's vision capabilities
2. Generates engaging captions for social media posts
3. Categorizes content automatically
4. Suggests relevant hashtags for Instagram and Facebook
5. Provides platform-specific formatting

## Key Design Principles

- **Modular Architecture**: Each component (AI analyzer, caption generator, hashtag generator, etc.) should be independent and testable
- **Platform Agnostic**: Core functionality should work regardless of social media platform
- **Extensible**: Easy to add new platforms or AI providers
- **Error Handling**: Robust error handling for API failures and invalid inputs
- **Configuration**: All settings should be configurable via environment variables

## Code Style Guidelines

- Use type hints throughout the codebase
- Follow PEP 8 naming conventions
- Include comprehensive docstrings for all classes and methods
- Use dataclasses for structured data
- Implement proper logging for debugging and monitoring

## Testing Approach

- Unit tests for each module
- Integration tests for API interactions
- Mock external dependencies in tests
- Test with various image formats and sizes
