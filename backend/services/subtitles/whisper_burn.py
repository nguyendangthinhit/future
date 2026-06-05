"""
Subtitles service — Whisper transcribe + FFmpeg burn-in.

Có 2 chế độ:
- Lightweight: dùng faster-whisper local nếu có sẵn; fallback về heuristic
  dựa trên word_count / duration_s (chia đều).
- Burn-in: dùng FFmpeg `subtitles=` filter để render sub cứng lên video.

Khi không có FFmpeg hoặc faster-whisper, các hàm trả về dict rỗng
{"srt": "", "burned_video_url": video_url_in} — caller tự quyết định có
cần retry hay dùng raw video.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Transcribe
# ---------------------------------------------------------------------------
def transcribe(audio_url: str, *, language: Optional[str] = None) -> dict:
    """
    Transcribe audio -> word-level JSON.

    Trả về:
        {
            "language": "vi",
            "words": [{"word": "...", "t_start": 0.0, "t_end": 0.5}, ...],
            "duration_s": 12.3,
        }
    """
    # Thử faster-whisper
    try:
        from faster_whisper import WhisperModel  # type: ignore

        # Tải audio về tmp
        with tempfile.TemporaryDirectory() as tmp:
            audio_path = os.path.join(tmp, "audio.mp3")
            _download(audio_url, audio_path)
            model = WhisperModel("base", device="cpu", compute_type="int8")
            segments, info = model.transcribe(
                audio_path, language=language, word_timestamps=True
            )
            words: list[dict] = []
            for seg in segments:
                for w in (seg.words or []):
                    words.append({
                        "word": w.word.strip(),
                        "t_start": float(w.start or 0.0),
                        "t_end": float(w.end or 0.0),
                    })
            return {
                "language": info.language,
                "words": words,
                "duration_s": float(info.duration or 0.0),
            }
    except Exception as e:
        print(f"[subtitles] faster-whisper không khả dụng: {e}. Fallback heuristic.")
        return _heuristic_transcribe(audio_url)


def _heuristic_transcribe(audio_url: str) -> dict:
    """
    Fallback: dùng VO text từ caller hoặc chia đều theo duration.
    Trả về structure rỗng — caller tự build srt từ VO text.
    """
    return {"language": "unknown", "words": [], "duration_s": 0.0}


# ---------------------------------------------------------------------------
# SRT builder
# ---------------------------------------------------------------------------
def build_srt(words: list[dict], max_words: int = 7) -> str:
    """
    Gom word-level thành SRT: 2 dòng / chunk, mỗi dòng tối đa max_words từ.
    """
    if not words:
        return ""

    lines: list[str] = []
    chunk: list[dict] = []
    for w in words:
        chunk.append(w)
        if sum(len(c["word"].split()) for c in chunk) >= max_words:
            lines.append(chunk)
            chunk = []
    if chunk:
        lines.append(chunk)

    out: list[str] = []
    for i, ch in enumerate(lines, start=1):
        t0 = ch[0]["t_start"]
        t1 = ch[-1]["t_end"]
        text = " ".join(c["word"] for c in ch)
        out.append(
            f"{i}\n"
            f"{_ts(t0)} --> {_ts(t1)}\n"
            f"{text}\n"
        )
    return "\n".join(out)


def build_srt_from_vo(vo_text: str, total_s: float) -> str:
    """
    Chia đều VO text thành SRT khi không có Whisper.
    Mỗi 7 từ = 1 dòng sub (giả định tốc độ đọc đều).
    """
    words = re.findall(r"\S+", vo_text)
    if not words or total_s <= 0:
        return ""
    per_line = 7
    per_word_s = total_s / max(1, len(words))
    out: list[str] = []
    idx = 1
    for i in range(0, len(words), per_line):
        chunk = words[i:i + per_line]
        t0 = i * per_word_s
        t1 = (i + len(chunk)) * per_word_s
        out.append(
            f"{idx}\n{_ts(t0)} --> {_ts(t1)}\n{' '.join(chunk)}\n"
        )
        idx += 1
    return "\n".join(out)


def _ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")


# ---------------------------------------------------------------------------
# Burn-in
# ---------------------------------------------------------------------------
def burn_subtitles(
    video_path: str,
    srt_text: str,
    *,
    font: str = "Arial",
    font_size: int = 18,
    outline_color: str = "&H000000",
    primary_color: str = "&HFFFFFF",
    margin_v: int = 80,
    output_path: Optional[str] = None,
) -> str:
    """
    Burn SRT vào video bằng FFmpeg `subtitles=` filter.
    Trả về đường dẫn file output.
    """
    if not srt_text.strip():
        return video_path
    if shutil.which("ffmpeg") is None:
        print("[subtitles] ffmpeg không có sẵn — bỏ qua burn-in.")
        return video_path

    if output_path is None:
        tmp = tempfile.mkdtemp()
        output_path = os.path.join(tmp, "with_subs.mp4")
    srt_path = os.path.join(os.path.dirname(output_path) or ".", "_subs.srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_text)

    # Lưu ý: filter subtitles= cần escape đường dẫn
    srt_filter = srt_path.replace("\\", "/").replace(":", "\\:")

    style = (
        f"FontName={font},FontSize={font_size},"
        f"PrimaryColour={primary_color},OutlineColour={outline_color},"
        f"Outline=2,Alignment=2,MarginV={margin_v}"
    )

    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"subtitles='{srt_filter}':force_style='{style}'",
        "-c:a", "copy", output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except subprocess.CalledProcessError as e:
        print(f"[subtitles] ffmpeg burn-in fail: {e.stderr.decode(errors='ignore')[:200]}")
        return video_path


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _download(url: str, dest: str) -> None:
    import httpx
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, follow_redirects=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)
