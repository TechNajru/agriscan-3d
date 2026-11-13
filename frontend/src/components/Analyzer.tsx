"use client";
import { useEffect, useRef, useState } from "react";
import { analyze, getConfig } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisResult, AppConfig } from "@/lib/types";
import CaptureInput from "./CaptureInput";
import ErrorBanner from "./ErrorBanner";
import ResultView from "./ResultView";
import ScanFrame from "./ScanFrame";

const SAMPLES = [
  { id: "good", card: true, label: { en: "Clean apple", hi: "साफ़ सेब" } },
  { id: "bruised", card: true, label: { en: "Bruised apple", hi: "चोट वाला सेब" } },
  { id: "unripe", card: false, label: { en: "Green apple", hi: "हरा सेब" } },
  { id: "rotten", card: true, label: { en: "Rotten patch", hi: "सड़ा हिस्सा" } },
];

export default function Analyzer() {
  const { t, lang } = useI18n();
  const [config, setConfig] = useState<AppConfig | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [fruit, setFruit] = useState("apple");
  const [useRef_, setUseRef] = useState(false);
  const [refMm, setRefMm] = useState("85.6");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<unknown>(null);
  const resultRef = useRef<HTMLDivElement>(null);

  useEffect(() => { getConfig().then(setConfig).catch(() => undefined); }, []);
  useEffect(() => { if (!file) { setPreview(null); return; } const u = URL.createObjectURL(file); setPreview(u); return () => URL.revokeObjectURL(u); }, [file]);

  const choose = (f: File, card = false) => { setFile(f); setResult(null); setError(null); setUseRef(card); };
  const reset = () => { setFile(null); setResult(null); setError(null); setUseRef(false); window.scrollTo({ top: 0, behavior: "smooth" }); };

  const run = async () => {
    if (!file) return;
    setBusy(true); setError(null); setResult(null);
    try {
      const mm = useRef_ ? parseFloat(refMm) || null : null;
      const r = await analyze(file, fruit, mm);
      setResult(r);
      setTimeout(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 80);
    } catch (e) { setError(e); } finally { setBusy(false); }
  };

  const loadSample = async (id: string, card: boolean) => {
    try {
      const blob = await (await fetch(`/samples/${id}.jpg`)).blob();
      choose(new File([blob], `${id}.jpg`, { type: "image/jpeg" }), card);
    } catch (e) { setError(e); }
  };

  return (
    <div className="space-y-8">
      <section className="max-w-3xl">
        <p className="label mb-3">{t("app.tagline")}</p>
        <h1 className="font-display text-[34px] font-semibold leading-[1.1] tracking-tight text-forest-dark sm:text-[46px]">{t("hero.title")}</h1>
        <p className="mt-4 max-w-2xl text-[17px] leading-relaxed text-muted">{t("hero.subtitle")}</p>
      </section>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,5fr)_minmax(0,7fr)]">
        <section className="card space-y-5 p-5 sm:p-6 lg:sticky lg:top-24">
          <div className="label">{t("step.source")}</div>
          {!file ? (
            <>
              <CaptureInput onFile={(f) => choose(f)} maxMb={config?.max_upload_mb ?? 10} />
              <div className="divider" />
              <div>
                <div className="font-display text-lg font-semibold">{t("samples.title")}</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {SAMPLES.map((s) => <button key={s.id} className="btn-ghost !px-4 !py-2 text-sm" onClick={() => loadSample(s.id, s.card)}>{s.label[lang]}</button>)}
                </div>
                <p className="mt-2 text-xs text-muted">{t("samples.note")}</p>
              </div>
            </>
          ) : (
            <>
              <ScanFrame scanning={busy}>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                {preview && <img src={preview} alt={t("preview.title")} className="block max-h-[420px] w-full object-contain" />}
              </ScanFrame>
              <button className="text-sm font-medium text-forest underline underline-offset-4 disabled:opacity-50" onClick={reset} disabled={busy}>{t("preview.remove")}</button>

              <div className="divider" />
              <div className="label">{t("step.options")}</div>
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm">
                  <span className="mb-1.5 block font-medium">{t("options.fruit")}</span>
                  <select value={fruit} onChange={(e) => setFruit(e.target.value)} className="w-full rounded-xl border border-line bg-white px-3 py-2.5">
                    {(config?.fruits ?? [{ id: "apple", label: "Apple" }]).map((f) => <option key={f.id} value={f.id}>{t(`fruit.${f.id}`)}</option>)}
                  </select>
                </label>
                <div className="text-sm">
                  <label className="flex cursor-pointer items-center gap-2.5 font-medium">
                    <input type="checkbox" checked={useRef_} onChange={(e) => setUseRef(e.target.checked)} className="h-5 w-5 accent-[#2F5D3A]" />
                    {t("options.reference")}
                  </label>
                  {useRef_ && (
                    <label className="mt-2 block">
                      <span className="text-xs text-muted">{t("options.reference_width")}</span>
                      <input inputMode="decimal" value={refMm} onChange={(e) => setRefMm(e.target.value)} className="mt-1 w-full rounded-xl border border-line bg-white px-3 py-2 font-mono" />
                    </label>
                  )}
                </div>
              </div>
              {useRef_ && <p className="text-xs text-muted">{t("options.reference_hint")}</p>}
              <ErrorBanner error={error} onClose={() => setError(null)} />
              <div className="sticky bottom-[76px] z-20 -mx-5 bg-gradient-to-t from-card via-card to-transparent px-5 pb-1 pt-4 sm:-mx-6 sm:px-6 md:static md:m-0 md:bg-none md:p-0">
                <button className="btn-primary w-full" onClick={run} disabled={busy}>{busy ? t("btn.analyzing") : t("btn.analyze")}</button>
              </div>
            </>
          )}
          {!file && <ErrorBanner error={error} onClose={() => setError(null)} />}
        </section>

        <section ref={resultRef} className="scroll-mt-24" aria-live="polite">
          {result ? <ResultView result={result} onReset={reset} /> : busy ? (
            <div className="tag-card animate-pulse space-y-4 px-7 pb-8 pt-12"><div className="h-24 w-24 rounded-full bg-kraft" /><div className="h-5 w-2/3 rounded bg-kraft" /><div className="h-24 rounded-xl bg-kraft/70" /><div className="h-4 w-1/2 rounded bg-kraft" /></div>
          ) : (
            <div className="tag-card px-6 pb-8 pt-12 sm:px-8">
              <h2 className="font-display text-2xl font-semibold">{t("result.title")}</h2>
              <ul className="mt-5 grid gap-3 sm:grid-cols-2">
                {["result.grade", "result.ripeness", "result.size", "result.defects", "result.recommendation", "result.why"].map((k, i) => (
                  <li key={k} className="flex items-center gap-3 rounded-xl border border-dashed border-line px-4 py-3 text-[15px]">
                    <span className="grid h-7 w-7 place-items-center rounded-full bg-forest-light font-mono text-xs text-forest">{i + 1}</span>{t(k)}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
