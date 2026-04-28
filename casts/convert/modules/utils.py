"""[Optional] Helper utilities used across the Convert graph.

Guidelines:
    - Extract reusable data processing or formatting logic.
    - Keep node implementations concise by delegating to helpers.
"""

import base64
import io
from typing import Optional

from PIL import Image

SUPPORTED_FORMATS = {"png", "jpeg", "jpg", "webp"}
MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB
EMOTICON_SIZE = (360, 360)


def decode_base64_image(base64_data: str) -> bytes:
    """Decode a base64 string to raw image bytes."""
    return base64.b64decode(base64_data)


def encode_image_to_base64(image_bytes: bytes) -> str:
    """Encode raw image bytes to a base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


def validate_image(
    image_bytes: bytes, image_format: str
) -> tuple[bool, Optional[str]]:
    """Validate image format, size, and integrity.

    Args:
        image_bytes: Raw image bytes.
        image_format: Expected format string (e.g. 'png', 'jpeg').

    Returns:
        Tuple of (is_valid, error_message). error_message is None when valid.
    """
    if image_format.lower() not in SUPPORTED_FORMATS:
        return False, f"Unsupported format '{image_format}'. Allowed: {SUPPORTED_FORMATS}"

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        size_mb = len(image_bytes) / (1024 * 1024)
        return False, f"Image size {size_mb:.1f}MB exceeds the 10MB limit."

    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception as exc:
        return False, f"Invalid or corrupted image: {exc}"

    return True, None


def resize_to_emoticon(image_bytes: bytes) -> bytes:
    """Resize and convert image to emoticon spec (360x360 PNG).

    Args:
        image_bytes: Raw image bytes in any supported format.

    Returns:
        PNG-encoded bytes at EMOTICON_SIZE resolution.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img = img.resize(EMOTICON_SIZE, Image.LANCZOS)
    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()


def to_square_rgba_png(image_bytes: bytes) -> bytes:
    """Convert image to square RGBA PNG required by dall-e-2 images.edit.

    Pads to square with transparent background, then converts to RGBA PNG.

    Args:
        image_bytes: Raw image bytes in any supported format.

    Returns:
        Square RGBA PNG bytes.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    w, h = img.size
    side = max(w, h)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(img, ((side - w) // 2, (side - h) // 2))
    output = io.BytesIO()
    square.save(output, format="PNG")
    return output.getvalue()


def bytes_to_file(image_bytes: bytes, filename: str) -> io.BytesIO:
    """Wrap raw bytes in a named BytesIO for OpenAI API calls.

    Args:
        image_bytes: Raw image bytes.
        filename: Filename with extension (e.g. 'input.png').

    Returns:
        BytesIO with .name attribute set.
    """
    buf = io.BytesIO(image_bytes)
    buf.name = filename
    return buf
