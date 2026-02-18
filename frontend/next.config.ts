import type { NextConfig } from "next";

const backendUrl = process.env.API_BACKEND_URL;
const publicApiUrl = process.env.NEXT_PUBLIC_API_URL;

if (!backendUrl && !publicApiUrl && process.env.NODE_ENV === "production") {
  console.warn(
    "\n⚠️  WARNING: Neither API_BACKEND_URL nor NEXT_PUBLIC_API_URL is set.\n" +
    "   API calls will fail in production. Set one of:\n" +
    "   - API_BACKEND_URL (for Next.js rewrites/proxy)\n" +
    "   - NEXT_PUBLIC_API_URL (for direct client-side calls)\n"
  );
}

const nextConfig: NextConfig = {
  async rewrites() {
    if (!backendUrl) return [];
    return [
      {
        source: "/api/:path*",
        destination: `${backendUrl}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
