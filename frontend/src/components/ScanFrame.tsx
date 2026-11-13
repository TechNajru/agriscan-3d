import type { ReactNode } from "react";

/** Image holder with inspection-station corner brackets and an optional scanning sweep. */
export default function ScanFrame({ children, scanning = false }: { children: ReactNode; scanning?: boolean }) {
  return (
    <div className="relative overflow-hidden rounded-xl bg-kraft/50">
      {children}
      <span className="corner tl" /><span className="corner tr" /><span className="corner bl" /><span className="corner br" />
      {scanning && <><div className="absolute inset-0 bg-forest/10" /><div className="scan-line" /></>}
    </div>
  );
}
