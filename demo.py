#!/usr/bin/env python3
"""
Demo script for Nano Banana - generates a sample image to test the API
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from utils.api_client import get_client
from PIL import Image

def main():
    """Run a simple demo"""
    print("🍌 Nano Banana Demo")
    print("=" * 40)
    
    # Load environment
    load_dotenv()
    
    # Get client
    client = get_client()
    
    if not client.is_ready():
        print("❌ Client not ready. Please check your API key in .env file")
        return
    
    print("✅ Client ready!")
    print("🎨 Generating demo image...")
    
    # Demo prompt
    prompt = (
        "A photorealistic image of a single nano banana on a clean white marble surface, "
        "illuminated by soft natural lighting, professional product photography style, "
        "sharp focus, minimal composition"
    )
    
    print(f"📝 Prompt: {prompt}")
    print("⏳ Please wait...")
    
    try:
        # Generate image
        response = client.generate_image(prompt)
        
        if response and response.get('images'):
            print(f"✅ Generated {len(response['images'])} image(s)!")
            
            # Save images
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for i, image in enumerate(response['images']):
                filename = f"demo_nano_banana_{timestamp}_{i+1}.png"
                filepath = os.path.join("generated_images", filename)
                
                # Create directory if it doesn't exist
                os.makedirs("generated_images", exist_ok=True)
                
                # Save image
                image.save(filepath)
                print(f"💾 Saved: {filepath}")
            
            # Display text response if any
            if response.get('text'):
                print("\n📝 AI Response:")
                for text in response['text']:
                    print(f"  {text}")
            
            print("\n🎉 Demo completed successfully!")
            print("💡 Open the saved image(s) to see the results")
            print("🚀 Run 'streamlit run app.py' to use the full app")
            
        else:
            print("❌ No images were generated")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("💡 Try checking your API key and internet connection")

if __name__ == "__main__":
    main()