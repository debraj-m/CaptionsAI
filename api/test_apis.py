"""
Test script for CaptionsAI APIs
"""

import requests
import os
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def find_test_image():
    """Find a test image in the parent directory"""
    parent_dir = Path(__file__).parent.parent
    
    for ext in ['.jpg', '.jpeg', '.png']:
        for pattern in ['test*', 'sample*', 'example*']:
            files = list(parent_dir.glob(f"{pattern}{ext}"))
            if files:
                return files[0]
    return None


def test_caption_api():
    """Test the Caption API"""
    print("Testing Caption API...")
    
    # Find a test image
    test_image_path = find_test_image()
    
    if not test_image_path:
        print("❌ No test image found. Please add a test image to the project directory.")
        return False
    
    try:
        # Test basic caption generation
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'style': 'casual',
                'platform': 'instagram',
                'include_emojis': True,
                'caption_variants': 2
            }
            
            response = requests.post('http://localhost:8000/captions/generate', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Caption API working!")
            print(f"Generated caption: {result['caption']}")
            print(f"Alternatives: {len(result['alternative_captions'])}")
            return True
        else:
            print(f"❌ Caption API failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Caption API. Make sure it's running on port 8000.")
        return False
    except Exception as e:
        print(f"❌ Caption API test failed: {e}")
        return False


def test_hashtag_api():
    """Test the Hashtag API"""
    print("Testing Hashtag API...")
    
    # Find a test image
    test_image_path = find_test_image()
    
    if not test_image_path:
        print("❌ No test image found. Please add a test image to the project directory.")
        return False
    
    try:
        # Test basic hashtag generation
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'platform': 'instagram',
                'max_hashtags': 10,
                'include_trending': True,
                'include_niche': True
            }
            
            response = requests.post('http://localhost:8001/hashtags/generate', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Hashtag API working!")
            print(f"Generated hashtags: {len(result['hashtags'])}")
            print(f"Hashtags: {result['hashtags'][:5]}...")  # Show first 5
            return True
        else:
            print(f"❌ Hashtag API failed with status {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Hashtag API. Make sure it's running on port 8001.")
        return False
    except Exception as e:
        print(f"❌ Hashtag API test failed: {e}")
        return False


def test_health_endpoints():
    """Test health endpoints"""
    print("Testing health endpoints...")
    
    try:
        # Test Caption API health
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print("✅ Caption API health check passed")
        else:
            print("❌ Caption API health check failed")
            return False
        
        # Test Hashtag API health
        response = requests.get('http://localhost:8001/health')
        if response.status_code == 200:
            print("✅ Hashtag API health check passed")
        else:
            print("❌ Hashtag API health check failed")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to APIs for health check")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("CaptionsAI API Tests")
    print("=" * 50)
    
    # Check if APIs are running
    print("Make sure both APIs are running:")
    print("- Caption API: python caption_api.py (port 8000)")
    print("- Hashtag API: python hashtag_api.py (port 8001)")
    print("- Or run both: python run_apis.py")
    print()
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in a .env file or environment variable")
        return
    
    # Run tests
    health_ok = test_health_endpoints()
    
    if health_ok:
        caption_ok = test_caption_api()
        hashtag_ok = test_hashtag_api()
        
        print("\n" + "=" * 50)
        if caption_ok and hashtag_ok:
            print("🎉 All tests passed! Your APIs are working correctly.")
        else:
            print("❌ Some tests failed. Check the output above for details.")
    else:
        print("❌ Health checks failed. Make sure the APIs are running.")


if __name__ == "__main__":
    main()
