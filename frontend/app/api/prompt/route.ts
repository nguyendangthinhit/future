import { NextRequest, NextResponse } from "next/server";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface PromptBody {
  content: string;
  videoType: "entertainment" | "ads" | null;
  duration: number | string | null;
  styleId: string | null;
  styleName?: string;
  useGoogleData: boolean;
  searchKeyword: string;
  hasImages: boolean;
}

// Duration tới từ form có thể là dạng "30-40" (range) -> lấy số đầu làm giây.
function parseDuration(d: number | string | null): number {
  if (typeof d === "number") return d;
  if (typeof d === "string") {
    const first = parseInt(d.split("-")[0], 10);
    if (!Number.isNaN(first)) return first;
  }
  return 60;
}

export async function POST(req: NextRequest) {
  const body = (await req.json()) as PromptBody;

  try {
    const res = await fetch(`${BACKEND_URL}/video/preview-prompt`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: body.content,
        video_type: body.videoType ?? "entertainment",
        style_name: body.styleName ?? "",
        duration: parseDuration(body.duration),
        country_code: "VN",
        use_google_data: body.useGoogleData,
        search_keyword: body.searchKeyword,
      }),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json({
        prompt: data.prompt ?? "",
        script: data.script,
        director_output: data.director_output,
        source: data.source ?? "gemini",
      });
    }
    // Backend trả lỗi -> rơi xuống mock cho luồng UI không vỡ.
  } catch {
    // Backend không chạy -> fallback mock.
  }

  return NextResponse.json({ prompt: mockPrompt(body), source: "mock" });
}

function mockPrompt(b: PromptBody): string {
  const kind = b.videoType === "ads" ? "quảng cáo" : "giải trí";
  const cameo = b.hasImages
    ? "\n- AutoCameo: giữ nhân vật/linh vật nhất quán xuyên suốt từ ảnh đính kèm."
    : "";
  const extra = b.useGoogleData
    ? `\n- Lồng ghép thông tin & trend mới nhất về "${b.searchKeyword || b.content}".`
    : "";
  return `Tạo video ${kind} thời lượng ${parseDuration(b.duration)} giây.

Ý tưởng gốc: ${b.content}

Chỉ đạo sản xuất (MarkX):
- Hook 3 giây đầu gây tò mò, giữ chân người xem.
- Nhịp cắt cảnh nhanh, bám theo phong cách đã chọn.
- Text overlay ngắn gọn, nổi bật ở các điểm nhấn.${cameo}${extra}

Camera: kết hợp pan/zoom mượt, ánh sáng phù hợp tông thương hiệu.`;
}
