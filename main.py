import streamlit as st
import os
import json
import re
import numpy as np
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageOps

try:
    from moviepy import ImageClip, CompositeVideoClip, vfx
except ImportError:
    st.error("MoviePy is not installed.")

# Load environment variables
load_dotenv()

# Initialize session state
if 'listing_text' not in st.session_state:
    st.session_state.listing_text = ""
if 'video_script' not in st.session_state:
    st.session_state.video_script = ""
if 'generated_video_path' not in st.session_state:
    st.session_state.generated_video_path = None
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []

# Sidebar Inputs (No Form - Live Updates)
st.sidebar.header("Property Details")
st.sidebar.text_input("Property Address", key='address_input')
st.sidebar.text_input("Asking Price", key='price_input')
st.sidebar.text_input("Bedrooms / Bathrooms", key='bed_bath_input')

st.title("Real Estate Beta")

uploaded_files = st.file_uploader("Upload Property Photos", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])

if uploaded_files:
    # Load and process images once, cache in session state
    if not st.session_state.processed_images or len(st.session_state.processed_images) != len(uploaded_files):
        st.session_state.processed_images = [
            ImageOps.exif_transpose(Image.open(file)) for file in uploaded_files
        ]
    
    st.write(f"{len(uploaded_files)} photos loaded")
    with st.expander("📸 Source Photos"):
        for i in range(0, len(st.session_state.processed_images), 4):
            cols = st.columns(4)
            batch = st.session_state.processed_images[i:i+4]
            for j, img in enumerate(batch):
                cols[j].image(img, use_container_width=True)

