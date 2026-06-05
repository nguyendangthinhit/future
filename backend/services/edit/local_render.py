"""Local publish-ready video fallback.

This is not a Seedance replacement. It creates deterministic MP4 preview/final
assets when no real video provider or FFmpeg binary is available, so the demo
still produces reviewable 9:16 and 1:1 videos with hard subtitles.
"""

from __future__ import annotations

import base64
import hashlib
import os
import re
import textwrap
from io import BytesIO
from typing import Any

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from models.brief import Brief


def render_publish_ready_video(
    brief: Brief,
    variant: dict,
    script: dict,
    pack: dict,
    *,
    output_root: str,
) -> dict[str, str]:
    """Render final MP4 files for all requested aspects."""

    variant_id = str(variant.get("id") or variant.get("variant_id") or "A")
    safe_brand = _slug(brief.brand.name or "brand")
    base_dir = os.path.join(output_root, "videos", safe_brand, variant_id)
    os.makedirs(base_dir, exist_ok=True)

    final_urls: dict[str, str] = {}
    for aspect in brief.constraints.aspect:
        size = (1080, 1920) if aspect == "9:16" else (1080, 1080)
        output_path = os.path.join(base_dir, f"final_{aspect.replace(':', 'x')}.mp4")
        _render_one_aspect(brief, variant, script, pack, output_path=output_path, size=size)
        final_urls[aspect] = output_path.replace("\\", "/")

    cover_path = os.path.join(base_dir, "cover.jpg")
    _render_cover(brief, variant, script, pack, cover_path=cover_path)
    final_urls["cover"] = cover_path.replace("\\", "/")
    return final_urls


def _render_one_aspect(
    brief: Brief,
    variant: dict,
    script: dict,
    pack: dict,
    *,
    output_path: str,
    size: tuple[int, int],
) -> None:
    fps = 12
    duration_s = max(6, min(int(brief.constraints.lengthSec), 30))
    total_frames = duration_s * fps
    scenes = script.get("scenes") or []
    if not scenes:
        scenes = [{"voiceover": script.get("hook", brief.theme), "text_overlay": script.get("hook", brief.theme)}]

    reference = _load_reference_image(brief.moodboardUrls[0] if brief.moodboardUrls else "")
    palette = _palette(brief)
    font_big = _font(62)
    font_med = _font(42)
    font_small = _font(30)

    writer = imageio.get_writer(output_path, fps=fps, codec="libx264", quality=8, macro_block_size=1)
    try:
        for frame_index in range(total_frames):
            progress = frame_index / max(1, total_frames - 1)
            scene_index = min(len(scenes) - 1, int(progress * len(scenes)))
            scene = scenes[scene_index]
            local_progress = (progress * len(scenes)) % 1.0

            image = _background(size, palette, progress)
            draw = ImageDraw.Draw(image)

            _draw_brand_header(draw, brief, variant, size, font_small, palette)
            if reference is not None:
                _draw_reference(image, reference, size, local_progress)

            if frame_index < fps * 3:
                headline = str(script.get("hook") or brief.theme)
            elif scene_index >= len(scenes) - 1:
                headline = str(script.get("cta") or pack.get("caption") or "Follow for more")
            else:
                headline = str(scene.get("text_overlay") or scene.get("voiceover") or brief.theme)

            body = str(scene.get("voiceover") or scene.get("action") or "")
            _draw_center_text(draw, headline, body, size, font_big, font_med, palette)
            _draw_caption_bar(draw, script, frame_index / fps, duration_s, size, font_small)
            _draw_progress(draw, progress, size, palette)

            writer.append_data(np.asarray(image))
    finally:
        writer.close()


def _render_cover(brief: Brief, variant: dict, script: dict, pack: dict, *, cover_path: str) -> None:
    size = (1080, 1920)
    image = _background(size, _palette(brief), 0.25)
    draw = ImageDraw.Draw(image)
    font_big = _font(72)
    font_med = _font(40)
    _draw_center_text(
        draw,
        str(script.get("hook") or pack.get("title") or brief.theme),
        f"{brief.brand.name} / Variant {variant.get('id', '')}",
        size,
        font_big,
        font_med,
        _palette(brief),
    )
    image.save(cover_path, quality=92)


def _background(size: tuple[int, int], palette: dict[str, tuple[int, int, int]], progress: float) -> Image.Image:
    width, height = size
    primary = palette["primary"]
    accent = palette["accent"]
    bg = palette["bg"]
    image = Image.new("RGB", size, bg)
    pixels = image.load()
    for y in range(height):
        blend = y / max(1, height - 1)
        wave = (np.sin((blend + progress) * np.pi * 2) + 1) / 2
        color = tuple(
            int(bg[i] * (1 - blend) + primary[i] * blend * 0.75 + accent[i] * wave * 0.18)
            for i in range(3)
        )
        for x in range(width):
            pixels[x, y] = color
    return image


