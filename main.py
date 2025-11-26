import streamlit as st
import os
import json
import re
import hashlib
import numpy as np
import base64
from io import BytesIO
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from PIL import Image, ImageOps
from utils.file_manager import FileManager

try:
    from moviepy import ImageClip, CompositeVideoClip, AudioFileClip, vfx
    from gtts import gTTS
except ImportError as e:
    st.error(f"Required library not installed: {e}")

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Listing Magic",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Premium CSS Styling - Loaded immediately to prevent FOUC
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@400;500;600;700&display=swap');

/* Global Color Variables */
:root {
    --primary-navy: #1E293B;
    --accent-gold: #D4AF37;
    --surface-white: #FFFFFF;
    --background-gray: #F8FAFC;
    --text-primary: #334155;
    --text-secondary: #64748B;
}

/* Main Background */
.main {
    background-color: var(--background-gray);
}

.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1200px;
    margin: 0 auto;
}

/* Premium Card Design with Hover Effect */
.result-card {
    background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
    padding: 2.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    border-left: 4px solid var(--accent-gold);
    margin-bottom: 1.5rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.card-header {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    font-size: 1.2rem;
    margin-bottom: 1.5rem;
    color: var(--primary-navy);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 0.75rem;
}

.result-card p {
    margin-bottom: 1.5em;
    line-height: 1.8;
    color: var(--text-primary);
    font-family: 'Inter', sans-serif;
}

/* Premium Button Styling with Gold Glow */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-gold) 0%, #C4A137 100%) !important;
    color: var(--primary-navy) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 20px rgba(212, 175, 55, 0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Typography Hierarchy */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--primary-navy) !important;
    font-weight: 700 !important;
}

h3 {
    margin-top: 2rem;
    margin-bottom: 1rem;
}

p, div, span, label {
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary);
}

/* Sidebar Styling */
section[data-testid="stSidebar"] {
    background-color: var(--primary-navy) !important;
}

section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* Metrics/Status Dashboard */
[data-testid="stMetricValue"] {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'Inter', sans-serif !important;
}

[data-testid="stMetricDelta"] {
    font-size: 0.875rem;
    font-family: 'Inter', sans-serif !important;
}

