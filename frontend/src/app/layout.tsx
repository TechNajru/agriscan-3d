import type { Metadata, Viewport } from "next";
import "@fontsource/fraunces/600.css";
import "@fontsource/fraunces/700.css";
import "@fontsource/dm-sans/400.css";
import "@fontsource/dm-sans/500.css";
import "@fontsource/dm-sans/700.css";
import "@fontsource/dm-mono/400.css";
import "@fontsource/dm-mono/500.css";
import "@fontsource/noto-sans-devanagari/400.css";
import "@fontsource/noto-sans-devanagari/500.css";
import "@fontsource/noto-sans-devanagari/700.css";
import "./globals.css";
import { LanguageProvider } from "@/lib/i18n";
import Shell from "@/components/Shell";

export const metadata: Metadata = {
  title: "AgriScan 3D | Fruit quality inspection",
  description: "Photograph a fruit and get defects, ripeness, size, a quality grade and a sorting recommendation in English or Hindi.",
};
export const viewport: Viewport = { themeColor: "#F4EFE4", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body><LanguageProvider><Shell>{children}</Shell></LanguageProvider></body>
    </html>
  );
}
