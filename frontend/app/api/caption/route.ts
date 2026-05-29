import { NextRequest, NextResponse } from "next/server";
import { readApiConfig, hasActiveKey } from "@/lib/api-config";

interface CaptionBody {
  content: string;
  channel: "facebook" | "tiktok" | null;
  styleId: string | null;
  videoType: "entertainment" | "ads" | null;
}

export async function POST(req: NextRequest) {
  const body = (await req.json()) as CaptionBody;
  const cfg = readApiConfig();

  if (!hasActiveKey(cfg)) {
    return NextResponse.json({ suggestions: mockCaptions(body), source: "mock" });
  }

  // TODO: cắm gọi Gemini/LightningAI thật ở đây khi đã có key.
  return NextResponse.json({ suggestions: mockCaptions(body), source: "mock" });
}

function mockCaptions(b: CaptionBody) {
  const isTikTok = b.channel === "tiktok";
  const topic = b.content.trim().slice(0, 60) || "nội dung của bạn";
  if (isTikTok) {
    return [
      {
        tone: "Trẻ trung",
        text: `${topic} 🔥 Xem hết đừng bỏ lỡ nha! #fyp #viral #xuhuong`,
      },
      {
        tone: "Tò mò",
        text: `Bạn đã biết điều này chưa? 👀 ${topic} #fyp #trending`,
      },
      {
        tone: "Ngắn gọn",
        text: `${topic} ✨ #fyp #foryou`,
      },
    ];
  }
  return [
    {
      tone: "Thân thiện",
      text: `${topic} 😍 Cùng khám phá ngay trong video dưới đây nhé! Để lại bình luận cho mình biết cảm nhận của bạn.`,
    },
    {
      tone: "Chuyên nghiệp",
      text: `${topic}. Mời bạn theo dõi video để biết thêm chi tiết. 👇`,
    },
    {
      tone: "Kêu gọi tương tác",
      text: `${topic} ❤️ Like & Share nếu bạn thấy hữu ích, và đừng quên theo dõi trang để cập nhật nội dung mới mỗi ngày!`,
    },
  ];
}
