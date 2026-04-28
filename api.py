"""FastAPI application for the Kakao Emoticon agent.

Endpoints:
    POST /convert  — Upload a photo, receive a Kakao-style emoticon image.
    GET  /health   — Liveness check.
"""

import base64

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import Response

from casts.convert.graph import convert_graph

app = FastAPI(
    title="Kakao Emoticon API",
    description="Upload a photo to receive a Kakao-style emoticon image.",
    version="0.1.0",
)

_COMPILED_GRAPH = convert_graph()

_MIME_TO_FORMAT: dict[str, str] = {
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/jpg": "jpeg",
    "image/webp": "webp",
}


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    """Liveness check."""
    return {"status": "ok"}


@app.post(
    "/convert",
    response_class=Response,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "360x360 PNG emoticon image.",
        },
        400: {"description": "Invalid or unsupported image."},
        422: {"description": "Validation error."},
    },
    tags=["convert"],
)
async def convert(file: UploadFile = File(..., description="Photo to convert (PNG/JPEG/WEBP, max 10 MB)")) -> Response:
    """Convert an uploaded photo into a Kakao emoticon-style PNG.

    - **file**: Image file (PNG, JPEG, or WEBP). Maximum size: 10 MB.

    Returns a 360×360 PNG image as binary content.
    """
    content_type = (file.content_type or "").lower()
    image_format = _MIME_TO_FORMAT.get(content_type)

    if image_format is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{content_type}'. Allowed: image/png, image/jpeg, image/webp.",
        )

    raw_bytes = await file.read()
    image_data = base64.b64encode(raw_bytes).decode("utf-8")

    result = await _COMPILED_GRAPH.ainvoke(
        {"image_data": image_data, "image_format": image_format}
    )

    if result.get("validation_error"):
        raise HTTPException(status_code=400, detail=result["validation_error"])

    emoticon_bytes = base64.b64decode(result["result"])
    return Response(content=emoticon_bytes, media_type="image/png")
