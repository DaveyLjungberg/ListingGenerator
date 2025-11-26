"""
Image Processor Utility

Handles image processing tasks including resizing, padding, and base64 encoding.
"""

import base64
from io import BytesIO
from PIL import Image


def image_to_base64(img, max_width=150):
    """
    Convert PIL image to base64 string for HTML embedding

    Args:
        img: PIL Image object
        max_width: Maximum width for thumbnail (default 150px)

    Returns:
        str: Base64-encoded image data URI
    """
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


def resize_with_padding(image, target_size=(1920, 1080)):
    """
    Resize image with letterboxing (padding) to fit target size

    Args:
        image: PIL Image object
        target_size: Tuple of (width, height) for output size

    Returns:
        PIL Image: Resized image with black padding
    """
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
