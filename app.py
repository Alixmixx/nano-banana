import streamlit as st
import os
from datetime import datetime
from PIL import Image

# Import utilities
from utils.api_client import get_client
from utils.image_utils import (
    display_response, create_image_upload_widget, init_image_session_state,
    add_to_image_history, display_image_history, clear_image_history
)

# Page configuration
st.set_page_config(
    page_title="Nano Banana - Gemini Image Generation",
    page_icon="🍌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_image_session_state()

# Sidebar
with st.sidebar:
    st.title("🍌 Nano Banana")
    st.caption("Gemini Image Generation API Tester")
    
    # API Key setup
    st.subheader("🔑 API Setup")
    
    # Check if API key is available
    client = get_client()
    
    if not client.get_api_key():
        st.error("🚨 API Key Required")
        st.write("Add your Google AI API key:")
        
        api_key_input = st.text_input(
            "API Key",
            type="password",
            help="Get your API key from https://aistudio.google.com/app/apikey"
        )
        
        if api_key_input:
            os.environ['GOOGLE_API_KEY'] = api_key_input
            st.success("✅ API key set! Refresh the page.")
            st.rerun()
        
        st.info("""
        **Setup Instructions:**
        1. Get API key from [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. Create `.env` file with `GOOGLE_API_KEY=your_key`
        3. Or enter it in the field above
        """)
    else:
        st.success("✅ API Key Configured")
        if st.button("🔄 Refresh Client"):
            client.initialize_client()
    
    st.divider()
    
    # Model selection
    st.subheader("⚙️ Settings")
    model = st.selectbox(
        "Model",
        ["gemini-2.5-flash-image-preview"],
        help="Gemini model for image generation"
    )
    
    # Image history management
    st.subheader("📸 Session")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📋 History"):
            st.session_state.show_history = not st.session_state.get('show_history', False)
    with col2:
        if st.button("🗑️ Clear"):
            clear_image_history()
            st.success("History cleared!")

# Main app
st.title("🍌 Nano Banana - Gemini Image Generation Testing")
st.caption("Comprehensive testing app for Google's Gemini Image Generation API")

# Show history if requested
if st.session_state.get('show_history', False):
    with st.expander("📸 Image Generation History", expanded=True):
        display_image_history()

# Main tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🎨 Text-to-Image",
    "✏️ Image Editing", 
    "🖼️ Multi-Image",
    "💬 Chat Mode",
    "📚 Stories/Recipes",
    "🔧 Advanced Editing",
    "📝 Prompt Templates",
    "📖 Documentation"
])

