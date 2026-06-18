import type { NextConfig } from "next";

const apiUrl = (process.env.API_URL ?? process.env.NEXT_PUBLIC_API_URL)?.replace(/\/$/, "");
const hasValidApiUrl = apiUrl?.startsWith("http://") || apiUrl?.startsWith("https://");

const nextConfig: NextConfig = {
  images: {
    // Bypass Next.js Image Optimization proxy to prevent 403
    // from Google Maps Place Photos (signed URLs reject server proxying)
    unoptimized: true,
    remotePatterns: [
      {
        protocol: "https",
        hostname: "images.unsplash.com",
      },
      {
        protocol: "https",
        hostname: "lh3.googleusercontent.com",
      },
      {
        protocol: "https",
        hostname: "dynamic-media-cdn.tripadvisor.com",
      },
    ],
  },
  // Izinkan akses dari IP lokal untuk testing mobile
  allowedDevOrigins: ["192.168.1.11", "192.168.110.246"],
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
