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
    validate_image,
)

_OPENAI_MODEL = "gpt-5.5-image"


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
    """Generate a Kakao emoticon using GPT-5.5 image (OpenAI Images Edit API).

    Takes the original image and transforms it into a cartoon/emoticon style
    in a single API call. Writes `styled_image` (raw bytes) to state.
    """

    def __init__(self):
        super().__init__()
        self._client: openai.OpenAI | None = None

    def _get_client(self) -> openai.OpenAI:
        if self._client is None:
            self._client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        return self._client

    def execute(self, state):
        image_bytes = decode_base64_image(state["image_data"])
        image_format = state["image_format"].lower()
        filename = f"input.{image_format}"

        response = self._get_client().images.edit(
            model=_OPENAI_MODEL,
            image=bytes_to_file(image_bytes, filename),
            prompt=EMOTICON_GENERATE_PROMPT,
            n=1,
            size="1024x1024",
            response_format="b64_json",
        )

        styled_b64: str = response.data[0].b64_json
        styled_image: bytes = base64.b64decode(styled_b64)
        return {"styled_image": styled_image}


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