/* Photo Thumbnails with Hover */
img {
    border-radius: 8px;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

img:hover {
    transform: scale(1.03);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
    z-index: 10;
}

/* File Uploader Styling */
[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"] + div {
    display: none !important;
}

[data-testid="stFileUploaderDropzone"] {
    text-align: center;
    border: 2px dashed var(--accent-gold) !important;
    background-color: rgba(212, 175, 55, 0.05) !important;
    border-radius: 12px !important;
}

/* Hide unnecessary elements */
[data-testid="InputInstructions"] {
    display: none !important;
}

/* Dividers */
hr {
    margin: 2rem 0;
    border: none;
    border-top: 2px solid #E2E8F0;
}

/* Input Fields */
input, textarea {
    font-family: 'Inter', sans-serif !important;
    border-radius: 8px !important;
}

/* Checkbox Styling */
[data-testid="stCheckbox"] {
    font-family: 'Inter', sans-serif !important;
}
</style>
""", unsafe_allow_html=True)

# Helper function for generating consistent listing IDs
def generate_listing_ids(address):
    """
    Generate consistent, traceable listing IDs
    Returns tuple: (listing_key, listing_id)
    """
    # Create timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create short hash from address for uniqueness
    address_hash = hashlib.md5(address.encode()).hexdigest()[:6].upper()
    
    # ListingKey: MLS-YYYYMMDDHHMMSS-HASH
    listing_key = f"MLS-{timestamp}-{address_hash}"
    
    # ListingId: LM (Listing Magic) + timestamp last 10 digits
    listing_id = f"LM{timestamp[-10:]}"
    
    return listing_key, listing_id

def parse_street_address(address):
    """
    Parse street address into components required by RESO
    
    Args:
        address: e.g., "383 East Main Street"
        
    Returns:
        dict with keys: street_number, street_name, street_suffix
        
    Examples:
        "383 East Main Street" -> {street_number: "383", street_name: "East Main", street_suffix: "Street"}
        "42 Oak Avenue" -> {street_number: "42", street_name: "Oak", street_suffix: "Avenue"}
        "100-102 Park Rd" -> {street_number: "100-102", street_name: "Park", street_suffix: "Rd"}
    """
    # Common street suffixes
    suffixes = [
        'Street', 'St', 'Avenue', 'Ave', 'Road', 'Rd', 'Boulevard', 'Blvd',
        'Drive', 'Dr', 'Lane', 'Ln', 'Court', 'Ct', 'Circle', 'Cir',
        'Place', 'Pl', 'Way', 'Terrace', 'Ter', 'Parkway', 'Pkwy'
    ]
    
    # Create regex pattern for suffixes (case insensitive)
    suffix_pattern = '|'.join([re.escape(s) for s in suffixes])
    
    # Pattern: (number) (street name) (suffix)
    pattern = r'^(\d+[-\d]*)\s+(.+?)\s+(' + suffix_pattern + r')\.?$'
    
    match = re.match(pattern, address.strip(), re.IGNORECASE)
    
    if match:
        return {
            'street_number': match.group(1),
            'street_name': match.group(2).strip(),
            'street_suffix': match.group(3).capitalize()
        }
    else:
        # Fallback: try to at least get the number
        number_match = re.match(r'^(\d+[-\d]*)\s+(.+)$', address.strip())
        if number_match:
            return {
                'street_number': number_match.group(1),
                'street_name': number_match.group(2).strip(),
                'street_suffix': None
            }
        else:
            # Can't parse - return address as street name
            return {
                'street_number': None,
                'street_name': address.strip(),
                'street_suffix': None
            }

# Helper functions for smart content regeneration
def get_inputs_hash(uploaded_files):
    """Generate hash of all current inputs"""
    inputs = {
        'files': [f.name for f in uploaded_files] if uploaded_files else [],
        'address': st.session_state.get('address_input', ''),
        'city': st.session_state.get('city_input', ''),
        'state': st.session_state.get('state_input', ''),
        'zip': st.session_state.get('zip_input', ''),
        'price': st.session_state.get('price_input', ''),
        'bed_bath': st.session_state.get('bed_bath_input', ''),
        'sqft': st.session_state.get('sqft_input', ''),
        'additional': st.session_state.get('additional_details_input', '')
    }
    inputs_str = json.dumps(inputs, sort_keys=True)
    return hashlib.md5(inputs_str.encode()).hexdigest()

def inputs_changed(uploaded_files):
    """Check if inputs changed since last generation"""
    current_hash = get_inputs_hash(uploaded_files)
    last_hash = st.session_state.get('last_generated_hash', '')
    return current_hash != last_hash

# Initialize session state
if 'listing_text' not in st.session_state:
    st.session_state.listing_text = ""
if 'video_script' not in st.session_state:
    st.session_state.video_script = ""
if 'generated_video_path' not in st.session_state:
    st.session_state.generated_video_path = None
if 'processed_images' not in st.session_state:
    st.session_state.processed_images = []
if 'cached_image_html' not in st.session_state:
    st.session_state.cached_image_html = ""
if 'features_sheet' not in st.session_state:
    st.session_state.features_sheet = ""
if 'last_generated_hash' not in st.session_state:
    st.session_state.last_generated_hash = ""
if 'file_manager' not in st.session_state:
    st.session_state.file_manager = FileManager()

# Premium Sidebar Design
st.sidebar.markdown("### 🏡 Property Details")
st.sidebar.markdown("---")

# Location Section
st.sidebar.markdown("### 📍 Location")
st.sidebar.text_input(
    "Street Address", 
    key='address_input', 
    placeholder="123 Main Street",
    on_change=lambda: None  # Instant update, no Enter needed
)

col1, col2 = st.sidebar.columns(2)
with col1:
    st.text_input(
        "City", 
        key='city_input', 
        placeholder="Boston",
        on_change=lambda: None
    )
with col2:
    st.text_input(
        "State", 
        key='state_input', 
        placeholder="MA",
        on_change=lambda: None
    )

st.sidebar.text_input(
    "ZIP Code", 
    key='zip_input', 
    placeholder="02101",
    on_change=lambda: None
)

st.sidebar.markdown("---")

# Property Info Section
st.sidebar.markdown("### 💰 Property Information")
st.sidebar.selectbox(
    "Property Type",
    options=[
        "Single Family Home",
        "Condo/Townhouse",
        "Multi-Family (2-4 units)",
        "Apartment",
        "Land/Lot",
        "Commercial",
        "Other"
    ],
    key='property_type_input',
    index=0
)
st.sidebar.text_input(
    "Asking Price",
    key='price_input',
    placeholder="$500,000",
    on_change=lambda: None
)
st.sidebar.text_input(
    "Bedrooms / Bathrooms", 
    key='bed_bath_input', 
    placeholder="3 bed / 2 bath",
    on_change=lambda: None
)
st.sidebar.text_input(
    "Square Feet", 
    key='sqft_input', 
    placeholder="1,850",
    on_change=lambda: None
)

st.sidebar.markdown("---")

# Additional Details Section
st.sidebar.markdown("### 📝 Additional Details")
st.sidebar.caption("*Optional - Add details not visible in photos*")
st.sidebar.text_area(
    "",
    key='additional_details_input',
    placeholder="Recent updates, nearby amenities, special features...",
    height=100,
    max_chars=500,
    label_visibility="collapsed",
    help="Add details not visible in photos: recent updates, nearby amenities, special features, etc."
)

st.sidebar.markdown("---")

# Listing Length Section
st.sidebar.markdown("### 📏 Listing Length")
st.sidebar.radio(
    "Select listing description length",
    options=[
        "Brief (150 words)",
        "Standard (250 words)",
        "Detailed (400 words)"
    ],
    key='listing_length_input',
    index=1,  # Default to Standard
    label_visibility="collapsed"
)

st.sidebar.markdown("---")
st.sidebar.caption("*Required: Address, City, State*")

st.markdown("""
<div style="
    text-align: center;
    padding: 3rem 0 2rem 0;
    background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
    margin: -2rem -3rem 2rem -3rem;
    border-radius: 0 0 24px 24px;
">
    <h1 style="
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        color: #FFFFFF;
        margin: 0 0 0.5rem 0;
        letter-spacing: -1px;
    ">✨ Listing Magic</h1>
    <p style="
        font-family: 'Inter', sans-serif;
        color: #D4AF37;
        font-size: 1.1rem;
        margin: 0;
        font-weight: 500;
    ">AI-Powered Real Estate Marketing</p>
</div>
""", unsafe_allow_html=True)

# Helper function to convert PIL image to base64
def image_to_base64(img, max_width=150):
    """Convert PIL image to base64 string for HTML embedding"""
    # Resize for thumbnail
    img_copy = img.copy()
    aspect_ratio = img_copy.height / img_copy.width
    new_height = int(max_width * aspect_ratio)
    img_copy = img_copy.resize((max_width, new_height), Image.Resampling.LANCZOS)

    # Convert to base64
    buffered = BytesIO()
    img_copy.save(buffered, format="JPEG", quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

# Create a container for the upload area
upload_container = st.container()

with upload_container:
    uploaded_files = st.file_uploader(
        "Upload Property Photos",
        accept_multiple_files=True,
        type=['jpg', 'png', 'jpeg'],
        label_visibility="visible"
    )

    if uploaded_files:
        # Load and cache images
        images_changed = not st.session_state.processed_images or len(st.session_state.processed_images) != len(uploaded_files)

        if images_changed:
            st.session_state.processed_images = [
                ImageOps.exif_transpose(Image.open(file)) for file in uploaded_files
            ]

            # Convert images to base64 for embedding (only when images change)
            img_html_list = []
            for img in st.session_state.processed_images:
                img_base64 = image_to_base64(img)
                img_html_list.append(f'<img src="{img_base64}" style="width: 100%; border-radius: 8px; margin: 5px;">')

            # Create grid of images (8 per row)
            num_cols = 8
            rows_html = []
            for i in range(0, len(img_html_list), num_cols):
                row_imgs = img_html_list[i:i+num_cols]
                row_html = '<div style="display: flex; gap: 10px; margin-bottom: 10px;">'
                for img_html in row_imgs:
                    row_html += f'<div style="flex: 1; min-width: 0;">{img_html}</div>'
                row_html += '</div>'
                rows_html.append(row_html)

            # Cache the generated HTML
            st.session_state.cached_image_html = ''.join(rows_html)

        # Display images inside the upload area with custom styling (use cached HTML)
        st.markdown(f"""
        <div style="
            margin-top: -10px;
            padding: 20px;
            background-color: #262730;
            border-radius: 0 0 8px 8px;
            border: 1px solid #464754;
            border-top: none;
        ">
            <p style="color: #a0a0a0; font-size: 14px; margin-bottom: 15px;">✓ {len(uploaded_files)} photos uploaded</p>
            {st.session_state.cached_image_html}
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")




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

def generate_video(images, file_manager):
    """
    Generate a property tour video from images

    Args:
        images: List of PIL Image objects
        file_manager: FileManager instance for temp file handling

    Returns:
        str: Path to the generated video file
    """
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
    output_path = file_manager.get_path("property_tour.mp4")

    # Write video file
    video.write_videofile(output_path, fps=24, codec='libx264', preset='ultrafast')
    return output_path

def extract_narration_from_script(script_text):
    """
    Extract only the spoken narration from a formatted video script.
    Removes timestamps, scene labels, and formatting - keeps only quoted narration.
    
    Args:
        script_text: Full video script with formatting
        
    Returns:
        Clean narration text ready for TTS
    """
    
    # Method 1: Extract text within double quotes (most reliable)
    # Finds all text between " and " characters
    quoted_text = re.findall(r'"([^"]*)"', script_text)
    
    if quoted_text:
        # Join all quoted sections with a space
        narration = ' '.join(quoted_text)
        
        # Clean up any extra spaces
        narration = re.sub(r'\s+', ' ', narration).strip()
        
        return narration
    
    # Method 2: If no quotes found, try to extract after "Audio (Voiceover):"
    voiceover_pattern = r'\*\*Audio \(Voiceover\):\*\*\s*(.+?)(?=\*\*\d|$)'
    voiceover_matches = re.findall(voiceover_pattern, script_text, re.DOTALL)
    
    if voiceover_matches:
        # Clean each match
        clean_matches = []
        for match in voiceover_matches:
            # Remove any remaining markdown
            clean = re.sub(r'\*\*', '', match)
            # Remove quotes if present
            clean = clean.strip().strip('"\'')
            clean_matches.append(clean)
        
        narration = ' '.join(clean_matches)
        narration = re.sub(r'\s+', ' ', narration).strip()
        return narration
    
    # Method 3: Last resort - try to remove obvious formatting
    lines = script_text.split('\n')
    clean_lines = []
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # Skip lines that start with timestamp formatting
        if re.match(r'^\*\*\d+:\d+', line):
            continue
        
        # Skip lines that are just Visual labels
        if re.match(r'^\*\*Visual:', line, re.IGNORECASE):
            continue
        
        # Skip scene headers
        if re.match(r'^Scene \d+:', line, re.IGNORECASE):
            continue
        
        # If we got here, might be narration
        # Remove markdown bold
        line = re.sub(r'\*\*', '', line)
        
        if line:
            clean_lines.append(line)
    
    narration = ' '.join(clean_lines)
    narration = re.sub(r'\s+', ' ', narration).strip()
    
    return narration

def generate_video_with_voiceover(images, script_text, file_manager):
    """
    Generate property tour video with AI voiceover

    Args:
        images: List of PIL Image objects
        script_text: Video script text containing narration
        file_manager: FileManager instance for temp file handling

    Returns:
        str: Path to the generated video file with voiceover
    """

    # CRITICAL: Clean the script to extract only narration
    clean_narration = extract_narration_from_script(script_text)

    # Validate we have narration to speak
    if not clean_narration or len(clean_narration.strip()) < 10:
        raise ValueError("Could not extract narration from script. Please check script format.")

    # Debug: Show what will be spoken
    print(f"DEBUG - Original script length: {len(script_text)} chars")
    print(f"DEBUG - Clean narration length: {len(clean_narration)} chars")
    print(f"DEBUG - Narration to speak: {clean_narration[:200]}...")  # First 200 chars

    # Generate voiceover audio from cleaned narration
    tts = gTTS(text=clean_narration, lang='en', slow=False)
    audio_path = file_manager.get_path("voiceover.mp3")
    tts.save(audio_path)

    # Load audio
    audio = AudioFileClip(audio_path)
    audio_duration = audio.duration

    # Calculate image duration based on audio length
    duration_per_image = audio_duration / len(images)

    # Create video clips
    clips = []
    for i, img in enumerate(images):
        # Images are already EXIF-transposed from cache
        img = resize_with_padding(img, (1920, 1080))
        img_array = np.array(img.convert('RGB'))

        clip = ImageClip(img_array).with_duration(duration_per_image)

        # Add crossfade transitions
        if i > 0:
            overlap = min(0.5, duration_per_image * 0.2)  # 20% overlap or 0.5s max
            start_time = i * (duration_per_image - overlap)
            clip = clip.with_start(start_time).with_effects([vfx.CrossFadeIn(overlap)])

        clips.append(clip)

    # Create composite video
    video = CompositeVideoClip(clips)

    # Add audio to video
    final_video = video.with_audio(audio)

    output_path = file_manager.get_path("property_tour_with_voice.mp4")
    final_video.write_videofile(output_path, fps=24, codec='libx264', preset='ultrafast', audio_codec='aac')

    # Cleanup temporary audio file
    if os.path.exists(audio_path):
        os.remove(audio_path)
    audio.close()
    video.close()

    return output_path

def generate_reso_data(images, addr, city, state, zip_code, price, beds_baths, sqft, additional_details, listing_description):
    """Generate RESO-compliant JSON data using Gemini photo analysis"""
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")
    
    client = genai.Client(api_key=api_key)
    
    # Generate consistent, traceable IDs
    listing_key, listing_id = generate_listing_ids(addr)
    
    # Parse street address components
    address_parts = parse_street_address(addr)
    
    # Construct full address
    full_address = f"{addr}, {city}, {state}"
    if zip_code and zip_code.strip():
        full_address += f" {zip_code}"
    
    # Construct comprehensive RESO generation prompt
    prompt = f"""
    You are a real estate data analyst creating MLS-compliant RESO JSON data.
    
    Property: {full_address}
    Price: {price}
    Bedrooms/Bathrooms: {beds_baths}
    Square Feet: {sqft if sqft else 'Not provided'}
    {f"Additional Details: {additional_details}" if additional_details else ""}
    
    Analyze the provided photos to identify:
    1. Architectural style (Colonial, Ranch, Contemporary, Victorian, etc.)
    2. Interior features (flooring type, countertops, built-ins, fireplaces, etc.)
    3. Appliances visible in photos (dishwasher, refrigerator, range, microwave, etc.)
    4. Heating/cooling systems (if visible - radiators, vents, AC units)
    5. Exterior features (deck, patio, fencing, landscaping, garage, etc.)
    6. Year built (estimate from architectural style - use null if very uncertain)
    7. Living area square footage (estimate from room sizes - use null if uncertain)
    
    Generate a complete RESO-compliant JSON object with these exact fields:
    
    CRITICAL: Use these EXACT values for address fields (do not parse differently):
    
    {{
      "ListingKey": "{listing_key}",
      "ListingId": "{listing_id}",
      "StandardStatus": "Active",
      "ListPrice": Extract numeric value from {price},
      "PropertyType": "Residential",
      "PropertySubType": Infer from photos ("Single Family Residence", "Condominium", "Townhouse", etc.),
      "UnparsedAddress": "{full_address}",
      "StreetNumber": "{address_parts['street_number']}",
      "StreetName": "{address_parts['street_name']}",
      "StreetSuffix": {f'"{address_parts["street_suffix"]}"' if address_parts['street_suffix'] else 'null'},
      "City": "{city}",
      "StateOrProvince": "{state}",
      "PostalCode": {f'"{zip_code}"' if zip_code else 'null'},
      "Country": "USA",
      "BedroomsTotal": Parse from {beds_baths},
      "BathroomsFull": Parse full baths from {beds_baths},
      "BathroomsHalf": Parse half baths from {beds_baths} or use 0,
      "LivingArea": {sqft if sqft else 'null'},
      "LivingAreaUnits": "Square Feet",
      "YearBuilt": Estimate from architectural style or use null,
      "Cooling": Array of cooling systems seen in photos ["Central Air", "Window Units", etc.] or empty array,
      "Heating": Array of heating systems seen ["Forced Air", "Radiators", "Natural Gas", etc.] or empty array,
      "InteriorFeatures": Array of features seen ["Hardwood Floors", "Granite Counters", "Recessed Lighting", "Crown Molding", "Fireplace", etc.],
      "Appliances": Array of appliances visible ["Dishwasher", "Disposal", "Microwave", "Range", "Refrigerator", "Washer", "Dryer", etc.],
      "ExteriorFeatures": Array of exterior features ["Deck", "Patio", "Fenced Yard", "Professional Landscaping", "Garage", etc.],
      "ArchitecturalStyle": Identify from photos,
      "Photos": [
        {{
          "Order": 1,
          "MediaURL": "placeholder",
          "Description": "Describe what this photo shows (e.g., 'Front Exterior', 'Living Room', 'Kitchen')"
        }},
        ... one entry for each photo provided
      ],
      "PublicRemarks": "{listing_description[:500]}"
    }}
    
    CRITICAL RULES:
    1. Output ONLY valid JSON, no markdown code blocks, no explanations
    2. Use null for uncertain fields (do not guess wildly)
    3. Make reasonable inferences from photos
    4. Maintain Fair Housing Act compliance (no discriminatory language)
    5. Use standard RESO field names exactly as shown
    6. Ensure all arrays are properly formatted
    7. Parse address components carefully
    
    Output the complete JSON object now:
    """
    
    # Prepare content for Gemini
    contents = [prompt] + images
    
    # Generate RESO data
    response = client.models.generate_content(
        model='gemini-3-pro-preview',
        contents=contents
    )
    
    # Parse JSON response
    response_text = response.text.strip()
    
    # Remove markdown code blocks if present
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
    
    # Parse and validate JSON
    try:
        reso_data = json.loads(response_text)
        return reso_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse RESO JSON: {e}\n\nResponse: {response_text}")

# Status Dashboard
if uploaded_files:
    st.markdown("""
    <h3 style="
        font-family: 'Playfair Display', serif;
        color: #1E293B;
        font-size: 1.8rem;
        margin-bottom: 1.5rem;
    ">📊 Generation Status</h3>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "✅" if st.session_state.listing_text else "⚪"
        st.metric("Listing", status, delta="Ready" if st.session_state.listing_text else "Not Generated")
    
    with col2:
        status = "✅" if st.session_state.features_sheet else "⚪"
        st.metric("Features", status, delta="Ready" if st.session_state.features_sheet else "Not Generated")
    
    with col3:
        status = "✅" if st.session_state.generated_video_path else "⚪"
        st.metric("Video", status, delta="Ready" if st.session_state.generated_video_path else "Not Generated")
    
    with col4:
        # Check if inputs changed
        changed = inputs_changed(uploaded_files) if st.session_state.listing_text else False
        status = "⚠️" if changed else "✅" if st.session_state.listing_text else "⚪"
        st.metric("Data Fresh", status, delta="Update Needed" if changed else "Current")
    
    st.markdown("---")

# Premium Button Layout
st.markdown("""
<h3 style="
    font-family: 'Playfair Display', serif;
    color: #1E293B;
    font-size: 1.8rem;
    margin-bottom: 1.5rem;
    text-align: center;
">🎬 Generate Content</h3>
""", unsafe_allow_html=True)

# Primary action row
col1, col2, col3 = st.columns(3)

with col1:
    generate_listing = st.button(
        "📝 Listing & Script",
        type="primary",
        width='stretch',
        help="Generate property listing description and video script"
    )

with col2:
    generate_features = st.button(
        "⭐ Features Sheet",
        width='stretch',
        help="Generate detailed property features document"
    )

with col3:
    download_reso = st.button(
        "📥 RESO Data",
        width='stretch',
        help="Download MLS-compliant RESO JSON"
    )

# Video generation (full width, secondary)
st.markdown("")  # Spacing
generate_video = st.button(
    "🎥 Generate Video with Voiceover",
    width='stretch',
    help="Create property tour video with AI narration"
)

# Force regenerate option (subtle, bottom)
st.markdown("")
force_regen = st.checkbox("🔄 Force regenerate (ignore cache)", value=False)

st.markdown("---")

# Main Action Buttons Logic
if generate_listing:
    if not uploaded_files:
        st.error("Please upload photos first.")
    elif not force_regen and not inputs_changed(uploaded_files) and st.session_state.listing_text:
        st.info("ℹ️ Content is up to date. No changes detected since last generation.")
    else:
        # Read values from session state
        addr = st.session_state.get('address_input', '')
        city = st.session_state.get('city_input', '')
        state = st.session_state.get('state_input', '')
        zip_code = st.session_state.get('zip_input', '')
        property_type = st.session_state.get('property_type_input', 'Single Family Home')
        price = st.session_state.get('price_input', '')
        beds = st.session_state.get('bed_bath_input', '')
        sqft = st.session_state.get('sqft_input', '')
        
        # Visual Debugger - Show what data is being sent
        st.info(f"🚀 Sending to Gemini: {addr}, {city}, {state} {zip_code} | {price} | {beds} | {sqft} sqft")
        
        # Validation - Stop if critical fields are empty
        if not addr or addr.strip() == '':
            st.error("⚠️ Error: Street address is required.")
        elif not city or city.strip() == '':
            st.error("⚠️ Error: City is required.")
        elif not state or state.strip() == '':
            st.error("⚠️ Error: State is required.")
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
                        city_display = city if city else ''
                        state_display = state if state else ''
                        zip_display = zip_code if zip_code else ''
                        price_display = price if price else 'Price Upon Request'
                        beds_display = beds if beds else 'Contact for Details'
                        sqft_display = sqft if sqft else 'N/A'
                        
                        # Construct full address for display
                        full_address = f"{addr_display}, {city_display}, {state_display} {zip_display}".strip(', ')
                        
                        # Get additional details from user input
                        additional_details = st.session_state.get('additional_details_input', '').strip()

                        # Extract word count from listing length selection
                        listing_length = st.session_state.get('listing_length_input', 'Standard (250 words)')
                        # Extract the number from the string (e.g., "Brief (150 words)" -> 150)
                        word_count_match = re.search(r'\((\d+) words\)', listing_length)
                        word_count = int(word_count_match.group(1)) if word_count_match else 250

                        # Construct prompt with actual values
                        prompt = f"""
                        You are a top-tier luxury real estate copywriter. Here are photos of {addr_display}, a {property_type} listed for {price_display}. The property has {beds_display}.

                        {f"IMPORTANT DETAILS TO HIGHLIGHT: {additional_details}" if additional_details else ""}

                        CRITICAL LEGAL CONSTRAINT: You must strictly adhere to the U.S. Fair Housing Act.
                        NEVER mention race, religion, gender, disability, or familial status.
                        DO NOT use phrases like "perfect for families", "great for kids", "bachelor pad", "walking distance to church", or "gentlemen's farm".

                        Focus strictly on the physical features, architectural style, and lifestyle amenities.

                        Output Requirements:
                        Provide the output in JSON format with two keys: "listing_description" and "video_script".
                        The values should be plain text (no HTML tags).
                        Format the output in clean Markdown. Ensure there is a double newline between every paragraph for proper spacing.

                        Listing Description: Write a {word_count}-word engaging, professional listing description tailored for a {property_type}. Use the provided address ({addr_display}) and price ({price_display}) in the first paragraph. Do not use placeholders like [Address] or [Price]. Highlight features appropriate for this property type as seen in the photos (e.g., natural light, flooring, appliances, common areas, etc.).

                        Social Media Video Script: Create a structured script for a 60-second video tour (Instagram Reel/TikTok style) that emphasizes the unique selling points of a {property_type}. Match specific voiceover lines to specific photo filenames provided.
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
                            
                            # Update hash after successful generation
                            st.session_state.last_generated_hash = get_inputs_hash(uploaded_files)

                            st.success("✅ Listing and script generated successfully!")
                            st.rerun()

                        except json.JSONDecodeError:
                            st.error("Failed to parse the response. Raw output:")
                            st.write(response.text)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# Generate Video Button (Always visible)
# Generate Video Button Logic
if generate_video:
    if not st.session_state.video_script:
        st.error("Please generate the listing script first!")
    elif not uploaded_files:
        st.error("Please upload photos first.")
    else:
        # Clean up old video if exists
        if st.session_state.generated_video_path and os.path.exists(st.session_state.generated_video_path):
            os.remove(st.session_state.generated_video_path)
        
        # Load images from cache
        images = st.session_state.processed_images
        
        if len(images) < 2:
            st.warning("Please upload at least 2 photos for a video tour.")
        else:
            # Generate video with voiceover
            with st.spinner("Generating voiceover..."):
                try:
                    with st.spinner("Creating video with voiceover..."):
                        video_path = generate_video_with_voiceover(
                            images,
                            st.session_state.video_script,
                            st.session_state.file_manager
                        )

                        st.session_state.generated_video_path = video_path
                        st.success("✅ Video with voiceover generated successfully!")
                        st.rerun()

                except Exception as e:
                    st.error(f"An error occurred during video generation: {e}")

# Generate Features Sheet Button Logic
if generate_features:
    if not uploaded_files:
        st.error("Please upload photos first.")
    elif not st.session_state.listing_text:
        st.error("Please generate the listing description first!")
    else:
        # Read values from session state
        addr = st.session_state.address_input
        property_type = st.session_state.get('property_type_input', 'Single Family Home')
        price = st.session_state.price_input
        beds = st.session_state.bed_bath_input
        additional_details = st.session_state.get('additional_details_input', '').strip()

        # Handle empty data gracefully
        addr_display = addr if addr else 'Unknown Address'
        price_display = price if price else 'Price Upon Request'
        beds_display = beds if beds else 'Contact for Details'

        with st.spinner("Generating detailed features sheet..."):
            try:
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    st.error("Please set your GOOGLE_API_KEY in the .env file.")
                else:
                    client = genai.Client(api_key=api_key)

                    # Construct features sheet prompt
                    prompt = f"""
                    You are a luxury real estate copywriter creating a detailed Property Features Sheet for potential buyers.

                    Property Type: {property_type}
                    Property: {addr_display}, listed for {price_display}, {beds_display}
                    
                    {f"IMPORTANT DETAILS TO HIGHLIGHT: {additional_details}" if additional_details else ""}
                    
                    Create a comprehensive Property Features Sheet (300-500 words) tailored for a {property_type} that includes:

                    1. An engaging, descriptive title for the property (not just the address)
                    2. Detailed descriptions of each room and living space appropriate for this property type
                    3. Unique features, architectural details, and character elements
                    4. Recent updates and improvements
                    5. Outdoor spaces, parking, and storage areas (if applicable to this property type)
                    6. Use descriptive, marketing-focused language that appeals to buyers interested in a {property_type}
                    
                    CRITICAL LEGAL CONSTRAINT: You must strictly adhere to the U.S. Fair Housing Act.
                    NEVER mention race, religion, gender, disability, or familial status.
                    DO NOT use phrases like "perfect for families", "great for kids", "bachelor pad", "walking distance to church", or "gentlemen's farm".
                    
                    Focus strictly on the physical features, architectural style, and lifestyle amenities.
                    
                    Format the output with:
                    - A compelling title on the first line
                    - Well-structured paragraphs with double newlines between them
                    - Descriptive, engaging language
                    - 300-500 words total
                    
                    Output ONLY the features sheet text, no JSON or additional formatting.
                    """
                    
                    # Prepare content for Gemini
                    images = st.session_state.processed_images
                    contents = [prompt] + images
                    
                    response = client.models.generate_content(
                        model='gemini-3-pro-preview',
                        contents=contents
                    )
                    
                    # Get and normalize the response
                    features_text = response.text.strip()
                    
                    # Normalize spacing
                    features_text = re.sub(r'\n\n+', '\n\n', features_text)
                    
                    # Store in session state
                    st.session_state.features_sheet = features_text

                    st.success("✅ Features sheet generated successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Download RESO Data Button Logic
if download_reso:
    if not uploaded_files:
        st.error("Please upload photos first.")
    elif not st.session_state.listing_text:
        st.error("Please generate the listing description first!")
    else:
        # Read values from session state
        addr = st.session_state.get('address_input', '')
        city = st.session_state.get('city_input', '')
        state = st.session_state.get('state_input', '')
        zip_code = st.session_state.get('zip_input', '')
        price = st.session_state.get('price_input', '')
        beds_baths = st.session_state.get('bed_bath_input', '')
        sqft = st.session_state.get('sqft_input', '')
        additional_details = st.session_state.get('additional_details_input', '').strip()
        
        with st.spinner("Generating RESO-compliant JSON data..."):
            try:
                # Generate RESO data
                reso_json = generate_reso_data(
                    st.session_state.processed_images,
                    addr,
                    city,
                    state,
                    zip_code,
                    price,
                    beds_baths,
                    sqft,
                    additional_details,
                    st.session_state.listing_text
                )
                
                # Create filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                safe_addr = addr.replace(' ', '_').replace(',', '').replace('/', '_')
                filename = f"RESO_{safe_addr}_{timestamp}.json"
                
                # Create download button
                st.download_button(
                    label="📥 Download RESO JSON",
                    data=json.dumps(reso_json, indent=2),
                    file_name=filename,
                    mime="application/json"
                )
                
                st.success("✅ RESO data generated successfully!")
                
                # Show preview of generated data
                with st.expander("Preview RESO Data"):
                    st.json(reso_json)
                    
            except Exception as e:
                st.error(f"An error occurred generating RESO data: {e}")

# Layout - Full width Features Sheet card, then 2-column layout for Listing and Script
if st.session_state.features_sheet:
    # Features Sheet Card (Full Width)
    features_content = st.session_state.features_sheet
    html_content = format_content_to_html(features_content, "Generate a features sheet to see it here.")
    
    st.markdown(f"""
    <div class="result-card">
        <div class="card-header">Property Features Sheet</div>
        <div>{html_content}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)  # Add spacing

# Layout Columns for Listing and Script
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
