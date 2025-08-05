"""
Demo script showing how to use the CaptionsAI APIs
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))


def find_test_image():
    """Find a test image in the parent directory"""
    parent_dir = Path(__file__).parent.parent
    
    # Look for existing images
    for ext in ['.jpg', '.jpeg', '.png']:
        for pattern in ['test*', 'sample*', 'example*', '*.jpg', '*.jpeg', '*.png']:
            files = list(parent_dir.glob(pattern))
            if files:
                return files[0]
    return None


def create_test_image_if_needed():
    """Create a simple test image if none exists"""
    # Look for existing images
    test_image_path = find_test_image()
    if test_image_path:
        return test_image_path
    
    # If no images found, create a simple one in parent directory
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        parent_dir = Path(__file__).parent.parent
        
        # Create a simple test image
        img = Image.new('RGB', (400, 300), color='lightblue')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        text = "CaptionsAI Test Image"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        position = ((400 - text_width) // 2, (300 - text_height) // 2)
        draw.text(position, text, fill='darkblue', font=font)
        
        # Save the test image in parent directory
        test_image_path = parent_dir / 'test_image.jpg'
        img.save(test_image_path)
        print(f"📸 Created test image: {test_image_path}")
        return test_image_path
        
    except ImportError:
        print("❌ Pillow not available, cannot create test image")
        print("   Please add an image file to the project directory")
        return None
    except Exception as e:
        print(f"❌ Could not create test image: {e}")
        return None


def demo_caption_api():
    """Demonstrate the Caption API"""
    print("🎨 Caption API Demo")
    print("-" * 40)
    
    # Create a simple test image if none exists
    test_image_path = create_test_image_if_needed()
    
    if not test_image_path:
        print("❌ No test image available")
        return
    
    try:
        # Basic caption generation
        print("📸 Generating basic caption...")
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
            print(f"✅ Success!")
            print(f"   Main Caption: {result['caption']}")
            print(f"   Alternatives: {len(result['alternative_captions'])}")
            for i, alt in enumerate(result['alternative_captions'][:2], 1):
                print(f"   Alt {i}: {alt}")
            print(f"   Word Count: {result['word_count']}")
            print(f"   Character Count: {result['character_count']}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
        
        print()
        
        # Advanced caption with personalization
        print("🎯 Generating personalized caption...")
        personalization = {
            "brand_name": "TechStartup",
            "brand_voice": "professional",
            "target_audience": "entrepreneurs",
            "industry": "technology"
        }
        
        context = {
            "content_goal": "engagement",
            "mood": "inspiring"
        }
        
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'style': 'professional',
                'platform': 'linkedin',
                'include_emojis': False,
                'personalization': json.dumps(personalization),
                'context': json.dumps(context)
            }
            
            response = requests.post('http://localhost:8000/captions/generate', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Personalized Caption: {result['caption']}")
            print(f"   Applied: {', '.join(result['personalization_applied'])}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Caption API. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"❌ Error: {e}")


def demo_hashtag_api():
    """Demonstrate the Hashtag API"""
    print("🏷️  Hashtag API Demo")
    print("-" * 40)
    
    # Create a simple test image if none exists
    test_image_path = create_test_image_if_needed()
    
    if not test_image_path:
        print("❌ No test image available")
        return
    
    try:
        # Basic hashtag generation
        print("📱 Generating Instagram hashtags...")
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'platform': 'instagram',
                'max_hashtags': 15,
                'include_trending': True,
                'include_niche': True
            }
            
            response = requests.post('http://localhost:8001/hashtags/generate', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Total Hashtags: {result['total_count']}")
            print(f"   Main Hashtags: {', '.join(result['hashtags'][:8])}")
            if result['trending_hashtags']:
                print(f"   Trending: {', '.join(result['trending_hashtags'][:5])}")
            if result['niche_hashtags']:
                print(f"   Niche: {', '.join(result['niche_hashtags'][:5])}")
            if result.get('engagement_potential'):
                print(f"   Engagement Potential: {result['engagement_potential']:.2f}")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
        
        print()
        
        # Branded hashtags
        print("🏢 Generating branded hashtags...")
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            data = {
                'platform': 'instagram',
                'max_hashtags': 10,
                'include_branded': True,
                'brand_name': 'TechCorp'
            }
            
            response = requests.post('http://localhost:8001/hashtags/generate', files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            if result['branded_hashtags']:
                print(f"   Branded Hashtags: {', '.join(result['branded_hashtags'])}")
            else:
                print("   No branded hashtags generated")
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Hashtag API. Make sure it's running on port 8001.")
    except Exception as e:
        print(f"❌ Error: {e}")


def check_apis_running():
    """Check if both APIs are running"""
    try:
        # Check Caption API
        response = requests.get('http://localhost:8000/health', timeout=2)
        caption_api_ok = response.status_code == 200
    except:
        caption_api_ok = False
    
    try:
        # Check Hashtag API
        response = requests.get('http://localhost:8001/health', timeout=2)
        hashtag_api_ok = response.status_code == 200
    except:
        hashtag_api_ok = False
    
    return caption_api_ok, hashtag_api_ok


def main():
    """Run the demo"""
    print("🚀 CaptionsAI APIs Demo")
    print("=" * 50)
    
    # Check if APIs are running
    caption_ok, hashtag_ok = check_apis_running()
    
    if not caption_ok or not hashtag_ok:
        print("⚠️  APIs Status:")
        print(f"   Caption API (port 8000): {'✅ Running' if caption_ok else '❌ Not running'}")
        print(f"   Hashtag API (port 8001): {'✅ Running' if hashtag_ok else '❌ Not running'}")
        print()
        print("To start the APIs:")
        print("   Option 1: python run_apis.py (both APIs)")
        print("   Option 2: python caption_api.py & python hashtag_api.py (separate)")
        print("   Option 3: Use VS Code tasks (Ctrl+Shift+P > Tasks: Run Task)")
        print()
        
        if not caption_ok and not hashtag_ok:
            print("❌ Both APIs are down. Please start them first.")
            return
    
    print("🎉 APIs are running! Starting demo...\n")
    
    if caption_ok:
        demo_caption_api()
        print()
    
    if hashtag_ok:
        demo_hashtag_api()
        print()
    
    print("=" * 50)
    print("🎊 Demo completed!")
    print()
    print("💡 Next steps:")
    print("   • Check the API documentation: http://localhost:8000/docs and http://localhost:8001/docs")
    print("   • Test with your own images")
    print("   • Integrate into your applications")
    print("   • Customize personalization and context parameters")


if __name__ == "__main__":
    main()
