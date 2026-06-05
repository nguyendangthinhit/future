"""
Edit / Concat — ghép các shot thành video hoàn chỉnh, thêm transition,
xuất 9:16 + 1:1.

Hiện tại ở mức skeleton: nếu có ffmpeg và có file shot thật thì concat;
nếu chưa có clip thật (mock mode) -> trả URL placeholder để caller
biết đã qua bước edit.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Optional
from urllib.parse import urlparse


def concat_clips(clip_paths: list[str], *, transitions: list[str] = None) -> str:
    """
    Ghép các clip thành 1 video dọc (9:16).
    Trả về đường dẫn file output.
    Nếu không có ffmpeg hoặc clip rỗng -> trả "".
    """
    if not clip_paths or shutil.which("ffmpeg") is None:
        return ""
    # Lọc file tồn tại
    with tempfile.TemporaryDirectory() as tmp:
        valid = []
        for index, clip in enumerate(clip_paths, start=1):
            materialized = _materialize_clip(clip, tmp, index)
            if materialized:
                valid.append(materialized)
        if not valid:
            return ""

        list_file = os.path.join(tmp, "list.txt")
        with open(list_file, "w", encoding="utf-8") as f:
            for p in valid:
                f.write(f"file '{p.replace(chr(92), '/')}'\n")
        out = os.path.join(tmp, "concat.mp4")
        cmd = [
            "ffmpeg", "-y", "-f", "concat", "-safe", "0",
            "-i", list_file, "-c", "copy", out,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[edit] concat fail: {e.stderr.decode(errors='ignore')[:200]}")
            return ""
        final = os.path.join(tempfile.gettempdir(), "edited_concat.mp4")
        shutil.copy(out, final)
        return final


def export_aspect(
    video_path: str,
    aspect: str = "9:16",
    *,
    output_path: Optional[str] = None,
) -> str:
    """
    Scale + crop video sang aspect ratio khác (9:16 hoặc 1:1).
    """
    if not video_path or not os.path.exists(video_path) or shutil.which("ffmpeg") is None:
        return video_path
    w, h = ("1080", "1920") if aspect == "9:16" else ("1080", "1080")
    if output_path is None:
        output_path = video_path.rsplit(".", 1)[0] + f"_{aspect.replace(':', 'x')}.mp4"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h}",
        "-c:a", "copy", output_path,
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return output_path
    except Exception as e:
        print(f"[edit] export_aspect fail: {e}")
        return video_path


def _materialize_clip(clip: str, tmp_dir: str, index: int) -> str:
    if not clip:
        return ""
    if os.path.exists(clip):
        return clip

    parsed = urlparse(clip)
    if parsed.scheme not in ("http", "https"):
        return ""

    suffix = os.path.splitext(parsed.path)[1] or ".mp4"
    dest = os.path.join(tmp_dir, f"clip_{index}{suffix}")
    try:
        import httpx

        with httpx.Client(timeout=60.0, follow_redirects=True) as client:
            response = client.get(clip)
            response.raise_for_status()
            with open(dest, "wb") as file:
                file.write(response.content)
        return dest
    except Exception as e:
        print(f"[edit] download clip fail: {e}")
        return ""
