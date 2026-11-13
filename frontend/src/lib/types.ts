export type Grade = "A" | "B" | "C" | "Reject";
export type Lang = "en" | "hi";
export type Bilingual = { en: string; hi: string };

export interface Defect { type: string; confidence: number; bbox: [number, number, number, number]; area_ratio: number }
export interface Reason { key: string; params: Record<string, string | number>; text: Bilingual }
export interface AnalysisResult {
  id: string; created_at: string; mode: string;
  fruit_type: string;
  image: { width: number; height: number };
  fruit_bbox: [number, number, number, number];
  ripeness: { label: "Unripe" | "Partially Ripe" | "Ripe" | "Overripe"; confidence: number; uniformity: number };
  size: { basis: "absolute" | "relative"; diameter_mm: number | null; class: "small" | "medium" | "large"; frame_pct: number; aspect_ratio: number; circularity: number };
  defects: Defect[]; defect_total_ratio: number; experimental: boolean;
  grade: Grade; score: number; recommendation_key: string; recommendation: Bilingual;
  reasons: Reason[]; explanation: Bilingual; warnings: string[];
  quality: { sharpness: number; brightness: number }; timing_ms: number;
  original_url: string; annotated_url: string;
}
export interface HistoryItem {
  id: string; created_at: string; mode: string; fruit_type: string; grade: Grade; score: number;
  ripeness: string; defect_count: number; recommendation_key: string;
}
export interface AppConfig {
  fruits: { id: string; label: string }[]; max_upload_mb: number; history_limit: number;
  experimental_defects: boolean; reference_card_mm: number;
}
