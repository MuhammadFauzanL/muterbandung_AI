"use client";

import { useState, useEffect, useRef } from 'react';

export interface RouteSegment {
  from: { name: string; lat: number; lng: number; type: 'destination' | 'accommodation'; index?: number };
  to: { name: string; lat: number; lng: number; type: 'destination' | 'accommodation'; index?: number };
  geometry: [number, number][]; // [lat, lng][]
  distance: number; // meters
  duration: number; // seconds
}

export interface RouteData {
  segments: RouteSegment[];
  totalDistance: number; // meters
  totalDuration: number; // seconds
  isLoading: boolean;
  error: string | null;
}

export interface RouteCalculation {
  segments: RouteSegment[];
  totalDistance: number;
  totalDuration: number;
  error: string | null;
}

export interface RoutePoint {
  name: string;
  lat: number;
  lng: number;
  type: 'destination' | 'accommodation';
  index?: number;
}

interface OsrmStep {
  geometry?: {
    coordinates?: [number, number][];
  };
}

interface OsrmLeg {
  distance?: number;
  duration?: number;
  steps?: OsrmStep[];
}

interface OsrmRoute {
  legs?: OsrmLeg[];
}

interface OsrmResponse {
  code?: string;
  routes?: OsrmRoute[];
}

const ROUTE_TIMEOUT_MS = 7000;
const routeCache = new Map<string, RouteSegment[]>();

/**
 * Creates a stable fingerprint for the points array to detect real changes.
 */
function getPointsFingerprint(points: RoutePoint[]): string {
  return points.map(p => `${p.lat.toFixed(6)},${p.lng.toFixed(6)}`).join('|');
}

function summarizeSegments(segments: RouteSegment[]): Pick<RouteCalculation, 'totalDistance' | 'totalDuration'> {
  return {
    totalDistance: segments.reduce((sum, segment) => sum + segment.distance, 0),
    totalDuration: segments.reduce((sum, segment) => sum + segment.duration, 0),
  };
}

function createFallbackSegment(from: RoutePoint, to: RoutePoint): RouteSegment {
  return {
    from,
    to,
    geometry: [[from.lat, from.lng], [to.lat, to.lng]],
    distance: haversineDistance(from.lat, from.lng, to.lat, to.lng),
    duration: 0,
  };
}

function createFallbackSegments(points: RoutePoint[]): RouteSegment[] {
  const segments: RouteSegment[] = [];

  for (let i = 0; i < points.length - 1; i++) {
    segments.push(createFallbackSegment(points[i], points[i + 1]));
  }

  return segments;
}

function getLegGeometry(leg: OsrmLeg | undefined, fallback: [number, number][]): [number, number][] {
  const coordinates = leg?.steps?.flatMap((step) => step.geometry?.coordinates || []) || [];
  const geometry = coordinates.map((coord) => [coord[1], coord[0]] as [number, number]);
  return geometry.length >= 2 ? geometry : fallback;
}

/**
 * Fetches all route legs in one OSRM request. This avoids slow serial requests.
 */
async function fetchRouteSegments(points: RoutePoint[], signal: AbortSignal): Promise<RouteSegment[] | null> {
  try {
    const coordinates = points.map((point) => `${point.lng},${point.lat}`).join(';');
    const url = `https://router.project-osrm.org/route/v1/driving/${coordinates}?overview=full&geometries=geojson&steps=true`;
    const response = await fetch(url, { signal });
    if (!response.ok) return null;

    const data = await response.json() as OsrmResponse;
    if (data.code !== 'Ok' || !data.routes || data.routes.length === 0) return null;

    const legs = data.routes[0].legs || [];
    if (legs.length !== points.length - 1) return null;

    return legs.map((leg, index) => {
      const from = points[index];
      const to = points[index + 1];
      const fallbackGeometry: [number, number][] = [[from.lat, from.lng], [to.lat, to.lng]];

      return {
        from,
        to,
        geometry: getLegGeometry(leg, fallbackGeometry),
        distance: leg.distance ?? haversineDistance(from.lat, from.lng, to.lat, to.lng),
        duration: leg.duration ?? 0,
      };
    });
  } catch {
    return null;
  }
}

export async function getRouteCalculation(points: RoutePoint[]): Promise<RouteCalculation> {
  if (points.length < 2) {
    return {
      segments: [],
      totalDistance: 0,
      totalDuration: 0,
      error: 'Rute belum tersedia karena kurang dari 2 lokasi dengan koordinat valid',
    };
  }

  const fingerprint = getPointsFingerprint(points);
  const cachedSegments = routeCache.get(fingerprint);
  if (cachedSegments) {
    return {
      segments: cachedSegments,
      ...summarizeSegments(cachedSegments),
      error: null,
    };
  }

  const controller = new AbortController();
  const timeoutId = window.setTimeout(() => controller.abort(), ROUTE_TIMEOUT_MS);

  try {
    const fetchedSegments = await fetchRouteSegments(points, controller.signal);
    const segments = fetchedSegments || createFallbackSegments(points);
    routeCache.set(fingerprint, segments);

    return {
      segments,
      ...summarizeSegments(segments),
      error: fetchedSegments ? null : 'Rute jalan tidak tersedia, memakai estimasi garis lurus',
    };
  } finally {
    window.clearTimeout(timeoutId);
  }
}

/**
 * Custom hook that fetches real driving routes from OSRM for a set of waypoints.
 */
export function useRouteData(points: RoutePoint[]): RouteData {
  const [segments, setSegments] = useState<RouteSegment[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const latestFingerprintRef = useRef<string>('');
  const fingerprint = getPointsFingerprint(points);

  useEffect(() => {
    // Need at least 2 points for a route
    if (points.length < 2) {
      return;
    }

    let cancelled = false;
    latestFingerprintRef.current = fingerprint;

    async function fetchAllSegments() {
      setIsLoading(true);
      setError(null);

      const result = await getRouteCalculation(points);

      if (!cancelled && latestFingerprintRef.current === fingerprint) {
        setSegments(result.segments);
        setIsLoading(false);
        setError(result.error);
      }
    }

    fetchAllSegments().catch(() => {
      if (!cancelled) {
        setError('Gagal memuat rute perjalanan');
        setIsLoading(false);
      }
    });

    return () => {
      cancelled = true;
    };
  }, [points, fingerprint]);

  const effectiveSegments = points.length < 2 ? [] : segments;
  const totalDistance = effectiveSegments.reduce((sum, s) => sum + s.distance, 0);
  const totalDuration = effectiveSegments.reduce((sum, s) => sum + s.duration, 0);

  return {
    segments: effectiveSegments,
    totalDistance,
    totalDuration,
    isLoading: points.length < 2 ? false : isLoading,
    error: points.length < 2 ? null : error,
  };
}

/**
 * Haversine distance in meters (fallback when OSRM fails)
 */
function haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371000;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
    Math.cos((lat2 * Math.PI) / 180) *
    Math.sin(dLon / 2) *
    Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}
