# HackathonDN - Auto Video Platform

Nền tảng tự động hóa quá trình sáng tạo và xuất bản video ngắn sử dụng AI, được thiết kế đặc biệt cho việc sản xuất hàng loạt video giải trí và quảng cáo trên Facebook và TikTok.

Dự án này là giải pháp end-to-end kết hợp:
1. **Frontend**: Giao diện Next.js hiện đại để người dùng lên ý tưởng, chọn phong cách và cấu hình lên lịch.
2. **Backend**: FastAPI xử lý các luồng công việc AI (Multi-Agent) để viết kịch bản, làm đạo diễn, tạo caption và render video.
3. **Workflow Automation**: Kết nối n8n để lên lịch tự động đăng bài lên các nền tảng mạng xã hội.

## Tính năng chính
- **Multi-Agent Pipeline**:
  - **Biên kịch (Scriptwriter)**: Tự động phân tích ý tưởng/từ khóa, viết kịch bản chi tiết gồm hook, body, CTA và overlay text.
  - **Đạo diễn (Director)**: Dịch kịch bản sang các "Camera Prompts" chuẩn xác và phong cách hình ảnh (style prompts) để gửi cho Video AI Engine.
- **Tích hợp Research (Google Serper)**: Tự động tìm kiếm thêm thông tin từ Google để làm phong phú kịch bản nếu người dùng cung cấp từ khóa. Cho phép người dùng tuỳ chỉnh lại kết quả nghiên cứu.
- **Tự động xoay vòng API Key (Key Rotation)**: Quản lý và tự động xoay vòng nhiều `GEMINI_API_KEY` để tránh giới hạn rate limit/quota, đảm bảo tính ổn định của hệ thống.
- **Tích hợp Video Engine (Ecomdy/Kling)**: Tự động render ảnh và prompt thành video. Hỗ trợ upload ảnh Mascot (Google Drive) để giữ nguyên nhân vật xuyên suốt video (Image-to-Video).
- **Trình tạo Caption Tự động**: Gợi ý caption tối ưu theo thuật toán của từng nền tảng (Facebook/TikTok) với hashtag phù hợp.
- **Theo dõi qua Google Sheets**: Quản lý lịch trình, tiến độ và trạng thái các video đang render thông qua Google Sheets.
- **Tích hợp n8n Webhook**: Đẩy kết quả cuối cùng sang n8n để phân phối tự động tới các mạng xã hội.

## Cấu trúc thư mục
```
.
├── backend/                  # Mã nguồn FastAPI Backend
│   ├── data/                 # Thư mục chứa dữ liệu tĩnh hoặc file tạm
│   ├── models/               # Các mô hình dữ liệu (Pydantic/DB)
│   ├── routers/              # Các API Endpoints (video, caption, research, trending...)
│   ├── services/             # Logic nghiệp vụ (Agents, API Key Manager, Serper, Ecomdy...)
│   ├── main.py               # Entry point của ứng dụng backend
│   └── requirements.txt      # Danh sách thư viện Python
├── frontend/                 # Mã nguồn Next.js Frontend
│   ├── app/                  # Các trang của ứng dụng (App Router)
│   ├── components/           # Các component tái sử dụng (Create Wizard, Stepper...)
│   ├── lib/                  # Các file tiện ích, kết nối API
│   └── package.json          # Danh sách thư viện Node.js
├── n8n/                      # Thư mục cấu hình n8n
│   └── n8n_workflow_template.json # Template quy trình n8n
└── scripts/                  # Các script công cụ phụ trợ
```

## Hướng dẫn cài đặt và khởi chạy

### Yêu cầu tiên quyết
- Node.js (>= 18.x)
- Python (>= 3.9)
- Một dự án Google Cloud Platform với Google Drive API và Google Sheets API được kích hoạt. Lấy file `credentials.json` (Service Account).
- Tài khoản và API Key của:
  - Gemini (Google Generative AI)
  - Serper (Tùy chọn cho tính năng tìm kiếm)
  - Ecomdy (API tạo video)

