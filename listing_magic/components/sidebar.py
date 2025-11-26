"""
Sidebar Component

Renders the property details input form in the sidebar.
"""

import streamlit as st


def render_sidebar():
    """
    Render the complete sidebar with all property input forms

    This component handles all user inputs for property details including
    location, property information, additional details, and listing length.
    """

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
