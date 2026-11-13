"use client";
import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import en from "@/i18n/en.json";
import hi from "@/i18n/hi.json";
import type { Lang } from "./types";

const dicts: Record<Lang, Record<string, string>> = { en, hi };
type Params = Record<string, string | number>;
interface Ctx { lang: Lang; setLang: (l: Lang) => void; t: (key: string, params?: Params) => string }
const I18nContext = createContext<Ctx | null>(null);
const STORAGE_KEY = "agriscan-lang";

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>("en");

  useEffect(() => {
    const saved = window.localStorage.getItem(STORAGE_KEY) as Lang | null;
    const initial: Lang = saved === "en" || saved === "hi" ? saved : navigator.language?.toLowerCase().startsWith("hi") ? "hi" : "en";
    setLangState(initial);
  }, []);
  useEffect(() => { document.documentElement.lang = lang; }, [lang]);

  const setLang = useCallback((l: Lang) => { setLangState(l); window.localStorage.setItem(STORAGE_KEY, l); }, []);
  const t = useCallback((key: string, params?: Params) => {
    let s = dicts[lang][key] ?? dicts.en[key] ?? key;
    if (params) for (const [k, v] of Object.entries(params)) s = s.replaceAll(`{${k}}`, String(v));
    return s;
  }, [lang]);
  const value = useMemo(() => ({ lang, setLang, t }), [lang, setLang, t]);
  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): Ctx {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used inside LanguageProvider");
  return ctx;
}
