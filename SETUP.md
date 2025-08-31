# 🍌 Nano Banana Setup Guide

Complete setup instructions for the Gemini Image Generation API testing app.

## Prerequisites

- Python 3.8 or higher
- Google AI API key
- Internet connection

## Quick Setup

### 1. Environment Setup

```bash
# Navigate to the project directory
cd nano-banana

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. API Key Configuration

1. **Get your API key:**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Configure the key:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env file and replace 'your_api_key_here' with your actual key
   # GOOGLE_API_KEY=your_actual_key_here
   ```

### 3. Test Installation

```bash
# Test API setup
python test_api.py

# Should show:
# ✅ ALL TESTS PASSED!
# ✅ Your Nano Banana setup is ready!
```

### 4. Launch the App

```bash
# Option 1: Use the startup script
python run_app.py

# Option 2: Run Streamlit directly
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## Manual Setup (Alternative)

If you prefer manual setup:

### Step 1: Install Python Dependencies

```bash
pip install streamlit>=1.49.1
pip install google-genai>=1.32.0
pip install Pillow>=11.3.0
pip install python-dotenv>=1.1.1
```

### Step 2: Set Environment Variable

```bash
# Option A: Set in terminal
export GOOGLE_API_KEY="your_api_key_here"

# Option B: Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Step 3: Create Directories

```bash
mkdir -p generated_images
mkdir -p .streamlit
```

## Project Structure

```
nano-banana/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                   # API key (create this)
├── .env.example          # API key template
├── .gitignore           # Git ignore rules
├── README.md            # Project documentation
├── SETUP.md             # This setup guide
├── run_app.py           # Startup script
├── test_api.py          # API testing script
├── utils/
│   ├── __init__.py
│   ├── api_client.py    # Gemini API client
│   └── image_utils.py   # Image handling utilities
├── generated_images/    # Generated images folder
└── .streamlit/
    └── config.toml      # Streamlit configuration
```

## Features Overview

### 🎨 Text-to-Image Generation
- Generate images from text descriptions
- Example prompts and templates
- Professional photography terminology

### ✏️ Image Editing
- Upload and modify existing images
- Before/after comparisons
- Contextual editing instructions

### 🖼️ Multi-Image Composition
- Combine up to 3 images
- Style transfer capabilities
- Product mockup creation

### 💬 Iterative Chat Mode
- Conversational image refinement
- Progressive enhancement
- Character consistency

### 📚 Stories & Recipes
- Multi-image sequences
- Step-by-step tutorials
- Narrative generation

### 🔧 Advanced Editing
- Inpainting (modify specific areas)
- Outpainting (extend images)
- Precision edits

### 📝 Prompt Templates
- Pre-built templates for common use cases
- Customizable variables
- Professional examples

### 📖 Documentation
- Complete API guide
- Best practices
- Troubleshooting

## Troubleshooting

### Common Issues

**1. "Client not ready" error:**
- Check your API key is correctly set
- Verify API key has proper permissions
- Try refreshing the client

**2. "Module not found" error:**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`

**3. "API key not found" error:**
- Check `.env` file exists and contains your key
- Verify environment variable is set
- Make sure there are no extra spaces in the key

**4. Slow image generation:**
- Check internet connection
- Simplify complex prompts
- Try during off-peak hours

### Getting Help

1. **Check the Documentation tab** in the app
2. **Review error messages** carefully
3. **Test with simple prompts** first
4. **Check API quotas** in Google AI Studio

## Security Notes

- Never commit your API key to version control
- Keep your `.env` file secure
- Use environment variables in production
- Monitor API usage and costs

## Performance Tips

- **Start simple** and iterate
- **Use chat mode** for refinements
- **Be specific** in prompts
- **Consider costs** - each image uses ~1290 tokens

## Updates

To update the app:

```bash
# Pull latest changes
git pull

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart the app
```

---

🍌 **Happy generating with Nano Banana!**

For issues or questions, check the Documentation tab in the app or review the troubleshooting section above.