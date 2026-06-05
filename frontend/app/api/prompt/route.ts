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
  targetLanguage: string;
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
        target_language: body.targetLanguage,
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
    
    // Nếu API backend trả về lỗi, ném lỗi thẳng về client để UI báo lỗi
    const errorText = await res.text();
    return NextResponse.json(
      { error: `Backend error: ${res.status} - ${errorText}` },
      { status: res.status }
    );
  } catch (err: any) {
    console.error("Lỗi gọi API preview-prompt:", err);
    return NextResponse.json(
      { error: `Lỗi kết nối Backend: ${err.message}` },
      { status: 500 }
    );
  }
}
