"""[Required] State definition shared across Convert graphs.

Guidelines:
    - Create TypedDict classes for input, output, overall state, and any other state you need.
    - Use `MessagesState` from langgraph.graph or use `Annotated[list[AnyMessage], add_messages]` for messages to enable proper message merging.
    - When inheriting from MessagesState, do not override the messages field.

Official document URL:
    - State: https://docs.langchain.com/oss/python/langgraph/graph-api#state
"""

from typing import Optional

from typing_extensions import TypedDict


class InputState(TypedDict):
    """Input state container.

    Attributes:
        image_data: Base64-encoded input image string.
        image_format: Image format ('png', 'jpeg', 'webp').
    """

    image_data: str
    image_format: str


class OutputState(TypedDict):
    """Output state container.

    Attributes:
        result: Base64-encoded emoticon image (PNG, 360x360).
        validation_error: Error message when image validation fails, None otherwise.
    """

    result: Optional[str]
    validation_error: Optional[str]


class State(TypedDict):
    """Internal graph state container.

    Attributes:
        image_data: Base64-encoded input image string.
        image_format: Image format ('png', 'jpeg', 'webp').
        image_valid: Whether the uploaded image passed validation.
        validation_error: Validation failure reason, None if valid.
        styled_image: Raw bytes of the style-transferred image from GPT-5.5 image.
        result: Base64-encoded final emoticon image (PNG, 360x360).
    """

    image_data: str
    image_format: str
    image_valid: bool
    validation_error: Optional[str]
    styled_image: Optional[bytes]
    result: Optional[str]
