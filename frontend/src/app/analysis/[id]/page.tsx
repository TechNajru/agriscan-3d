"use client";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import ErrorBanner from "@/components/ErrorBanner";
import ResultView from "@/components/ResultView";
import { getAnalysis } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import type { AnalysisResult } from "@/lib/types";

export default function AnalysisPage() {
  const { id } = useParams<{ id: string }>();
  const { t } = useI18n();
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<unknown>(null);
  useEffect(() => { getAnalysis(id).then(setResult).catch(setError); }, [id]);
  return (
    <div className="space-y-6">
      <Link href="/history" className="text-sm font-medium text-forest underline underline-offset-4">← {t("nav.history")}</Link>
      <ErrorBanner error={error} />
      {!result && !error && <div className="card h-64 animate-pulse" />}
      {result && <ResultView result={result} />}
    </div>
  );
}
