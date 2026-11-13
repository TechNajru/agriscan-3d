"use client";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import ErrorBanner from "@/components/ErrorBanner";
import GradeStamp from "@/components/GradeStamp";
import { deleteAnalysis, getHistory } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { HistoryItem } from "@/lib/types";

export default function HistoryPage() {
  const { t, lang } = useI18n();
  const [items, setItems] = useState<HistoryItem[] | null>(null);
  const [limit, setLimit] = useState(10);
  const [error, setError] = useState<unknown>(null);

  const load = useCallback(() => { getHistory().then((r) => { setItems(r.items); setLimit(r.limit); }).catch(setError); }, []);
  useEffect(load, [load]);
  const fmt = (iso: string) => new Intl.DateTimeFormat(lang === "hi" ? "hi-IN" : "en-IN", { dateStyle: "medium", timeStyle: "short" }).format(new Date(iso));
  const remove = async (id: string) => { try { await deleteAnalysis(id); load(); } catch (e) { setError(e); } };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-[34px] font-semibold tracking-tight text-forest-dark">{t("history.title")}</h1>
        <p className="mt-1 text-muted">{t("history.subtitle", { n: limit })}</p>
      </div>
      <ErrorBanner error={error} onClose={() => setError(null)} />
      {items === null && !error && <div className="card h-40 animate-pulse" />}
      {items?.length === 0 && (
        <div className="card flex flex-col items-center gap-4 px-6 py-14 text-center">
          <p className="max-w-sm text-muted">{t("history.empty")}</p>
          <Link href="/" className="btn-primary">{t("nav.analyze")}</Link>
        </div>
      )}
      {!!items?.length && (
        <ul className="space-y-3">
          {items.map((it) => (
            <li key={it.id} className="card flex flex-wrap items-center gap-x-5 gap-y-3 p-4 sm:p-5">
              <GradeStamp grade={it.grade} size={64} />
              <div className="min-w-[160px] flex-1">
                <div className="font-medium">{t(`fruit.${it.fruit_type}`)} · <span className="text-muted">{t(`ripeness.${it.ripeness}`)}</span></div>
                <div className="text-[15px]">{t(`recommendation.${it.recommendation_key}`)}</div>
                <div className="mt-0.5 font-mono text-xs text-muted">{fmt(it.created_at)} · {t("history.defects")}: {it.defect_count} · {it.score}/100</div>
              </div>
              <div className="flex gap-2">
                <Link href={`/analysis/${it.id}`} className="btn-ghost !px-4 !py-2 text-sm">{t("btn.open")}</Link>
                <button onClick={() => remove(it.id)} className="btn-ghost !px-4 !py-2 text-sm hover:!border-apple hover:!text-apple">{t("history.delete")}</button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