# Custom CSS
st.markdown("""
<style>
.result-card {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    color: #000000;
    margin-top: 0px;
    font-family: 'Georgia', serif;
    min-height: 500px;
}
.card-header {
    font-family: 'Helvetica Neue', sans-serif;
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 15px;
    border-bottom: 2px solid #f0f0f0;
    padding-bottom: 8px;
    color: #34495e;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.result-card p {
    margin-bottom: 1.5em;
    line-height: 1.6;
}
.result-card p:last-child {
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

# Video Generation Helper
def format_content_to_html(content, placeholder_text):
    """Convert markdown paragraphs to HTML with proper spacing"""
    if content and content != placeholder_text:
        paragraphs = content.split('\n\n')
        return ''.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])
    return f'<p>{content}</p>'

def resize_with_padding(image, target_size=(1920, 1080)):
    # Calculate aspect ratio
    width, height = image.size
    target_width, target_height = target_size
    
    aspect_ratio = width / height
    target_aspect_ratio = target_width / target_height
    
    if aspect_ratio > target_aspect_ratio:
        # Width is the limiting factor
        new_width = target_width
        new_height = int(target_width / aspect_ratio)
    else:
        # Height is the limiting factor
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
        
    # Resize image
    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Create black background
    new_image = Image.new("RGB", target_size, (0, 0, 0))
    
    # Paste resized image in center
    x_offset = (target_width - new_width) // 2
    y_offset = (target_height - new_height) // 2
    new_image.paste(resized_image, (x_offset, y_offset))
    
    return new_image

def generate_video(images):
    clips = []
    for i, img in enumerate(images):
        # Images are already EXIF-transposed from cache
        
        # Resize with padding (Letterboxing)
        img = resize_with_padding(img, (1920, 1080))
        
        # Convert PIL Image to numpy array
        img_array = np.array(img.convert('RGB'))
        
        # Create ImageClip
        clip = ImageClip(img_array).with_duration(3)
        
        # Apply crossfade and positioning
        if i > 0:
            start_time = i * 2  # 3s duration - 1s overlap
            clip = clip.with_start(start_time).with_effects([vfx.CrossFadeIn(1)])
        
        clips.append(clip)
    
    # Create composite video
    video = CompositeVideoClip(clips)
    output_path = "property_tour.mp4"
    
    # Write video file
    video.write_videofile(output_path, fps=24, codec='libx264', preset='ultrafast')
    return output_path

# Main Action Buttons
if st.button("Generate Listing & Script", type="primary"):
    if not uploaded_files:
        st.error("Please upload photos first.")
    else:
        # Read values directly from session state using widget keys
        addr = st.session_state.address_input
        price = st.session_state.price_input
        beds = st.session_state.bed_bath_input
        
        # Visual Debugger - Show what data is being sent
        st.info(f"🚀 Sending to Gemini: {addr} | {price} | {beds}")
        
        # Validation - Stop if address is empty
        if not addr or addr.strip() == '':
            st.error("⚠️ Error: Address is missing. Please type an address in the sidebar and click 'Update Details'.")
        else:
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                st.error("Please set your GOOGLE_API_KEY in the .env file.")
            else:
                with st.spinner("Analyzing property photos..."):
                    try:
                        client = genai.Client(api_key=api_key)
                        
                        # DEBUG PRINT - Show what Python sees
                        print(f"DEBUG: Sending Address: {addr}, Price: {price}, Beds/Baths: {beds}")
                        
                        # Handle empty data gracefully
                        addr_display = addr if addr else 'Unknown Address'
                        price_display = price if price else 'Price Upon Request'
                        beds_display = beds if beds else 'Contact for Details'
                        
                        # Construct prompt with actual values
                        prompt = f"""
                        You are a top-tier luxury real estate copywriter. Here are photos of {addr_display}, listed for {price_display}. The home has {beds_display}.

                        CRITICAL LEGAL CONSTRAINT: You must strictly adhere to the U.S. Fair Housing Act.
                        NEVER mention race, religion, gender, disability, or familial status.
                        DO NOT use phrases like "perfect for families", "great for kids", "bachelor pad", "walking distance to church", or "gentlemen's farm".

                        Focus strictly on the physical features, architectural style, and lifestyle amenities.

                        Output Requirements:
                        Provide the output in JSON format with two keys: "listing_description" and "video_script".
                        The values should be plain text (no HTML tags).
                        Format the output in clean Markdown. Ensure there is a double newline between every paragraph for proper spacing.
                        
                        Listing Description: Write a 250-word engaging, professional listing description. Use the provided address ({addr_display}) and price ({price_display}) in the first paragraph. Do not use placeholders like [Address] or [Price]. Highlight features seen in the photos (e.g., natural light, flooring, appliances).
                        
                        Social Media Video Script: Create a structured script for a 60-second video tour (Instagram Reel/TikTok style). Match specific voiceover lines to specific photo filenames provided.
                        """
                        
                        # Prepare content for Gemini
                        images = st.session_state.processed_images
                        
                        contents = [prompt] + images
                        
                        response = client.models.generate_content(
                            model='gemini-3-pro-preview', 
                            contents=contents
                        )
                        
                        # Parse JSON and display
                        try:
                            # Clean up response text if it has markdown code blocks
                            text = response.text
                            if "```json" in text:
                                text = text.split("```json")[1].split("```")[0]
                            elif "```" in text:
                                text = text.split("```")[1].split("```")[0]
                            
                            data = json.loads(text)
                            
                            # Post-processing for spacing - ensure consistent double newlines between paragraphs
                            listing_desc = data.get('listing_description', 'No description generated.')
                            video_script = data.get('video_script', 'No script generated.')
                            
                            # Use regex to normalize all consecutive newlines (2 or more) to exactly 2 newlines
                            # This ensures consistent spacing regardless of how the AI formatted the text
                            listing_desc = re.sub(r'\n\n+', '\n\n', listing_desc)
                            video_script = re.sub(r'\n\n+', '\n\n', video_script)

                            # Store in session state
                            st.session_state.listing_text = listing_desc
                            st.session_state.video_script = video_script
                            
                            st.success("✅ Listing and script generated successfully!")
                                
                        except json.JSONDecodeError:
                            st.error("Failed to parse the response. Raw output:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# Generate Video Button (Always visible)
if st.button("Generate Video"):
    if not st.session_state.video_script:
        st.error("Please generate the listing script first!")
    elif not uploaded_files:
        st.error("Please upload photos first.")
    else:
        with st.spinner("Generating video tour..."):
            try:
                # Clean up old video if exists
                if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
                    os.remove(st.session_state.generated_video_path)
                
                # Load images from cache
                images = st.session_state.processed_images
                
                if len(images) < 2:
                    st.warning("Please upload at least 2 photos for a video tour.")
                else:
                    video_path = generate_video(images)
                    st.session_state.generated_video_path = video_path
                    st.success("Video generated successfully!")
                    st.rerun()
            except Exception as e:
                st.error(f"An error occurred during video generation: {e}")

# Layout Columns
col1, col2 = st.columns(2)

with col1:
    # Listing Description Card
    listing_content = st.session_state.listing_text if st.session_state.listing_text else "Generate a listing to see it here."
    html_content = format_content_to_html(listing_content, "Generate a listing to see it here.")
    
    st.markdown(f"""
    <div class="result-card">
        <div class="card-header">Listing Description</div>
        <div>{html_content}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Video Section at the top of right column
    if st.session_state.generated_video_path:
        st.video(st.session_state.generated_video_path)
    
    # Video Script Card
    script_content = st.session_state.video_script if st.session_state.video_script else "Generate a script to see it here."
    html_content = format_content_to_html(script_content, "Generate a script to see it here.")
    
    st.markdown(f"""
    <div class="result-card">
        <div class="card-header">Video Script</div>
        <div>{html_content}</div>
    </div>
    """, unsafe_allow_html=True)
