# Nano Banana - Gemini Image Generation Testing App

A comprehensive Streamlit application for testing and exploring the Google Gemini Image Generation API (Nano Banana). This app provides an interactive interface to test all features of the Gemini 2.5 Flash Image Preview model.

## Features

### 🎨 Core Image Generation
- **Text-to-Image**: Generate high-quality images from text descriptions
- **Image Editing**: Modify existing images with text prompts
- **Multi-Image Composition**: Combine multiple images into new creations
- **Style Transfer**: Apply artistic styles to images

### 💬 Interactive Features
- **Chat Mode**: Iterative image refinement through conversation
- **Story Generation**: Create multi-image stories and recipes
- **Advanced Editing**: Inpainting, outpainting, and precision edits

### 🛠️ Developer Tools
- **Prompt Templates**: Pre-built prompts for common use cases
- **Code Examples**: Copy-paste code snippets
- **API Documentation**: Interactive guide with best practices
- **Cost Calculator**: Estimate API usage costs

## Setup

1. **Clone and navigate to the project:**
   ```bash
   cd nano-banana
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API key:**
   - Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Copy `.env.example` to `.env`
   - Add your API key to the `.env` file:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```

5. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## Usage

The app is organized into tabs covering different aspects of the Gemini Image Generation API:

1. **Text-to-Image**: Basic image generation from text prompts
2. **Image Editing**: Upload images and modify them with text
3. **Multi-Image**: Combine multiple images into compositions
4. **Chat Mode**: Interactive image refinement through conversation
5. **Stories/Recipes**: Generate multi-image sequences
6. **Advanced Editing**: Specialized editing techniques
7. **Prompt Templates**: Ready-to-use prompt examples
8. **Documentation**: API guide and best practices

## API Features Covered

- ✅ Text-to-Image generation
- ✅ Image + Text-to-Image editing
- ✅ Multi-Image to Image composition
- ✅ Iterative refinement (chat mode)
- ✅ High-fidelity text rendering
- ✅ Character consistency
- ✅ Style transfer
- ✅ Inpainting and outpainting
- ✅ Sequential art generation

## Requirements

- Python 3.8+
- Google AI API key
- Streamlit 1.49.1+
- google-genai 1.32.0+

## License

This project is for educational and testing purposes. Please respect Google's usage policies and terms of service when using the Gemini API.