"""
FastAPI Implementation of Google Gemini Image Generation API

This module provides a complete FastAPI server implementation that wraps the Google Gemini
Image Generation API with proper validation, error handling, and documentation.

Usage:
    pip install fastapi uvicorn python-multipart google-genai pillow
    uvicorn fastapi_implementation:app --reload
"""

import os
import io
import base64
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
from PIL import Image
import google.genai as genai
from google.genai import types

# Initialize Gemini client
security = HTTPBearer()

# In-memory storage for chat sessions (use Redis/database in production)
chat_sessions: Dict[str, Any] = {}

# Configuration
class Settings:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    DEFAULT_MODEL = "gemini-2.5-flash-image-preview"
    MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB
    MAX_PROMPT_LENGTH = 2000

settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Gemini client on startup
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is required")
    
    genai.configure(api_key=settings.GOOGLE_API_KEY)
    yield

app = FastAPI(
    title="Google Gemini Image Generation API",
    description="Complete API for Google's Gemini Image Generation capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class ResponseModality(str, Enum):
    TEXT = "Text"
    IMAGE = "Image"

class CompositionStyle(str, Enum):
    BLEND = "blend"
    REPLACE = "replace"
    OVERLAY = "overlay"
    MONTAGE = "montage"

class ContentType(str, Enum):
    STORY = "story"
    RECIPE = "recipe"
    TUTORIAL = "tutorial"
    COMIC = "comic"
    CUSTOM = "custom"

class StyleType(str, Enum):
    VAN_GOGH = "van_gogh"
    PICASSO = "picasso"
    MONET = "monet"
    DIGITAL_ART = "digital_art"
    ANIME = "anime"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    PHOTOGRAPHIC = "photographic"
    MINIMALIST = "minimalist"
    ABSTRACT = "abstract"

class Direction(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    ALL = "all"

# Request Models
class TextToImageRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=2000, description="Detailed text description for image generation")
    model: str = Field(default=settings.DEFAULT_MODEL, description="Gemini model to use")
    response_modalities: List[ResponseModality] = Field(default=[ResponseModality.TEXT, ResponseModality.IMAGE])
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0, description="Controls randomness")
    top_k: Optional[int] = Field(default=40, ge=1, le=100, description="Limits token selection")
    top_p: Optional[float] = Field(default=0.95, ge=0.0, le=1.0, description="Nucleus sampling threshold")

class ImageEditRequest(BaseModel):
    prompt: str = Field(..., min_length=5, max_length=1000, description="Instructions for editing the image")
    model: str = Field(default=settings.DEFAULT_MODEL)
    preserve_subject: bool = Field(default=True, description="Whether to preserve the main subject")
    edit_strength: float = Field(default=0.8, ge=0.1, le=1.0, description="Strength of the editing effect")

class MultiImageRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=1000, description="Instructions for combining images")
    model: str = Field(default=settings.DEFAULT_MODEL)
    composition_style: CompositionStyle = Field(default=CompositionStyle.BLEND, description="Style of composition")

class ChatCreateRequest(BaseModel):
    model: str = Field(default=settings.DEFAULT_MODEL)
    system_prompt: Optional[str] = Field(None, description="Initial system instructions")

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000, description="Text message or instruction")
    continue_generation: bool = Field(default=True, description="Whether to continue from previous generation")

class StoryGenerationRequest(BaseModel):
    description: str = Field(..., min_length=20, max_length=2000, description="Overall description of the story")
    num_images: int = Field(..., ge=2, le=15, description="Number of images in the sequence")
    content_type: ContentType = Field(default=ContentType.STORY, description="Type of sequential content")
    style: Optional[str] = Field(None, description="Visual style for the sequence")
    model: str = Field(default=settings.DEFAULT_MODEL)

class InpaintRequest(BaseModel):
    prompt: str = Field(..., description="Description of what to paint in the region")
    region_description: Optional[str] = Field(None, description="Natural language description of the region")
    model: str = Field(default=settings.DEFAULT_MODEL)

class OutpaintRequest(BaseModel):
    prompt: str = Field(..., description="Description of how to extend the image")
    direction: List[Direction] = Field(..., min_items=1, description="Directions to extend the image")
    extension_ratio: float = Field(default=0.5, ge=0.1, le=2.0, description="How much to extend")
    model: str = Field(default=settings.DEFAULT_MODEL)

