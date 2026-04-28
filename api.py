"""FastAPI application for the Kakao Emoticon agent.

Endpoints:
    POST /convert  — Upload a photo, receive a Kakao-style emoticon image.
    GET  /health   — Liveness check.
"""

import base64
import logging
import traceback

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, Response

load_dotenv()

from casts.convert.graph import convert_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s\n%s", exc, traceback.format_exc())
    return JSONResponse(status_code=500, content={"detail": str(exc), "type": type(exc).__name__})


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
    },
    tags=["convert"],
)
async def convert(file: UploadFile = File(..., description="Photo to convert (PNG/JPEG/WEBP, max 10 MB)")) -> Response:
    """Convert an uploaded photo into a Kakao emoticon-style PNG."""
    content_type = (file.content_type or "").lower()
    image_format = _MIME_TO_FORMAT.get(content_type)

    if image_format is None:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported content type '{content_type}'. Allowed: image/png, image/jpeg, image/webp.",
        )

    raw_bytes = await file.read()
    image_data = base64.b64encode(raw_bytes).decode("utf-8")

    logger.info("Invoking convert graph for %s (%d bytes)", image_format, len(raw_bytes))

    result = await _COMPILED_GRAPH.ainvoke(
        {"image_data": image_data, "image_format": image_format}
    )

    if result.get("validation_error"):
        raise HTTPException(status_code=400, detail=result["validation_error"])

    emoticon_bytes = base64.b64decode(result["result"])
    return Response(content=emoticon_bytes, media_type="image/png")

