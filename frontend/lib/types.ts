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
  duration: string | null;
  content: string;
  useGoogleData: boolean;
  searchKeyword: string;
  images: UploadedImage[];
  styleId: string | null;
  caption: string;
  generatedPrompt: string;
  researchBrief: ResearchBrief | null;
}

export interface UploadedImage {
  id: string;
  name: string;
  dataUrl: string;
  size: number;
  file?: File;
}

export interface CaptionSuggestion {
  text: string;
  tone: string;
}

export interface ResearchStage {
  id: number;
  title: string;
  detail: string;
  duration_hint: string;
  enabled: boolean;
}

export interface ResearchBrief {
  topic: string;
  summary: string;
  stages: ResearchStage[];
  key_facts: { text: string; enabled: boolean }[];
}
