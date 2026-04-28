"""[Required] Node implementations for the Convert graph.

Guidelines:
    - Derive each node from :class:`BaseNode` or :class:`AsyncBaseNode`.
    - Implement :meth:`execute` to process state and return updates.
    - Choose your node signature based on what you need:
      * Simple: `def execute(self, state)` - Only needs state
      * With config: `def execute(self, state, config)` - Needs thread_id, tags
      * With runtime: `def execute(self, state, runtime)` - Needs store, stream
      * Full: `def execute(self, state, config, runtime)` - Needs everything
    - Use `self.log()` for debugging when `verbose=True`.

Official document URL:
    - Nodes: https://docs.langchain.com/oss/python/langgraph/graph-api#nodes
"""

import base64
import os

import openai

from casts.base_node import BaseNode
from casts.convert.modules.prompts import EMOTICON_GENERATE_PROMPT
from casts.convert.modules.utils import (
    bytes_to_file,
    decode_base64_image,
    encode_image_to_base64,
    resize_to_emoticon,
    to_square_rgba_png,
    validate_image,
)

_DEFAULT_OPENAI_MODEL = "gpt-image-2"
_DEFAULT_FALLBACK_MODEL = "dall-e-2"


class ImageValidateNode(BaseNode):
    """Validate the uploaded image (format, size, integrity).

    Writes `image_valid` and `validation_error` to state.
    """

    def __init__(self):
        super().__init__()

    def execute(self, state):
        image_bytes = decode_base64_image(state["image_data"])
        is_valid, error = validate_image(image_bytes, state["image_format"])
        return {
            "image_valid": is_valid,
            "validation_error": error,
        }


class EmoticonGenerateNode(BaseNode):
    """Generate a Kakao emoticon using the OpenAI Images API.

    Sends the original image with a style prompt via the image edit endpoint.
    Writes `styled_image` (raw bytes) to state.
    """

    def __init__(self):
        super().__init__()
        self._client: openai.OpenAI | None = None

    def _get_client(self) -> openai.OpenAI:
        if self._client is None:
            self._client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return self._client

    def _edit_with_model(self, model: str, image_bytes: bytes, image_format: str):
        if model == "dall-e-2":
            edit_image = to_square_rgba_png(image_bytes)
            image_file = bytes_to_file(edit_image, "input.png")
            return self._get_client().images.edit(
                model=model,
                image=image_file,
                prompt=EMOTICON_GENERATE_PROMPT,
                n=1,
                response_format="b64_json",
                size="1024x1024",
            )

        file_ext = "jpg" if image_format == "jpeg" else image_format
        image_file = bytes_to_file(image_bytes, f"input.{file_ext}")
        return self._get_client().images.edit(
            model=model,
            image=image_file,
            prompt=EMOTICON_GENERATE_PROMPT,
            output_format="png",
            size="1024x1024",
        )

    def _create_edit(self, image_bytes: bytes, image_format: str):
        model = os.getenv("OPENAI_IMAGE_MODEL", _DEFAULT_OPENAI_MODEL)
        fallback_model = os.getenv("OPENAI_IMAGE_FALLBACK_MODEL", _DEFAULT_FALLBACK_MODEL)

        try:
            return self._edit_with_model(model, image_bytes, image_format)
        except openai.PermissionDeniedError as exc:
            if fallback_model and fallback_model != model:
                self.log("Primary image model denied; retrying fallback", model=model)
                return self._edit_with_model(fallback_model, image_bytes, image_format)
            raise exc

    def execute(self, state):
        image_bytes = decode_base64_image(state["image_data"])
        image_format = state["image_format"].lower()
        response = self._create_edit(image_bytes, image_format)

        if response.data and response.data[0].b64_json:
            styled_image: bytes = base64.b64decode(response.data[0].b64_json)
            return {"styled_image": styled_image}

        raise RuntimeError(f"No image data in OpenAI Images response: {response}")


class ImageFormatNode(BaseNode):
    """Resize and encode the generated image to Kakao emoticon spec.

    Resizes to 360x360 PNG and base64-encodes the result into `result`.
    """

    def __init__(self):
        super().__init__()

    def execute(self, state):
        emoticon_bytes = resize_to_emoticon(state["styled_image"])
        result = encode_image_to_base64(emoticon_bytes)
        return {"result": result}
