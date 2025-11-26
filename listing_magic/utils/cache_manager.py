"""
Cache Manager Utility

Manages caching and change detection for smart content regeneration.
"""

import json
import hashlib
import streamlit as st


def get_inputs_hash(uploaded_files):
    """
    Generate hash of all current inputs

    Args:
        uploaded_files: List of uploaded file objects from Streamlit

    Returns:
        str: MD5 hash of all inputs
    """
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
    """
    Check if inputs changed since last generation

    Args:
        uploaded_files: List of uploaded file objects from Streamlit

    Returns:
        bool: True if inputs have changed, False otherwise
    """
    current_hash = get_inputs_hash(uploaded_files)
    last_hash = st.session_state.get('last_generated_hash', '')
    return current_hash != last_hash
