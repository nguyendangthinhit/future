"""Voice / TTS service.

Provider order:
1. ElevenLabs when ELEVENLABS_API_KEY is configured.
2. Legacy Ecomdy TTS when available.
3. Mock metadata so factory demos can keep running without quota.
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional


try:
    from services.tts_service import generate_tts, poll_tts_status
    _HAS_ECOMDY = True
except Exception:
    _HAS_ECOMDY = False


async def synthesize(
    text: str,
    *,
    voice_id: Optional[str] = None,
) -> dict:
    if not text or not text.strip():
        raise ValueError("text is empty")

    if os.getenv("ELEVENLABS_API_KEY"):
        return await _synthesize_elevenlabs(text, voice_id=voice_id)

    if _HAS_ECOMDY and os.getenv("ECOMDY_API_KEY"):
        return await _synthesize_ecomdy(text, voice_id=voice_id)

    return _mock_voice(text)


async def _synthesize_elevenlabs(text: str, *, voice_id: Optional[str]) -> dict:
    import httpx

    api_key = os.getenv("ELEVENLABS_API_KEY", "")
    selected_voice = voice_id or os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    output_format = os.getenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")

    url = (
        f"https://api.elevenlabs.io/v1/text-to-speech/{selected_voice}"
        f"?output_format={output_format}"
    )
    payload = {
        "text": text,
        "model_id": model_id,
        "voice_settings": {
            "stability": float(os.getenv("ELEVENLABS_STABILITY", "0.45")),
            "similarity_boost": float(os.getenv("ELEVENLABS_SIMILARITY_BOOST", "0.75")),
        },
    }
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, headers=headers, json=payload)
        if response.status_code >= 400:
            raise RuntimeError(f"ElevenLabs TTS HTTP {response.status_code}: {response.text[:300]}")

    output_path = _voice_output_path(text, selected_voice)
    with open(output_path, "wb") as file:
        file.write(response.content)

    return {
        "audio_url": output_path,
        "audio_path": output_path,
        "duration_s": _estimate_duration(text),
        "provider": "elevenlabs",
        "voice_id": selected_voice,
    }


async def _synthesize_ecomdy(text: str, *, voice_id: Optional[str]) -> dict:
    job_id = await generate_tts(text, voice_id=voice_id)
    if not job_id:
        raise RuntimeError("Ecomdy TTS did not return a job_id.")
    audio_url = await poll_tts_status(job_id)
    return {
        "audio_url": audio_url,
        "duration_s": _estimate_duration(text),
        "provider": "legacy-ecomdy",
        "voice_id": voice_id,
    }


def _mock_voice(text: str) -> dict:
    return {
        "audio_url": "",
        "duration_s": _estimate_duration(text),
        "provider": "mock",
        "voice_id": None,
    }


def _voice_output_path(text: str, voice_id: str) -> str:
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    output_dir = os.path.join(root, "outputs", "voice")
    os.makedirs(output_dir, exist_ok=True)
    digest = hashlib.sha1(f"{voice_id}:{text}".encode("utf-8")).hexdigest()[:16]
    return os.path.join(output_dir, f"vo_{digest}.mp3")


def _estimate_duration(text: str) -> float:
    word_count = len(text.split())
    return round(max(1.0, word_count / 2.5), 2)


def extract_voiceover_from_script(script: dict) -> str:
    parts = []
    for scene in script.get("scenes", []):
        line = scene.get("voiceover") or scene.get("dialogue")
        if line:
            parts.append(line.strip())
    if not parts:
        hook = script.get("hook") or script.get("hook_instruction")
        if hook:
            parts.append(hook)
    return " ".join(parts)