### 1. Cài đặt Backend
1. Di chuyển vào thư mục `backend/`:
   ```bash
   cd backend
   ```
2. Tạo môi trường ảo (khuyến nghị) và kích hoạt:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Trên Windows: venv\Scripts\activate
   ```
3. Cài đặt thư viện:
   ```bash
   pip install -r requirements.txt
   ```
4. Đổi tên file `.env.example` thành `.env` và điền đầy đủ các thông tin:
   ```env
   # API Keys
   GEMINI_API_KEY="key1,key2,key3" # Hỗ trợ cơ chế tự xoay vòng API Key
   SERPER_API_KEY="your_serper_key"
   ECOMDY_API_KEY="your_ecomdy_key"

   # Google Service Account (Đường dẫn tới file JSON, ví dụ: ../credentials.json)
   GOOGLE_CREDENTIALS_FILE="path/to/credentials.json"
   GOOGLE_DRIVE_FOLDER_ID="your_drive_folder_id"
   GOOGLE_SHEET_ID="your_sheet_id"

   # n8n
   N8N_WEBHOOK_URL="http://your-n8n.com/webhook/create-video"
   ```
5. Chạy server FastAPI:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   Backend sẽ chạy tại `http://localhost:8000`. Bạn có thể truy cập `http://localhost:8000/docs` để xem tài liệu API (Swagger UI).

### 2. Cài đặt Frontend
1. Di chuyển vào thư mục `frontend/`:
   ```bash
   cd frontend
   ```
2. Cài đặt các gói phụ thuộc:
   ```bash
   npm install
   # hoặc yarn install / pnpm install
   ```
3. Chạy server phát triển Next.js:
   ```bash
   npm run dev
   ```
   Frontend sẽ chạy tại `http://localhost:3000`.

### 3. Cài đặt n8n (Tùy chọn để tự động đăng)
1. Cài đặt và khởi chạy n8n trên môi trường của bạn.
2. Import file workflow từ `n8n/n8n_workflow_template.json` vào n8n.
3. Cấu hình lại các webhook và thông tin kết nối (Facebook/TikTok) trong n8n cho phù hợp.
4. Cập nhật `N8N_WEBHOOK_URL` trong file `.env` của backend.

## Quy trình hoạt động (Workflow)
1. **Người dùng** truy cập giao diện web (Frontend) và tạo một Video Request. Họ nhập nội dung, chọn loại video, thời lượng, phong cách, đính kèm ảnh (mascot) và lịch lên bài.
2. Nếu bật tính năng **"Tự động bổ sung data từ Google"**, hệ thống sẽ dùng `Serper` tìm kiếm thông tin và cho phép người dùng tùy chỉnh.
3. Yêu cầu được gửi xuống **Backend**. Backend ghi trạng thái "pending" vào **Google Sheets**.
4. Upload hình ảnh đính kèm (mascot) lên **Google Drive**.
5. Kích hoạt **Background Task**:
   - **Scriptwriter Agent** sinh kịch bản.
   - **Director Agent** sinh prompt hình ảnh.
   - Gọi Ecomdy API để tiến hành render (Image-to-Video).
6. Khi video được render xong, Backend gọi webhook đến **n8n**.
7. **n8n** nhận video, lưu lại và đến giờ được lập lịch sẽ tự động publish lên **Facebook** / **TikTok**.

## Thông tin thêm
- **Cơ chế xoay vòng API Key**: Tệp `backend/services/api_key_manager.py` tự động nhận diện danh sách các key Gemini (cách nhau bởi dấu phẩy). Khi gặp giới hạn quota (429) hoặc lỗi xác thực (401/403), hệ thống sẽ chuyển sang key tiếp theo để không làm gián đoạn tác vụ.
- **Frontend Components**: Các luồng tạo video được thực hiện từng bước thông qua component `create-wizard.tsx` với thiết kế dạng Step Wizard đẹp mắt, dễ sử dụng.

---
*Dự án HackathonDN - Nâng tầm trải nghiệm tự động hóa tạo video!*