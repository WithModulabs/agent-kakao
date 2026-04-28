"""Test Convert graph nodes."""

from __future__ import annotations

import base64
import io

from PIL import Image

from casts.convert.modules.nodes import ImageValidateNode


def _sample_png_b64() -> str:
    image = Image.new("RGBA", (16, 16), (255, 255, 255, 255))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")


def test_image_validate_node_accepts_valid_png() -> None:
    node = ImageValidateNode()
    result = node.execute({"image_data": _sample_png_b64(), "image_format": "png"})

    assert result == {"image_valid": True, "validation_error": None}


def test_image_validate_node_rejects_unsupported_format() -> None:
    node = ImageValidateNode()
    result = node.execute({"image_data": _sample_png_b64(), "image_format": "gif"})

    assert result["image_valid"] is False
    assert "Unsupported format" in result["validation_error"]
