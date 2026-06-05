"""__init__ cho services.subtitles"""
from .whisper_burn import build_srt, build_srt_from_vo, burn_subtitles, transcribe


def _srt_timestamp(seconds: float) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}".replace(".", ",")


def generate_srt_from_script(script: dict, total_duration: int = 30) -> str:
    scenes = script.get("scenes", [])
    if not scenes:
        return ""

    duration_per_scene = total_duration / len(scenes)
    current_time = 0.0
    subtitle_index = 1
    srt_content = []

    for scene in scenes:
        dialogue = (scene.get("dialogue") or scene.get("voiceover") or "").strip()
        if dialogue:
            start_time = current_time
            end_time = current_time + duration_per_scene
            srt_content.extend([
                str(subtitle_index),
                f"{_srt_timestamp(start_time)} --> {_srt_timestamp(end_time)}",
                dialogue,
                "",
            ])
            subtitle_index += 1
        current_time += duration_per_scene

    return "\n".join(srt_content)


__all__ = [
    "transcribe",
    "build_srt",
    "build_srt_from_vo",
    "burn_subtitles",
    "generate_srt_from_script",
]
