"""[Optional] Conditional routing functions for Convert graphs.

Guidelines:
    - Each function accepts the current state and returns the next node key.
    - Use for branches that require multiple downstream paths.

Official document URL:
    - Conditions: https://docs.langchain.com/oss/python/langgraph/graph-api#conditional-edges
"""

from langgraph.graph import END


def validate_route(state) -> str:
    """Route based on image validation result.

    Returns:
        'EmoticonGenerateNode' if the image passed validation,
        END otherwise (validation_error is already set in state).
    """
    if state.get("image_valid"):
        return "EmoticonGenerateNode"
    return END
