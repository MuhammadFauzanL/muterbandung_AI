import type { NextConfig } from "next";

const apiUrl = (process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL)?.replace(/\/$/, "");
const hasValidApiUrl = apiUrl?.startsWith("http://") || apiUrl?.startsWith("https://");

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
      },
    ],
  },
  // Izinkan akses dari IP lokal untuk testing mobile
  allowedDevOrigins: ["192.168.1.11"],
  async rewrites() {
    if (!apiUrl || !hasValidApiUrl) {
      return [];
    }

    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
