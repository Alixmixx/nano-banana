#!/usr/bin/env python3
"""
Test script for Nano Banana API integration
"""

import os
import sys
from dotenv import load_dotenv
from utils.api_client import get_client

def test_api_setup():
    """Test basic API setup and connection"""
    print("🍌 Testing Nano Banana API Setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Get client
    client = get_client()
    
    # Check API key
    api_key = client.get_api_key()
    if not api_key:
        print("❌ No API key found!")
        print("Please set GOOGLE_API_KEY in your .env file or environment variables")
        return False
    
    print(f"✅ API key found (ends with: ...{api_key[-4:]})")
    
    # Test client initialization
    if client.is_ready():
        print("✅ Client initialized successfully")
    else:
        print("❌ Client failed to initialize")
        return False
    
    return True

def test_simple_generation():
    """Test simple image generation"""
    print("\n🎨 Testing simple image generation...")
    
    client = get_client()
    if not client.is_ready():
        print("❌ Client not ready")
        return False
    
    try:
        # Simple test prompt
        test_prompt = "A simple drawing of a banana"
        print(f"Prompt: {test_prompt}")
        
        response = client.generate_image(test_prompt)
        
        if response and response.get('images'):
            print(f"✅ Generated {len(response['images'])} image(s)")
            return True
        else:
            print("❌ No images generated")
            return False
            
    except Exception as e:
        print(f"❌ Error during generation: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("🍌 NANO BANANA API TEST")
    print("=" * 50)
    
    # Test API setup
    if not test_api_setup():
        print("\n❌ API setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Test simple generation (commented out by default to avoid using API credits)
    # Uncomment the following lines if you want to test actual image generation
    """
    if not test_simple_generation():
        print("\n❌ Image generation test failed.")
        sys.exit(1)
    """
    
    print("\n" + "=" * 50)
    print("✅ ALL TESTS PASSED!")
    print("✅ Your Nano Banana setup is ready!")
    print("✅ Run 'streamlit run app.py' to start the app")
    print("=" * 50)

if __name__ == "__main__":
    main()