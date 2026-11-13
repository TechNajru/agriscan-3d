import type { Grade } from "@/lib/types";

export const GRADE_COLOR: Record<Grade, string> = { A: "#2F7D43", B: "#B98A1E", C: "#CC6A1B", Reject: "#B3261E" };

export default function GradeStamp({ grade, size = 96, animate = false }: { grade: Grade; size?: number; animate?: boolean }) {
  return (
    <div role="img" aria-label={`Grade ${grade}`} className={`grade-stamp ${animate ? "animate-stamp" : ""}`}
         style={{ width: size, height: size, color: GRADE_COLOR[grade], fontSize: size * 0.56 }}>
      {grade === "Reject" ? (
        <svg width={size * 0.5} height={size * 0.5} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3.4" strokeLinecap="round"><path d="M5 5l14 14M19 5L5 19" /></svg>
      ) : grade}
    </div>
  );
}
