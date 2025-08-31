import streamlit as st
from PIL import Image
import io
import os
from datetime import datetime
from typing import List, Optional, Union
import base64


def display_images(images: List[Image.Image], captions: Optional[List[str]] = None, width: Optional[int] = None):
    """Display a list of images in Streamlit"""
    if not images:
        return
    
    if len(images) == 1:
        st.image(images[0], caption=captions[0] if captions else None, width=width)
    else:
        cols = st.columns(min(len(images), 3))
        for i, img in enumerate(images):
            col_idx = i % len(cols)
            with cols[col_idx]:
                caption = captions[i] if captions and i < len(captions) else f"Image {i+1}"
                st.image(img, caption=caption, width=width)


def display_response(response_data: dict):
    """Display API response with text and images"""
    if not response_data:
        st.error("No response data to display")
        return
    
    # Display text content
    if response_data.get('text'):
        for text_part in response_data['text']:
            st.write(text_part)
    
    # Display images
    if response_data.get('images'):
        display_images(response_data['images'])
        
        # Add download buttons for images
        if len(response_data['images']) == 1:
            img_bytes = image_to_bytes(response_data['images'][0])
            st.download_button(
                label="Download Image",
                data=img_bytes,
                file_name=f"generated_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
        else:
            st.write("**Download Images:**")
            for i, img in enumerate(response_data['images']):
                img_bytes = image_to_bytes(img)
                st.download_button(
                    label=f"Download Image {i+1}",
                    data=img_bytes,
                    file_name=f"generated_image_{i+1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key=f"download_{i}"
                )


def save_image(image: Image.Image, filename: str = None, folder: str = "generated_images") -> str:
    """Save image to folder and return the path"""
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    if filename is None:
        filename = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    
    filepath = os.path.join(folder, filename)
    image.save(filepath)
    return filepath


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """Convert PIL Image to bytes"""
    img_bytes = io.BytesIO()
    image.save(img_bytes, format=format)
    return img_bytes.getvalue()


def bytes_to_image(img_bytes: bytes) -> Image.Image:
    """Convert bytes to PIL Image"""
    return Image.open(io.BytesIO(img_bytes))


def resize_image(image: Image.Image, max_size: tuple = (1024, 1024)) -> Image.Image:
    """Resize image maintaining aspect ratio"""
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    return image


def create_image_gallery(images: List[Image.Image], titles: Optional[List[str]] = None, columns: int = 3):
    """Create a gallery view of images"""
    if not images:
        st.info("No images to display")
        return
    
    # Calculate rows needed
    rows = (len(images) + columns - 1) // columns
    
    for row in range(rows):
        cols = st.columns(columns)
        for col in range(columns):
            idx = row * columns + col
            if idx < len(images):
                with cols[col]:
                    title = titles[idx] if titles and idx < len(titles) else f"Image {idx + 1}"
                    st.image(images[idx], caption=title, use_container_width=True)


def validate_image_upload(uploaded_file) -> Optional[Image.Image]:
    """Validate and convert uploaded file to PIL Image"""
    if uploaded_file is None:
        return None
    
    try:
        image = Image.open(uploaded_file)
        # Convert to RGB if necessary (for PNG with transparency)
        if image.mode in ('RGBA', 'LA', 'P'):
            rgb_image = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            rgb_image.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = rgb_image
        return image
    except Exception as e:
        st.error(f"Error loading image: {str(e)}")
        return None


def create_before_after_view(before_image: Image.Image, after_image: Image.Image):
    """Create a before/after comparison view"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Before")
        st.image(before_image, use_container_width=True)
    
    with col2:
        st.subheader("After")
        st.image(after_image, use_container_width=True)


def get_image_info(image: Image.Image) -> dict:
    """Get basic information about an image"""
    return {
        'size': image.size,
        'mode': image.mode,
        'format': getattr(image, 'format', 'Unknown'),
        'width': image.width,
        'height': image.height
    }


def display_image_info(image: Image.Image):
    """Display image information in Streamlit"""
    info = get_image_info(image)
    
    st.write(f"**Size:** {info['width']} x {info['height']} pixels")
    st.write(f"**Mode:** {info['mode']}")
    if info['format'] != 'Unknown':
        st.write(f"**Format:** {info['format']}")


def create_image_upload_widget(
    key: str,
    label: str = "Upload Image",
    accept_multiple: bool = False,
    help_text: str = None
) -> Union[Image.Image, List[Image.Image], None]:
    """Create image upload widget with validation"""
    
    if help_text is None:
        help_text = "Upload PNG, JPG, or JPEG images"
    
    uploaded_files = st.file_uploader(
        label,
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=accept_multiple,
        help=help_text,
        key=key
    )
    
    if not uploaded_files:
        return None
    
    if accept_multiple:
        if not isinstance(uploaded_files, list):
            uploaded_files = [uploaded_files]
        
        images = []
        for uploaded_file in uploaded_files:
            image = validate_image_upload(uploaded_file)
            if image:
                images.append(image)
        
        return images if images else None
    else:
        return validate_image_upload(uploaded_files)


# Session state management for images
def init_image_session_state():
    """Initialize session state for image management"""
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'image_history' not in st.session_state:
        st.session_state.image_history = []


def add_to_image_history(image: Image.Image, prompt: str, operation: str = "generate"):
    """Add image to session history"""
    if 'image_history' not in st.session_state:
        st.session_state.image_history = []
    
    st.session_state.image_history.append({
        'image': image,
        'prompt': prompt,
        'operation': operation,
        'timestamp': datetime.now()
    })


def clear_image_history():
    """Clear image history"""
    if 'image_history' in st.session_state:
        st.session_state.image_history = []


def display_image_history():
    """Display image generation history"""
    if 'image_history' not in st.session_state or not st.session_state.image_history:
        st.info("No images generated yet")
        return
    
    st.subheader("Generated Images History")
    
    for i, entry in enumerate(reversed(st.session_state.image_history)):
        with st.expander(f"Image {len(st.session_state.image_history) - i} - {entry['operation'].title()} - {entry['timestamp'].strftime('%H:%M:%S')}"):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image(entry['image'], use_container_width=True)
                
                # Download button
                img_bytes = image_to_bytes(entry['image'])
                st.download_button(
                    label="Download",
                    data=img_bytes,
                    file_name=f"image_{i}_{entry['timestamp'].strftime('%Y%m%d_%H%M%S')}.png",
                    mime="image/png",
                    key=f"history_download_{i}"
                )
            
            with col2:
                st.write(f"**Operation:** {entry['operation'].title()}")
                st.write(f"**Prompt:** {entry['prompt']}")
                st.write(f"**Generated:** {entry['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")