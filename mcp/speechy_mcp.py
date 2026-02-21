"""
speechy_mcp.py - MCP server for Speechy TTS endpoint
Gives Claude a voice through your PipeWire/Piper setup.
No Wyoming. No ceremony. Just speak.
"""

import json
import os

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

SPEECHY_BASE_URL = os.environ.get("SPEECHY_URL", "http://localhost:5050")

mcp = FastMCP("speechy_mcp")

_client = httpx.AsyncClient(base_url=SPEECHY_BASE_URL, timeout=30.0)


async def _get(path: str) -> dict:
    r = await _client.get(path)
    r.raise_for_status()
    return r.json()


async def _speak(text: str, voice: Optional[str] = None) -> dict:
    payload = {"text": text}
    if voice:
        payload["voice"] = voice
    r = await _client.post("/speak", json=payload)
    r.raise_for_status()
    return r.json()


class SpeakInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    text: str = Field(
        ...,
        description=(
            "The text to speak aloud. Should be natural, conversational — not markdown. "
            "Keep it to a sentence or two; this is speech, not an essay."
        ),
        min_length=1,
        max_length=2000,
    )
    voice: Optional[str] = Field(
        default=None,
        description=(
            "Piper voice name (e.g. 'en_US-amy-medium', 'en_US-joe-medium'). "
            "If omitted, uses Speechy's configured default. "
            "Pick based on what the moment calls for — warm, clear, dry, expressive."
        ),
    )


class EmptyInput(BaseModel):
    model_config = ConfigDict(extra="forbid")


@mcp.tool(
    name="speechy_speak",
    annotations={
        "title": "Speak aloud via Speechy",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False,
    },
)
async def speechy_speak(params: SpeakInput) -> str:
    """Send text to the Speechy TTS endpoint and play it through the host speakers.

    Text goes in, audio comes out of the user's PipeWire setup via piper-tts.
    Choose voice based on context — don't always default to the same one.
    Silence is also an option; not everything needs to be said aloud.

    Args:
        params (SpeakInput): Input containing:
            - text (str): What to say. Natural language, not markdown.
            - voice (Optional[str]): Piper voice name. None uses Speechy default.

    Returns:
        str: JSON with status, text spoken, and voice used.
    """
    try:
        result = await _speak(params.text, params.voice)
        return json.dumps(result, indent=2)
    except httpx.HTTPStatusError as e:
        return json.dumps({"error": f"Speechy returned {e.response.status_code}", "detail": e.response.text})
    except httpx.ConnectError:
        return json.dumps({"error": f"Cannot reach Speechy at {SPEECHY_BASE_URL}. Is the container running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {type(e).__name__}: {e}"})


@mcp.tool(
    name="speechy_list_voices",
    annotations={
        "title": "List available Speechy voices",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def speechy_list_voices(params: EmptyInput) -> str:
    """List all voice models currently available in Speechy.

    Use this to discover what's in the voices/ directory before speaking,
    especially if you want to pick something that fits the moment.

    Returns:
        str: JSON list of available voice names.
    """
    try:
        result = await _get("/voices")
        return json.dumps(result, indent=2)
    except httpx.ConnectError:
        return json.dumps({"error": f"Cannot reach Speechy at {SPEECHY_BASE_URL}. Is the container running?"})
    except Exception as e:
        return json.dumps({"error": f"Unexpected error: {type(e).__name__}: {e}"})


@mcp.tool(
    name="speechy_health",
    annotations={
        "title": "Check Speechy health",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def speechy_health(params: EmptyInput) -> str:
    """Check if Speechy is up and responding.

    Returns:
        str: JSON health status from Speechy.
    """
    try:
        result = await _get("/health")
        return json.dumps(result, indent=2)
    except httpx.ConnectError:
        return json.dumps({"status": "unreachable", "error": f"Cannot connect to Speechy at {SPEECHY_BASE_URL}"})
    except Exception as e:
        return json.dumps({"error": f"{type(e).__name__}: {e}"})


if __name__ == "__main__":
    mcp.run()
