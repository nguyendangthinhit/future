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
  duration: string | null;
  targetLanguage: string;
  content: string;
  useGoogleData: boolean;
  searchKeyword: string;
  engineType: "mascot" | "avatar";
  avatarId: string;
  voiceId: string;
  images: UploadedImage[];
  styleId: string | null;
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

export interface BrandPalette {
  primary: string;
  accent: string;
  bg: string;
}

export interface BrandFonts {
  display: string;
  body: string;
}

export interface BriefBrand {
  name: string;
  toneOfVoice: string;
  palette: BrandPalette;
  fonts: BrandFonts;
  logoUrl?: string | null;
  voiceId?: string | null;
  claimsAllowed: string[];
  claimsForbidden: string[];
}

export interface BriefAudience {
  segment: string;
  age: string;
  locale: string;
}

export interface BriefConstraints {
  lengthSec: 15 | 20 | 30;
  aspect: Array<"9:16" | "1:1">;
  mustInclude: string[];
  mustAvoid: string[];
}

export interface FactoryBrief {
  theme: string;
  brand: BriefBrand;
  audience: BriefAudience;
  platform: "tiktok" | "reels" | "shorts" | "all";
  constraints: BriefConstraints;
  moodboardUrls?: string[];
  variantsTarget: 1 | 2;
}

export interface FactoryVariantPack {
  variant_id: string;
  variant_angle: string;
  script: Record<string, unknown>;
  storyboard: Record<string, unknown>;
  pack: Record<string, unknown>;
  final_video_urls?: string[];
  clip_urls?: string[];
  qa?: {
    score?: {
      total?: number;
      passed?: boolean;
      hook?: number;
      brand?: number;
      compliance?: number;
      audio?: number;
      pacing?: number;
      caption?: number;
      cta?: number;
    };
    notes?: string[];
    feedback_for_director?: string;
  };
  qa_passed?: boolean;
}

export interface FactoryResult {
  plan: Record<string, unknown>;
  brand_lock: Record<string, unknown>;
  variants: FactoryVariantPack[];
  publishable_variants?: FactoryVariantPack[];
  trace: Array<Record<string, unknown>>;
  wall_s: number;
  elapsed_s?: number;
  brief: Record<string, unknown>;
}
