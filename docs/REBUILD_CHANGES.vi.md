# Tổng kết thay đổi sau rebuild BX-T1 Content Factory

Tài liệu này ghi lại những gì đã thay đổi so với thời điểm đầu tiên đọc project. Phạm vi hoàn thành là toàn bộ phần có thể triển khai và kiểm chứng trong repo local, ngoại trừ tích hợp thật Seedance/Seed2 BytePlus theo yêu cầu loại trừ.

## 1. Trạng thái ban đầu

Project ban đầu là một nền tảng tạo video tự động theo luồng tương đối tuyến tính:

- Frontend Next.js có các trang create, dashboard, history, verify, schedule, settings nhưng chủ yếu phục vụ luồng tạo/render video đơn.
- Backend FastAPI có router video, verify, dashboard, trending, caption, research.
- Pipeline agent cũ chủ yếu gồm scriptwriter/director, chưa có orchestrator đa agent rõ ràng.
- Chưa có brief schema chuẩn giữa frontend và backend cho brand kit, audience, platform, constraints.
- Chưa có factory endpoint trả nhiều biến thể A/B từ cùng một brief.
- Chưa có QA rubric/publishable gate cho từng variant.
- Chưa có trace agent để UI quan sát DAG orchestration.
- Chưa có workflow TRAE và sample briefs đúng format content factory.
- Chưa có demo bắt buộc “one input change” để chứng minh output thay đổi theo audience.

## 2. Kiến trúc mới sau rebuild

Project đã được chuyển từ “single video render wrapper” sang “Content Factory”:

- Một brief đầu vào sinh ra ít nhất 2 variant A/B.
- Pipeline gồm nhiều agent: planner, brand steward, copywriter, director, visualist, renderer, voice, subtitler, editor, QA, packer.
- Backend có factory orchestrator riêng, chạy theo crew variant.
- Mỗi variant có script, storyboard, prompt pack, QA score, caption/title/hashtag và trạng thái publishable.
- Kết quả được ghi thành pack để frontend review, dashboard, history và schedule dùng lại.
- Có trace agent phục vụ live DAG và audit pipeline.

## 3. Backend đã thay đổi

### Factory router

Thêm `backend/routers/factory.py` với các endpoint:

- `POST /api/v1/factory/generate`: nhận brief, chạy factory, trả pack A/B.
- `GET /api/v1/factory/trace`: trả trace agent gần nhất.
- `GET /api/v1/factory/last-pack`: đọc pack gần nhất từ `outputs/last_factory_pack.json`.
- `GET /api/v1/factory/samples`: đọc các sample brief trong `briefs/`.
- `POST /api/v1/factory/demo-one-input-change`: chạy demo đổi audience và ghi artifact.
- `POST /api/v1/factory/schedule-handoff`: tạo payload bàn giao schedule/n8n từ variant đã chọn.

### Orchestrator đa agent

Thêm cụm `backend/services/orchestrator/`:

- `factory.py`: pipeline chính cho Content Factory.
- `smoke_test.py`: kiểm tra end-to-end với sample brief.
- `demo_briefs.py`: chạy nhiều sample brief và ghi `outputs/demo_briefs.json`.

Orchestrator hiện xử lý:

- planner + brand steward dùng chung cho toàn brief.
- copywriter/director/visualist/packer theo từng variant.
- trace từng agent.
- QA gate publishable.
- retry nhẹ nếu QA fail.
- output `publishable_variants`.
- ghi thời gian chạy `wall_s`.

### Agents mới

Thêm/cập nhật các agent trong `backend/services/agents/`:

- `planner.py`: tạo hướng sáng tạo A/B.
- `brand_steward.py`: khóa brand rules, palette, font, claims.
- `copywriter.py`: tạo hook/script/CTA.
- `director.py`: tạo storyboard/shot list.
- `visualist.py`: tinh chỉnh prompt visual.
- `packer.py`: tạo title/caption/hashtag/schedule hint.
- `pipeline.py`: giữ compatibility cho luồng cũ và nối sang factory.

### Model gateway

Thêm `backend/model_gateway/`:

- Cho phép route backend model theo `MODEL_BACKEND`.
- Có smoke test đảm bảo fallback rõ ràng.
- Hiện vẫn dùng legacy/mock/local fallback vì BytePlus thật đã được loại trừ khỏi scope.

### Brand kit, QA, subtitles, voice, edit

Thêm các module phục vụ publishable layer:

- `backend/services/brand_kit/`: kiểm tra/áp dụng brand constraints.
- `backend/services/qa/`: rubric QA và publishability score.
- `backend/services/subtitles/`: tạo SRT/burn subtitle compatibility.
- `backend/services/voice/`: TTS adapter/mock fallback.
- `backend/services/edit/`: concat, subtitle burn, logo overlay, color grade, export aspect.

### Scheduler

Cập nhật `backend/services/scheduler.py`:

- Không còn chỉ gợi ý video cũ.
- Chạy factory với trending/local data.
- Tạo record verify-ready từ output factory.

### Compatibility với luồng cũ

Giữ tương thích để project không vỡ:

- `backend/routers/video.py` vẫn tồn tại cho các luồng cũ/schedule cũ.
- `backend/services/agents/pipeline.py` vẫn hỗ trợ `run_full_pipeline`.
- Các route cũ vẫn import được.

## 4. Frontend đã thay đổi

### Trang create `/`