class StyleTransferRequest(BaseModel):
    style: Optional[StyleType] = Field(None, description="Predefined style name")
    style_strength: float = Field(default=0.8, ge=0.1, le=1.0, description="Strength of style application")
    preserve_content: bool = Field(default=True, description="Whether to preserve original content structure")
    model: str = Field(default=settings.DEFAULT_MODEL)

# Response Models
class ImageMetadata(BaseModel):
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    generation_time: float
    image_dimensions: Optional[Dict[str, int]] = None
    safety_ratings: Optional[List[Dict[str, str]]] = None

class ImageGenerationResponse(BaseModel):
    text: List[str] = Field(default=[], description="AI-generated text descriptions")
    images: List[str] = Field(default=[], description="Base64-encoded generated images")
    metadata: ImageMetadata

class StoryImage(BaseModel):
    image: str = Field(..., description="Base64-encoded image")
    sequence_number: int
    description: str
    timestamp: datetime

class StoryMetadata(BaseModel):
    total_images: int
    content_type: str
    generation_time: float
    total_tokens: int

class StoryGenerationResponse(BaseModel):
    images: List[StoryImage]
    story_metadata: StoryMetadata

class ChatSession(BaseModel):
    session_id: str = Field(..., description="Unique session identifier")
    created_at: datetime
    model: str
    message_count: int = Field(default=0)
    context_length: int = Field(default=0, description="Current context window usage")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    request_id: str = Field(..., description="Unique request identifier")

# Utility Functions
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Authorization header."""
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="API key required")
    
    # In production, verify against your API key database
    # For demo purposes, we accept any key that matches the environment variable
    if credentials.credentials != settings.GOOGLE_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return credentials.credentials

def validate_image_file(file: UploadFile) -> Image.Image:
    """Validate and convert uploaded file to PIL Image."""
    if file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes")
    
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        image = Image.open(io.BytesIO(file.file.read()))
        if image.mode == 'RGBA':
            # Convert RGBA to RGB with white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        return image
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image file: {str(e)}")

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return base64.b64encode(buffer.getvalue()).decode()

async def generate_with_gemini(prompt: str, images: Optional[List[Image.Image]] = None, model: str = settings.DEFAULT_MODEL) -> Dict[str, Any]:
    """Generate content using Gemini API."""
    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        
        # Prepare content
        content_parts = [prompt]
        if images:
            content_parts.extend(images)
        
        # Generate content
        response = client.models.generate_content(
            model=model,
            contents=content_parts,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'],
                temperature=1.0
            )
        )
        
        # Process response
        result = {
            'text': [],
            'images': [],
            'raw_response': response
        }
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                result['text'].append(part.text)
            elif hasattr(part, 'inline_data'):
                # Convert binary data to PIL Image and then to base64
                image_data = part.inline_data.data
                image = Image.open(io.BytesIO(image_data))
                result['images'].append(image_to_base64(image))
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

def create_metadata(response_data: Dict[str, Any], generation_time: float, model: str) -> ImageMetadata:
    """Create metadata from response."""
    return ImageMetadata(
        model=model,
        prompt_tokens=45,  # Estimate, not available in current API
        completion_tokens=1290,  # Estimate for image generation
        total_tokens=1335,
        generation_time=generation_time,
        image_dimensions={"width": 1024, "height": 1024} if response_data.get('images') else None
    )

# API Endpoints
@app.post("/generate-image", response_model=ImageGenerationResponse, tags=["text-to-image"])
async def generate_image(
    request: TextToImageRequest,
    api_key: str = Depends(verify_api_key)
):
    """Generate image from text description."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        result = await generate_with_gemini(request.prompt, model=request.model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, request.model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/edit-image", response_model=ImageGenerationResponse, tags=["image-editing"])
