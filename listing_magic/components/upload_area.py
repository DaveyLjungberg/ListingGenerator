"""
Upload Area Component

Renders the photo upload area with embedded thumbnail preview.
"""

import streamlit as st
from PIL import Image, ImageOps

# Import from our utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.image_processor import image_to_base64


def render_upload_area():
    """
    Render the file upload area with embedded image thumbnails

    Returns:
        list: List of uploaded files or None if no files uploaded

    Side effects:
        - Updates st.session_state.processed_images with EXIF-corrected images
        - Updates st.session_state.cached_image_html with rendered thumbnail HTML
    """

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
                # Load images with EXIF correction AND resize for API efficiency
                processed = []
                for file in uploaded_files:
                    img = Image.open(file)
                    img = ImageOps.exif_transpose(img)

                    # PERFORMANCE FIX: Resize large images to max 512px width
                    # Smaller images = faster API upload and processing
                    max_width = 512
                    if img.width > max_width:
                        ratio = max_width / img.width
                        new_height = int(img.height * ratio)
                        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)

                    processed.append(img)

                st.session_state.processed_images = processed

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

    return uploaded_files
