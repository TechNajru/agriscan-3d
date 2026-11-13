"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { useI18n } from "@/lib/i18n";
import Brand from "./Brand";

function LanguageToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <div className="seg" role="group" aria-label="Language">
      {(["en", "hi"] as const).map((l) => (
        <button key={l} aria-pressed={lang === l} onClick={() => setLang(l)} lang={l} className="!px-3 !py-1.5">{t(`lang.${l}`)}</button>
      ))}
    </div>
  );
}

const NAV = [
  { href: "/", key: "nav.analyze", icon: "M4 7V5a1 1 0 0 1 1-1h2M17 4h2a1 1 0 0 1 1 1v2M20 17v2a1 1 0 0 1-1 1h-2M7 20H5a1 1 0 0 1-1-1v-2M8 12h8" },
  { href: "/history", key: "nav.history", icon: "M12 7v5l3 2M21 12a9 9 0 1 1-3-6.7M21 4v4h-4" },
];

export default function Shell({ children }: { children: ReactNode }) {
  const path = usePathname();
  const { t } = useI18n();
  const active = (href: string) => (href === "/" ? path === "/" : path.startsWith(href));
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-30 border-b border-line/80 bg-paper/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center gap-4 px-4 py-3 md:px-6">
          <Link href="/" className="flex items-center gap-2.5" aria-label={t("app.name")}>
            <Brand />
            <span className="font-display text-[22px] font-bold leading-none tracking-tight text-forest-dark">AgriScan <span className="text-apple">3D</span></span>
          </Link>
          <nav className="ml-6 hidden gap-1 md:flex">
            {NAV.map((n) => (
              <Link key={n.href} href={n.href} className={`rounded-full px-4 py-2 text-[15px] font-medium transition ${active(n.href) ? "bg-forest-light text-forest-dark" : "text-muted hover:text-ink"}`}>{t(n.key)}</Link>
            ))}
          </nav>
          <div className="ml-auto"><LanguageToggle /></div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl flex-1 px-4 pb-32 pt-6 md:px-6 md:pb-16 md:pt-10">{children}</main>
      <footer className="hidden border-t border-line/80 py-6 text-center text-[13px] text-muted md:block">{t("footer.disclaimer")}</footer>
      <nav className="fixed inset-x-0 bottom-0 z-30 grid grid-cols-2 border-t border-line bg-card/95 pb-[env(safe-area-inset-bottom)] backdrop-blur md:hidden" aria-label="Primary">
        {NAV.map((n) => (
          <Link key={n.href} href={n.href} className={`flex flex-col items-center gap-1 py-2.5 text-[12px] font-medium ${active(n.href) ? "text-forest" : "text-muted"}`}>
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round"><path d={n.icon} /></svg>
            {t(n.key)}
          </Link>
        ))}
      </nav>
    </div>
  );
}
