"use client";
import { useState } from "react";
import { assetUrl, reportUrl } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisResult } from "@/lib/types";
import GradeStamp, { GRADE_COLOR } from "./GradeStamp";
import ScanFrame from "./ScanFrame";

const RIPE_STEPS = ["Unripe", "Partially Ripe", "Ripe", "Overripe"] as const;

export default function ResultView({ result, onReset }: { result: AnalysisResult; onReset?: () => void }) {
  const { t, lang } = useI18n();
  const [hover, setHover] = useState<number | null>(null);
  const { width: W, height: H } = result.image;
  const color = GRADE_COLOR[result.grade];
  const fs = Math.max(W, H) / 52;
  const abs = result.size.basis === "absolute";

  return (
    <div className="animate-rise space-y-5">
      <div className="grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]">
        {/* inspected photo with vector overlay */}
        <div className="card p-3">
          <ScanFrame>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={assetUrl(result.original_url)} alt="" className="block h-auto w-full" width={W} height={H} />
            <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="absolute inset-0 h-full w-full" aria-hidden="true">
              <rect x={result.fruit_bbox[0]} y={result.fruit_bbox[1]} width={result.fruit_bbox[2] - result.fruit_bbox[0]} height={result.fruit_bbox[3] - result.fruit_bbox[1]}
                    fill="none" stroke="#2F6FD2" strokeWidth={2.5} strokeDasharray="10 6" vectorEffect="non-scaling-stroke" rx={6} />
              {result.defects.map((d, i) => (
                <g key={i} opacity={hover === null || hover === i ? 1 : 0.35}>
                  <rect x={d.bbox[0]} y={d.bbox[1]} width={d.bbox[2] - d.bbox[0]} height={d.bbox[3] - d.bbox[1]} fill={hover === i ? "rgba(196,69,47,.22)" : "none"}
                        stroke="#C4452F" strokeWidth={hover === i ? 4 : 3} vectorEffect="non-scaling-stroke" rx={4} />
                  <rect x={d.bbox[0]} y={Math.max(d.bbox[1] - fs * 1.7, 0)} width={fs * 7.4} height={fs * 1.55} fill="#C4452F" rx={3} />
                  <text x={d.bbox[0] + fs * 0.4} y={Math.max(d.bbox[1] - fs * 0.55, fs * 1.0)} fontSize={fs} fill="#fff" fontFamily="DM Mono, monospace">
                    {(t(`defect.${d.type}`) || d.type).slice(0, 10)} {d.confidence.toFixed(2)}
                  </text>
                </g>
              ))}
            </svg>
          </ScanFrame>
          <div className="mt-3 flex flex-wrap items-center justify-between gap-2 px-1 text-xs text-muted">
            <span className="label">{t("result.time", { ms: result.timing_ms })}</span>
            {result.experimental && <span className="rounded-full bg-amber/20 px-3 py-1 font-mono text-[11px] uppercase tracking-wider text-[#7a5600]">{t("result.experimental")}</span>}
          </div>
        </div>

        {/* specimen tag */}
        <div className="tag-card px-5 pb-6 pt-10 sm:px-7">
          <div className="flex items-center gap-5">
            <GradeStamp grade={result.grade} size={96} animate />
            <div className="min-w-0">
              <div className="label">{t("result.grade")}</div>
              <div className="font-display text-[26px] font-semibold leading-tight">{t(`grade.${result.grade}`)}</div>
              <div className="mt-2 flex items-center gap-2" aria-label={`${t("result.score")} ${result.score}`}>
                <div className="h-2 w-28 overflow-hidden rounded-full bg-kraft"><div className="h-full rounded-full" style={{ width: `${result.score}%`, background: color }} /></div>
                <span className="font-mono text-sm">{result.score}<span className="text-muted">/100</span></span>
              </div>
            </div>
          </div>

          <div className="mt-5 rounded-xl p-4" style={{ background: `${color}14`, borderLeft: `4px solid ${color}` }}>
            <div className="label">{t("result.recommendation")}</div>
            <div className="mt-1 text-[17px] font-semibold">{result.recommendation[lang]}</div>
          </div>

          <div className="divider my-5" />
          <dl className="space-y-4 text-[15px]">
            <div>
              <div className="flex items-baseline justify-between"><dt className="label">{t("result.ripeness")}</dt>
                <dd className="font-mono text-xs text-muted" title={t("result.heuristic")}>{result.ripeness.confidence.toFixed(2)} · {t("result.heuristic")}</dd></div>
              <div className="mt-2 grid grid-cols-4 gap-1" role="img" aria-label={t(`ripeness.${result.ripeness.label}`)}>
                {RIPE_STEPS.map((s) => (
                  <div key={s} className={`rounded-md px-1 py-1.5 text-center text-[11px] font-medium leading-tight ${s === result.ripeness.label ? "bg-forest text-white" : "bg-kraft/70 text-muted"}`}>{t(`ripeness.${s}`)}</div>
                ))}
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div><dt className="label">{abs ? t("result.size_abs") : t("result.size_rel")}</dt>
                <dd className="mt-1 font-mono text-xl">{abs ? `${result.size.diameter_mm} ${t("unit.mm")}` : t(`size.${result.size.class}`)}
                  {abs && <span className="ml-2 rounded-full bg-kraft px-2 py-0.5 font-sans text-xs">{t(`size.${result.size.class}`)}</span>}</dd>
                {!abs && <dd className="mt-0.5 text-xs text-muted">{t("size.fill", { pct: result.size.frame_pct })}</dd>}</div>
              <div><dt className="label">{t("result.fruit")}</dt><dd className="mt-1 text-xl font-medium">{t(`fruit.${result.fruit_type}`)}</dd></div>
              <div><dt className="label">{t("result.uniformity")}</dt><dd className="mt-1 font-mono text-lg">{result.ripeness.uniformity.toFixed(2)}</dd></div>
              <div><dt className="label">{t("result.shape")}</dt><dd className="mt-1 font-mono text-lg">{result.size.circularity.toFixed(2)}</dd></div>
            </div>
            {!abs && <p className="text-xs text-muted">{t("size.relative_note")}</p>}
          </dl>
        </div>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card p-5 sm:p-6">
          <h3 className="label mb-3">{t("result.defects")}</h3>
          {result.defects.length === 0 ? <p className="font-medium text-forest">{t("result.no_defects")}</p> : (
            <ul className="space-y-3">
              {result.defects.map((d, i) => (
                <li key={i} onMouseEnter={() => setHover(i)} onMouseLeave={() => setHover(null)} className="rounded-lg px-2 py-1.5 transition hover:bg-kraft/50">
                  <div className="flex items-center justify-between gap-3 text-[15px]">
                    <span className="flex items-center gap-2 font-medium"><span className="h-2.5 w-2.5 rounded-full bg-apple" />{t(`defect.${d.type}`)}</span>
                    <span className="font-mono text-xs text-muted">{d.confidence.toFixed(2)} · {(d.area_ratio * 100).toFixed(1)}%</span>
                  </div>
                  <div className="mt-1.5 h-1.5 overflow-hidden rounded-full bg-kraft"><div className="h-full rounded-full bg-apple" style={{ width: `${Math.min(100, (d.area_ratio / 0.25) * 100)}%` }} /></div>
                </li>
              ))}
            </ul>
          )}
          {result.experimental && <p className="mt-4 rounded-lg bg-amber/15 px-3 py-2 text-[13px] text-[#6d4e00]">{t("result.experimental_note")}</p>}
        </div>

        <div className="card p-5 sm:p-6">
          <h3 className="label mb-3">{t("result.why")}</h3>
          <ul className="space-y-2">
            {result.reasons.map((r, i) => (
              <li key={i} className="flex gap-2.5 text-[15px]"><span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full" style={{ background: color }} />{r.text[lang]}</li>
            ))}
          </ul>
          <p className="mt-4 border-t border-dashed border-line pt-4 text-[15px] leading-relaxed">{result.explanation[lang]}</p>
          {result.warnings.length > 0 && (
            <div className="mt-4"><div className="label mb-1">{t("result.warnings")}</div>
              <ul className="list-disc pl-5 text-[13px] text-muted">{result.warnings.map((w) => <li key={w}>{t(`warning.${w}`)}</li>)}</ul></div>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-3">
        <a className="btn-primary" href={reportUrl(result.id, lang)} target="_blank" rel="noopener noreferrer">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 4v11M7.5 11 12 15.5 16.5 11M5 20h14" /></svg>
          {t("btn.download")}
        </a>
        {onReset && <button className="btn-ghost" onClick={onReset}>{t("btn.reset")}</button>}
      </div>
      <p className="text-xs text-muted md:hidden">{t("footer.disclaimer")}</p>
    </div>
  );
}
