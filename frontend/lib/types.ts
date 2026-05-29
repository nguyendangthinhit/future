export type VideoType = "entertainment" | "ads";
export type Channel = "facebook" | "tiktok";

export interface StyleOption {
  id: string;
  name: string;
  description: string;
  videoType: VideoType | "both";
  emoji: string;
  gradient: string;
}

export interface CreateVideoForm {
  videoType: VideoType | null;
  channel: Channel | null;
  scheduledDate: string;
  scheduledTime: string;
  duration: number | null;
  content: string;
  useGoogleData: boolean;
  searchKeyword: string;
  images: UploadedImage[];
  styleId: string | null;
  caption: string;
  generatedPrompt: string;
}

export interface UploadedImage {
  id: string;
  name: string;
  dataUrl: string;
  size: number;
}

export interface CaptionSuggestion {
  text: string;
  tone: string;
}
