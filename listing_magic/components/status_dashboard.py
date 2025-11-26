"""
Status Dashboard Component

Renders the generation status metrics showing what content has been generated.
"""

import streamlit as st

# Import from our utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cache_manager import inputs_changed


def render_status_dashboard(uploaded_files):
    """
    Render the status dashboard showing generation progress

    Args:
        uploaded_files: List of uploaded files (used to check if inputs changed)

    Displays:
        - Listing status (generated or not)
        - Features sheet status (generated or not)
        - Video status (generated or not)
        - Data freshness status (whether inputs have changed since last generation)
    """

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
