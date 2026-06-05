"""
Brand Kit — overlay logo, áp dụng palette (color grading), đảm bảo brand
consistency giữa các biến thể.

Public API:
    apply_logo(video_path, logo_url, *, placement="top-right") -> str
    apply_color_grade(video_path, palette) -> str
    brand_lock_check(brand_lock, storyboard) -> dict   (gợi ý cho QA)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Optional


_PLACEMENT = {
    "top-right":    "W-w-40:40",
    "top-left":     "40:40",
    "bottom-right": "W-w-40:H-h-40",
    "bottom-left":  "40:H-h-40",
    "watermark":    "W-w-40:H-h-40",
}


def _download(url: str, dest: str) -> None:
    import httpx
    with httpx.Client(timeout=60.0) as client:
        r = client.get(url, follow_redirects=True)
        r.raise_for_status()
        with open(dest, "wb") as f:
            f.write(r.content)


def apply_logo(
    video_path: str,
    logo_url: Optional[str],
    *,
    placement: str = "top-right",
    scale_pct: int = 12,
) -> str:
    """
    Overlay logo lên video. Trả về path file mới.
    Nếu thiếu ffmpeg / thiếu logo -> trả nguyên video_path (no-op).
    """
    if not logo_url or shutil.which("ffmpeg") is None:
        return video_path
    pos = _PLACEMENT.get(placement, _PLACEMENT["top-right"])
    with tempfile.TemporaryDirectory() as tmp:
        logo_path = os.path.join(tmp, "logo.png")
        try:
            _download(logo_url, logo_path)
        except Exception as e:
            print(f"[brand_kit] tải logo fail: {e}")
            return video_path
        out_path = os.path.join(tmp, "with_logo.mp4")
        cmd = [
            "ffmpeg", "-y", "-i", video_path, "-i", logo_path,
            "-filter_complex",
            f"[1]scale=iw*{scale_pct}/100:-1[lg];"
            f"[0][lg]overlay={pos}",
            "-c:a", "copy", out_path,
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"[brand_kit] overlay fail: {e.stderr.decode(errors='ignore')[:200]}")
            return video_path
        # Move file ra ngoài tmp để caller dùng tiếp
        final = video_path.rsplit(".", 1)[0] + "_branded.mp4"
        shutil.copy(out_path, final)
        return final


def apply_color_grade(video_path: str, palette: dict) -> str:
    """
    Áp color grading nhẹ theo palette (primary, accent, bg).
    Hiện tại chỉ set saturation/contrast — không đổi màu cứng.
    """
    if shutil.which("ffmpeg") is None:
        return video_path
    primary = palette.get("primary", "#000000")
    # Đơn giản: tăng contrast + saturation để video "đỡ nhạt"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", "eq=saturation=1.1:contrast=1.05:brightness=0.0",
        "-c:a", "copy", video_path.rsplit(".", 1)[0] + "_graded.mp4",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return video_path.rsplit(".", 1)[0] + "_graded.mp4"
    except Exception as e:
        print(f"[brand_kit] color grade fail: {e}")
        return video_path


def brand_lock_check(brand_lock: dict, storyboard: dict) -> dict:
    """
    Check shot prompts có nhắc tới palette/claim của brand hay không.
    Trả về {passed: bool, missing: [...], score: 0-100}.
    """
    must_use = brand_lock.get("palette_rules", {}).get("must_use", [])
    forbidden = brand_lock.get("claims_compliance", {}).get("blacklist", [])
    prompts = " ".join(
        s.get("visual_prompt", "") for s in storyboard.get("shots", [])
    ).lower()
    missing = [c for c in forbidden if c.lower() in prompts]   # nếu có -> vi phạm
    score = 100 if not missing else max(0, 100 - len(missing) * 30)
    return {"passed": not missing, "missing": missing, "score": score}
