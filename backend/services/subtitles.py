import datetime

def srt_timestamp(seconds: float) -> str:
    """Chuyển đổi giây sang định dạng HH:MM:SS,mmm của SRT"""
    td = datetime.timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

def generate_srt_from_script(script: dict, total_duration: int = 30) -> str:
    """
    Tạo nội dung file SRT từ kịch bản phân cảnh.
    Giả định chia đều thời lượng cho các cảnh nếu không có timestamp rõ ràng.
    """
    scenes = script.get("scenes", [])
    if not scenes:
        return ""
    
    num_scenes = len(scenes)
    duration_per_scene = total_duration / num_scenes if num_scenes > 0 else total_duration
    
    srt_content = []
    current_time = 0.0
    
    subtitle_index = 1
    for scene in scenes:
        dialogue = scene.get("dialogue", "").strip()
        if dialogue:
            start_time = current_time
            end_time = current_time + duration_per_scene
            
            srt_content.append(str(subtitle_index))
            srt_content.append(f"{srt_timestamp(start_time)} --> {srt_timestamp(end_time)}")
            srt_content.append(dialogue)
            srt_content.append("")  # Dòng trống ngăn cách
            
            subtitle_index += 1
            
        current_time += duration_per_scene
        
    return "\n".join(srt_content)