`frontend/app/page.tsx` dùng `FactoryWizard` thay cho wizard cũ:

- Nhập brief theo schema mới.
- Nhập brand kit, audience, platform, constraints.
- Chọn 1/2 variants.
- Gọi `/factory/generate`.
- Hiển thị trace/DAG và variant output.

### Factory wizard

Thêm `frontend/components/factory-wizard.tsx`:

- Form theo schema Content Factory.
- Tạo pack A/B.
- Hiển thị plan, brand lock, variants, QA.
- Hỗ trợ xem output pack ngay sau khi generate.

### Trang verify `/verify`

Cập nhật `frontend/app/verify/page.tsx`:

- Đọc `last_factory_pack`.
- So sánh variant side-by-side.
- Hiển thị QA score, hook, CTA, caption.
- Có hành động approve local cho editor review.

### Trang dashboard `/dashboard`

Viết lại `frontend/app/dashboard/page.tsx`:

- Hiển thị số variants.
- Hiển thị publishable variants.
- Hiển thị pass rate và average QA.
- Hiển thị wall time.
- Hiển thị trace agent.

### Trang history `/history`

Viết lại `frontend/app/history/page.tsx`:

- Đọc sample briefs.
- Có demo “Run one-input-change”.
- Chạy cùng brief nhưng đổi audience sang millennial mom.
- So sánh before/after theo variant, hook và QA.

### Trang schedule `/schedule`

Viết lại `frontend/app/schedule/page.tsx`:

- Không còn tập trung upload video thủ công.
- Chọn variant đã publishable từ last pack.
- Chọn platform, ngày, giờ, caption.
- Gọi `/factory/schedule-handoff`.
- Ghi payload ra `outputs/schedule_handoff.json`.
- Gửi n8n nếu có `N8N_WEBHOOK_URL` thật.

### Trang settings `/settings`

Viết lại `frontend/app/settings/page.tsx`:

- Editor brand name.
- Tone of voice.
- Palette.
- Fonts.
- Voice ID.
- Claims allowed/forbidden.
- Lưu localStorage để phục vụ cấu hình demo.

### API/types frontend

Cập nhật:

- `frontend/lib/types.ts`: thêm `FactoryBrief`, `FactoryResult`, `FactoryVariantPack`.
- `frontend/lib/api.ts`: thêm các hàm factory generate, trace, last-pack, samples, demo, schedule handoff.
- `frontend/app/api/caption/route.ts`: sửa import lỗi và giữ mock caption route hoạt động.

## 5. TRAE workflow và tài liệu

Thêm/cập nhật deliverables:

- `trae/workflows/content-factory.trae.json`: mô tả DAG agent theo Content Factory.
- `trae/workflows/schemas/brief.schema.json`: schema brief cho workflow.
- `trae/workflows/schemas/variant.schema.json`: schema variant output.
- `docs/WORKFLOW.md`: tài liệu workflow 1 trang.
- `docs/ARCHITECTURE.md`: mô tả kiến trúc.
- `BX-T1_REBUILD_RECOMMENDATION.vi.md`: tài liệu recommendation tiếng Việt.

## 6. Sample briefs và artifacts

Thêm sample briefs trong `briefs/`:

- `coffee-genz.json`
- `coffee-millennial-mom.json`
- `skincare-ab.json`
- `clinic-services.json`

Artifacts đã sinh trong `outputs/`:

- `last_factory_pack.json`: pack gần nhất từ factory generate.
- `demo_briefs.json`: kết quả chạy demo nhiều brief.
- `one_input_change_demo.json`: kết quả demo đổi một input.
- `schedule_handoff.json`: payload bàn giao schedule/n8n.
- `.gitkeep`: giữ thư mục outputs trong repo.

## 7. Những gì đã kiểm chứng

Các lệnh đã chạy thành công:

```bash
python -c "import main; print('main import ok')"
python -m services.orchestrator.smoke_test
python -m model_gateway.smoke_test
python services/orchestrator/demo_briefs.py
npm run build
npx tsc --noEmit
```

Ngoài ra đã kiểm tra trực tiếp:

- Factory generate tạo được 2 variants.
- Demo one-input-change chạy được và ghi artifact.
- Schedule handoff tạo được payload và ghi artifact.

## 8. Những phần cố ý chưa làm

Các phần sau chưa được triển khai thật vì nằm ngoài scope bạn yêu cầu hoặc cần credential/runtime bên ngoài:

- Seedance/Seed2 BytePlus thật.
- Gọi n8n thật nếu chưa cấu hình `N8N_WEBHOOK_URL`.
- Render video thật bằng provider trả clip thật nếu chưa có key/quota.
- TRAE CLI thật `trae run ...` nếu môi trường chưa cài TRAE CLI.
- Video demo quay màn hình/narration để nộp bài.

## 9. Kết luận

So với lúc đầu, project hiện đã có khung Content Factory đầy đủ:

- Có brief schema chuẩn.
- Có orchestrator đa agent.
- Có A/B variants.
- Có brand lock.
- Có QA gate.
- Có trace/DAG visibility.
- Có frontend control plane cho create, verify, dashboard, history, schedule, settings.
- Có sample briefs và output artifacts.
- Có workflow TRAE và tài liệu clone/run.

Phần còn lại duy nhất để chạy production thật là cắm credential/provider thật cho BytePlus, n8n và các dịch vụ render/voice nếu muốn thay mock/fallback.
