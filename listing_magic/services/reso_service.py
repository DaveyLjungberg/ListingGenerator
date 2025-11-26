"""
RESO Service

Handles generation of RESO-compliant MLS data including listing IDs
and complete property data structures.
"""

import os
import json
import hashlib
from datetime import datetime
from google import genai

# Import from our utils
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.address_parser import parse_street_address


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


def generate_reso_data(images, addr, city, state, zip_code, price, beds_baths, sqft, additional_details, listing_description, property_type):
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

    IMPORTANT - Property Type: The user selected property type: {property_type}
    Use this for the PropertySubType field in the RESO JSON. Map it appropriately:
    - "Single Family Home" → "Single Family Residence"
    - "Condo/Townhouse" → "Condominium" or "Townhouse" (analyze photos to determine)
    - "Multi-Family (2-4 units)" → "Multi-Family"
    - "Apartment" → "Apartment"
    - "Land/Lot" → "Lots and Land"
    - "Commercial" → "Commercial"
    - "Other" → Analyze photos and infer appropriate subtype

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
      "PropertySubType": Use the mapping from user-selected property type "{property_type}" as instructed above,
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