def _draw_brand_header(
    draw: ImageDraw.ImageDraw,
    brief: Brief,
    variant: dict,
    size: tuple[int, int],
    font: ImageFont.ImageFont,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    width, _ = size
    text = f"{brief.brand.name or 'Brand'}  /  Variant {variant.get('id', '')}"
    draw.rounded_rectangle((48, 48, width - 48, 122), radius=28, fill=(0, 0, 0, 105))
    draw.text((78, 70), text, font=font, fill=(255, 255, 255))


def _draw_reference(image: Image.Image, reference: Image.Image, size: tuple[int, int], progress: float) -> None:
    width, height = size
    ref = reference.copy().convert("RGB")
    target_w = int(width * 0.42)
    target_h = int(height * 0.28)
    ref.thumbnail((target_w, target_h))
    x = width - ref.width - 70
    y = int(height * 0.18 + np.sin(progress * np.pi * 2) * 18)
    image.paste(ref, (x, y))


def _draw_center_text(
    draw: ImageDraw.ImageDraw,
    headline: str,
    body: str,
    size: tuple[int, int],
    font_big: ImageFont.ImageFont,
    font_med: ImageFont.ImageFont,
    palette: dict[str, tuple[int, int, int]],
) -> None:
    width, height = size
    y = int(height * 0.42)
    lines = _wrap(headline, 18 if width < height else 24)
    for line in lines[:4]:
        bbox = draw.textbbox((0, 0), line, font=font_big)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x + 4, y + 4), line, font=font_big, fill=(0, 0, 0))
        draw.text((x, y), line, font=font_big, fill=(255, 255, 255))
        y += 78

    body_lines = _wrap(body, 32 if width < height else 42)
    y += 18
    for line in body_lines[:3]:
        bbox = draw.textbbox((0, 0), line, font=font_med)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font_med, fill=(235, 245, 255))
        y += 52


def _draw_caption_bar(
    draw: ImageDraw.ImageDraw,
    script: dict,
    current_s: float,
    duration_s: int,
    size: tuple[int, int],
    font: ImageFont.ImageFont,
) -> None:
    width, height = size
    text = _caption_for_time(script, current_s, duration_s)
    if not text:
        return
    lines = _wrap(text, 38 if width < height else 52)[:2]
    bar_h = 150
    y0 = height - bar_h - 72
    draw.rounded_rectangle((48, y0, width - 48, y0 + bar_h), radius=34, fill=(0, 0, 0, 160))
    y = y0 + 32
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=font, fill=(255, 255, 255))
        y += 38


def _draw_progress(
    draw: ImageDraw.ImageDraw,
    progress: float,
    size: tuple[int, int],
    palette: dict[str, tuple[int, int, int]],
) -> None:
    width, height = size
    x0, y0 = 64, height - 48
    x1 = width - 64
    draw.rounded_rectangle((x0, y0, x1, y0 + 12), radius=6, fill=(255, 255, 255, 70))
    draw.rounded_rectangle((x0, y0, x0 + int((x1 - x0) * progress), y0 + 12), radius=6, fill=palette["accent"])


def _caption_for_time(script: dict, current_s: float, duration_s: int) -> str:
    scenes = script.get("scenes") or []
    if not scenes:
        return str(script.get("hook") or "")
    index = min(len(scenes) - 1, int((current_s / max(1, duration_s)) * len(scenes)))
    scene = scenes[index]
    return str(scene.get("voiceover") or scene.get("dialogue") or scene.get("text_overlay") or "")


def _load_reference_image(source: str) -> Image.Image | None:
    if not source:
        return None
    try:
        if source.startswith("data:image"):
            encoded = source.split(",", 1)[1]
            return Image.open(BytesIO(base64.b64decode(encoded)))
        if os.path.exists(source):
            return Image.open(source)
    except Exception:
        return None
    return None


def _font(size: int) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def _palette(brief: Brief) -> dict[str, tuple[int, int, int]]:
    return {
        "primary": _hex(brief.brand.palette.primary, (20, 20, 35)),
        "accent": _hex(brief.brand.palette.accent, (80, 180, 255)),
        "bg": _hex(brief.brand.palette.bg, (8, 8, 12)),
    }


def _hex(value: str, fallback: tuple[int, int, int]) -> tuple[int, int, int]:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", str(value or ""))
    if not match:
        return fallback
    raw = match.group(1)
    return tuple(int(raw[i : i + 2], 16) for i in (0, 2, 4))


def _wrap(text: str, width: int) -> list[str]:
    cleaned = re.sub(r"\s+", " ", str(text or "")).strip()
    if not cleaned:
        return []
    return textwrap.wrap(cleaned, width=width, break_long_words=False)


def _slug(text: str) -> str:
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:8]
    base = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower() or "brand"
    return f"{base}-{digest}"
