"use client";
import { useI18n } from "@/lib/i18n";
import { ApiError } from "@/lib/api";

export function errorText(t: (k: string, p?: Record<string, string | number>) => string, e: unknown): string {
  if (e instanceof ApiError) return t(`errors.${e.code}`, e.params);
  return t("errors.server");
}

export default function ErrorBanner({ error, onClose }: { error: unknown; onClose?: () => void }) {
  const { t } = useI18n();
  if (!error) return null;
  return (
    <div role="alert" className="flex items-start gap-3 rounded-xl border border-apple/30 bg-apple/10 px-4 py-3 text-[15px] text-[#7a2518]">
      <svg className="mt-0.5 shrink-0" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="12" cy="12" r="9" /><path d="M12 7v6M12 16.5v.5" /></svg>
      <span className="flex-1">{typeof error === "string" ? error : errorText(t, error)}</span>
      {onClose && <button onClick={onClose} aria-label="Close" className="text-lg leading-none opacity-60 hover:opacity-100">×</button>}
    </div>
  );
}
