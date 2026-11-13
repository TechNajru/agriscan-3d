"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n";
import ErrorBanner from "./ErrorBanner";

type Source = "upload" | "webcam" | "phone";
const TYPES = ["image/jpeg", "image/png", "image/webp"];

function WebcamPane({ onFile }: { onFile: (f: File) => void }) {
  const { t } = useI18n();
  const video = useRef<HTMLVideoElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const [live, setLive] = useState(false);
  const [facing, setFacing] = useState<"environment" | "user">("environment");
  const [error, setError] = useState<string | null>(null);

  const stop = useCallback(() => { stream.current?.getTracks().forEach((tr) => tr.stop()); stream.current = null; setLive(false); }, []);
  useEffect(() => stop, [stop]);

  const start = useCallback(async (mode: "environment" | "user") => {
    setError(null); stop();
    if (!window.isSecureContext || !navigator.mediaDevices?.getUserMedia) { setError(t("errors.camera_insecure")); return; }
    try {
      const s = await navigator.mediaDevices.getUserMedia({ video: { facingMode: mode, width: { ideal: 1920 }, height: { ideal: 1080 } }, audio: false });
      stream.current = s;
      if (video.current) { video.current.srcObject = s; await video.current.play(); }
      setFacing(mode); setLive(true);
    } catch (e) {
      const name = (e as DOMException).name;
      setError(name === "NotAllowedError" ? t("errors.camera_denied") : t("errors.camera_unavailable"));
    }
  }, [stop, t]);

  const snap = () => {
    const v = video.current; if (!v) return;
    const c = document.createElement("canvas"); c.width = v.videoWidth; c.height = v.videoHeight;
    c.getContext("2d")!.drawImage(v, 0, 0);
    c.toBlob((b) => { if (b) { onFile(new File([b], `capture-${Date.now()}.jpg`, { type: "image/jpeg" })); stop(); } }, "image/jpeg", 0.92);
  };

  return (
    <div className="space-y-3">
      <div className="relative aspect-[4/3] overflow-hidden rounded-xl bg-ink/90">
        <video ref={video} playsInline muted className={`h-full w-full object-cover ${live ? "" : "hidden"}`} />
        {!live && <div className="grid h-full place-items-center p-6 text-center text-sm text-white/80">{t("camera.hint")}</div>}
        {live && <><span className="corner tl !border-white" /><span className="corner tr !border-white" /><span className="corner bl !border-white" /><span className="corner br !border-white" /></>}
      </div>
      <ErrorBanner error={error} />
      <div className="flex flex-wrap gap-2">
        {!live ? <button className="btn-primary" onClick={() => start(facing)}>{t("camera.start")}</button> : (
          <>
            <button className="btn-primary" onClick={snap}>{t("camera.capture")}</button>
            <button className="btn-ghost" onClick={() => start(facing === "environment" ? "user" : "environment")}>{t("camera.switch")}</button>
            <button className="btn-ghost" onClick={stop}>{t("camera.stop")}</button>
          </>
        )}
      </div>
    </div>
  );
}

export default function CaptureInput({ onFile, maxMb }: { onFile: (f: File) => void; maxMb: number }) {
  const { t } = useI18n();
  const [source, setSource] = useState<Source>("upload");
  const [drag, setDrag] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const pick = useRef<HTMLInputElement>(null);
  const phone = useRef<HTMLInputElement>(null);

  const accept = (f: File | undefined | null) => {
    if (!f) return;
    if (!TYPES.includes(f.type)) { setError(t("errors.invalid_file")); return; }
    if (f.size > maxMb * 1024 * 1024) { setError(t("errors.file_too_large", { max: maxMb })); return; }
    setError(null); onFile(f);
  };
  const tabs: { id: Source; label: string }[] = [
    { id: "upload", label: t("source.upload") }, { id: "webcam", label: t("source.webcam") }, { id: "phone", label: t("source.phone") },
  ];

  return (
    <div className="space-y-4">
      <div className="seg w-full justify-between sm:w-auto" role="tablist">
        {tabs.map((s) => (
          <button key={s.id} role="tab" aria-selected={source === s.id} onClick={() => { setSource(s.id); setError(null); }} className="flex-1 sm:flex-none">{s.label}</button>
        ))}
      </div>

      {source === "upload" && (
        <label onDragOver={(e) => { e.preventDefault(); setDrag(true); }} onDragLeave={() => setDrag(false)}
               onDrop={(e) => { e.preventDefault(); setDrag(false); accept(e.dataTransfer.files[0]); }}
               className={`flex cursor-pointer flex-col items-center gap-3 rounded-2xl border-2 border-dashed px-6 py-12 text-center transition ${drag ? "border-forest bg-forest-light" : "border-line bg-card hover:border-forest/60"}`}>
          <span className="grid h-14 w-14 place-items-center rounded-full bg-forest-light text-forest">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d="M12 16V5M7.5 9.5 12 5l4.5 4.5M5 19h14" /></svg>
          </span>
          <span className="font-display text-xl font-semibold">{t("drop.title")}</span>
          <span className="text-sm text-muted">{t("drop.or")} <span className="font-medium text-forest underline underline-offset-4">{t("drop.browse")}</span></span>
          <span className="max-w-xs text-xs text-muted">{t("drop.hint")}</span>
          <input ref={pick} type="file" accept={TYPES.join(",")} className="sr-only" onChange={(e) => { accept(e.target.files?.[0]); e.target.value = ""; }} />
        </label>
      )}

      {source === "webcam" && <WebcamPane onFile={(f) => accept(f)} />}

      {source === "phone" && (
        <div className="flex flex-col items-center gap-4 rounded-2xl border border-line bg-card px-6 py-10 text-center">
          <span className="grid h-16 w-16 place-items-center rounded-full bg-forest text-white">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 8h3l1.5-2h7L17 8h3v11H4z" /><circle cx="12" cy="13" r="3.5" /></svg>
          </span>
          <button className="btn-primary" onClick={() => phone.current?.click()}>{t("phone.button")}</button>
          <p className="max-w-xs text-sm text-muted">{t("phone.hint")}</p>
          <input ref={phone} type="file" accept="image/*" capture="environment" className="sr-only" onChange={(e) => { accept(e.target.files?.[0]); e.target.value = ""; }} />
        </div>
      )}
      <ErrorBanner error={error} onClose={() => setError(null)} />
    </div>
  );
}