# Tab 1: Text-to-Image Generation
with tab1:
    st.header("🎨 Text-to-Image Generation")
    st.write("Generate high-quality images from text descriptions.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Prompt input
        prompt = st.text_area(
            "Enter your prompt:",
            placeholder="A photorealistic image of a nano banana in a futuristic laboratory...",
            height=100,
            help="Be descriptive! Include details about style, lighting, composition, and mood."
        )
        
        # Example prompts
        st.subheader("💡 Example Prompts")
        example_prompts = {
            "Photorealistic": "A photorealistic close-up of a nano banana on a marble kitchen counter, illuminated by soft natural light from a window, with water droplets on its surface",
            "Artistic": "A minimalist digital art piece featuring a single nano banana floating in a vast white space, rendered in a modern abstract style",
            "Fantasy": "A magical nano banana glowing with ethereal light in an enchanted forest, surrounded by fireflies and mystical fog",
            "Product Shot": "A high-end product photograph of a nano banana on a sleek black surface with professional studio lighting and subtle reflections"
        }
        
        selected_example = st.selectbox("Choose an example:", ["Custom"] + list(example_prompts.keys()))
        
        if selected_example != "Custom":
            if st.button(f"Use {selected_example} Example"):
                st.session_state.text_to_image_prompt = example_prompts[selected_example]
                st.rerun()
        
        # Use example prompt if selected
        if 'text_to_image_prompt' in st.session_state:
            prompt = st.session_state.text_to_image_prompt
        
        # Generate button
        if st.button("🎨 Generate Image", type="primary", disabled=not prompt.strip()):
            if client.is_ready():
                with st.spinner("Generating image..."):
                    response = client.generate_image(prompt, model=model)
                    
                    if response:
                        st.success("✅ Image generated successfully!")
                        display_response(response)
                        
                        # Add to history
                        if response.get('images'):
                            for img in response['images']:
                                add_to_image_history(img, prompt, "text-to-image")
                    else:
                        st.error("❌ Failed to generate image")
            else:
                st.error("❌ Client not ready. Check your API key.")
    
    with col2:
        st.subheader("📋 Tips")
        st.info("""
        **Best Practices:**
        - Be specific and descriptive
        - Include lighting details
        - Mention camera angles
        - Specify art style
        - Add mood/atmosphere
        
        **Good Example:**
        "A photorealistic macro shot of a nano banana, captured with shallow depth of field, warm golden hour lighting, on a rustic wooden table"
        """)

# Tab 2: Image Editing
with tab2:
    st.header("✏️ Image Editing")
    st.write("Upload an image and modify it with text prompts.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Image")
        uploaded_image = create_image_upload_widget(
            key="image_edit_upload",
            label="Choose an image to edit",
            help="Upload PNG, JPG, or JPEG files"
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Original Image", use_container_width=True)
            
            # Image info
            st.write(f"Size: {uploaded_image.size[0]} x {uploaded_image.size[1]} pixels")
    
    with col2:
        st.subheader("✏️ Edit Instructions")
        edit_prompt = st.text_area(
            "What would you like to change?",
            placeholder="Add a wizard hat to the subject, change the background to a magical forest...",
            height=100,
            help="Describe the modifications you want to make"
        )
        
        # Common editing operations
        st.write("**Common Operations:**")
        edit_examples = {
            "Add Element": "Add a red hat to the person in the image",
            "Change Background": "Change the background to a tropical beach scene",
            "Change Style": "Transform this photo into a watercolor painting",
            "Change Colors": "Change all blue elements to green",
            "Remove Element": "Remove all text from this image",
            "Change Expression": "Make the person smile more naturally"
        }
        
        selected_edit = st.selectbox("Quick edits:", ["Custom"] + list(edit_examples.keys()))
        if selected_edit != "Custom" and st.button(f"Use '{selected_edit}' Example"):
            edit_prompt = edit_examples[selected_edit]
            st.rerun()
        
        # Edit button
        if st.button("✏️ Edit Image", type="primary", disabled=not (uploaded_image and edit_prompt.strip())):
            if client.is_ready():
                with st.spinner("Editing image..."):
                    response = client.edit_image(edit_prompt, uploaded_image, model=model)
                    
                    if response:
                        st.success("✅ Image edited successfully!")
                        
                        # Show before/after
                        st.subheader("📊 Results")
                        result_col1, result_col2 = st.columns(2)
                        
                        with result_col1:
                            st.write("**Before:**")
                            st.image(uploaded_image, use_container_width=True)
                        
                        with result_col2:
                            st.write("**After:**")
                            if response.get('images'):
                                st.image(response['images'][0], use_container_width=True)
                                add_to_image_history(response['images'][0], edit_prompt, "image-edit")
                        
                        # Display full response
                        display_response(response)
                    else:
                        st.error("❌ Failed to edit image")
            else:
                st.error("❌ Client not ready. Check your API key.")

# Tab 3: Multi-Image Composition
with tab3:
    st.header("🖼️ Multi-Image Composition")
    st.write("Combine multiple images into new compositions or transfer styles.")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Images")
        uploaded_images = create_image_upload_widget(
            key="multi_image_upload",
            label="Upload multiple images (max 3)",
            accept_multiple=True,
            help="Upload 2-3 images to combine them"
        )
        
        if uploaded_images:
            st.write(f"**Uploaded {len(uploaded_images)} image(s):**")
            for i, img in enumerate(uploaded_images[:3]):  # Limit to 3 images
                st.image(img, caption=f"Image {i+1}", width=200)
    
    with col2:
        st.subheader("🎯 Composition Instructions")
        composition_prompt = st.text_area(
            "How should the images be combined?",
            placeholder="Combine the person from image 1 with the background from image 2, make it look like a professional portrait...",
            height=120,
            help="Describe how the images should be combined"
        )
        
        # Composition examples
        st.write("**Composition Types:**")
        comp_examples = {
            "Subject Replacement": "Take the subject from image 1 and place them in the setting from image 2",
            "Style Transfer": "Apply the artistic style from image 1 to the content of image 2",
            "Background Swap": "Keep the subject from image 1 but use the background from image 2",
            "Blend Elements": "Seamlessly blend elements from both images into a new scene",
            "Product Mockup": "Place the product from image 1 onto the surface shown in image 2"
        }
        
        selected_comp = st.selectbox("Composition type:", ["Custom"] + list(comp_examples.keys()))
        if selected_comp != "Custom" and st.button(f"Use '{selected_comp}' Template"):
            composition_prompt = comp_examples[selected_comp]
            st.rerun()
        
        # Compose button
        if st.button("🖼️ Create Composition", type="primary", 
                    disabled=not (uploaded_images and len(uploaded_images) >= 2 and composition_prompt.strip())):
            if client.is_ready():
                with st.spinner("Creating composition..."):
                    response = client.edit_image(composition_prompt, uploaded_images[:3], model=model)
                    
                    if response:
                        st.success("✅ Composition created successfully!")
                        display_response(response)
                        
                        # Add to history
                        if response.get('images'):
                            for img in response['images']:
                                add_to_image_history(img, composition_prompt, "multi-image")
                    else:
                        st.error("❌ Failed to create composition")
            else:
                st.error("❌ Client not ready. Check your API key.")

# Tab 4: Iterative Chat Mode
with tab4:
    st.header("💬 Iterative Chat Mode")
    st.write("Have a conversation to progressively refine your images.")
    
    # Initialize chat session
    if 'chat_session' not in st.session_state:
        st.session_state.chat_session = None
        st.session_state.chat_history = []
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat controls
        chat_col1, chat_col2 = st.columns([3, 1])
        with chat_col1:
            if st.button("🆕 Start New Chat Session", type="primary"):
                if client.is_ready():
                    st.session_state.chat_session = client.create_chat(model=model)
                    st.session_state.chat_history = []
                    st.success("New chat session started!")
                    st.rerun()
        
        with chat_col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.chat_session = None
                st.session_state.chat_history = []
                st.success("Chat cleared!")
                st.rerun()
        
        # Chat interface
        if st.session_state.chat_session:
            st.subheader("💬 Chat with Gemini")
            
            # Message input
            message = st.text_input(
                "Your message:",
                placeholder="Create an image of a cat, then we can modify it...",
                key="chat_message_input"
            )
            
            if st.button("💬 Send Message", disabled=not message.strip()):
                with st.spinner("Sending message..."):
                    response = client.send_chat_message(st.session_state.chat_session, message)
                    
                    if response:
                        # Add to chat history
                        st.session_state.chat_history.append({
                            'user': message,
                            'assistant': response,
                            'timestamp': datetime.now()
                        })
                        
                        # Add images to history
                        if response.get('images'):
                            for img in response['images']:
                                add_to_image_history(img, message, "chat")
                        
                        st.rerun()
            
            # Display chat history
            st.subheader("💭 Conversation")
            for i, chat_entry in enumerate(st.session_state.chat_history):
                with st.container():
                    st.write(f"**You:** {chat_entry['user']}")
                    st.write(f"**Gemini:**")
                    display_response(chat_entry['assistant'])
                    st.write(f"*{chat_entry['timestamp'].strftime('%H:%M:%S')}*")
                    st.divider()
        
        else:
            st.info("👆 Start a new chat session to begin conversational image generation")
    
    with col2:
        st.subheader("💡 Chat Tips")
        st.info("""
        **Conversation Flow:**
        1. Start with initial image request
        2. Ask for specific modifications
        3. Request style changes
        4. Fine-tune details
        5. Try different variations
        
        **Example Conversation:**
        - "Create a cat sitting on a chair"
        - "Make the cat orange"
        - "Add a wizard hat"
        - "Change background to space"
        - "Make it more cartoonish"
        """)
        
        st.subheader("📋 Quick Prompts")
        quick_prompts = [
            "Create a simple landscape",
            "Make it more colorful",
            "Add some people",
            "Change to nighttime",
            "Make it more artistic",
            "Add text saying 'Hello World'"
        ]
        
        for prompt in quick_prompts:
            if st.button(prompt, key=f"quick_{prompt}", use_container_width=True):
                if st.session_state.chat_session:
                    with st.spinner("Sending..."):
                        response = client.send_chat_message(st.session_state.chat_session, prompt)
                        if response:
                            st.session_state.chat_history.append({
                                'user': prompt,
                                'assistant': response,
                                'timestamp': datetime.now()
                            })
                            if response.get('images'):
                                for img in response['images']:
                                    add_to_image_history(img, prompt, "chat")
                            st.rerun()

# Tab 5: Stories/Recipes Generation
with tab5:
    st.header("📚 Stories & Recipes Generation")
    st.write("Generate multi-image sequences for stories, recipes, or tutorials.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Content type selection
        content_type = st.selectbox(
            "Content Type:",
            ["Story", "Recipe", "Tutorial", "Custom"]
        )
        
        if content_type == "Story":
            story_prompt = st.text_area(
                "Story Description:",
                placeholder="Create a 6-part adventure story about a brave nano banana exploring different worlds...",
                height=100
            )
            num_images = st.slider("Number of images:", 3, 10, 6)
            
        elif content_type == "Recipe":
            recipe_prompt = st.text_area(
                "Recipe Description:",
                placeholder="Show me how to make nano banana pancakes with step-by-step images...",
                height=100
            )
            num_images = st.slider("Number of steps:", 4, 12, 8)
            
        elif content_type == "Tutorial":
            tutorial_prompt = st.text_area(
                "Tutorial Description:",
                placeholder="Create a visual tutorial showing how to plant and grow nano bananas...",
                height=100
            )
            num_images = st.slider("Number of steps:", 4, 15, 10)
            
        else:  # Custom
            custom_prompt = st.text_area(
                "Custom Description:",
                placeholder="Describe what kind of multi-image sequence you want...",
                height=100
            )
            num_images = st.slider("Number of images:", 2, 15, 6)
        
        # Generate button
        prompt_text = locals().get(f"{content_type.lower()}_prompt", "")
        
        if st.button(f"📚 Generate {content_type}", type="primary", disabled=not prompt_text.strip()):
            if client.is_ready():
                with st.spinner(f"Generating {content_type.lower()}..."):
                    # Create comprehensive prompt
                    full_prompt = f"Create a {num_images}-part {content_type.lower()} with images: {prompt_text}"
                    
                    response = client.generate_image(full_prompt, model=model)
                    
                    if response:
                        st.success(f"✅ {content_type} generated successfully!")
                        display_response(response)
                        
                        # Add to history
                        if response.get('images'):
                            for img in response['images']:
                                add_to_image_history(img, full_prompt, f"{content_type.lower()}-sequence")
                    else:
                        st.error(f"❌ Failed to generate {content_type.lower()}")
            else:
                st.error("❌ Client not ready. Check your API key.")
    
    with col2:
        st.subheader("📋 Templates")
        
        templates = {
            "Story": {
                "Adventure": "A thrilling 8-part adventure story featuring a brave character exploring mysterious lands",
                "Mystery": "A 6-part mystery story with clues and revelations leading to a surprising conclusion",
                "Fantasy": "A magical 10-part fantasy tale with mythical creatures and enchanted worlds"
            },
            "Recipe": {
                "Baking": "Step-by-step visual guide for baking delicious nano banana bread",
                "Cooking": "How to prepare a gourmet nano banana dish from start to finish",
                "Dessert": "Creating an elaborate nano banana dessert with artistic presentation"
            },
            "Tutorial": {
                "Gardening": "Complete guide to growing nano bananas from seed to harvest",
                "Art": "How to draw realistic nano bananas using different techniques",
                "Science": "Scientific experiment showing nano banana properties and reactions"
            }
        }
        
        if content_type in templates:
            st.write(f"**{content_type} Templates:**")
            for template_name, template_desc in templates[content_type].items():
                if st.button(template_name, key=f"template_{template_name}", use_container_width=True):
                    st.session_state[f"{content_type.lower()}_prompt"] = template_desc
                    st.rerun()
        
        st.subheader("💡 Tips")
        st.info(f"""
        **For {content_type}s:**
        - Be specific about the sequence
        - Mention visual continuity
        - Include character descriptions
        - Specify the narrative arc
        - Consider pacing and flow
        """)

# Tab 6: Advanced Editing
with tab6:
    st.header("🔧 Advanced Editing Techniques")
    st.write("Specialized editing features like inpainting, outpainting, and precision edits.")
    
    # Editing technique selection
    technique = st.selectbox(
        "Editing Technique:",
        ["Inpainting (Modify specific areas)", "Outpainting (Extend image)", "Style Transfer", "Detail Enhancement", "Background Replacement"]
    )
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Image")
        advanced_image = create_image_upload_widget(
            key="advanced_edit_upload",
            label="Choose an image for advanced editing"
        )
        
        if advanced_image:
            st.image(advanced_image, caption="Original Image", use_container_width=True)
    
    with col2:
        st.subheader(f"🎯 {technique}")
        
        if technique == "Inpainting (Modify specific areas)":
            area_description = st.text_input(
                "Describe the area to modify:",
                placeholder="the person's shirt, the background building, the cat's face..."
            )
            
            modification = st.text_area(
                "What should replace it?",
                placeholder="a red sweater, a mountain landscape, a surprised expression...",
                height=80
            )
            
            advanced_prompt = f"In this image, change only {area_description} to {modification}. Keep everything else exactly the same."
            
        elif technique == "Outpainting (Extend image)":
            direction = st.selectbox("Extend in which direction?", ["all sides", "top", "bottom", "left", "right"])
            extension_desc = st.text_area(
                "What should be added?",
                placeholder="more of the same landscape, additional room space, sky and clouds...",
                height=80
            )
            
            advanced_prompt = f"Extend this image on the {direction} by adding {extension_desc}. Maintain the same style and lighting."
            
        elif technique == "Style Transfer":
            style = st.selectbox(
                "Artistic Style:",
                ["Van Gogh impressionist", "Picasso cubist", "anime/manga", "watercolor painting", "oil painting", "digital art", "pencil sketch"]
            )
            
            advanced_prompt = f"Transform this image into the style of {style}. Preserve the original composition but render it with the characteristic techniques and aesthetics of {style}."
            
        elif technique == "Detail Enhancement":
            enhancement_type = st.selectbox(
                "Enhancement Type:",
                ["sharpen details", "enhance colors", "improve lighting", "add texture", "increase realism"]
            )
            
            advanced_prompt = f"Enhance this image by {enhancement_type}. Improve the overall quality while maintaining the original composition and subject matter."
            
        else:  # Background Replacement
            new_background = st.text_area(
                "New Background Description:",
                placeholder="a tropical beach at sunset, a modern office space, a fantasy forest...",
                height=80
            )
            
            advanced_prompt = f"Replace the background of this image with {new_background}. Keep the main subject exactly the same but place them in the new environment with appropriate lighting and shadows."
        
        st.text_area(
            "Generated Prompt:",
            value=advanced_prompt,
            height=100,
            disabled=True,
            help="This is the automatically generated prompt based on your selections"
        )
        
        # Edit button
        if st.button("🔧 Apply Advanced Edit", type="primary", 
                    disabled=not (advanced_image and advanced_prompt.strip())):
            if client.is_ready():
                with st.spinner("Applying advanced edit..."):
                    response = client.edit_image(advanced_prompt, advanced_image, model=model)
                    
                    if response:
                        st.success("✅ Advanced edit applied successfully!")
                        
                        # Show before/after comparison
                        st.subheader("📊 Before & After")
                        comp_col1, comp_col2 = st.columns(2)
                        
                        with comp_col1:
                            st.write("**Original:**")
                            st.image(advanced_image, use_container_width=True)
                        
                        with comp_col2:
                            st.write("**Edited:**")
                            if response.get('images'):
                                st.image(response['images'][0], use_container_width=True)
                                add_to_image_history(response['images'][0], advanced_prompt, f"advanced-{technique}")
                        
                        display_response(response)
                    else:
                        st.error("❌ Failed to apply advanced edit")
            else:
                st.error("❌ Client not ready. Check your API key.")

# Tab 7: Prompt Templates
with tab7:
    st.header("📝 Prompt Templates & Examples")
    st.write("Pre-built prompts and templates for common use cases.")
    
    # Template categories
    template_category = st.selectbox(
        "Template Category:",
        ["Photorealistic Scenes", "Artistic Styles", "Product Photography", "Character Design", "Landscapes", "Text & Typography"]
    )
    
    templates_db = {
        "Photorealistic Scenes": {
            "Portrait Photography": {
                "template": "A photorealistic {shot_type} portrait of a {subject_description}, {expression}, shot with a {camera_specs}, {lighting_description}. Professional photography, sharp focus, {mood} mood.",
                "example": "A photorealistic close-up portrait of a young woman with curly hair, gentle smile, shot with a 85mm lens at f/1.4, soft natural lighting from a large window. Professional photography, sharp focus, warm and inviting mood.",
                "variables": ["shot_type", "subject_description", "expression", "camera_specs", "lighting_description", "mood"]
            },
            "Street Photography": {
                "template": "A photorealistic street scene in {location}, {time_of_day}, featuring {main_subject}. Shot with {camera_style}, {weather_conditions}, {atmosphere}.",
                "example": "A photorealistic street scene in Tokyo, golden hour, featuring people crossing a busy intersection. Shot with documentary photography style, light rain creating reflections, bustling urban atmosphere.",
                "variables": ["location", "time_of_day", "main_subject", "camera_style", "weather_conditions", "atmosphere"]
            }
        },
        "Artistic Styles": {
            "Digital Art": {
                "template": "A {style_type} digital artwork of {subject}, rendered in {art_technique}, with {color_palette} colors and {composition_style} composition. {additional_effects}.",
                "example": "A cyberpunk digital artwork of a futuristic city, rendered in neon-lit vector art style, with electric blue and purple colors and dynamic diagonal composition. Glowing effects and particle systems.",
                "variables": ["style_type", "subject", "art_technique", "color_palette", "composition_style", "additional_effects"]
            },
            "Traditional Art": {
                "template": "A {medium} painting of {subject} in the style of {artist_style}, using {technique}, {color_approach}, painted on {canvas_type}.",
                "example": "A watercolor painting of a mountain landscape in the style of Turner, using wet-on-wet technique, luminous atmospheric colors, painted on textured watercolor paper.",
                "variables": ["medium", "subject", "artist_style", "technique", "color_approach", "canvas_type"]
            }
        },
        "Product Photography": {
            "E-commerce": {
                "template": "A professional product photograph of {product}, shot on {background}, with {lighting_setup}. {camera_angle}, {focus_style}, commercial photography style.",
                "example": "A professional product photograph of a luxury watch, shot on white seamless background, with three-point softbox lighting. 45-degree angle, macro focus on details, commercial photography style.",
                "variables": ["product", "background", "lighting_setup", "camera_angle", "focus_style"]
            },
            "Lifestyle": {
                "template": "A lifestyle product shot featuring {product} in {setting}, {usage_context}. Natural lighting, {mood}, {target_audience} aesthetic.",
                "example": "A lifestyle product shot featuring wireless headphones in a modern coffee shop, person working on laptop. Natural window lighting, relaxed morning mood, young professional aesthetic.",
                "variables": ["product", "setting", "usage_context", "mood", "target_audience"]
            }
        },
        "Character Design": {
            "Fantasy": {
                "template": "A {character_type} character design, {physical_description}, wearing {clothing_armor}, holding {equipment}. {art_style} style, {pose}, {background_setting}.",
                "example": "A female elf warrior character design, tall with silver hair and piercing green eyes, wearing ornate leather armor with gold trim, holding an enchanted bow. Fantasy art style, confident battle stance, mystical forest background.",
                "variables": ["character_type", "physical_description", "clothing_armor", "equipment", "art_style", "pose", "background_setting"]
            },
            "Modern": {
                "template": "A modern character design of {profession}, {age_appearance}, {distinctive_features}, wearing {outfit_style}. {art_medium} illustration, {personality_traits} expression, {setting}.",
                "example": "A modern character design of a detective, middle-aged appearance, sharp eyes and graying beard, wearing a classic trench coat. Digital illustration, determined and thoughtful expression, city street at night.",
                "variables": ["profession", "age_appearance", "distinctive_features", "outfit_style", "art_medium", "personality_traits", "setting"]
            }
        },
        "Landscapes": {
            "Natural": {
                "template": "A {landscape_type} landscape during {time}, featuring {main_elements}. {weather_conditions}, {lighting_quality}, {photographic_style}.",
                "example": "A mountain valley landscape during sunrise, featuring snow-capped peaks and alpine lake. Clear skies with morning mist, golden hour lighting, landscape photography with telephoto compression.",
                "variables": ["landscape_type", "time", "main_elements", "weather_conditions", "lighting_quality", "photographic_style"]
            },
            "Urban": {
                "template": "An urban {cityscape_type} of {city_description}, {architectural_style}, {time_period}. {viewing_angle}, {lighting_atmosphere}, {mood}.",
                "example": "An urban skyline of a futuristic metropolis, sleek glass and steel architecture, cyberpunk aesthetic. Aerial drone perspective, neon-lit night atmosphere, dramatic and imposing mood.",
                "variables": ["cityscape_type", "city_description", "architectural_style", "time_period", "viewing_angle", "lighting_atmosphere", "mood"]
            }
        },
        "Text & Typography": {
            "Logo Design": {
                "template": "A {logo_style} logo for {business_type} called '{business_name}', featuring {design_elements}, {color_scheme} color scheme, {typography_style} typography.",
                "example": "A minimalist logo for coffee shop called 'Bean & Brew', featuring a stylized coffee bean, warm brown and cream color scheme, modern sans-serif typography.",
                "variables": ["logo_style", "business_type", "business_name", "design_elements", "color_scheme", "typography_style"]
            },
            "Typography Art": {
                "template": "A typographic artwork with the text '{text_content}' in {font_style} style, {layout_approach}, {decorative_elements}, {background_treatment}.",
                "example": "A typographic artwork with the text 'Create Magic' in hand-lettered calligraphy style, flowing curved layout, golden flourishes and swirls, dark gradient background.",
                "variables": ["text_content", "font_style", "layout_approach", "decorative_elements", "background_treatment"]
            }
        }
    }
    
    if template_category in templates_db:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📋 Available Templates")
            
            for template_name, template_data in templates_db[template_category].items():
                with st.expander(template_name):
                    st.write("**Template:**")
                    st.code(template_data["template"], language="text")
                    
                    st.write("**Example:**")
                    st.write(template_data["example"])
                    
                    st.write("**Variables:**")
                    st.write(", ".join(f"`{var}`" for var in template_data["variables"]))
                    
                    if st.button(f"Use {template_name} Template", key=f"use_template_{template_name}"):
                        st.session_state.selected_template = template_data
                        st.session_state.template_name = template_name
                        st.rerun()
        
        with col2:
            st.subheader("🛠️ Template Builder")
            
            if 'selected_template' in st.session_state:
                template_data = st.session_state.selected_template
                template_name = st.session_state.template_name
                
                st.write(f"**Editing: {template_name}**")
                
                # Variable inputs
                variable_values = {}
                for variable in template_data["variables"]:
                    variable_values[variable] = st.text_input(
                        f"{variable.replace('_', ' ').title()}:",
                        key=f"var_{variable}",
                        help=f"Enter value for {variable}"
                    )
                
                # Generate customized prompt
                customized_prompt = template_data["template"]
                for var, value in variable_values.items():
                    if value.strip():
                        customized_prompt = customized_prompt.replace(f"{{{var}}}", value)
                
                st.write("**Generated Prompt:**")
                st.text_area(
                    "Your customized prompt:",
                    value=customized_prompt,
                    height=100,
                    key="customized_prompt"
                )
                
                # Generate button
                if st.button("🎨 Generate from Template", type="primary"):
                    if client.is_ready():
                        with st.spinner("Generating from template..."):
                            response = client.generate_image(customized_prompt, model=model)
                            
                            if response:
                                st.success("✅ Image generated from template!")
                                display_response(response)
                                
                                if response.get('images'):
                                    for img in response['images']:
                                        add_to_image_history(img, customized_prompt, f"template-{template_name}")
                            else:
                                st.error("❌ Failed to generate image")
                    else:
                        st.error("❌ Client not ready. Check your API key.")
            else:
                st.info("👈 Select a template from the left to start customizing")
    
    # Custom template creation
    st.divider()
    st.subheader("➕ Create Custom Template")
    
    with st.expander("Build Your Own Template"):
        custom_name = st.text_input("Template Name:")
        custom_template = st.text_area(
            "Template (use {variable_name} for variables):",
            placeholder="A {style} image of {subject} with {colors} colors...",
            height=80
        )
        
        if custom_template and custom_name:
            # Extract variables from template
            import re
            variables = re.findall(r'\{(\w+)\}', custom_template)
            
            if variables:
                st.write("**Detected Variables:**", ", ".join(variables))
                
                if st.button("💾 Save Custom Template"):
                    # In a real app, you'd save this to a database or file
                    st.success(f"Template '{custom_name}' saved!")

# Tab 8: Documentation
with tab8:
    st.header("📖 Documentation & Best Practices")
    st.write("Complete guide to using the Gemini Image Generation API effectively.")
    
    doc_section = st.selectbox(
        "Documentation Section:",
        ["Getting Started", "API Features", "Prompt Engineering", "Best Practices", "Limitations", "Troubleshooting", "Code Examples"]
    )
    
    if doc_section == "Getting Started":
        st.subheader("🚀 Getting Started with Nano Banana")
        
        st.write("""
        ### What is Nano Banana?
        Nano Banana is the codename for Google's Gemini Image Generation API. It enables you to:
        - Generate images from text descriptions
        - Edit existing images with text prompts
        - Combine multiple images into new compositions
        - Have conversational interactions to refine images iteratively
        
        ### Quick Start
        1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
        2. **Set up Environment**: Add your API key to `.env` file or environment variables
        3. **Choose a Tab**: Start with "Text-to-Image" for basic generation
        4. **Write a Prompt**: Be descriptive and specific
        5. **Generate**: Click generate and wait for results
        """)
        
        st.code("""
# Basic usage example
from google import genai
from google.genai import types

client = genai.Client(api_key="your_api_key")

response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=["A photorealistic image of a nano banana in space"],
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image']
    )
)
        """, language="python")
    
    elif doc_section == "API Features":
        st.subheader("🔧 API Features Overview")
        
        features = {
            "Text-to-Image": {
                "description": "Generate high-quality images from text descriptions",
                "use_cases": ["Creative art", "Concept visualization", "Marketing materials", "Illustrations"],
                "example": "A surreal landscape with floating islands and waterfalls"
            },
            "Image Editing": {
                "description": "Modify existing images using text prompts",
                "use_cases": ["Photo retouching", "Style changes", "Object addition/removal", "Background replacement"],
                "example": "Change the cat's fur color from black to orange"
            },
            "Multi-Image Composition": {
                "description": "Combine elements from multiple images",
                "use_cases": ["Product mockups", "Style transfer", "Character consistency", "Scene composition"],
                "example": "Place the person from image 1 in the setting from image 2"
            },
            "Iterative Chat": {
                "description": "Refine images through conversation",
                "use_cases": ["Progressive refinement", "Character development", "Artistic exploration", "Feedback incorporation"],
                "example": "Make the lighting warmer... now add some fog... perfect!"
            },
            "Sequential Generation": {
                "description": "Create stories, tutorials, or recipes with multiple images",
                "use_cases": ["Storytelling", "Educational content", "Process documentation", "Comic creation"],
                "example": "Show the 8 steps of making banana bread"
            }
        }
        
        for feature, details in features.items():
            with st.expander(f"📋 {feature}"):
                st.write(f"**Description:** {details['description']}")
                st.write(f"**Use Cases:** {', '.join(details['use_cases'])}")
                st.write(f"**Example:** *{details['example']}*")
    
    elif doc_section == "Prompt Engineering":
        st.subheader("✍️ Prompt Engineering Guide")
        
        st.write("""
        ### Core Principle: Describe the Scene, Don't List Keywords
        
        The most important rule is to write descriptive, narrative prompts rather than keyword lists.
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("❌ **Poor Prompt:**")
            st.code("cat, red, sitting, chair, indoor", language="text")
            
        with col2:
            st.write("✅ **Good Prompt:**")
            st.code("A fluffy red tabby cat sitting comfortably on a vintage wooden chair in a cozy living room", language="text")
        
        st.write("### Prompt Structure Template")
        st.code("""
[Image Type] of [Main Subject] [doing/being] [Action/State]
in/on/at [Setting/Location], 
[Lighting Description], 
[Style/Mood], 
[Technical Details]
        """, language="text")
        
        st.write("### Essential Elements to Include")
        
        elements = {
            "Subject Description": ["Physical appearance", "Clothing/accessories", "Expression/pose", "Age/characteristics"],
            "Setting & Environment": ["Location type", "Time of day/season", "Weather conditions", "Background elements"],
            "Lighting & Atmosphere": ["Light source", "Quality (soft/harsh)", "Direction", "Color temperature", "Mood"],
            "Style & Technical": ["Art style", "Camera angle", "Composition", "Color palette", "Artistic medium"],
            "Quality & Details": ["Resolution hints", "Focus areas", "Texture details", "Professional terms"]
        }
        
        for category, items in elements.items():
            with st.expander(f"🔍 {category}"):
                for item in items:
                    st.write(f"• {item}")
        
        st.write("### Prompt Examples by Category")
        
        example_prompts = {
            "Portrait Photography": "A professional headshot of a confident businesswoman in her 40s, wearing a navy blue blazer, gentle smile, shot with an 85mm lens at f/2.8, soft natural lighting from a large window, clean white background, corporate photography style",
            "Landscape": "A breathtaking sunrise over a misty mountain valley, golden hour lighting illuminating snow-capped peaks, alpine lake reflecting the sky, captured with wide-angle lens, landscape photography, serene and majestic mood",
            "Product Photography": "A high-end product photograph of a luxury watch on a black marble surface, three-point studio lighting setup, macro lens capturing intricate details, subtle reflections, commercial photography style, premium aesthetic",
            "Artistic/Creative": "A whimsical watercolor illustration of a magical forest, soft pastel colors, dappled sunlight filtering through leaves, fairy-tale atmosphere, children's book illustration style, dreamlike and enchanting",
            "Street Photography": "A candid street scene in Tokyo during a light rain, neon signs reflecting on wet pavement, people with umbrellas walking past, shot with documentary photography style, urban atmosphere, evening blue hour"
        }
        
        for category, prompt in example_prompts.items():
            with st.expander(f"📝 {category}"):
                st.code(prompt, language="text")
    
    elif doc_section == "Best Practices":
        st.subheader("⭐ Best Practices")
        
        practices = {
            "Prompt Writing": [
                "Be hyper-specific with descriptions",
                "Use professional photography/art terminology",
                "Include lighting and mood details",
                "Specify camera angles and composition",
                "Mention artistic style or medium"
            ],
            "Image Editing": [
                "Describe changes in context of the original image",
                "Be specific about what to keep vs. change",
                "Use 'semantic masking' language",
                "Preserve important details explicitly",
                "Consider lighting consistency"
            ],
            "Multi-Image Work": [
                "Limit to 3 images maximum",
                "Describe how images should combine",
                "Be specific about which elements to use",
                "Consider style consistency",
                "Explain desired composition"
            ],
            "Iterative Refinement": [
                "Start with broad concepts, then refine",
                "Make one change at a time",
                "Use conversational language",
                "Reference previous images in context",
                "Build character consistency"
            ]
        }
        
        for category, tips in practices.items():
            with st.expander(f"💡 {category}"):
                for tip in tips:
                    st.write(f"• {tip}")
        
        st.write("### Performance Tips")
        st.info("""
        - **Cost Management**: Each image generation uses tokens (approximately 1290 tokens per image)
        - **Quality vs Speed**: More detailed prompts may take longer but produce better results
        - **Iteration Strategy**: Use chat mode for progressive refinement rather than regenerating from scratch
        - **Image Size**: Model works best up to 1024x1024 pixels
        - **Batch Processing**: For multiple similar images, use a single request with quantity specified
        """)
    
    elif doc_section == "Limitations":
        st.subheader("⚠️ Current Limitations")
        
        limitations = {
            "Technical": [
                "Model works best with up to 3 input images",
                "No audio or video input support",
                "Limited to certain languages (EN, es-MX, ja-JP, zh-CN, hi-IN)",
                "All generated images include SynthID watermark",
                "May not always follow exact number of output images requested"
            ],
            "Content": [
                "Cannot upload images of children in EEA, CH, and UK",
                "Subject to Google's usage policies",
                "Cannot generate inappropriate or harmful content",
                "May struggle with very specific brand logos or copyrighted material",
                "Text rendering, while good, may not always be perfect"
            ],
            "Performance": [
                "Higher latency compared to specialized image models",
                "Token-based pricing can be expensive for high usage",
                "May require multiple iterations for perfect results",
                "Limited control over exact image dimensions",
                "Processing time varies with complexity"
            ]
        }
        
        for category, items in limitations.items():
            with st.expander(f"📋 {category} Limitations"):
                for item in items:
                    st.write(f"• {item}")
        
        st.write("### When to Use Imagen Instead")
        st.info("""
        Consider using Imagen (Google's specialized image model) when:
        - You need the highest possible image quality
        - Photorealism is the top priority
        - You need precise typography and text rendering
        - Cost efficiency is important for high-volume usage
        - You don't need conversational/iterative features
        """)
    
    elif doc_section == "Troubleshooting":
        st.subheader("🔧 Troubleshooting Guide")
        
        issues = {
            "API Key Issues": {
                "symptoms": ["Authentication errors", "Client not ready", "Access denied"],
                "solutions": [
                    "Verify API key is correct",
                    "Check API key has proper permissions",
                    "Ensure key is set in environment variables or .env file",
                    "Try refreshing the client connection"
                ]
            },
            "Poor Image Quality": {
                "symptoms": ["Blurry images", "Incorrect details", "Wrong style"],
                "solutions": [
                    "Make prompts more specific and detailed",
                    "Add professional photography terminology",
                    "Specify lighting and composition",
                    "Include quality indicators like 'high resolution', 'sharp focus'",
                    "Try iterative refinement in chat mode"
                ]
            },
            "Slow Generation": {
                "symptoms": ["Long wait times", "Timeouts", "Connection errors"],
                "solutions": [
                    "Simplify complex prompts",
                    "Reduce number of images requested",
                    "Check internet connection",
                    "Try generating during off-peak hours",
                    "Use shorter, more focused prompts"
                ]
            },
            "Unexpected Results": {
                "symptoms": ["Wrong subject", "Missing elements", "Incorrect style"],
                "solutions": [
                    "Be more explicit in descriptions",
                    "Use step-by-step instructions",
                    "Reference specific art styles or photographers",
                    "Use negative prompts (semantic negative)",
                    "Try multiple variations of the same prompt"
                ]
            }
        }
        
        for issue, details in issues.items():
            with st.expander(f"❓ {issue}"):
                st.write("**Symptoms:**")
                for symptom in details["symptoms"]:
                    st.write(f"• {symptom}")
                st.write("**Solutions:**")
                for solution in details["solutions"]:
                    st.write(f"• {solution}")
    
    elif doc_section == "Code Examples":
        st.subheader("💻 Code Examples")
        
        st.write("### Basic Image Generation")
        st.code("""
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

# Initialize client
client = genai.Client(api_key="your_api_key")

# Generate image
prompt = "A photorealistic nano banana in a laboratory setting"
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt],
    config=types.GenerateContentConfig(
        response_modalities=['Text', 'Image']
    )
)

# Process response
for part in response.candidates[0].content.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = Image.open(BytesIO(part.inline_data.data))
        image.save("generated_image.png")
        """, language="python")
        
        st.write("### Image Editing")
        st.code("""
from google import genai
from PIL import Image

client = genai.Client(api_key="your_api_key")

# Load existing image
image = Image.open("path/to/your/image.png")

# Edit with text prompt
prompt = "Add a wizard hat to the person in this image"
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt, image]
)

# Save edited image
for part in response.candidates[0].content.parts:
    if part.inline_data is not None:
        edited_image = Image.open(BytesIO(part.inline_data.data))
        edited_image.save("edited_image.png")
        """, language="python")
        
        st.write("### Chat Mode for Iterative Editing")
        st.code("""
# Create chat session
chat = client.chats.create(model="gemini-2.5-flash-image-preview")

# First message
response1 = chat.send_message("Create a cat sitting on a chair")

# Continue the conversation
response2 = chat.send_message("Make the cat orange")
response3 = chat.send_message("Add a wizard hat")
response4 = chat.send_message("Change the background to a library")

# Each response can contain both text and images
        """, language="python")
        
        st.write("### Multi-Image Composition")
        st.code("""
from PIL import Image

# Load multiple images
image1 = Image.open("person.jpg")
image2 = Image.open("background.jpg")

# Combine them
prompt = "Place the person from the first image into the setting from the second image"
response = client.models.generate_content(
    model="gemini-2.5-flash-image-preview",
    contents=[prompt, image1, image2]
)
        """, language="python")
        
        st.write("### Error Handling")
        st.code("""
import streamlit as st

def generate_image_safely(client, prompt, model):
    try:
        response = client.models.generate_content(
            model=model,
            contents=[prompt],
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        return response
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# Usage
response = generate_image_safely(client, prompt, model)
if response:
    # Process successful response
    process_response(response)
else:
    st.warning("Failed to generate image. Please try again.")
        """, language="python")

# Footer
st.divider()
st.write("---")
st.caption("🍌 Nano Banana - Gemini Image Generation API Testing App | Built with Streamlit")
st.caption("For issues or feedback, visit the [GitHub repository](https://github.com/your-repo/nano-banana)")

# API Status indicator
if client.is_ready():
    st.success("🟢 API Connection: Ready")
else:
    st.error("🔴 API Connection: Not Ready")