# Google Gemini Image Generation API Guide

## Overview

This guide provides comprehensive documentation for integrating with Google's Gemini Image Generation API using the Gemini 2.5 Flash Image Preview model. The API offers state-of-the-art image generation, editing, and composition capabilities with built-in watermarking and safety features.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication](#authentication)
3. [API Endpoints](#api-endpoints)
4. [Best Practices](#best-practices)
5. [Prompt Engineering](#prompt-engineering)
6. [Error Handling](#error-handling)
7. [Rate Limits & Pricing](#rate-limits--pricing)
8. [Examples](#examples)
9. [Troubleshooting](#troubleshooting)
10. [Migration Guide](#migration-guide)

## Quick Start

### 1. Get API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Copy and secure your key

### 2. Basic Setup

```bash
# Install required dependencies
pip install google-genai pillow requests

# Set environment variable
export GOOGLE_API_KEY="your_api_key_here"
```

### 3. First Request

```python
import requests
import base64
import json

# Simple text-to-image generation
url = "http://localhost:8000/generate-image"
headers = {
    "Authorization": f"Bearer {your_api_key}",
    "Content-Type": "application/json"
}

data = {
    "prompt": "A professional photograph of a golden retriever sitting in a sunny park, shot with a DSLR camera, shallow depth of field, warm natural lighting",
    "model": "gemini-2.5-flash-image-preview"
}

response = requests.post(url, headers=headers, json=data)
result = response.json()

# Save the generated image
if result.get('images'):
    image_data = base64.b64decode(result['images'][0])
    with open('generated_image.png', 'wb') as f:
        f.write(image_data)
```

## Authentication

### API Key Authentication

The API uses Bearer token authentication with your Google AI API key:

```http
Authorization: Bearer YOUR_API_KEY
```

### Environment Setup

Set up your API key using one of these methods:

1. **Environment Variable** (Recommended):
   ```bash
   export GOOGLE_API_KEY="your_api_key_here"
   ```

2. **`.env` File**:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Direct Header**:
   ```python
   headers = {"Authorization": "Bearer your_api_key_here"}
   ```

### Security Best Practices

- ✅ Use environment variables for API keys
- ✅ Rotate keys regularly
- ✅ Restrict key permissions when possible
- ❌ Never hardcode API keys in source code
- ❌ Don't commit keys to version control

## API Endpoints

### Text-to-Image Generation

Generate images from text descriptions.

**Endpoint**: `POST /generate-image`

**Parameters**:
- `prompt` (required): Detailed text description
- `model`: Model name (default: "gemini-2.5-flash-image-preview")
- `response_modalities`: Response types (default: ["Text", "Image"])
- `temperature`: Randomness control (0.0-2.0)

**Example**:
```python
data = {
    "prompt": "A macro photograph of a dewdrop on a rose petal at sunrise, captured with a 100mm macro lens, golden hour lighting, extremely sharp focus on the dewdrop with beautiful bokeh in the background",
    "temperature": 0.8
}
```

### Image Editing

Modify existing images with text instructions.

**Endpoint**: `POST /edit-image`

**Parameters**:
- `prompt` (required): Editing instructions
- `image` (required): Image file to edit
- `preserve_subject`: Keep main subject intact
- `edit_strength`: Editing intensity (0.1-1.0)

**Example**:
```python
files = {'image': open('photo.jpg', 'rb')}
data = {
    'prompt': 'Replace the background with a cozy coffee shop interior, keep the person exactly as they are',
    'preserve_subject': True,
    'edit_strength': 0.7
}
```

### Multi-Image Composition

Combine 2-3 images into new compositions.

**Endpoint**: `POST /compose-images`

**Parameters**:
- `prompt` (required): Composition instructions
- `images` (required): 2-3 image files
- `composition_style`: Blending method

**Example**:
```python
files = [
    ('images', open('person.jpg', 'rb')),
    ('images', open('background.jpg', 'rb'))
]
data = {
    'prompt': 'Place the person from the first image into the scenic background of the second image, making it look like a professional outdoor portrait',
    'composition_style': 'blend'
}
```

### Chat Mode

Interactive conversational image generation.

**Create Session**: `POST /chat/create`
```python
data = {
    "model": "gemini-2.5-flash-image-preview",
    "system_prompt": "You are an expert photographer helping refine images iteratively."
}
```

**Send Message**: `POST /chat/{sessionId}/message`
```python
data = {
    "message": "Make the lighting softer and add more warmth to the colors"
}
```

### Sequential Story Generation

Generate image sequences for stories and tutorials.

**Endpoint**: `POST /story/generate`

**Example**:
```python
data = {
    "description": "A step-by-step visual guide for making homemade pizza, from preparing the dough to the final baked result",
    "num_images": 6,
    "content_type": "recipe",
    "style": "clean, professional food photography with natural lighting"
}
```

### Advanced Editing

#### Inpainting
**Endpoint**: `POST /advanced/inpaint`

Modify specific regions within images.

```python
files = {'image': open('scene.jpg', 'rb')}
data = {
    'prompt': 'A red vintage car',
    'region_description': 'the blue car in the center of the image'
}
```

#### Outpainting
**Endpoint**: `POST /advanced/outpaint`

Extend image boundaries.

```python
data = {
    'prompt': 'Continue the mountain landscape with more peaks and a valley below',
    'direction': ['top', 'right'],
    'extension_ratio': 0.8
}
```

#### Style Transfer
**Endpoint**: `POST /advanced/style-transfer`

Apply artistic styles to images.

```python
files = {'image': open('photo.jpg', 'rb')}
data = {
    'style': 'van_gogh',
    'style_strength': 0.8,
    'preserve_content': True
}
```

## Best Practices

### Prompt Engineering

#### ✅ DO:
- **Use narrative descriptions**: "A professional headshot of a confident businesswoman in her 40s, wearing a navy blazer..."
- **Include technical details**: Camera settings, lighting, composition
- **Specify mood and atmosphere**: "warm golden hour lighting", "cozy and inviting atmosphere"
- **Be hyper-specific**: Exact colors, textures, angles, styles

#### ❌ DON'T:
- Use keyword lists: "woman, business, professional, headshot, lighting"
- Be overly vague: "a nice picture of a person"
- Include inappropriate content
- Expect perfect text rendering (though it's improved)

### Image Quality Optimization

1. **Resolution**: Works best up to 1024x1024 pixels
2. **File Size**: Keep uploads under 20MB
3. **Format**: Use PNG or high-quality JPEG
4. **Lighting**: Specify lighting conditions in prompts
5. **Composition**: Include camera angles and framing details

### Performance Tips

- **Batch Requests**: Group similar generations when possible
- **Cache Results**: Store frequently used images
- **Optimize Prompts**: Shorter, specific prompts often work better
- **Use Chat Mode**: For iterative refinements instead of separate requests

## Error Handling

### Common Error Codes

| Code | Type | Description | Solution |
|------|------|-------------|----------|
| 400 | `invalid_request` | Malformed request | Check required parameters |
| 401 | `unauthorized` | Invalid API key | Verify API key is correct |
| 413 | `file_too_large` | Image file too big | Reduce image size to <20MB |
| 429 | `rate_limit_exceeded` | Too many requests | Implement exponential backoff |
| 500 | `server_error` | Internal error | Retry after delay |

### Error Response Format

```json
{
  "error": "invalid_request",
  "message": "The prompt is too long. Maximum length is 2000 characters.",
  "details": {
    "field": "prompt",
    "max_length": 2000,
    "current_length": 2150
  },
  "request_id": "req_123456789"
}
```

### Retry Logic Example

```python
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "POST"],
        backoff_factor=1
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

def generate_with_retry(prompt, max_retries=3):
    session = create_session_with_retries()
    
    for attempt in range(max_retries):
        try:
            response = session.post(url, json={"prompt": prompt})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait_time)
```

## Rate Limits & Pricing

### Rate Limits

- **Free Tier**: 15 requests per minute
- **Paid Tier**: 600 requests per minute
- **Concurrent**: Maximum 5 simultaneous requests

### Pricing Structure

- **Input Tokens**: $0.00025 per 1K tokens
- **Output Tokens**: $0.00125 per 1K tokens
- **Images**: ~1,290 tokens per generated image
- **Typical Cost**: ~$1.61 per generated image

### Cost Optimization

1. **Optimize Prompts**: Shorter prompts = lower input costs
2. **Batch Operations**: Group similar requests
3. **Cache Results**: Store and reuse generated images
4. **Use Chat Mode**: More efficient for iterative edits

## Examples

### Product Photography

```python
# High-end product shot
prompt = """
A professional high-end product photograph of a luxury mechanical watch 
lying on a clean white marble surface, shot from a 45-degree angle with 
soft diffused lighting from the left side creating subtle shadows. The 
watch has a silver stainless steel case with a black leather strap and 
a white dial with silver hands. Studio photography, tack sharp focus, 
minimalist composition, white background, commercial photography style.
"""

response = requests.post(url, json={"prompt": prompt})
```

### Portrait Photography

```python
# Professional headshot
prompt = """
A professional corporate headshot of a confident businesswoman in her 30s, 
shoulder-length brown hair, wearing a charcoal gray blazer over a white 
blouse, genuine warm smile, shot with an 85mm lens at f/2.8, soft natural 
window lighting from camera left, clean white background, corporate 
photography style, sharp focus on eyes, professional and approachable.
"""
```

### Artistic Scene

```python
# Fantasy landscape
prompt = """
A mystical forest clearing at twilight, ancient oak trees with glowing 
mushrooms growing on their trunks, soft ethereal mist floating between 
the trees, fireflies dancing in the air, a small crystal-clear stream 
flowing through the center, dappled moonlight filtering through the 
canopy above, fantasy art style, magical atmosphere, rich deep colors, 
painted in the style of classical fantasy illustrations.
"""
```

### Image Editing Example

```python
# Background replacement
files = {'image': open('portrait.jpg', 'rb')}
data = {
    'prompt': '''Replace the current background with a cozy bookshop interior. 
    Show tall wooden bookshelves filled with books, warm golden lighting from 
    vintage pendant lights, a few leather armchairs, and large windows with 
    soft natural light. Keep the person exactly as they are, maintaining the 
    same lighting on their face and clothing.''',
    'preserve_subject': True,
    'edit_strength': 0.8
}

response = requests.post('/edit-image', files=files, data=data)
```

### Multi-Image Composition

```python
# Combining person and background
files = [
    ('images', open('person.jpg', 'rb')),
    ('images', open('cafe_interior.jpg', 'rb'))
]
data = {
    'prompt': '''Place the person from the first image into the café setting 
    from the second image. Make them appear to be sitting at one of the tables, 
    with natural lighting that matches the café's ambiance. Ensure the scale 
    and perspective look realistic, and blend the lighting so it appears they 
    were originally photographed in that location.''',
    'composition_style': 'blend'
}

response = requests.post('/compose-images', files=files, data=data)
```

### Story Generation

```python
# Recipe tutorial
data = {
    "description": """A complete visual guide for making chocolate chip cookies 
    from scratch. Start with gathering ingredients, then mixing the dough, 
    shaping the cookies, baking them in the oven, and finally showing the 
    delicious finished cookies. Each step should be clearly photographed with 
    professional food photography lighting and styling.""",
    "num_images": 6,
    "content_type": "recipe",
    "style": "clean professional food photography, bright natural lighting, modern kitchen setting"
}

response = requests.post('/story/generate', json=data)
```

### Chat Mode Workflow

```python
# Create chat session
session_response = requests.post('/chat/create', json={
    "model": "gemini-2.5-flash-image-preview",
    "system_prompt": "You are a professional photographer helping to refine and improve images."
})
session_id = session_response.json()['session_id']

# Initial generation
first_message = {
    "message": "Create a professional headshot of a business executive"
}
response1 = requests.post(f'/chat/{session_id}/message', json=first_message)

# Refinement
second_message = {
    "message": "Make the lighting softer and add more warmth to create a more approachable feeling"
}
response2 = requests.post(f'/chat/{session_id}/message', json=second_message)

# Further refinement
third_message = {
    "message": "Change the background to a modern office setting with blurred city views"
}
response3 = requests.post(f'/chat/{session_id}/message', json=third_message)
```

## Troubleshooting

### Common Issues

#### 1. **Images Not Generating**

**Symptoms**: Empty response or error messages
**Solutions**:
- Verify API key is correct and active
- Check prompt length (max 2000 characters)
- Ensure prompt doesn't violate content policies
- Try simpler prompts first

#### 2. **Poor Image Quality**

**Symptoms**: Blurry, distorted, or low-quality images
**Solutions**:
- Be more specific in prompts
- Include technical photography details
- Specify resolution and quality requirements
- Use professional terminology

#### 3. **Inconsistent Results**

**Symptoms**: Highly variable output quality
**Solutions**:
- Lower temperature parameter (0.4-0.6)
- Use more detailed, specific prompts
- Include style and mood descriptions
- Try multiple generations with same prompt

#### 4. **Slow Response Times**

**Symptoms**: Long wait times for generation
**Solutions**:
- Optimize prompt length
- Avoid peak usage times
- Use simpler compositions initially
- Implement proper timeout handling

#### 5. **Upload Errors**

**Symptoms**: File upload failures
**Solutions**:
- Check file size (max 20MB)
- Use supported formats (PNG, JPG, JPEG)
- Verify file isn't corrupted
- Try compressing large images

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def debug_request(url, data):
    logger.debug(f"Request URL: {url}")
    logger.debug(f"Request data: {data}")
    
    response = requests.post(url, json=data)
    
    logger.debug(f"Response status: {response.status_code}")
    logger.debug(f"Response headers: {response.headers}")
    
    if response.status_code != 200:
        logger.error(f"Error response: {response.text}")
    
    return response
```

### Performance Monitoring

Track API performance metrics:

```python
import time
from dataclasses import dataclass
from typing import List

@dataclass
class RequestMetrics:
    timestamp: float
    duration: float
    status_code: int
    prompt_length: int
    success: bool

class APIMonitor:
    def __init__(self):
        self.metrics: List[RequestMetrics] = []
    
    def track_request(self, prompt: str, response_time: float, status_code: int):
        metric = RequestMetrics(
            timestamp=time.time(),
            duration=response_time,
            status_code=status_code,
            prompt_length=len(prompt),
            success=status_code == 200
        )
        self.metrics.append(metric)
    
    def get_success_rate(self, window_minutes: int = 60) -> float:
        cutoff = time.time() - (window_minutes * 60)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff]
        
        if not recent_metrics:
            return 0.0
        
        successful = sum(1 for m in recent_metrics if m.success)
        return successful / len(recent_metrics)
    
    def get_avg_response_time(self, window_minutes: int = 60) -> float:
        cutoff = time.time() - (window_minutes * 60)
        recent_metrics = [m for m in self.metrics if m.timestamp > cutoff and m.success]
        
        if not recent_metrics:
            return 0.0
        
        return sum(m.duration for m in recent_metrics) / len(recent_metrics)
```

## Migration Guide

### From OpenAI DALL-E

| DALL-E Parameter | Gemini Equivalent | Notes |
|------------------|-------------------|-------|
| `prompt` | `prompt` | Same, but use narrative style |
| `n` | Multiple requests | Gemini generates one image per request |
| `size` | Specify in prompt | "1024x1024 resolution" |
| `response_format` | Fixed base64 | Always returns base64 encoded |

**Example Migration**:

```python
# DALL-E style (old)
openai.Image.create(
    prompt="A cat sitting on a windowsill",
    n=1,
    size="1024x1024"
)

# Gemini style (new)
requests.post('/generate-image', json={
    "prompt": "A beautiful tabby cat sitting peacefully on a wooden windowsill, natural lighting from the window, cozy home interior, 1024x1024 resolution, photorealistic"
})
```

### From Midjourney

| Midjourney Feature | Gemini Equivalent | Notes |
|--------------------|-------------------|-------|
| `--v` versions | Model parameter | Use "gemini-2.5-flash-image-preview" |
| `--ar` aspect ratio | Specify in prompt | "16:9 aspect ratio" |
| `--stylize` | Temperature | Use temperature 0.8-1.2 |
| `--chaos` | Higher temperature | Use temperature 1.5-2.0 |

### From Stable Diffusion

- **Positive prompts**: Use as main prompt with narrative style
- **Negative prompts**: Include "avoid" or "without" in main prompt  
- **CFG Scale**: Map to temperature (7-12 CFG ≈ 0.6-1.0 temperature)
- **Steps**: Not configurable, handled automatically
- **Samplers**: Not configurable, handled automatically

## Advanced Integration Patterns

### Webhook Integration

Set up webhooks for long-running generation tasks:

```python
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def handle_completion():
    data = request.json
    
    # Process completed generation
    image_data = data.get('images', [])
    request_id = data.get('request_id')
    
    # Store result in database
    store_generated_image(request_id, image_data)
    
    return jsonify({'status': 'received'})

def generate_with_webhook(prompt, callback_url):
    data = {
        'prompt': prompt,
        'webhook_url': callback_url,
        'async': True
    }
    
    response = requests.post('/generate-image', json=data)
    return response.json().get('request_id')
```

### Batch Processing

Process multiple images efficiently:

```python
import asyncio
import aiohttp
from typing import List

async def generate_batch(prompts: List[str], max_concurrent: int = 5) -> List[dict]:
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def generate_single(session, prompt):
        async with semaphore:
            async with session.post('/generate-image', json={'prompt': prompt}) as response:
                return await response.json()
    
    async with aiohttp.ClientSession() as session:
        tasks = [generate_single(session, prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
    
    return results

# Usage
prompts = [
    "A red sports car in a garage",
    "A mountain landscape at sunset", 
    "A modern kitchen interior"
]

results = asyncio.run(generate_batch(prompts))
```

### Quality Scoring

Implement automatic quality assessment:

```python
from PIL import Image
import numpy as np

def assess_image_quality(image_data: bytes) -> dict:
    """Basic image quality metrics."""
    image = Image.open(io.BytesIO(image_data))
    array = np.array(image)
    
    # Calculate basic metrics
    brightness = np.mean(array)
    contrast = np.std(array)
    sharpness = np.var(np.gradient(np.mean(array, axis=2)))
    
    # Color diversity
    unique_colors = len(np.unique(array.reshape(-1, array.shape[-1]), axis=0))
    color_diversity = unique_colors / (array.shape[0] * array.shape[1])
    
    return {
        'brightness': float(brightness),
        'contrast': float(contrast),
        'sharpness': float(sharpness),
        'color_diversity': float(color_diversity),
        'resolution': f"{image.size[0]}x{image.size[1]}",
        'file_size': len(image_data)
    }

def generate_with_quality_check(prompt: str, min_quality_score: float = 0.7) -> dict:
    """Generate image and retry if quality is too low."""
    max_attempts = 3
    
    for attempt in range(max_attempts):
        response = requests.post('/generate-image', json={'prompt': prompt})
        result = response.json()
        
        if result.get('images'):
            image_data = base64.b64decode(result['images'][0])
            quality = assess_image_quality(image_data)
            
            # Simple quality score (you can make this more sophisticated)
            quality_score = (
                quality['contrast'] / 255 * 0.3 +
                quality['sharpness'] / 1000 * 0.3 +
                quality['color_diversity'] * 0.4
            )
            
            if quality_score >= min_quality_score:
                result['quality_metrics'] = quality
                result['quality_score'] = quality_score
                return result
        
        # If not good enough, try with slightly modified prompt
        prompt += f" (attempt {attempt + 2})"
    
    return result  # Return last attempt even if quality is low
```

## Support & Community

### Official Resources

- **Documentation**: [Google AI Documentation](https://ai.google.dev/docs)
- **API Reference**: [Generative Language API](https://ai.google.dev/api)
- **Support**: [Google AI Support](https://support.google.com/ai)

### Community Resources

- **GitHub Issues**: Report bugs and feature requests
- **Stack Overflow**: Tag questions with `google-gemini` and `image-generation`
- **Discord/Reddit**: Join AI development communities

### Getting Help

When asking for help, include:

1. **Full error message** and status code
2. **Minimal reproducible example**
3. **API version** and model used
4. **Expected vs actual behavior**
5. **Request/response details** (without API keys)

Example help request:

```
Title: Getting 400 error with multi-image composition

Description:
I'm trying to combine two images but getting a 400 error. Here's my code:

```python
# Code example here
```

Error message:
```
{"error": "invalid_request", "message": "..."}
```

Expected: Images should be composed successfully
Actual: Getting 400 bad request error

Additional context:
- Using gemini-2.5-flash-image-preview model
- Images are both under 5MB
- Same code works with single image editing
```

This comprehensive guide should help you successfully integrate and use the Google Gemini Image Generation API in your applications.