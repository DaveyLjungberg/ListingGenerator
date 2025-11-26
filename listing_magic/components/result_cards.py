"""
Result Cards Component

Renders the generated content in premium styled cards.
"""

import os
import streamlit as st


def format_content_to_html(content, placeholder_text):
    """
    Convert markdown paragraphs to HTML with proper spacing

    Args:
        content: Text content with markdown-style double newlines
        placeholder_text: Text to check against for empty state

    Returns:
        str: HTML formatted paragraphs
    """
    if content and content != placeholder_text:
        paragraphs = content.split('\n\n')
        return ''.join([f'<p>{p.strip()}</p>' for p in paragraphs if p.strip()])
    return f'<p>{content}</p>'


def render_result_cards():
    """
    Render all result cards for generated content

    Displays:
        - Features sheet (full width if available)
        - Listing description (left column)
        - Video (right column, if available)
        - Video script (right column)
    """

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
        video_path = st.session_state.generated_video_path
        if video_path and os.path.exists(video_path):
            st.video(video_path)
        elif video_path:
            # Path exists in session but file is missing
            st.warning("⚠️ Video file not found. Please regenerate the video.")

        # Video Script Card
        script_content = st.session_state.video_script if st.session_state.video_script else "Generate a script to see it here."
        html_content = format_content_to_html(script_content, "Generate a script to see it here.")

        st.markdown(f"""
        <div class="result-card">
            <div class="card-header">Video Script</div>
            <div>{html_content}</div>
        </div>
        """, unsafe_allow_html=True)
