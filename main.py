"""
Listing Magic - AI-Powered Real Estate Marketing Platform

Main application file orchestrating all components and services.
"""

import streamlit as st
import os
import json
import re
from datetime import datetime
from dotenv import load_dotenv

# Import our modular components
from listing_magic.styles import get_premium_css
from listing_magic.components import (
    render_sidebar,
    render_upload_area,
    render_status_dashboard,
    render_result_cards
)
from listing_magic.services import (
    generate_video_with_voiceover,
    generate_reso_data,
    generate_listing_content,
    generate_features_sheet
)
from listing_magic.utils import (
    FileManager,
    get_inputs_hash,
    inputs_changed
)

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Listing Magic",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Apply premium CSS styling
st.markdown(get_premium_css(), unsafe_allow_html=True)

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

# Render sidebar with property input forms
render_sidebar()

# Hero Header
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

# Render upload area with embedded thumbnails
uploaded_files = render_upload_area()

# Render status dashboard
render_status_dashboard(uploaded_files)

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
        use_container_width=True,
        help="Generate property listing description and video script"
    )

with col2:
    generate_features = st.button(
        "⭐ Features Sheet",
        use_container_width=True,
        help="Generate detailed property features document"
    )

with col3:
    download_reso = st.button(
        "📥 RESO Data",
        use_container_width=True,
        help="Download MLS-compliant RESO JSON"
    )

# Video generation (full width, secondary)
st.markdown("")  # Spacing
generate_video = st.button(
    "🎥 Generate Video with Voiceover",
    use_container_width=True,
    help="Create property tour video with AI narration"
)

# Force regenerate option (subtle, bottom)
st.markdown("")
force_regen = st.checkbox("🔄 Force regenerate (ignore cache)", value=False)

st.markdown("---")

# ============================================================================
# BUTTON HANDLERS
# ============================================================================

# Generate Listing & Script Button Handler
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
                st.error("⚠️ GOOGLE_API_KEY not found!")
                st.info("""
                **Setup Instructions:**
                1. Create a `.env` file in your project root
                2. Add: `GOOGLE_API_KEY=your_api_key_here`
                3. Get your key from: https://makersuite.google.com/app/apikey
                4. Restart the Streamlit app
                """)
                st.stop()
            else:
                with st.spinner("Analyzing property photos..."):
                    try:
                        # Handle empty data gracefully
                        addr_display = addr if addr else 'Unknown Address'
                        price_display = price if price else 'Price Upon Request'
                        beds_display = beds if beds else 'Contact for Details'

                        # Get additional details from user input
                        additional_details = st.session_state.get('additional_details_input', '').strip()

                        # Extract word count from listing length selection
                        listing_length = st.session_state.get('listing_length_input', 'Standard (250 words)')
                        word_count_match = re.search(r'\((\d+) words\)', listing_length)
                        word_count = int(word_count_match.group(1)) if word_count_match else 250

                        # Generate listing content using service
                        listing_desc, video_script = generate_listing_content(
                            st.session_state.processed_images,
                            addr_display,
                            price_display,
                            beds_display,
                            property_type,
                            additional_details,
                            word_count
                        )

                        # Store in session state
                        st.session_state.listing_text = listing_desc
                        st.session_state.video_script = video_script

                        # Update hash after successful generation
                        st.session_state.last_generated_hash = get_inputs_hash(uploaded_files)

                        st.success("✅ Listing and script generated successfully!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"An error occurred: {e}")

# Generate Video Button Handler
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

# Generate Features Sheet Button Handler
if generate_features:
    if not uploaded_files:
        st.error("Please upload photos first.")
    elif not st.session_state.listing_text:
        st.error("Please generate the listing description first!")
    else:
        # Read values from session state
        addr = st.session_state.get('address_input', '')
        property_type = st.session_state.get('property_type_input', 'Single Family Home')
        price = st.session_state.get('price_input', '')
        beds = st.session_state.get('bed_bath_input', '')
        additional_details = st.session_state.get('additional_details_input', '').strip()

        # Handle empty data gracefully
        addr_display = addr if addr else 'Unknown Address'
        price_display = price if price else 'Price Upon Request'
        beds_display = beds if beds else 'Contact for Details'

        with st.spinner("Generating detailed features sheet..."):
            try:
                api_key = os.getenv("GOOGLE_API_KEY")
                if not api_key:
                    st.error("⚠️ GOOGLE_API_KEY not found!")
                    st.info("""
                    **Setup Instructions:**
                    1. Create a `.env` file in your project root
                    2. Add: `GOOGLE_API_KEY=your_api_key_here`
                    3. Get your key from: https://makersuite.google.com/app/apikey
                    4. Restart the Streamlit app
                    """)
                    st.stop()
                else:
                    # Generate features sheet using service
                    features_text = generate_features_sheet(
                        st.session_state.processed_images,
                        addr_display,
                        price_display,
                        beds_display,
                        property_type,
                        additional_details
                    )

                    # Store in session state
                    st.session_state.features_sheet = features_text

                    st.success("✅ Features sheet generated successfully!")
                    st.rerun()

            except Exception as e:
                st.error(f"An error occurred: {e}")

# Download RESO Data Button Handler
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
        property_type = st.session_state.get('property_type_input', 'Single Family Home')
        price = st.session_state.get('price_input', '')
        beds_baths = st.session_state.get('bed_bath_input', '')
        sqft = st.session_state.get('sqft_input', '')
        additional_details = st.session_state.get('additional_details_input', '').strip()

        with st.spinner("Generating RESO-compliant JSON data..."):
            try:
                # Generate RESO data using service
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
                    st.session_state.listing_text,
                    property_type
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

# Render result cards for generated content
render_result_cards()

# Cleanup temp files on session end
if st.session_state.get('cleanup_registered') is None:
    st.session_state.cleanup_registered = True
    import atexit
    atexit.register(st.session_state.file_manager.cleanup)