async def edit_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    model: str = Form(default=settings.DEFAULT_MODEL),
    preserve_subject: bool = Form(default=True),
    edit_strength: float = Form(default=0.8),
    api_key: str = Depends(verify_api_key)
):
    """Edit existing image with text instructions."""
    start_time = asyncio.get_event_loop().time()
    
    # Validate image
    pil_image = validate_image_file(image)
    
    # Create editing prompt
    if preserve_subject:
        full_prompt = f"{prompt}. Preserve the main subject exactly as it is."
    else:
        full_prompt = prompt
    
    try:
        result = await generate_with_gemini(full_prompt, [pil_image], model=model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compose-images", response_model=ImageGenerationResponse, tags=["multi-image"])
async def compose_images(
    prompt: str = Form(...),
    images: List[UploadFile] = File(...),
    model: str = Form(default=settings.DEFAULT_MODEL),
    composition_style: CompositionStyle = Form(default=CompositionStyle.BLEND),
    api_key: str = Depends(verify_api_key)
):
    """Combine multiple images into new compositions."""
    start_time = asyncio.get_event_loop().time()
    
    # Validate image count
    if len(images) < 2:
        raise HTTPException(
            status_code=400, 
            detail="Must provide at least 2 images"
        )
    
    # Validate and process images
    pil_images = [validate_image_file(img) for img in images]
    
    # Enhance prompt with composition style
    style_instructions = {
        CompositionStyle.BLEND: "seamlessly blend the elements together",
        CompositionStyle.REPLACE: "replace elements from one image with another",
        CompositionStyle.OVERLAY: "overlay elements maintaining distinct layers",
        CompositionStyle.MONTAGE: "create an artistic montage composition"
    }
    
    full_prompt = f"{prompt}. {style_instructions[composition_style]}."
    
    try:
        result = await generate_with_gemini(full_prompt, pil_images, model=model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/create", response_model=ChatSession, tags=["chat"])
async def create_chat(
    request: ChatCreateRequest,
    api_key: str = Depends(verify_api_key)
):
    """Create a new chat session for iterative image generation."""
    session_id = str(uuid.uuid4())
    
    # Initialize chat with Gemini
    try:
        client = genai.Client(api_key=settings.GOOGLE_API_KEY)
        chat = client.chats.create(
            model=request.model,
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image'],
                temperature=1.0
            )
        )
        
        # Store session
        chat_sessions[session_id] = {
            'chat': chat,
            'model': request.model,
            'created_at': datetime.now(),
            'message_count': 0,
            'context_length': 0
        }
        
        return ChatSession(
            session_id=session_id,
            created_at=datetime.now(),
            model=request.model,
            message_count=0,
            context_length=0
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create chat session: {str(e)}")

@app.post("/chat/{session_id}/message", response_model=ImageGenerationResponse, tags=["chat"])
async def send_chat_message(
    session_id: str,
    message: str = Form(...),
    image: Optional[UploadFile] = File(None),
    continue_generation: bool = Form(default=True),
    api_key: str = Depends(verify_api_key)
):
    """Send message to chat session."""
    start_time = asyncio.get_event_loop().time()
    
    # Get session
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    session = chat_sessions[session_id]
    
    try:
        # Prepare message content
        content_parts = [message]
        if image:
            pil_image = validate_image_file(image)
            content_parts.append(pil_image)
        
        # Send message to chat
        response = session['chat'].send_message(content_parts)
        
        # Process response
        result = {
            'text': [],
            'images': []
        }
        
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'text') and part.text:
                result['text'].append(part.text)
            elif hasattr(part, 'inline_data'):
                image_data = part.inline_data.data
                pil_image = Image.open(io.BytesIO(image_data))
                result['images'].append(image_to_base64(pil_image))
        
        # Update session
        session['message_count'] += 1
        session['context_length'] += len(message)
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, session['model'])
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/story/generate", response_model=StoryGenerationResponse, tags=["story"])
async def generate_story(
    request: StoryGenerationRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Generate sequential images for stories and tutorials."""
    start_time = asyncio.get_event_loop().time()
    
    try:
        story_images = []
        total_tokens = 0
        
        # Generate each image in sequence
        for i in range(request.num_images):
            # Create sequence-specific prompt
            sequence_prompt = f"""
            {request.description}
            
            This is image {i+1} of {request.num_images} in the sequence.
            {f'Style: {request.style}' if request.style else ''}
            
            Focus on the {'beginning' if i == 0 else 'middle' if i < request.num_images-1 else 'conclusion'} 
            part of the story/sequence.
            """
            
            # Generate image
            result = await generate_with_gemini(sequence_prompt, model=request.model)
            
            if result['images']:
                story_images.append(StoryImage(
                    image=result['images'][0],
                    sequence_number=i + 1,
                    description=result['text'][0] if result['text'] else f"Scene {i+1}",
                    timestamp=datetime.now()
                ))
            
            total_tokens += 1335  # Estimated tokens per image
        
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return StoryGenerationResponse(
            images=story_images,
            story_metadata=StoryMetadata(
                total_images=len(story_images),
                content_type=request.content_type.value,
                generation_time=generation_time,
                total_tokens=total_tokens
            )
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/advanced/inpaint", response_model=ImageGenerationResponse, tags=["advanced"])
async def inpaint_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    region_description: Optional[str] = Form(None),
    model: str = Form(default=settings.DEFAULT_MODEL),
    api_key: str = Depends(verify_api_key)
):
    """Modify specific regions within an image."""
    start_time = asyncio.get_event_loop().time()
    
    pil_image = validate_image_file(image)
    
    # Create inpainting prompt
    if region_description:
        full_prompt = f"In the region described as '{region_description}', {prompt}"
    else:
        full_prompt = f"Modify the specified area: {prompt}"
    
    try:
        result = await generate_with_gemini(full_prompt, [pil_image], model=model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/advanced/outpaint", response_model=ImageGenerationResponse, tags=["advanced"])
async def outpaint_image(
    prompt: str = Form(...),
    image: UploadFile = File(...),
    direction: List[Direction] = Form(...),
    extension_ratio: float = Form(default=0.5),
    model: str = Form(default=settings.DEFAULT_MODEL),
    api_key: str = Depends(verify_api_key)
):
    """Extend image boundaries in specified directions."""
    start_time = asyncio.get_event_loop().time()
    
    pil_image = validate_image_file(image)
    
    # Create outpainting prompt
    direction_text = ', '.join([d.value for d in direction])
    full_prompt = f"""
    Extend this image in the {direction_text} direction(s) by {extension_ratio}x.
    {prompt}
    Maintain visual consistency and style with the original image.
    """
    
    try:
        result = await generate_with_gemini(full_prompt, [pil_image], model=model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/advanced/style-transfer", response_model=ImageGenerationResponse, tags=["advanced"])
async def style_transfer(
    image: UploadFile = File(...),
    style: Optional[StyleType] = Form(None),
    style_reference_image: Optional[UploadFile] = File(None),
    style_strength: float = Form(default=0.8),
    preserve_content: bool = Form(default=True),
    model: str = Form(default=settings.DEFAULT_MODEL),
    api_key: str = Depends(verify_api_key)
):
    """Apply artistic styles to images."""
    start_time = asyncio.get_event_loop().time()
    
    pil_image = validate_image_file(image)
    images = [pil_image]
    
    # Handle style reference image
    if style_reference_image:
        style_image = validate_image_file(style_reference_image)
        images.append(style_image)
        prompt = f"Apply the artistic style from the second image to the first image with {style_strength} strength."
    elif style:
        style_descriptions = {
            StyleType.VAN_GOGH: "Vincent van Gogh's post-impressionist style with bold brushstrokes and vibrant colors",
            StyleType.PICASSO: "Pablo Picasso's cubist style with geometric forms and multiple perspectives",
            StyleType.MONET: "Claude Monet's impressionist style with soft brushwork and light effects",
            StyleType.DIGITAL_ART: "modern digital art style with clean lines and vibrant colors",
            StyleType.ANIME: "Japanese anime/manga art style",
            StyleType.OIL_PAINTING: "classical oil painting technique",
            StyleType.WATERCOLOR: "watercolor painting technique with soft, flowing colors",
            StyleType.PHOTOGRAPHIC: "photorealistic style",
            StyleType.MINIMALIST: "minimalist art style with simple forms and limited colors",
            StyleType.ABSTRACT: "abstract art style with non-representational forms"
        }
        
        prompt = f"Apply {style_descriptions[style]} to this image with {style_strength} strength."
    else:
        raise HTTPException(status_code=400, detail="Must specify either style or style_reference_image")
    
    if preserve_content:
        prompt += " Preserve the original content structure and composition."
    
    try:
        result = await generate_with_gemini(prompt, images, model=model)
        generation_time = asyncio.get_event_loop().time() - start_time
        
        return ImageGenerationResponse(
            text=result['text'],
            images=result['images'],
            metadata=create_metadata(result, generation_time, model)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now()}

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    request_id = str(uuid.uuid4())
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "message": exc.detail,
            "request_id": request_id
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler."""
    request_id = str(uuid.uuid4())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "server_error",
            "message": "An internal server error occurred",
            "request_id": request_id
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_implementation:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )