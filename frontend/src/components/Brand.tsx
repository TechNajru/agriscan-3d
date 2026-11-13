export default function Brand({ size = 34 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 40 40" aria-hidden="true">
      <path d="M4 13V6a2 2 0 0 1 2-2h7M27 4h7a2 2 0 0 1 2 2v7M36 27v7a2 2 0 0 1-2 2h-7M13 36H6a2 2 0 0 1-2-2v-7" fill="none" stroke="#2F5D3A" strokeWidth="2.6" strokeLinecap="round" />
      <path d="M20 14c-2.2-1.6-6-1.4-7.9 1.6-2.2 3.4-.9 8.6 1.6 11 1.4 1.3 3 1.1 4.1.6.8-.4 1.7-.4 2.4 0 1.1.5 2.7.7 4.1-.6 2.5-2.4 3.8-7.6 1.6-11C23.9 12.6 22.2 12.4 20 14Z" fill="#C4452F" />
      <path d="M20 14c.1-2.2 1-4 3-5" stroke="#2F5D3A" strokeWidth="2" strokeLinecap="round" fill="none" />
      <path d="M21 11c1.5-1.6 3.6-1.7 4.8-1.2-.4 1.6-2.2 2.7-4.8 1.2Z" fill="#7FA650" />
    </svg>
  );
}
