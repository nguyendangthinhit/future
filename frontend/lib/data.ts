import type { StyleOption, VideoType } from "./types";

export const STYLES: StyleOption[] = [
  {
    id: "style_001",
    name: "Energetic Trending",
    description: "Nhịp nhanh, màu sắc bão hòa, text lớn giữa màn hình",
    videoType: "entertainment",
    emoji: "⚡",
    gradient: "from-orange-400 to-pink-500",
  },
  {
    id: "style_002",
    name: "Cinematic Story",
    description: "Điện ảnh, chuyển cảnh mượt, tông màu trầm ấm",
    videoType: "entertainment",
    emoji: "🎬",
    gradient: "from-slate-600 to-slate-900",
  },
  {
    id: "style_003",
    name: "Cozy Lifestyle",
    description: "Nhẹ nhàng, ấm cúng, nhạc lo-fi, ánh sáng tự nhiên",
    videoType: "entertainment",
    emoji: "🌿",
    gradient: "from-emerald-300 to-teal-500",
  },
  {
    id: "style_004",
    name: "Clean Product Ad",
    description: "Tối giản, nền sạch, tập trung sản phẩm, CTA rõ ràng",
    videoType: "ads",
    emoji: "📦",
    gradient: "from-sky-400 to-indigo-500",
  },
  {
    id: "style_005",
    name: "Bold Promo",
    description: "Mạnh mẽ, tương phản cao, giá & ưu đãi nổi bật",
    videoType: "ads",
    emoji: "🔥",
    gradient: "from-red-500 to-amber-500",
  },
  {
    id: "style_006",
    name: "Friendly Explainer",
    description: "Thân thiện, minh họa đơn giản, dẫn dắt từng bước",
    videoType: "both",
    emoji: "💡",
    gradient: "from-violet-400 to-fuchsia-500",
  },
];

export const DURATIONS: Record<VideoType, number[]> = {
  entertainment: [30, 60, 90],
  ads: [15, 30, 60],
};

export const stylesFor = (type: VideoType | null) =>
  !type
    ? []
    : STYLES.filter((s) => s.videoType === type || s.videoType === "both");
