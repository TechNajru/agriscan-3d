import type { AnalysisResult, AppConfig, HistoryItem, Lang } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "";

export class ApiError extends Error {
  constructor(public code: string, public params: Record<string, string | number> = {}, public status = 0) { super(code); }
}

export const assetUrl = (path: string) => `${BASE}${path}`;
export const reportUrl = (id: string, lang: Lang) => `${BASE}/api/analysis/${id}/report.pdf?lang=${lang}`;

async function request(path: string, init?: RequestInit): Promise<Response> {
  let res: Response;
  try { res = await fetch(`${BASE}${path}`, init); } catch { throw new ApiError("network"); }
  if (res.ok) return res;
  let code = "server"; let params: Record<string, string | number> = {};
  try {
    const body = await res.json();
    if (body?.detail && typeof body.detail === "object" && !Array.isArray(body.detail)) { code = body.detail.code ?? code; params = body.detail.params ?? {}; }
  } catch { /* non-JSON error body */ }
  throw new ApiError(code, params, res.status);
}

export async function analyze(file: File, fruit: string, referenceMm: number | null): Promise<AnalysisResult> {
  const form = new FormData();
  form.append("image", file);
  form.append("fruit", fruit);
  if (referenceMm) form.append("reference_width_mm", String(referenceMm));
  return (await request("/api/analyze", { method: "POST", body: form })).json();
}
export const getConfig = async (): Promise<AppConfig> => (await request("/api/config")).json();
export const getHistory = async (): Promise<{ limit: number; items: HistoryItem[] }> => (await request("/api/history", { cache: "no-store" })).json();
export const getAnalysis = async (id: string): Promise<AnalysisResult> => (await request(`/api/analysis/${id}`, { cache: "no-store" })).json();
export const deleteAnalysis = async (id: string): Promise<void> => { await request(`/api/analysis/${id}`, { method: "DELETE" }); };
