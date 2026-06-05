# Kế hoạch Kiến trúc: Tách luồng Tạo Video & Lên lịch, hỗ trợ Avatar AI

Ý tưởng của anh cực kỳ chuẩn xác cho một luồng làm việc thực tế (MVP): AI sinh ra "phôi" (footage), con người chỉnh sửa hậu kỳ (CapCut), sau đó mới đưa lên hệ thống tự động đăng bài.

Dưới đây là kế hoạch chi tiết để hiện thực hóa luồng này:

## Đề xuất bổ sung (Suggestions)
> [!TIP]
> **Tự động sinh file Phụ đề (.srt):** Vì user sẽ tải video về CapCut để edit, hệ thống nên tự động xuất lời thoại kịch bản thành file `.srt` và cho phép tải về. User chỉ cần kéo thả `.srt` vào CapCut là có ngay phụ đề tiếng Việt siêu chuẩn mà không cần gõ lại.
> **Lưu trữ Video:** Khi user upload video đã edit lên để hẹn giờ đăng, ta sẽ tái sử dụng tài khoản Google Drive (nhờ Service Account) để host file `.mp4`, lấy link trực tiếp đẩy sang n8n.

## Open Questions

> [!WARNING]
> 1. **Dung lượng lưu trữ:** Upload file MP4 lên Google Drive cá nhân (hoặc Shared Drive) sẽ tốn dung lượng khá nhanh. Team mình có Google Workspace hay tài khoản Drive nào dung lượng lớn (15GB - 100GB) để cấp quyền cho Service Account không ạ?
> 2. **Cache Avatar:** Em sẽ hardcode danh sách 20 avatar này vào backend để web load cực nhanh (thay vì mỗi lần mở web lại gọi API Ecomdy). Anh đồng ý chứ?

## Proposed Changes

---

### Backend Components

#### [MODIFY] `routers/video.py`
- Bỏ bước gọi webhook `n8n` ra khỏi `process_video_background`. Cập nhật trạng thái chỉ đến `rendered`.
- Viết lại hàm tạo video hỗ trợ 2 chế độ (Engine Type):
  - **`engine=mascot`**: Gọi `/video/generate` (API cũ - video câm).
  - **`engine=avatar`**: Nhận `avatar_id`, gọi `/avatar/generate` (API mới - người mẫu nhép miệng).
- Thêm tính năng tự động tạo file nội dung `.srt` text từ kịch bản để trả về cho Client.
- **[NEW] API `GET /api/v1/video/avatars`**: Trả về danh sách 20 Avatar kèm thumbnail.
- **[NEW] API `POST /api/v1/video/schedule`**: Nhận Upload file `.mp4` (đã qua CapCut), Upload lên Google Drive, và bắn Webhook thông tin sang hệ thống **n8n**.

#### [MODIFY] `services/drive_service.py`
- Tái sử dụng logic của `upload_image` để tạo hàm `upload_video(file)` chuyên biệt xử lý lưu trữ MP4.

---

### Frontend Components

#### [MODIFY] `components/create-wizard.tsx`
- Cắt bỏ các form field: "Chọn Kênh", "Thời gian hẹn giờ".
- Thêm 1 Tab/Bước chọn Engine:
  - **Option 1: Tải Mascot Cá Nhân (Video câm)** -> Hiện form Upload Image.
  - **Option 2: Chọn Avatar AI (Có tiếng, nhép miệng)** -> Fetch danh sách từ API `/avatars` và hiển thị dưới dạng Grid để user click chọn mặt người mẫu.
- Sửa lại màn hình Hoàn thành (Success View):
  - Thay vì hiện thông báo "Đã lên lịch", hiển thị: Video Preview.
  - Các nút: `Tải Video (MP4)`, `Tải Phụ Đề (SRT)`.
  - Hai Action Button lớn: `Tiếp tục: Lên lịch đăng ngay` hoặc `Làm sau`.

#### [NEW] `app/schedule/page.tsx`
- Xây dựng một UI mới toanh chuyên cho việc Hẹn giờ đăng bài.
- Giao diện gồm:
  - Upload Box: Nhận file `.mp4` (video cuối cùng đã edit).
  - Khung Caption: Lấy caption gợi ý từ kịch bản cũ hoặc gõ mới.
  - Form: Chọn kênh (TikTok/Facebook) và Hẹn giờ.
- Khi bấm "Submit", UI sẽ show progress bar tải video lên Server và đẩy sang n8n.

## Verification Plan

### Automated Tests
- Gửi request đến `/api/v1/video/avatars` đảm bảo trả về HTTP 200 và cấu trúc list 20 avatars.
- Test hàm `upload_video` lên Google Drive với file MP4 nhẹ.

### Manual Verification
1. Lên web tạo video với mode **Avatar AI**, chờ xem hệ thống có trả video nhép miệng đúng lời thoại không.
2. Tải video và file `.srt` xuống, mở trên máy tính kiểm tra.
3. Chuyển sang màn hình "Lên Lịch Đăng", upload lại 1 file mp4 bất kỳ và xác nhận webhook n8n đã nhận đủ link video và dữ liệu lịch đăng.
