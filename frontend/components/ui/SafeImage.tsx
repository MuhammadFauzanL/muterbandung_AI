"use client";

/**
 * SafeImage Component
 *
 * A resilient image component that handles broken/expired external URLs
 * (e.g., Google Maps Place Photos that return 403) by falling back to
 * a gradient placeholder with an icon.
 *
 * Uses native <img> for external URLs to bypass Next.js Image Optimization
 * proxy, which gets blocked by Google's signed URL system.
 */
import { useState, useCallback } from "react";
import Image from "next/image";

/** Category-based fallback colors for visual variety */
const CATEGORY_COLORS: Record<string, string> = {
  "Wisata Alam": "from-emerald-400 to-teal-600",
  "Tempat Kuliner": "from-amber-400 to-orange-600",
  "Rekreasi Keluarga": "from-sky-400 to-blue-600",
  "Taman Kota": "from-lime-400 to-green-600",
  "Tempat Belajar": "from-violet-400 to-purple-600",
  "Tempat Seni": "from-rose-400 to-pink-600",
  "Tempat Sejarah": "from-yellow-400 to-amber-600",
  "Tempat Camping": "from-emerald-500 to-green-700",
  "Wisata Satwa": "from-cyan-400 to-teal-600",
  "Tempat Belanja": "from-fuchsia-400 to-pink-600",
};

const DEFAULT_GRADIENT = "from-slate-300 to-slate-500";

interface SafeImageProps {
  src: string | undefined | null;
  alt: string;
  fill?: boolean;
  width?: number;
  height?: number;
  sizes?: string;
  className?: string;
  priority?: boolean;
  loading?: "eager" | "lazy";
  /** Category name for fallback color matching */
  category?: string;
  /** Custom fallback element (overrides default) */
  fallback?: React.ReactNode;
}

/**
 * Check if URL is from a source known to block server-side proxying.
 * These URLs must be loaded directly by the browser, not through
 * Next.js Image Optimization.
 */
function isBlockedByProxy(url: string): boolean {
  return (
    url.includes("lh3.googleusercontent.com/gps-cs-s") ||
    url.includes("dynamic-media-cdn.tripadvisor.com")
  );
}

/**
 * Check if URL is a local/internal asset that can safely use Next.js Image.
 */
function isLocalAsset(url: string): boolean {
  return url.startsWith("/") && !url.startsWith("//");
}

export function SafeImage({
  src,
  alt,
  fill,
  width,
  height,
  sizes,
  className = "",
  priority = false,
  loading,
  category,
  fallback,
}: SafeImageProps) {
  const [hasError, setHasError] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const handleError = useCallback(() => {
    setHasError(true);
  }, []);

  const handleLoad = useCallback(() => {
    setIsLoaded(true);
  }, []);

  // If no src or error occurred, show fallback
  if (!src || hasError) {
    if (fallback) return <>{fallback}</>;

    const gradient =
      (category && CATEGORY_COLORS[category]) || DEFAULT_GRADIENT;

    return (
      <div
        className={`bg-gradient-to-br ${gradient} flex items-center justify-center ${
          fill ? "absolute inset-0" : ""
        } ${className}`}
        style={!fill && width && height ? { width, height } : undefined}
        role="img"
        aria-label={alt}
      >
        <div className="flex flex-col items-center gap-1.5 text-white/70">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="h-6 w-6 sm:h-8 sm:w-8"
          >
            <rect width="18" height="18" x="3" y="3" rx="2" ry="2" />
            <circle cx="9" cy="9" r="2" />
            <path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21" />
          </svg>
          <span className="text-[9px] sm:text-[11px] font-medium text-center px-2 line-clamp-1">
            {alt}
          </span>
        </div>
      </div>
    );
  }

  // For URLs that get blocked by Next.js Image Optimization proxy,
  // use native <img> to let the browser fetch directly
  if (isBlockedByProxy(src) && !isLocalAsset(src)) {
    return (
      <>
        {/* Loading skeleton shown until image loads */}
        {!isLoaded && (
          <div
            className={`bg-slate-200 animate-pulse ${
              fill ? "absolute inset-0" : ""
            }`}
          />
        )}
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={src}
          alt={alt}
          loading={priority ? "eager" : loading || "lazy"}
          onError={handleError}
          onLoad={handleLoad}
          className={`${className} ${!isLoaded ? "opacity-0" : "opacity-100"} transition-opacity duration-300`}
          style={
            fill
              ? {
                  position: "absolute",
                  top: 0,
                  left: 0,
                  width: "100%",
                  height: "100%",
                  objectFit: "cover",
                }
              : width && height
                ? { width, height }
                : undefined
          }
        />
      </>
    );
  }

  // For safe URLs (Unsplash, local assets), use Next.js Image for optimization
  return (
    <Image
      src={src}
      alt={alt}
      fill={fill}
      width={!fill ? width : undefined}
      height={!fill ? height : undefined}
      sizes={sizes}
      className={className}
      priority={priority}
      loading={!priority ? loading : undefined}
      onError={handleError}
      onLoad={handleLoad}
    />
  );
}
