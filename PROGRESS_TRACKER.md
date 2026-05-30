# 🚀 NHẬT KÝ TIẾN ĐỘ & TRIỂN KHAI (FULL-STACK & AI)

*File này dùng để theo dõi tiến độ cá nhân của Core Developer. Hãy đổi `[ ]` thành `[x]` khi hoàn thành một task, và ghi chú ngắn gọn cách bạn đã triển khai nó (ví dụ: dùng thư viện gì, gặp lỗi gì và cách fix).*

---

## 📅 NGÀY 1: SETUP MÔI TRƯỜNG & KHỞI TẠO DỰ ÁN

- `[x]` **Khởi tạo Backend FastAPI**
  - *Mô tả triển khai:* Đã tạo cấu trúc backend chuẩn (main.py, routers, services, models). Đã init requirements.txt với FastAPI, Uvicorn, Google Auth, v.v.
- `[x]` **Khởi tạo Frontend Next.js 14**
  - *Mô tả triển khai:* Khởi tạo thành công repo `nguyendangthinhit/future` trên GitHub với Next.js 14, Tailwind CSS và TypeScript. Framework hoàn toàn khớp với PRD.
- `[x]` **Cài đặt các bộ Taste Skill (`design-taste-frontend`, `high-end-visual-design`)**
  - *Mô tả triển khai:* Đã pull thành công các bộ hướng dẫn thiết kế UI Premium vào dự án.

## 📅 NGÀY 2: GOOGLE SHEETS SERVICE & DATA MODELS

- `[x]` **Kết nối Google Sheets API (gspread)**
  - *Mô tả triển khai:* Đã setup service đọc/ghi sheet với google-auth.
- `[x]` **Viết các hàm CRUD (create_video_record, update_video_status)**
  - *Mô tả triển khai:* Đã triển khai trong `services/sheets.py`.
- `[x]` **Định nghĩa Pydantic Data Models (CreateVideoRequest, VideoResponse)**
  - *Mô tả triển khai:* Đã định nghĩa model ở `models/video.py`.
- `[ ]` **Tạo UI Form cơ bản trên Next.js (bằng HTML thường để test API)**
  - *Mô tả triển khai:* 

## 📅 NGÀY 3: TÍCH HỢP MULTI-AGENT PIPELINE (CORE)

- `[x]` **Load dữ liệu thị hiếu & Case studies từ JSON tĩnh**
  - *Mô tả triển khai:* Đã tạo mock data trong `data/country_profiles.json` và `viral_case_studies.json`.
- `[x]` **Cấu hình Agent 1: Biên Kịch (Scriptwriter) gọi Gemini API**
  - *Mô tả triển khai:* Xây dựng logic gọi Gemini với prompt kết hợp context quốc gia.
- `[x]` **Cấu hình Agent 2: Đạo Diễn (Director) gọi Gemini API**
  - *Mô tả triển khai:* Đã cấu hình đổi output từ Kling sang Ecomdy API theo định hướng.
- `[x]` **Viết Orchestrator ghép 2 Agent lại (Pipeline)**
  - *Mô tả triển khai:* Nối luồng hoàn thiện tại `services/agents/pipeline.py`.

## 📅 NGÀY 4: API ENDPOINTS & WEBHOOK n8n

- `[x]` **Hoàn thiện API `/video/create` (Luồng thủ công)**
  - *Mô tả triển khai:* Hoàn thiện tại `routers/video.py`.
- `[x]` **Viết HTTP Request gọi Webhook sang n8n để kích hoạt render video**
  - *Mô tả triển khai:* Tích hợp httpx để POST webhook, đã đổi payload sang ecomdy_prompts.
- `[x]` **Hoàn thiện API `/video/callback` (Để n8n gọi về khi xong)**
  - *Mô tả triển khai:* Xong logic cập nhật Google Sheet qua status.

## 📅 NGÀY 5: 


- `[x]` **Tích hợp Cloudinary để upload ảnh (Mascot Image)**
  - *Mô tả triển khai:* Đã thay thế Cloudinary bằng Google Drive API (`drive_service.py`) để tối ưu.
- `[x]` **Thiết lập Cron Job (APScheduler) chạy lúc 2:00 AM**
  - *Mô tả triển khai:* Đã triển khai `services/scheduler.py` gọi luồng Auto Suggest.
- `[x]` **Viết API `/verify` để load danh sách ý tưởng và duyệt**
  - *Mô tả triển khai:* Hoàn thiện trong `routers/verify.py`.

## 📅 NGÀY 6: HOÀN THIỆN FRONTEND NEXT.JS (UI/UX)

- `[ ]` **Hoàn thiện giao diện Trang Tạo Video (`/create`)**
  - *Mô tả triển khai:* (Sử dụng Taste Skill để style như thế nào? Dùng Tailwind classes gì?)
- `[ ]` **Hoàn thiện giao diện Trang Kiểm duyệt (`/verify`)**
  - *Mô tả triển khai:* 
- `[ ]` **Dựng Dashboard tổng quan (KPIs, Charts)**
  - *Mô tả triển khai:* (Dùng thư viện Recharts ra sao?)

## 📅 NGÀY 7: DEPLOY & FIX BUGS

- `[ ]` **Deploy Backend lên Railway / Render**
  - *Mô tả triển khai:* (Cấu hình biến môi trường trên server)
- `[ ]` **Deploy Frontend lên Vercel**
  - *Mô tả triển khai:* 
- `[ ]` **Chạy kiểm thử End-to-End toàn bộ hệ thống 5 lần**
  - *Mô tả triển khai:* (Ghi lại kết quả test, có bug nào phát sinh phút chót không?)
- `[ ]` **Đóng băng Code (Code Freeze) sẵn sàng Pitching!**
  - *Mô tả triển khai:* 
