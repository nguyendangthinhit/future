import { NextRequest, NextResponse } from "next/server";
import { readApiConfig, hasActiveKey } from "@/lib/api-config";

interface PromptBody {
  content: string;
  videoType: "entertainment" | "ads" | null;
  duration: number | null;
  styleId: string | null;
  useGoogleData: boolean;
  searchKeyword: string;
  hasImages: boolean;
}

export async function POST(req: NextRequest) {
  const body = (await req.json()) as PromptBody;
  const cfg = readApiConfig();

  if (!hasActiveKey(cfg)) {
    return NextResponse.json({ prompt: mockPrompt(body), source: "mock" });
  }

  // TODO: cắm gọi Gemini/LightningAI thật ở đây khi đã có key.
  // Hiện tại trả mock để giữ luồng test giao diện ổn định.
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
  return `Tạo video ${kind} thời lượng ${b.duration ?? "60"} giây.

Ý tưởng gốc: ${b.content}

Chỉ đạo sản xuất (MarkX):
- Hook 3 giây đầu gây tò mò, giữ chân người xem.
- Nhịp cắt cảnh nhanh, bám theo phong cách đã chọn.
- Text overlay ngắn gọn, nổi bật ở các điểm nhấn.${cameo}${extra}

Camera: kết hợp pan/zoom mượt, ánh sáng phù hợp tông thương hiệu.`;
}
