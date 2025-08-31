import os
from typing import List, Optional, Union
from PIL import Image
import streamlit as st
from google import genai
from google.genai import types
import io


class GeminiImageClient:
    """Singleton client for Gemini Image Generation API"""
    
    _instance = None
    _client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self.initialize_client()
    
    def initialize_client(self):
        """Initialize the Gemini client with API key"""
        api_key = self.get_api_key()
        if api_key:
            try:
                self._client = genai.Client(api_key=api_key)
                return True
            except Exception as e:
                st.error(f"Failed to initialize Gemini client: {str(e)}")
                return False
        return False
    
    def get_api_key(self) -> Optional[str]:
        """Get API key from environment, .env file, or Streamlit secrets"""
        # Try environment variable first
        api_key = os.getenv('GOOGLE_API_KEY')
        if api_key:
            return api_key
        
        # Try Streamlit secrets
        try:
            api_key = st.secrets.get('GOOGLE_API_KEY')
            if api_key:
                return api_key
        except:
            pass
        
        # Try loading from .env file
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                return api_key
        except ImportError:
            pass
        
        return None
    
    def is_ready(self) -> bool:
        """Check if client is ready to use"""
        return self._client is not None
    
    def generate_image(
        self,
        prompt: str,
        model: str = "gemini-2.5-flash-image-preview",
        response_modalities: List[str] = None
    ) -> Optional[dict]:
        """Generate image from text prompt"""
        if not self.is_ready():
            st.error("Client not initialized. Please check your API key.")
            return None
        
        if response_modalities is None:
            response_modalities = ['Text', 'Image']
        
        try:
            response = self._client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=response_modalities
                )
            )
            
            return self._process_response(response)
            
        except Exception as e:
            st.error(f"Error generating image: {str(e)}")
            return None
    
    def edit_image(
        self,
        prompt: str,
        images: Union[Image.Image, List[Image.Image]],
        model: str = "gemini-2.5-flash-image-preview"
    ) -> Optional[dict]:
        """Edit image(s) with text prompt"""
        if not self.is_ready():
            st.error("Client not initialized. Please check your API key.")
            return None
        
        try:
            # Prepare content list
            content = [prompt]
            
            if isinstance(images, Image.Image):
                content.append(images)
            elif isinstance(images, list):
                content.extend(images)
            
            response = self._client.models.generate_content(
                model=model,
                contents=content
            )
            
            return self._process_response(response)
            
        except Exception as e:
            st.error(f"Error editing image: {str(e)}")
            return None
    
    def create_chat(self, model: str = "gemini-2.5-flash-image-preview"):
        """Create a chat session for iterative image generation"""
        if not self.is_ready():
            st.error("Client not initialized. Please check your API key.")
            return None
        
        try:
            return self._client.chats.create(model=model)
        except Exception as e:
            st.error(f"Error creating chat session: {str(e)}")
            return None
    
    def send_chat_message(self, chat, message: str) -> Optional[dict]:
        """Send message to chat session"""
        if not chat:
            st.error("No chat session available.")
            return None
        
        try:
            response = chat.send_message(message)
            return self._process_response(response)
        except Exception as e:
            st.error(f"Error sending chat message: {str(e)}")
            return None
    
    def _process_response(self, response) -> dict:
        """Process API response and extract text and images"""
        result = {
            'text': [],
            'images': [],
            'raw_response': response
        }
        
        try:
            for part in response.parts:
                if part.text:
                    result['text'].append(part.text)
                elif hasattr(part, 'as_image'):
                    image = part.as_image()
                    if image:
                        result['images'].append(image)
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
        
        return result


def get_client() -> GeminiImageClient:
    """Get or create the singleton client instance"""
    return GeminiImageClient()