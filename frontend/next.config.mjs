/** @type {import('next').NextConfig} */
const proxy = process.env.API_PROXY_URL;   // local dev: set to http://localhost:8000 to avoid CORS
const nextConfig = {
  output: "standalone",
  reactStrictMode: true,
  eslint: { ignoreDuringBuilds: true },
  poweredByHeader: false,
  async rewrites() {
    if (!proxy) return [];
    return [
      { source: "/api/:path*", destination: `${proxy}/api/:path*` },
      { source: "/outputs/:path*", destination: `${proxy}/outputs/:path*` },
    ];
  },
  async headers() {
    return [{ source: "/(.*)", headers: [
      { key: "X-Content-Type-Options", value: "nosniff" },
      { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
      { key: "Permissions-Policy", value: "camera=(self)" },
    ] }];
  },
};
export default nextConfig;
