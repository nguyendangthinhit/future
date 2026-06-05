"""
TTS Service: Gọi Ecomdy TTS API để tạo giọng đọc, sau đó ghép audio vào video bằng moviepy.
"""
import os
import httpx
import asyncio
import tempfile


ECOMDY_API_URL = "https://api.ecomdy.co/v1"


async def generate_tts(text: str, voice_id: str = None) -> str:
    """
    Gọi Ecomdy TTS API. Trả về job_id.
    Nếu không truyền voice_id, dùng giọng mặc định (English male).
    """
    api_key = os.getenv("ECOMDY_API_KEY")
    if not api_key:
        print("Warning: ECOMDY_API_KEY not set. Skipping TTS.")
        return None

    # Dùng voice mặc định nếu không truyền
    if not voice_id:
        voice_id = os.getenv("DEFAULT_VOICE_ID", "7644282781753131016")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "text": text,
        "voice_id": voice_id,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ECOMDY_API_URL}/tts/generate",
            json=payload,
            headers=headers,
            timeout=30.0,
        )

        if response.status_code in (200, 201, 202):
            data = response.json().get("data", {})
            job_id = data.get("job_id") or data.get("id")
            if not job_id:
                raise Exception(f"TTS: không tìm thấy job_id: {response.text}")
            print(f"[TTS] Job submitted: {job_id}")
            return job_id
        else:
            print(f"[TTS] Error: {response.text}")
            raise Exception(f"TTS API failed: {response.status_code}: {response.text}")


async def poll_tts_status(job_id: str, max_retries: int = 40, delay_seconds: int = 3) -> str:
    """
    Polling TTS job. Trả về audio_url khi hoàn thành.
    """
    if not job_id:
        return None

    api_key = os.getenv("ECOMDY_API_KEY")
    headers = {"Authorization": f"Bearer {api_key}"}

    async with httpx.AsyncClient() as client:
        for i in range(max_retries):
            response = await client.get(
                f"{ECOMDY_API_URL}/jobs/{job_id}",
                headers=headers,
                timeout=10.0,
            )

            if response.status_code == 200:
                data = response.json().get("data", {})
                status = str(data.get("status", "")).upper()
                output_url = data.get("output_url")

                if output_url and status in ("COMPLETED", "SUCCESS", "SUCCEEDED", "DONE", "FINISHED"):
                    print(f"[TTS] Hoàn thành! Audio URL: {output_url}")
                    return output_url
                if output_url and status not in ("PENDING", "PROCESSING", "QUEUED", "RUNNING"):
                    return output_url
                if status in ("FAILED", "ERROR"):
                    error_data = data.get("error", {})
                    err_msg = error_data.get("message", "Unknown error")
                    print(f"[TTS] FAILED: {err_msg}")
                    raise Exception(f"TTS failed: {err_msg}")

            await asyncio.sleep(delay_seconds)

    raise Exception("TTS polling timeout.")


async def merge_video_audio(video_url: str, audio_url: str) -> str:
    """
    Download video + audio, ghép bằng moviepy, upload kết quả lên imgbb.
    Trả về URL của video đã ghép.
    """
    from moviepy import VideoFileClip, AudioFileClip

    tmp_dir = tempfile.mkdtemp()
    video_path = os.path.join(tmp_dir, "video.mp4")
    audio_path = os.path.join(tmp_dir, "audio.mp3")
    output_path = os.path.join(tmp_dir, "merged.mp4")

    try:
        # Download video và audio song song
        async with httpx.AsyncClient(timeout=60.0) as client:
            print(f"[MERGE] Đang tải video và audio...")
            video_resp, audio_resp = await asyncio.gather(
                client.get(video_url, follow_redirects=True),
                client.get(audio_url, follow_redirects=True),
            )

        with open(video_path, "wb") as f:
            f.write(video_resp.content)
        with open(audio_path, "wb") as f:
            f.write(audio_resp.content)

        print(f"[MERGE] Đang ghép video + audio bằng moviepy...")

        # Dùng asyncio.to_thread vì moviepy là blocking
        def _merge():
            video_clip = VideoFileClip(video_path)
            audio_clip = AudioFileClip(audio_path)

            # Nếu audio dài hơn video, cắt audio. Nếu ngược lại, giữ nguyên.
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.with_subclip(0, video_clip.duration)

            final = video_clip.with_audio(audio_clip)
            final.write_videofile(
                output_path,
                codec="libx264",
                audio_codec="aac",
                logger=None,  # Tắt log moviepy cho sạch terminal
            )
            video_clip.close()
            audio_clip.close()
            final.close()

        await asyncio.to_thread(_merge)

        print(f"[MERGE] Ghép xong! File: {output_path}")

        # Upload video đã ghép lên hosting (dùng imgbb cho ảnh, nhưng video thì trả file path)
        # Vì imgbb không hỗ trợ video, ta trả về file path tạm. 
        # Trong thực tế sẽ upload lên cloud storage.
        return output_path

    except Exception as e:
        print(f"[MERGE] Lỗi ghép video: {e}")
        import traceback
        traceback.print_exc()
        # Nếu merge lỗi, trả về video gốc (câm) thay vì crash toàn bộ
        return None


def extract_dialogue_from_script(script: dict) -> str:
    """
    Trích xuất toàn bộ lời thoại từ kịch bản để gửi cho TTS.
    """
    dialogues = []
    scenes = script.get("scenes", [])
    for scene in scenes:
        dialogue = scene.get("dialogue", "")
        if dialogue:
            dialogues.append(dialogue)
    
    if not dialogues:
        # Fallback: dùng hook_instruction hoặc title
        hook = script.get("hook_instruction", "")
        if hook:
            dialogues.append(hook)
    
    return " ".join(dialogues)
