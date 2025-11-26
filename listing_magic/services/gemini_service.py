"""
Gemini Service

Handles all AI content generation using Google Gemini API including
listing descriptions, video scripts, and features sheets.
"""

import os
import json
import re
from google import genai


def generate_listing_content(images, addr_display, price_display, beds_display, property_type, additional_details, word_count):
    """
    Generate listing description and video script using Gemini

    Args:
        images: List of PIL Image objects
        addr_display: Formatted address string
        price_display: Formatted price string
        beds_display: Formatted beds/baths string
        property_type: Type of property (Single Family Home, Condo, etc.)
        additional_details: Additional property details to highlight
        word_count: Target word count for listing description

    Returns:
        tuple: (listing_description, video_script)
    """

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")

    client = genai.Client(api_key=api_key)

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

    # PERFORMANCE FIX: Limit to 3 images for fastest response
    # Testing with minimal images to debug slow generation
    limited_images = images[:3]
    print(f"Sending {len(limited_images)} images to API...")
    contents = [prompt] + limited_images

    # Call Gemini API
    response = client.models.generate_content(
        model='gemini-3-pro-preview',
        contents=contents
    )

    # Parse JSON and clean up response
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

    return listing_desc, video_script


def generate_features_sheet(images, addr_display, price_display, beds_display, property_type, additional_details):
    """
    Generate detailed property features sheet using Gemini

    Args:
        images: List of PIL Image objects
        addr_display: Formatted address string
        price_display: Formatted price string
        beds_display: Formatted beds/baths string
        property_type: Type of property (Single Family Home, Condo, etc.)
        additional_details: Additional property details to highlight

    Returns:
        str: Formatted features sheet text
    """

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment")

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

    # PERFORMANCE FIX: Limit to 3 images for fastest response
    # Testing with minimal images to debug slow generation
    limited_images = images[:3]
    print(f"Sending {len(limited_images)} images to API...")
    contents = [prompt] + limited_images

    # Call Gemini API
    response = client.models.generate_content(
        model='gemini-3-pro-preview',
        contents=contents
    )

    # Get and normalize the response
    features_text = response.text.strip()

    # Normalize spacing
    features_text = re.sub(r'\n\n+', '\n\n', features_text)

    return features_text
