import { NextRequest, NextResponse } from "next/server";

interface CaptionBody {
  content: string;
  channel: "facebook" | "tiktok" | null;
  styleId: string | null;
  videoType: "entertainment" | "ads" | null;
}

export async function POST(req: NextRequest) {
  const body = (await req.json()) as CaptionBody;
  return NextResponse.json({ suggestions: mockCaptions(body), source: "mock" });
}

function mockCaptions(body: CaptionBody) {
  const topic = body.content.trim().slice(0, 60) || "noi dung cua ban";
  if (body.channel === "tiktok") {
    return [
      {
        tone: "Tre trung",
        text: `${topic} - xem het de khong bo lo. #fyp #viral #xuhuong`,
      },
      {
        tone: "To mo",
        text: `Ban da biet dieu nay chua? ${topic} #fyp #trending`,
      },
      {
        tone: "Ngan gon",
        text: `${topic} #fyp #foryou`,
      },
    ];
  }

  return [
    {
      tone: "Than thien",
      text: `${topic}. Cung kham pha trong video va de lai binh luan cua ban.`,
    },
    {
      tone: "Chuyen nghiep",
      text: `${topic}. Moi ban theo doi video de biet them chi tiet.`,
    },
    {
      tone: "Keu goi tuong tac",
      text: `${topic}. Like, share va theo doi de cap nhat noi dung moi moi ngay.`,
    },
  ];
}
