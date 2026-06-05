# BX-T1 Submission Status

## Đã khớp sau vòng sửa cuối

- Brief đầu vào có theme, brand kit, audience, platform, constraints, ảnh moodboard/reference.
- UI tạo pack có upload ảnh và chọn `1` hoặc `2` variants.
- Pipeline agentic factory chạy qua planner, brand steward, copywriter, director, visualist, renderer, voice, subtitler, editor, QA, packer.
- Có 2 variants sáng tạo A/B khác nhau cho sample F&B:
  - A: `trend-led Gen Z hook`
  - B: `product-led demo`
- Có QA score nội bộ và cả hai variants đạt publishable:
  - A: 88/100
  - B: 94/100
- Có MP4 publish-ready fallback thật khi chưa có provider video:
  - `outputs/videos/highlands-coffee-b29f62f3/A/final_9x16.mp4`
  - `outputs/videos/highlands-coffee-b29f62f3/A/final_1x1.mp4`
  - `outputs/videos/highlands-coffee-b29f62f3/B/final_9x16.mp4`
  - `outputs/videos/highlands-coffee-b29f62f3/B/final_1x1.mp4`
- Có cover art local:
  - `outputs/videos/highlands-coffee-b29f62f3/A/cover.jpg`
  - `outputs/videos/highlands-coffee-b29f62f3/B/cover.jpg`
- Có demo one-input-change:
  - `outputs/one_input_change_demo.json`
  - Gen Z output chuyển sang mom-oriented output khi đổi audience.
- Có demo walkthrough video fallback:
  - `outputs/videos/markx-content-factory-339051aa/demo/final_9x16.mp4`
  - `outputs/videos/markx-content-factory-339051aa/demo/final_1x1.mp4`
- Có TRAE workflow template:
  - `trae/workflows/content-factory.trae.json`
- Có tài liệu workflow 1 trang:
  - `docs/WORKFLOW.md`

## Còn chưa khớp do đã loại trừ khỏi scope hiện tại

- Seedance 2.0 BytePlus thật chưa được gọi production.
- `backend/model_gateway/byteplus_backend.py` vẫn là gateway/skeleton chờ endpoint/key chính thức.

## Lưu ý kỹ thuật

- Vì máy local không có FFmpeg system binary, project dùng fallback Python `imageio/imageio-ffmpeg` để tạo MP4 thật.
- Fallback này không thay thế Seedance, nhưng đủ để có artifact video review/publish-ready ở local khi chưa có BytePlus key.
