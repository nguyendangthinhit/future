import { readFileSync } from "fs";
import { join } from "path";

export interface ApiConfig {
  provider: string;
  geminiKey: string;
  geminiModel: string;
  lightningBaseUrl: string;
  openaiKey: string;
  openaiModel: string;
}

/**
 * Đọc api_key.txt ở thư mục gốc frontend. Mỗi dòng dạng KEY=value.
 * Trả về config; value rỗng => coi như chưa cấu hình (chạy mock).
 */
export function readApiConfig(): ApiConfig {
  const defaults: ApiConfig = {
    provider: "gemini",
    geminiKey: "",
    geminiModel: "gemini-1.5-pro",
    lightningBaseUrl: "https://api.lightning.ai/v1",
    openaiKey: "",
    openaiModel: "gpt-4o",
  };

  try {
    const raw = readFileSync(join(process.cwd(), "api_key.txt"), "utf-8");
    const map: Record<string, string> = {};
    for (const line of raw.split(/\r?\n/)) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith("#")) continue;
      const eq = trimmed.indexOf("=");
      if (eq === -1) continue;
      map[trimmed.slice(0, eq).trim()] = trimmed.slice(eq + 1).trim();
    }
    return {
      provider: map.PROVIDER || defaults.provider,
      geminiKey: map.GEMINI_API_KEY || "",
      geminiModel: map.GEMINI_MODEL || defaults.geminiModel,
      lightningBaseUrl: map.LIGHTNING_BASE_URL || defaults.lightningBaseUrl,
      openaiKey: map.OPENAI_API_KEY || "",
      openaiModel: map.OPENAI_MODEL || defaults.openaiModel,
    };
  } catch {
    return defaults;
  }
}

export function hasActiveKey(cfg: ApiConfig): boolean {
  return cfg.provider === "openai" ? !!cfg.openaiKey : !!cfg.geminiKey;
}
