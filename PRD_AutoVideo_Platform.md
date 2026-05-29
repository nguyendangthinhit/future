#  TÀI LIỆU KỸ THUẬT – AUTO VIDEO PLATFORM
**Phiên bản:** 1.0.0  
**Ngày tạo:** 2026-05-29  
**Trạng thái:** Bản nội bộ – sẵn sàng triển khai  
**Loại dự án:** Open Source  

---

## MỤC LỤC

1. [Tổng quan sản phẩm](#1-tổng-quan-sản-phẩm)
2. [Kiến trúc hệ thống](#2-kiến-trúc-hệ-thống)
3. [Tech Stack](#3-tech-stack)
4. [Luồng hoạt động chi tiết](#4-luồng-hoạt-động-chi-tiết)
5. [Schema dữ liệu](#5-schema-dữ-liệu)
6. [Cơ chế phân tích thị hiếu theo quốc gia](#6-cơ-chế-phân-tích-thị-hiếu-theo-quốc-gia)
7. [Cơ chế tự động đề xuất nội dung](#7-cơ-chế-tự-động-đề-xuất-nội-dung)
8. [Module Web UI – Chi tiết màn hình](#8-module-web-ui--chi-tiết-màn-hình)
9. [Module Dashboard – Chi tiết màn hình](#9-module-dashboard--chi-tiết-màn-hình)
10. [Luồng n8n – Chi tiết từng node](#10-luồng-n8n--chi-tiết-từng-node)
11. [API Endpoints](#11-api-endpoints)
12. [Cấu hình & Triển khai (Setup Guide)](#12-cấu-hình--triển-khai-setup-guide)
13. [Giới hạn & Hạn mức](#13-giới-hạn--hạn-mức)
14. [Rủi ro & Kế hoạch dự phòng](#14-rủi-ro--kế-hoạch-dự-phòng)

---

## 1. TỔNG QUAN SẢN PHẨM

### 1.1. Mô tả

**Auto Video Platform** là một nền tảng mã nguồn mở (open source) cho phép cá nhân và tổ chức tự động hóa toàn bộ quy trình sản xuất và đăng tải video ngắn lên các kênh mạng xã hội (Facebook Fanpage, TikTok).

Người dùng chỉ cần cung cấp ý tưởng, nội dung, và lựa chọn phong cách thiết kế. Hệ thống sẽ tự động dựng video hoàn chỉnh và đăng lên đúng kênh, đúng thời điểm đã lên lịch.

### 1.2. Mục tiêu sản phẩm

| Mục tiêu | Mô tả |
|---|---|
| **Tự động hóa** | Giảm thiểu thao tác thủ công trong quy trình tạo & đăng video |
| **Đa đặc vụ (Multi-Agent)** | Tách nhỏ luồng tư duy LLM thành Biên kịch (Scriptwriter) & Đạo diễn (Director) để kịch bản chuyên sâu hơn |
| **Cá nhân hóa & AutoCameo** | Tối ưu nội dung theo thị hiếu quốc gia và giữ tính nhất quán thương hiệu bằng Mascot Image |
| **Đề xuất thông minh** | LLM tự phân tích comment và xu hướng để đề xuất ý tưởng mới mỗi ngày |
| **Dễ triển khai** | ~95% đã được cấu hình sẵn, người dùng chỉ cần khai báo lại kênh của mình |
| **Mã nguồn mở** | Cho phép cộng đồng clone, tùy biến, và đóng góp |

### 1.3. Loại hình & Thời lượng video được hỗ trợ

| Loại hình | Thời lượng có thể chọn |
|---|---|
| Video giải trí | 30 giây / 60 giây / 90 giây |
| Video quảng cáo | 15 giây / 30 giây / 60 giây |

### 1.4. Kênh đăng hỗ trợ

- Facebook Fanpage (qua Facebook Graph API)
- TikTok (qua TikTok Content Posting API)

---

## 2. KIẾN TRÚC HỆ THỐNG

```
┌─────────────────────────────────────────────────────────────────────┐
│                          NGƯỜI DÙNG                                 │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                ┌───────────────▼────────────────┐
                │         WEB UI (Next.js)        │
                │  - Trang tạo video              │
                │  - Trang verify ý tưởng         │
                │  - Dashboard tổng quan          │
                └───────────────┬────────────────┘
                                │ HTTP POST (JSON payload)
                ┌───────────────▼────────────────┐
                │       BACKEND API (FastAPI)     │
                │  - Xử lý form                  │
                │  - Multi-Agent: Biên kịch (Script) & Đạo diễn (Camera) │
                │  - Gọi Google Search (optional) │
                │  - Ghi vào Google Sheet         │
                │  - Trigger n8n webhook          │
                └──────┬─────────────┬───────────┘
                       │             │
          ┌────────────▼──┐   ┌──────▼─────────────┐
          │  Google Sheet │   │    n8n Workflow      │
          │  (Database)   │   │  - Nhận webhook      │
          │               │   │  - Tạo video (AI)    │
          └────────┬──────┘   │  - Đăng lên FB/TT   │
                   │          │  - Cập nhật Sheet    │
                   │          └──────────────────────┘
                   │
          ┌────────▼────────────────────────────────────────┐
          │              LUỒNG CRON HÀNG NGÀY               │
          │  - Crawl comments từ FB/TikTok                  │
          │  - Crawl trending data theo quốc gia            │
          │  - Multi-Agent: Biên kịch & Đạo diễn phân tích  │
          │  - Ghi vào Sheet với trạng thái "verify"        │
          └─────────────────────────────────────────────────┘
```

---

## 3. TECH STACK

### 3.1. Frontend

| Thành phần | Công nghệ | Lý do chọn |
|---|---|---|
| Framework | **Next.js 14** (App Router) | SSR/SSG, file-based routing, tối ưu SEO |
| Styling | **Tailwind CSS** + **shadcn/ui** | Nhanh, đồng bộ, component library chuyên nghiệp |
| State Management | **Zustand** | Nhẹ, đủ dùng cho app quy mô này |
| HTTP Client | **Axios** | Quen thuộc, interceptor dễ cấu hình |
| Charts (Dashboard) | **Recharts** | Tích hợp tốt với React |
| Form validation | **React Hook Form** + **Zod** | Type-safe, hiệu suất cao |

### 3.2. Backend

| Thành phần | Công nghệ | Lý do chọn |
|---|---|---|
| Framework | **FastAPI** (Python) | Async, OpenAPI tự động, tích hợp tốt với AI libs |
| LLM | **Google Gemini 1.5 Pro** (qua API) | Hỗ trợ tiếng Việt tốt, context window lớn, chi phí hợp lý |
| Google Search | **Serper API** (hoặc SerpAPI) | Cào kết quả Google hợp lệ theo từ khóa |
| Google Sheets | **gspread** (Python lib) | Đơn giản, đủ mạnh để đọc/ghi Sheet |
| Job Scheduling | **APScheduler** (Python) | Tích hợp cron job trực tiếp trong FastAPI |
| Authentication | **JWT** (PyJWT) | Stateless, phù hợp REST API |

### 3.3. Tạo video AI (Local Engine)

| Thành phần | Công nghệ | Ghi chú |
|---|---|---|
| Video Engine | **ViMax** (github.com/HKUDS/ViMax) | Multi-agent framework, chạy local bằng Python, dùng `uv` |
| Video Generation Model | **Google Veo API** (qua ViMax) | Rate limit: 2 req/min, 10 video/ngày |
| Image Generation | **Google Nanobanana API** (qua ViMax) | 10 req/min, 500/ngày |
| LLM (trong ViMax) | **Gemini 2.5 Flash** (qua OpenRouter) | 500 req/min, 2000/ngày |
| Input hỗ trợ | Text (idea, script, novel) + Ảnh (AutoCameo) | Ảnh dùng để giữ nhân vật nhất quán |

> **Lưu ý:** ViMax KHÔNG có REST API. Backend FastAPI sẽ bọc (wrap) ViMax pipeline thành service endpoint để gọi từ web.

### 3.4. Tự động hóa đăng bài (Scheduled Publishing)

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| Workflow Engine | **n8n** (self-hosted) | Scheduled publishing — KHÔNG dùng để tạo video |
| Trigger | Cron/Schedule trigger trong n8n | Đọc Google Sheet theo lịch, đăng bài đúng ngày giờ |
| Đăng Facebook | Facebook Graph API v19.0 (qua n8n node) | Upload video + caption lên Fanpage |
| Đăng TikTok | TikTok Content Posting API v2 (qua n8n node) | Upload video + caption lên TikTok |

> **Vai trò n8n đã thay đổi:** n8n KHÔNG còn orchestrate pipeline tạo video (vì ViMax không có node native trong n8n). n8n chỉ đảm nhận việc **đọc Google Sheet → upload video + đăng bài lên FB/TikTok theo đúng lịch đã plan**. Luồng: user tick chọn trên web → Sheet ghi lịch (video URL, caption, ngày giờ) → n8n cron trigger → upload & post.

### 3.5. Infrastructure

| Thành phần | Công nghệ |
|---|---|
| Hosting Backend | **Railway** hoặc **Render** (free tier dùng được) |
| Hosting Frontend | **Vercel** |
| n8n Hosting | **Railway** hoặc tự host trên VPS |
| Database | **Google Sheets** (MVP) → có thể migrate sang PostgreSQL sau |
| File Storage | **Cloudinary** (lưu ảnh user upload) |
| Crawl FB/TikTok | **Apify** (platform scraping hợp lệ) |

### 3.6. Đóng gói & Phân phối (Docker)

| Thành phần | Image/Container |
|---|---|
| Backend + ViMax | `auto-video-backend` — Python 3.12, FastAPI + ViMax pipeline, GPU optional |
| Frontend | `auto-video-frontend` — Node.js 20, Next.js 14 |
| n8n | `n8nio/n8n` (official image) |

**Lý do dùng Docker:**
- ViMax yêu cầu Python 3.12 + nhiều dependencies (`uv sync`) — container hóa đảm bảo môi trường nhất quán.
- Khách hàng/người dùng mới chỉ cần `docker compose up` là chạy toàn bộ hệ thống, không cần cài đặt thủ công.
- Dễ vận chuyển, demo, và triển khai trên bất kỳ máy nào có Docker.

**docker-compose.yml sẽ bao gồm:**
```yaml
services:
  backend:    # FastAPI + ViMax engine
  frontend:   # Next.js web UI
  n8n:        # Scheduled publishing workflow
```

> Người dùng chỉ cần cấu hình file `.env` (API keys) và chạy `docker compose up -d` là có toàn bộ hệ thống hoạt động.

---

## 4. LUỒNG HOẠT ĐỘNG CHI TIẾT

### 4.1. Luồng tạo video theo yêu cầu (Manual Flow)

```
[Người dùng] 
    │
    ├─ 1. Truy cập Web UI → Trang "Tạo Video"
    │
    ├─ 2. Điền form:
    │       - Loại video (giải trí / quảng cáo)
    │       - Kênh đăng (Facebook / TikTok)
    │       - Ngày đăng dự kiến
    │       - Nội dung (văn bản mô tả ý tưởng)
    │       - Style (chọn từ danh sách sẵn có)
    │       - Thời lượng
    │       - Hình ảnh đính kèm / Linh vật (AutoCameo) để giữ nhân vật cố định
    │       - [Chỉ cho giải trí] Tích "Thêm data từ Google" (tùy chọn)
    │       - Caption: tự nhập hoặc click "AI Gợi ý Caption" để LLM sinh caption
    │
    ├─ 3. Submit form → Backend nhận request
    │
    ├─ 4. Backend xử lý (Multi-Agent Pipeline via ViMax):
    │       - Upload ảnh lên Cloudinary → lấy URL
    │       - Nếu "Thêm data": gọi Serper API để tìm kiếm → tổng hợp nội dung
    │       - Gọi ViMax pipeline (Idea2Video / Script2Video):
    │           * ViMax Agent Biên Kịch: Viết kịch bản chi tiết
    │           * ViMax Agent Đạo Diễn: Dịch kịch bản thành Camera Prompts
    │           * ViMax AutoCameo: Giữ nhân vật nhất quán từ ảnh upload (nếu có)
    │           * ViMax Video Generator (Veo): Render video
    │       - Video output → upload lên storage → lấy video URL
    │       - Ghi vào Google Sheet: trạng thái = "pending", video_url, caption, scheduled_date
    │
    ├─ 5. n8n Scheduled Publishing:
    │       - Cron trigger đọc Google Sheet
    │       - Khi đến đúng ngày/giờ đã plan:
    │           * Upload video lên FB/TikTok
    │           * Đăng bài kèm caption đã lưu
    │       - Cập nhật Google Sheet: trạng thái = "done", post_id, post_url
    │
    └─ 6. Web UI polling trạng thái → hiển thị thông báo thành công
```

### 4.2. Luồng tự động hàng ngày (Cron Flow)

```
[Cron: 2:00 AM hàng ngày]
    │
    ├─ Bước A – Crawl Comments:
    │       - Gọi Apify Actor: Facebook Post Comments Scraper
    │       - Gọi Apify Actor: TikTok Comments Scraper
    │       - Lọc comment: loại bỏ spam, emoji-only, quảng cáo
    │       - Kết quả: danh sách comment thô
    │
    ├─ Bước B – Crawl Trending Data theo Quốc gia:
    │       (Chi tiết tại Mục 6)
    │       - Lấy trending hashtags từ TikTok theo khu vực
    │       - Lấy insight sở thích người xem theo quốc gia
    │       - Gọi Gemini để phân tích → lưu vào file JSON cache
    │
    ├─ Bước C – Đối chiếu nội dung:
    │       - Lấy toàn bộ video đã đăng từ Google Sheet (trạng thái = "done")
    │       - Lấy toàn bộ ý tưởng đang chờ (trạng thái = "verify")
    │       - Gọi Gemini: kiểm tra xem từng comment có nội dung
    │         trùng với video đã làm không (embedding similarity)
    │
    ├─ Bước D – Multi-Agent Tổng hợp & Gợi ý:
    │       - Với mỗi comment chưa được làm thành video:
    │           * Agent Biên Kịch: Đọc comment + trending data → Lên kịch bản (storyboard, thoại, text overlay).
    │           * Agent Đạo Diễn: Dịch kịch bản thành Camera Prompts + Style phù hợp.
    │           * Output gợi ý: tiêu đề video, mô tả nội dung, style, hook instruction.
    │
    └─ Bước E – Ghi vào Google Sheet:
            - Ghi mỗi ý tưởng vào Sheet: trạng thái = "verify"
            - Gửi notification cho người dùng (email/Telegram)
```

---

## 5. SCHEMA DỮ LIỆU

### 5.1. Google Sheet – Sheet "video_queue"

| Cột | Tên cột | Kiểu dữ liệu | Mô tả | Ví dụ |
|---|---|---|---|---|
| A | `id` | String (UUID) | ID duy nhất của row | `vid_20260529_001` |
| B | `created_at` | DateTime | Thời điểm tạo record | `2026-05-29 19:00:00` |
| C | `scheduled_date` | Date | Ngày dự kiến đăng | `2026-06-01` |
| D | `channel` | Enum | Kênh đăng | `facebook` / `tiktok` |
| E | `video_type` | Enum | Loại video | `entertainment` / `ads` |
| F | `duration` | Integer | Thời lượng (giây) | `30` / `60` / `90` |
| G | `raw_content` | String | Nội dung người dùng nhập hoặc comment gốc | `"Review bánh mì Hà Nội..."` |
| H | `style_id` | String | ID style đã chọn | `style_001` |
| I | `style_name` | String | Tên style | `"Energetic Trending"` |
| J | `extra_data` | String | Dữ liệu bổ sung từ Google Search (nếu có) | `"Theo VnExpress, doanh thu..."` |
| K | `country_hook` | String | Kiểu hook theo quốc gia | `"VN_STRONG_HOOK_5S"` |
| L | `final_prompt` | Text | Prompt hoàn chỉnh gửi sang n8n | *(xem Mục 5.3)* |
| M | `image_urls` | String (JSON array) | URL ảnh đính kèm | `["https://...","https://..."]` |
| N | `status` | Enum | Trạng thái | `verify` / `pending` / `processing` / `done` / `failed` |
| O | `video_url` | String | URL video sau khi đăng | `https://fb.com/...` |
| P | `post_id` | String | ID bài đăng trên nền tảng | `1234567890` |
| Q | `source` | Enum | Nguồn tạo | `manual` / `auto_suggest` |
| R | `caption` | Text | Caption/mô tả bài đăng kèm video (user tự nhập hoặc AI gợi ý) | `"Top 5 quán cà phê Đà Nẵng #cafe #danang"` |
| S | `error_log` | Text | Ghi log lỗi nếu có | `"Kling API timeout"` |
| T | `approved_by` | String | Người dùng đã approve (verify flow) | `user@email.com` |
| U | `approved_at` | DateTime | Thời điểm approve | `2026-05-29 20:00:00` |

### 5.2. Google Sheet – Sheet "styles"

| Cột | Tên cột | Mô tả | Ví dụ |
|---|---|---|---|
| A | `style_id` | ID duy nhất | `style_001` |
| B | `style_name` | Tên hiển thị | `Energetic Trending` |
| C | `video_type` | Áp dụng cho loại video nào | `entertainment` |
| D | `description` | Mô tả style | `Nhịp nhanh, màu sắc bão hòa, text lớn` |
| E | `prompt_template` | Template prompt cho style này | `"Tạo video với phong cách năng động, cắt cảnh mỗi 2-3 giây..."` |
| F | `thumbnail_preview` | URL ảnh preview style | `https://...` |
| G | `is_active` | Có đang được sử dụng không | `TRUE` / `FALSE` |

### 5.3. Google Sheet – Sheet "trending_data"

| Cột | Tên cột | Mô tả |
|---|---|---|
| A | `country_code` | Mã quốc gia ISO | `VN` / `US` / `TH` |
| B | `country_name` | Tên quốc gia | `Việt Nam` |
| C | `platform` | Nền tảng | `tiktok` / `facebook` |
| D | `hook_style` | Kiểu hook phù hợp | `STRONG_SHOCK_5S` |
| E | `hook_description` | Mô tả chi tiết kiểu hook | `"5 giây đầu cần có yếu tố giật gân, câu hỏi bất ngờ..."` |
| F | `avg_video_pacing` | Nhịp cắt cảnh trung bình | `fast` / `medium` / `slow` |
| G | `preferred_music_type` | Nhạc nền ưa thích | `trending_pop` / `lo-fi` |
| H | `trending_hashtags` | Top hashtags trending | `#xahoi #viral #trending` |
| I | `content_preferences` | Chủ đề nội dung được xem nhiều | `comedy,food,lifestyle,review` |
| J | `last_updated` | Lần cập nhật cuối | `2026-05-29` |

### 5.4. Payload ghi vào Google Sheet (từ Backend sau khi ViMax render xong)

```json
{
  "id": "vid_20260529_001",
  "channel": "tiktok",
  "video_type": "entertainment",
  "duration": 60,
  "final_prompt": "Tạo video TikTok thời lượng 60 giây, phong cách Energetic Trending...",
  "style": {
    "id": "style_001",
    "name": "Energetic Trending"
  },
  "country_hook": {
    "code": "VN_STRONG_HOOK_5S",
    "instruction": "5 giây đầu phải có yếu tố gây shock hoặc câu hỏi kích thích tò mò"
  },
  "image_urls": [
    "https://res.cloudinary.com/xxx/image/upload/abc.jpg"
  ],
  "video_url": "https://storage.example.com/videos/vid_20260529_001.mp4",
  "caption": "Top 5 quán cà phê Đà Nẵng bạn phải thử! ☕ #cafe #danang #review",
  "scheduled_date": "2026-06-01",
  "scheduled_time": "18:00",
  "page_id": "YOUR_FACEBOOK_PAGE_ID",
  "tiktok_account_id": "YOUR_TIKTOK_ACCOUNT_ID",
  "status": "pending"
}
```

---

## 6. CƠ CHẾ PHÂN TÍCH THỊ HIẾU THEO QUỐC GIA (HYBRID APPROACH)

### 6.1. Mục tiêu
Tối ưu hóa nội dung, nhịp điệu (pacing), và phần mở đầu (hook) của kịch bản video sao cho phù hợp với văn hóa và sở thích người xem ở từng quốc gia mục tiêu. Để đảm bảo tính khả thi và ổn định cao cho Hackathon, hệ thống sử dụng mô hình kết hợp (Hybrid) 2 lớp dữ liệu.

### 6.2. Mô hình dữ liệu 2 lớp

**Lớp 1: Baseline Country Profiles (Dữ liệu tĩnh - Core Knowledge)**
- **Mô tả:** Sử dụng khối kiến thức khổng lồ về văn hóa/marketing của các mô hình LLM (Gemini 1.5 Pro) để sinh sẵn một file `country_profiles.json` chứa đặc tính cốt lõi của ~10 quốc gia.
- **Dữ liệu bao gồm:** Kiểu Hook ưa thích, nhịp cắt cảnh, màu sắc chủ đạo, loại nhạc nền.
- **Ưu điểm:** Đảm bảo độ trễ (latency) bằng 0, không bao giờ bị lỗi kết nối, tiết kiệm chi phí API.

**Lớp 2: Live Trending Data (Dữ liệu động - Real-time Trends)**
- **Mô tả:** Thu thập các từ khóa và hashtag đang nóng nhất trong 24h qua tại quốc gia đó để cung cấp chất liệu xu hướng cho Biên kịch AI.
- **Nguồn lấy dữ liệu:**
  - **Pytrends (Python):** Lấy Top Google Searches hằng ngày (Miễn phí, dễ triển khai bằng vài dòng code).
  - **Apify TikTok Scraper:** (Tùy chọn) Lấy Top Hashtags theo khu vực qua API.
- **Mục đích:** Giúp kịch bản không chỉ chuẩn văn hóa mà còn bắt kịp trend mới nhất.

### 6.3. Quy trình tích hợp vào Prompt

```text
[Lấy Baseline Profile từ JSON] ──┐
                                 │
[Lấy Top Keywords từ Pytrends] ──┼──► [Gộp thành System Prompt] ──► [Agent Biên Kịch (Gemini)]
                                 │
[Nội dung ý tưởng gốc/Comment] ──┘
```

### 6.4. Ví dụ Dữ liệu Tĩnh (Country Profile - Việt Nam)

```json
{
  "country_code": "VN",
  "country_name": "Việt Nam",
  "hook_style": "Giật gân, câu hỏi tò mò trong 3s đầu, drama",
  "pacing": "Nhanh, cắt cảnh liên tục (fast-paced)",
  "visual_vibe": "Màu sắc nổi bật, text to giữa màn hình",
  "preferred_music": "Trending TikTok, VinaHouse remix",
  "description": "Người xem dễ mất kiên nhẫn. Thích giải trí, review thực tế."
}
```

### 6.5. Áp dụng thực tế
Khi Agent Biên kịch nhận được lệnh tạo video về "Cà phê sáng" tại thị trường "VN", nó sẽ đọc profile trên và tự động thiết kế kịch bản:
- Mở đầu bằng 1 câu hỏi gây tò mò (Hook).
- Lồng ghép từ khóa đang hot từ Pytrends vào kịch bản.
- Ghi chú cho Đạo diễn: "Text to chớp nhoáng giữa màn hình, nhạc VinaHouse".

---

## 7. CƠ CHẾ TỰ ĐỘNG ĐỀ XUẤT NỘI DUNG

### 7.1. Lịch chạy

- **Thời gian:** 2:00 AM hàng ngày (giờ Việt Nam, UTC+7)
- **Công nghệ:** APScheduler trong FastAPI backend
- **Thời gian chạy ước tính:** 10–20 phút mỗi lần

### 7.2. Chi tiết từng bước

**Bước 1 – Crawl Comments**
- Gọi Apify Actor `apify/facebook-comments-scraper` với Page ID đã khai báo
- Gọi Apify Actor `apify/tiktok-comment-scraper` với TikTok account đã khai báo
- Giới hạn: lấy tối đa 200 comment mới nhất mỗi kênh, trong 7 ngày qua
- Lọc: bỏ comment dưới 10 ký tự, comment chỉ có emoji, comment chứa link spam

**Bước 2 – Crawl Trending Data**
- Gọi TikTok Research API lấy trending hashtags theo `region=VN`
- Gọi Pytrends lấy top 10 từ khóa tìm kiếm trong 7 ngày qua tại Việt Nam
- Gọi Gemini để tổng hợp → cập nhật Sheet "trending_data"

**Bước 3 – Deduplication (Chống trùng lặp)**
- Lấy toàn bộ nội dung video đã đăng từ Sheet (status = "done")
- Lấy toàn bộ ý tưởng đang chờ duyệt (status = "verify")
- Dùng Gemini để so sánh từng comment với danh sách nội dung đã có:
  - Nếu tương đồng > 80% → bỏ qua
  - Nếu tương đồng ≤ 80% → tiếp tục sang Bước 4

**Bước 4 – Sinh ý tưởng**

Gemini nhận input:
```
- Comment gốc: [nội dung comment]
- Country profile: [JSON profile của quốc gia/kênh]
- Danh sách style khả dụng: [list styles từ Sheet "styles"]
- Video đã đăng gần đây: [5 video gần nhất]
```

Gemini trả về:
```json
{
  "suggested_title": "Tên gợi ý cho video",
  "content_outline": "Mô tả 3-5 câu về nội dung video",
  "recommended_style_id": "style_002",
  "hook_instruction": "Mở đầu bằng câu hỏi: Bạn có biết...",
  "estimated_duration": 60,
  "reasoning": "Comment hỏi về X, chủ đề này chưa có video, trending tại VN"
}
```

**Bước 5 – Ghi vào Google Sheet**
- Ghi record mới vào Sheet "video_queue" với status = `verify`
- Source = `auto_suggest`
- Gửi email/Telegram notification cho người dùng

### 7.3. Luồng Verify (Kiểm duyệt)

Người dùng vào trang Verify trên Web UI:
- Xem danh sách các ý tưởng với status = `verify`
- Mỗi ý tưởng hiển thị: nội dung, style gợi ý, hook instruction, lý do đề xuất
- Hành động:
  - **✅ Approve:** Chuyển status → `pending`, hệ thống tự động trigger n8n
  - **✏️ Edit & Approve:** Chỉnh sửa nội dung trước khi approve
  - **❌ Reject:** Xóa record hoặc đánh dấu `rejected`

---

## 8. MODULE WEB UI – CHI TIẾT MÀN HÌNH

### 8.1. Trang "Tạo Video" (/create)

**Layout:** Single-page form với thanh tiến trình (Step 1 → Step 2 → Step 3)

**Step 1 – Cấu hình cơ bản:**
- Radio button: Loại video (Giải trí / Quảng cáo)
- Radio button: Kênh đăng (Facebook / TikTok)
- Date picker: Ngày đăng dự kiến
- Dropdown: Thời lượng (các lựa chọn phụ thuộc vào loại video đã chọn ở trên)

**Step 2 – Nội dung:**
- Textarea: "Nhập ý tưởng / nội dung video của bạn"
- Toggle: "Tự động bổ sung data từ Google" *(chỉ hiện với video giải trí)*
  - Nếu bật: hiện thêm input "Từ khóa tìm kiếm" (tự động gợi ý từ nội dung đã nhập)
- Upload zone: Tải hình ảnh đính kèm (tối đa 5 ảnh, mỗi ảnh ≤ 10MB, định dạng JPG/PNG/WEBP)

**Step 3 – Style:**
- Grid card 2-3 cột: Hiển thị các style với thumbnail preview
- Mỗi card hiển thị: Tên style, mô tả ngắn, loại video phù hợp
- Chỉ hiển thị style phù hợp với loại video đã chọn ở Step 1

**Step 4 – Caption (Mô tả bài đăng):**
- Textarea: "Nhập caption cho bài đăng" (mô tả kèm video khi đăng lên FB/TikTok)
- Nút **"AI Gợi ý Caption"**: Gọi LLM tự động sinh caption dựa trên nội dung video, style, và platform đã chọn
  - Khi click: hiển thị 2-3 gợi ý caption → user chọn 1 hoặc chỉnh sửa
  - Caption được tối ưu theo platform (FB dài hơn, TikTok ngắn + hashtags)
- User có thể tự điền hoặc dùng gợi ý AI, hoặc kết hợp cả hai
- Hiển thị character count + giới hạn theo platform (FB: 63.206 ký tự, TikTok: 2.200 ký tự)

**Sau khi submit:**
- Hiển thị màn hình "Đang xử lý..." với progress indicator
- Polling API mỗi 5 giây để kiểm tra trạng thái
- Khi done: Hiển thị link video, thumbnail, và thống kê nhanh

### 8.2. Trang "Kiểm duyệt Ý tưởng" (/verify)

- Bảng danh sách ý tưởng đang chờ duyệt (status = verify)
- Mỗi row có thể expand để xem chi tiết: hook instruction, reasoning của AI, style gợi ý
- Nút hành động: Approve / Edit & Approve / Reject
- Badge số lượng ý tưởng đang chờ trên menu

### 8.3. Trang Dashboard (/dashboard)

*(Chi tiết tại Mục 9)*

---

## 9. MODULE DASHBOARD – CHI TIẾT MÀN HÌNH

### 9.1. Layout tổng quan

```
┌──────────────────────────────────────────────────────┐
│  [Tab: Facebook Page A]  [Tab: TikTok Channel B]  +  │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [KPI Card: Tổng Video]  [KPI Card: Followers]       │
│  [KPI Card: Avg. Views]  [KPI Card: Tổng Revenue]    │
│                                                      │
│  [Biểu đồ Line: Lượt xem theo ngày – 30 ngày qua]   │
│                                                      │
│  [Bảng: Danh sách video gần đây]                     │
│  Cột: Thumbnail | Tiêu đề | Ngày đăng | Views |      │
│        Likes | Comments | Trạng thái | Actions       │
└──────────────────────────────────────────────────────┘
```

### 9.2. KPI Cards

| Card | Dữ liệu | Nguồn |
|---|---|---|
| Tổng số video | Đếm record status=done | Google Sheet |
| Tổng lượt xem | Gọi FB/TikTok API lấy view count | FB Graph API / TikTok API |
| Số người theo dõi | Gọi FB/TikTok API | FB Graph API / TikTok API |
| Video pending | Đếm record status=pending | Google Sheet |
| Video cần duyệt | Đếm record status=verify | Google Sheet |

### 9.3. Chi tiết từng video

Khi click vào một video trong bảng:
- Modal/trang chi tiết hiển thị:
  - Thumbnail + player (embed)
  - Prompt đã dùng để tạo video
  - Style đã chọn
  - Thống kê: Views, Likes, Comments, Shares, Retention rate
  - Biểu đồ: Lượt xem theo giờ trong ngày đăng

---

## 10. LUỒNG N8N – SCHEDULED PUBLISHING

### Workflow: "Scheduled Post to Social Media"

```
[Schedule Trigger] (Cron: mỗi 15 phút kiểm tra Sheet)
    │
    ├─ Node: "Read Google Sheet" (Google Sheets node)
    │       Đọc tab "video_queue", lọc các row có:
    │       - status = "pending"
    │       - scheduled_date <= ngày giờ hiện tại
    │       - video_url != empty
    │
    ├─ Node: "Filter Ready Posts" (Filter node)
    │       Chỉ giữ lại các row đã đủ điều kiện đăng
    │       (có video_url, có caption, đúng lịch)
    │
    ├─ Node: "Route by Channel" (Switch node)
    │       Nếu channel = "facebook" → Branch Facebook
    │       Nếu channel = "tiktok"   → Branch TikTok
    │
    ├─ [Branch Facebook]
    │       Node: "Upload Video to Facebook" (HTTP Request / FB node)
    │       POST https://graph.facebook.com/v19.0/{page_id}/videos
    │       Params: { file_url: video_url, description: caption }
    │
    ├─ [Branch TikTok]
    │       Node: "Upload Video to TikTok" (HTTP Request / TikTok node)
    │       POST https://open.tiktokapis.com/v2/post/publish/video/init/
    │       Params: { video_url, title: caption, privacy_level }
    │
    ├─ Node: "Update Google Sheet" (Google Sheets node)
    │       Cập nhật row:
    │       status = "done", post_id = [ID bài đăng], post_url = [URL bài đăng]
    │
    └─ Node: "Callback to Backend" (HTTP Request)
            POST {callback_url}
            Body: { sheet_id, status: "done", post_url, post_id }
```

> **Lưu ý:** n8n KHÔNG tạo video. Video đã được render bởi ViMax (local) và URL đã lưu sẵn trong Sheet. n8n chỉ đọc Sheet theo schedule và upload + đăng bài khi đến đúng thời điểm.

---

## 11. API ENDPOINTS

### Backend FastAPI

**Base URL:** `https://your-api.com/api/v1`

#### Video Management

| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/video/create` | Tạo video mới (manual) |
| `GET` | `/video/list` | Lấy danh sách tất cả video |
| `GET` | `/video/{id}` | Lấy chi tiết một video |
| `GET` | `/video/status/{id}` | Kiểm tra trạng thái video |
| `POST` | `/video/callback` | Nhận callback từ n8n sau khi đăng xong |
| `DELETE` | `/video/{id}` | Xóa một video record |

#### Caption

| Method | Endpoint | Mô tả |
|---|---|---|
| `POST` | `/caption/generate` | AI sinh caption dựa trên nội dung, style, platform. Trả về 2-3 gợi ý |

#### Verify Flow

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/verify/list` | Lấy danh sách ý tưởng cần duyệt |
| `POST` | `/verify/{id}/approve` | Approve ý tưởng → chuyển sang pending |
| `POST` | `/verify/{id}/reject` | Reject ý tưởng |
| `PUT` | `/verify/{id}/edit` | Chỉnh sửa nội dung trước khi approve |

#### Styles

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/styles` | Lấy danh sách style |
| `POST` | `/styles` | Thêm style mới |
| `PUT` | `/styles/{id}` | Cập nhật style |
| `DELETE` | `/styles/{id}` | Xóa style |

#### Dashboard Data

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/dashboard/kpi` | Lấy KPI tổng quan |
| `GET` | `/dashboard/channels` | Danh sách kênh đang quản lý |
| `GET` | `/dashboard/chart/views` | Dữ liệu biểu đồ lượt xem |

#### Trending Data

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/trending/{country_code}` | Lấy profile xu hướng theo quốc gia |
| `POST` | `/trending/refresh` | Trigger refresh trending data thủ công |

---

## 12. CẤU HÌNH & TRIỂN KHAI (SETUP GUIDE)

### 12.1. Yêu cầu trước khi cài đặt

- [ ] Node.js 20+ và Python 3.11+
- [ ] Tài khoản Google Cloud (để dùng Sheets API + Gemini API)
- [ ] Tài khoản n8n (self-hosted hoặc cloud)
- [ ] Tài khoản Facebook Developer + Page ID + Access Token
- [ ] Tài khoản TikTok for Developers + Content Posting API access
- [ ] Tài khoản Kling AI (hoặc RunwayML) + API key
- [ ] Tài khoản Apify + API key
- [ ] Tài khoản Cloudinary + API key
- [ ] Tài khoản Serper API + API key (nếu dùng tính năng "Thêm data từ Google")

### 12.2. Biến môi trường (.env)

```env
# Gemini (Backend LLM)
GEMINI_API_KEY=your_gemini_api_key

# ViMax (Video Engine)
OPENROUTER_API_KEY=your_openrouter_api_key
GOOGLE_AI_STUDIO_API_KEY=your_google_ai_studio_key

# Google Sheets
GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service_account.json
GOOGLE_SHEET_ID=your_google_sheet_id

# Facebook
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_ACCESS_TOKEN=your_long_lived_page_token

# TikTok
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_ACCESS_TOKEN=your_access_token

# Apify
APIFY_API_TOKEN=your_apify_token
APIFY_FB_ACTOR_ID=apify/facebook-comments-scraper
APIFY_TIKTOK_ACTOR_ID=apify/tiktok-comment-scraper

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Serper (Google Search)
SERPER_API_KEY=your_serper_api_key

# n8n
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/scheduled-post
N8N_API_KEY=your_n8n_api_key

# JWT
JWT_SECRET_KEY=your_very_long_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440

# App
APP_ENV=production
APP_HOST=0.0.0.0
APP_PORT=8000
TARGET_COUNTRY=VN
```

### 12.3. Các bước triển khai

```bash
# 1. Clone repo
git clone https://github.com/your-org/auto-video-platform.git
cd auto-video-platform

# 2. Cài đặt Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Điền các biến môi trường vào .env
uvicorn main:app --host 0.0.0.0 --port 8000

# 3. Cài đặt Frontend
cd ../frontend
npm install
cp .env.local.example .env.local
# Điền NEXT_PUBLIC_API_URL=https://your-api.com
npm run dev

# 4. Cài đặt n8n
# Import file workflow từ: /n8n/auto_video_workflow.json
# Cấu hình credentials trong n8n UI

# 5. Tạo Google Sheet từ template
# Truy cập link template: [Template URL]
# File → Make a copy → Đổi tên và lưu vào Drive của bạn
# Chia sẻ Sheet với Service Account email của bạn (Editor)
```

### 12.4. Google Sheet Template

Cấu trúc Google Sheet gồm 3 tab:
1. **video_queue** – Hàng đợi và lịch sử video
2. **styles** – Danh mục phong cách video
3. **trending_data** – Dữ liệu thị hiếu theo quốc gia

---

## 13. GIỚI HẠN & HẠN MỨC

| Hạng mục | Giới hạn | Ghi chú |
|---|---|---|
| Video tạo/ngày | 10 video | Chặn cứng từ Google Veo API (2 req/min, 10/ngày) |
| Dung lượng ảnh upload | 10MB/ảnh, 5 ảnh/lần | Cloudinary free tier |
| Thời gian render video | Tùy thuộc ViMax pipeline | Ước tính 5–15 phút/video |
| Comment crawl/ngày | 200 comment/kênh | Apify limit |
| Số kênh quản lý | Không giới hạn | Phụ thuộc số tài khoản FB/TikTok |
| Gemini API calls/phút | 60 requests | Gemini 1.5 Pro free tier (Backend) |
| OpenRouter (ViMax LLM) | 500 req/min, 2000/ngày | Gemini 2.5 Flash qua OpenRouter |
| Image gen (ViMax) | 10 req/min, 500/ngày | Google Nanobanana API |
| Google Sheets rows | ~50.000 rows | Thực tế dùng được nhiều năm |

### Chi phí ước tính (hàng tháng, cho 1 kênh)

| Dịch vụ | Gói | Chi phí ước tính |
|---|---|---|
| Gemini API (Backend) | Pay-per-use | ~$5–15 |
| OpenRouter (ViMax LLM) | Pay-per-use | ~$5–10 |
| Google AI Studio (Veo + Image) | Free tier / Pay-per-use | $0–20 |
| Apify | Starter | ~$49 |
| Serper API | 2,500 queries | ~$50 |
| Cloudinary | Free tier | $0 |
| Railway (hosting) | Developer | ~$5 |
| **Tổng** | | **~$114–149/tháng** |

---

## 14. RỦI RO & KẾ HOẠCH DỰ PHÒNG

| Rủi ro | Mức độ | Kế hoạch dự phòng |
|---|---|---|
| Google Veo API rate limit (10 video/ngày) | Cao | Lên lịch render trải đều trong ngày, ưu tiên video đã approve |
| Facebook API đổi chính sách | Trung bình | Theo dõi changelog Meta, cập nhật kịp thời |
| TikTok ban tài khoản auto-post | Cao | Rate limit 3 video/ngày, dùng scheduled post API chính thức |
| Google Sheets đạt giới hạn | Thấp | Migration script sang PostgreSQL |
| Apify scraper bị block | Trung bình | Rotate proxy, backup sang Bright Data |
| Nội dung AI vi phạm policy | Trung bình | Content moderation layer trước khi đăng |
| Gemini API downtime | Thấp | Fallback sang OpenAI GPT-4o |
| ViMax pipeline lỗi / timeout | Trung bình | Retry 2 lần, log error, thông báo user qua web UI |

---

## 15. TÍNH NĂNG PHÁT TRIỂN SAU (PHASE 2)

Dưới đây là các tính năng mở rộng sẽ được bổ sung sau khi hoàn thiện MVP (1 tuần Hackathon):

- **Kiểm duyệt chất lượng bằng thị giác (VLM Quality Control):** 
  Sau khi Kling AI render xong video, hệ thống (n8n) sẽ trích xuất 1 frame (thumbnail) và gửi ngược lại cho Gemini 1.5 Pro (Vision). Gemini đóng vai trò là "Agent Kiểm Duyệt" để đánh giá xem hình ảnh có bị lỗi, chữ bị méo, hay màu sắc sai lệch không. Nếu Pass mới cho phép đăng, nếu Fail thì tự động retry hoặc gửi thông báo.

---

*Tài liệu này được tạo ngày 2026-05-29. Phiên bản tiếp theo sẽ bổ sung: ERD diagram, Sequence diagram chi tiết, và Test plan.*
