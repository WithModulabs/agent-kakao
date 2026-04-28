"""Test the Convert graph."""

from __future__ import annotations

import base64
import io
from types import SimpleNamespace

import httpx
from openai import PermissionDeniedError
from PIL import Image

from casts.convert.graph import convert_graph


def _sample_png_b64(size: tuple[int, int] = (32, 32)) -> str:
    image = Image.new("RGBA", size, (255, 220, 160, 255))
    output = io.BytesIO()
    image.save(output, format="PNG")
    return base64.b64encode(output.getvalue()).decode("utf-8")


class _FakeImages:
    def __init__(self, b64_json: str):
        self._b64_json = b64_json
        self.calls = []

    def edit(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(data=[SimpleNamespace(b64_json=self._b64_json)])


class _FakeOpenAI:
    def __init__(self, *args, **kwargs):
        self.images = _FakeImages(_sample_png_b64((64, 64)))


def test_convert_graph_returns_resized_png(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("casts.convert.modules.nodes.openai.OpenAI", _FakeOpenAI)

    graph = convert_graph()
    result = graph.invoke({"image_data": _sample_png_b64(), "image_format": "png"})

    assert result["validation_error"] is None
    assert result["result"] is not None

    image = Image.open(io.BytesIO(base64.b64decode(result["result"])))
    assert image.size == (360, 360)
    assert image.format == "PNG"


class _FallbackImages(_FakeImages):
    def edit(self, **kwargs):
        self.calls.append(kwargs)
        if kwargs["model"] == "gpt-image-2":
            response = httpx.Response(
                status_code=403,
                request=httpx.Request("POST", "https://api.openai.com/v1/images/edits"),
            )
            raise PermissionDeniedError(
                "organization verification required",
                response=response,
                body=None,
            )
        return SimpleNamespace(data=[SimpleNamespace(b64_json=self._b64_json)])


class _FallbackOpenAI:
    instance: "_FallbackOpenAI | None" = None

    def __init__(self, *args, **kwargs):
        self.images = _FallbackImages(_sample_png_b64((64, 64)))
        _FallbackOpenAI.instance = self


def test_convert_graph_falls_back_when_gpt_image_2_is_denied(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr("casts.convert.modules.nodes.openai.OpenAI", _FallbackOpenAI)

    graph = convert_graph()
    result = graph.invoke({"image_data": _sample_png_b64(), "image_format": "png"})

    assert result["result"] is not None
    calls = _FallbackOpenAI.instance.images.calls
    assert [call["model"] for call in calls] == ["gpt-image-2", "dall-e-2"]
    assert "background" not in calls[0]
    assert calls[1]["response_format"] == "b64_json"
    assert calls[1]["image"].name == "input.png"
    assert "4x4 grid" in calls[0]["prompt"]
    assert "사랑해" in calls[0]["prompt"]
