# model_gateway — Hướng dẫn dùng & lộ trình swap BytePlus

## Mục đích
Tách phần gọi model ra khỏi business logic, để có thể **swap backend** mà không phải đụng vào code agent/pipeline:
- **legacy** (mặc định hiện tại): Gemini cho LLM + Ecomdy cho video.
- **byteplus** (khi có key): Seed 2.0 / ModelArk cho LLM + Seedance 2.0 cho video.

## Cấu trúc
```
backend/model_gateway/
├── __init__.py              # public API: get_llm, get_video, current_backend
├── interfaces.py            # LLMClient, VideoClient (ABC) + LLMResult, VideoJob
├── legacy_backend.py        # LegacyLLMClient, LegacyVideoClient (wrap code cũ)
├── byteplus_backend.py      # Seed2Client, SeedanceVideoClient (skeleton, sẵn sàng khi có key)
├── factory.py               # chọn backend theo env MODEL_BACKEND
├── EXAMPLE.py               # demo cách gọi
└── smoke_test.py            # test import + routing (không cần API key)
```

## Quy tắc dùng
- **KHÔNG** import trực tiếp `services.llm_manager` hay `services.ecomdy` từ code mới.
- **CHỈ** dùng `from model_gateway import get_llm, get_video`.
- Code cũ vẫn chạy song song, không bị xóa.

Ví dụ:
```python
from model_gateway import get_llm, get_video

llm = get_llm()
plan = llm.generate("Trả JSON {ok: true}", json_mode=True).json

video = get_video()
job = await video.submit("a coffee cup, neon", mode="t2v", duration_s=5, seed=42)
url = await video.poll(job.job_id)
```

## Cách bật BytePlus khi có key
1. Điền key vào `backend/.env`:
   ```
   MODEL_BACKEND=byteplus
   BYTEPLUS_SEED2_API_KEY=...
   BYTEPLUS_SEEDANCE_API_KEY=...
   ```
2. (Tuỳ chọn) cập nhật endpoint trong `byteplus_backend.py` cho khớp tài liệu chính thức BytePlus.
3. Restart backend. App log sẽ in `provider=byteplus-seed2` / `byteplus-seedance`.
4. Nếu muốn rollback: đổi `MODEL_BACKEND=legacy` rồi restart.

## Đã verify
- `python -c "from model_gateway import get_llm, get_video"` → OK, không kéo SDK nặng.
- Singleton: `get_llm() is get_llm()` → True.
- Env sai / thiếu → fallback `legacy` hoặc raise `RuntimeError` có message rõ.

## Khi nào xài backend nào
| Tình huống | Backend |
|---|---|
| Đang dev, chưa có key BytePlus | `legacy` |
| Có key Seed 2.0 nhưng chưa có Seedance | `byteplus` (LLM sẽ chạy thật, video fallback… xem dưới) |
| Có đủ cả 2 key | `byteplus` |
| Demo muốn chắc chắn mock không lộ | `legacy` + không truyền `ECOMDY_API_KEY` |
