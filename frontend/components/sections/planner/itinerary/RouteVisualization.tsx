"use client";

import { useState, useMemo, useCallback, useEffect } from 'react';
import { Map, Navigation, Clock, Route, ChevronLeft, ChevronRight, Locate, ArrowRight } from 'lucide-react';
import dynamic from 'next/dynamic';
import { destinationsService } from '@/services/destinations';
import { useRouteData, type RoutePoint } from './useRouteData';

const DynamicMap = dynamic(() => import('./MapComponent'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gradient-to-br from-slate-100 to-slate-50 animate-pulse flex flex-col items-center justify-center gap-3">
      <div className="route-spinner" />
      <span className="text-sm font-medium text-slate-400">Memuat Peta...</span>
    </div>
  )
});

interface Location {
  id?: string;
  slug?: string;
  latitude?: number;
  longitude?: number;
  title?: string;
  name?: string;
}

interface RouteVisualizationProps {
  destinations: Location[];
  accommodations?: Location[];
}

function formatDistance(meters: number): string {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

function formatDuration(seconds: number): string {
  if (seconds <= 0) return '-';
  const mins = Math.round(seconds / 60);
  if (mins < 60) return `${mins} menit`;
  const hours = Math.floor(mins / 60);
  const remainMins = mins % 60;
  if (remainMins === 0) return `${hours} jam`;
  return `${hours} jam ${remainMins} mnt`;
}

const SEGMENT_COLORS = [
  '#0E75BC',
  '#6366F1',
  '#10B981',
  '#F59E0B',
  '#EC4899',
  '#8B5CF6',
  '#14B8A6',
  '#F97316',
];

type Coordinates = { latitude: number; longitude: number };

function getValidCoordinates(latitude?: number, longitude?: number): Coordinates | null {
  if (
    typeof latitude !== 'number' ||
    typeof longitude !== 'number' ||
    !Number.isFinite(latitude) ||
    !Number.isFinite(longitude) ||
    latitude < -90 ||
    latitude > 90 ||
    longitude < -180 ||
    longitude > 180
  ) {
    return null;
  }

  return { latitude, longitude };
}

function getDestinationKey(destination: Location, index: number): string {
  return destination.slug || destination.id || destination.title || `destination-${index}`;
}

function getResolvedCoordinates(
  location: Location,
  resolvedCoordinates: Record<string, Coordinates>,
  key: string,
): Coordinates | null {
  return getValidCoordinates(location.latitude, location.longitude) || resolvedCoordinates[key] || null;
}

export function RouteVisualization({ destinations, accommodations = [] }: RouteVisualizationProps) {
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(0);
  const [resolvedDestinationCoordinates, setResolvedDestinationCoordinates] = useState<Record<string, Coordinates>>({});

  useEffect(() => {
    let cancelled = false;

    const missingDestinations = destinations
      .map((destination, index) => ({
        destination,
        key: getDestinationKey(destination, index),
        lookupSlug: destination.slug || destination.id,
      }))
      .filter(({ destination, key, lookupSlug }) => (
        !!lookupSlug &&
        !getValidCoordinates(destination.latitude, destination.longitude) &&
        !resolvedDestinationCoordinates[key]
      ));

    if (missingDestinations.length === 0) return;

    async function resolveMissingCoordinates() {
      const results = await Promise.all(
        missingDestinations.map(async ({ key, lookupSlug }) => {
          if (!lookupSlug) return null;

          try {
            const detail = await destinationsService.getBySlug(lookupSlug);
            const coordinates = getValidCoordinates(detail.latitude, detail.longitude);
            return coordinates ? { key, coordinates } : null;
          } catch {
            return null;
          }
        }),
      );

      if (cancelled) return;

      setResolvedDestinationCoordinates((current) => {
        let changed = false;
        const next = { ...current };

        results.forEach((result) => {
          if (!result) return;
          next[result.key] = result.coordinates;
          changed = true;
        });

        return changed ? next : current;
      });
    }

    resolveMissingCoordinates();

    return () => {
      cancelled = true;
    };
  }, [destinations, resolvedDestinationCoordinates]);

  // Track which items are missing coordinates
  const missingCoordItems = useMemo(() => {
    const items: string[] = [];
    destinations.forEach((d, index) => {
      const key = getDestinationKey(d, index);
      if (!getResolvedCoordinates(d, resolvedDestinationCoordinates, key)) {
        items.push(d.title || 'Destinasi');
      }
    });
    accommodations.forEach(a => {
      if (!getValidCoordinates(a.latitude, a.longitude)) items.push(a.name || 'Penginapan');
    });
    return items;
  }, [destinations, accommodations, resolvedDestinationCoordinates]);

  // Construct points array
  const points: RoutePoint[] = useMemo(() => {
    const result: RoutePoint[] = [];
    let destIndex = 1;

    destinations.forEach((d, index) => {
      const key = getDestinationKey(d, index);
      const coordinates = getResolvedCoordinates(d, resolvedDestinationCoordinates, key);

      if (coordinates) {
        result.push({
          name: d.title || 'Destinasi',
          lat: coordinates.latitude,
          lng: coordinates.longitude,
          type: 'destination',
          index: destIndex,
        });
      }
      destIndex++;
    });

    accommodations.forEach(a => {
      const coordinates = getValidCoordinates(a.latitude, a.longitude);

      if (coordinates) {
        result.push({
          name: a.name || 'Penginapan',
          lat: coordinates.latitude,
          lng: coordinates.longitude,
          type: 'accommodation',
        });
      }
    });

    return result;
  }, [destinations, accommodations, resolvedDestinationCoordinates]);

  // Fetch real routes
  const { segments, totalDistance, totalDuration, isLoading, error } = useRouteData(points);
  const safeActiveSegmentIndex = activeSegmentIndex === -1
    ? -1
    : Math.min(activeSegmentIndex, Math.max(segments.length - 1, 0));

  const handlePrev = useCallback(() => {
    setActiveSegmentIndex(prev => Math.max(0, prev - 1));
  }, []);

  const handleNext = useCallback(() => {
    setActiveSegmentIndex(prev => Math.min(segments.length - 1, prev + 1));
  }, [segments.length]);

  const handleMarkerClick = useCallback((pointIndex: number) => {
    // If clicking a point, activate the segment that starts from it
    if (pointIndex < segments.length) {
      setActiveSegmentIndex(pointIndex);
    } else if (pointIndex > 0) {
      // If clicking last point, activate last segment
      setActiveSegmentIndex(segments.length - 1);
    }
  }, [segments.length]);

  const handleViewAll = useCallback(() => {
    setActiveSegmentIndex(-1);
  }, []);

  const hasRoutes = segments.length > 0;
  const activeSeg = safeActiveSegmentIndex >= 0 && safeActiveSegmentIndex < segments.length
    ? segments[safeActiveSegmentIndex]
    : null;

  return (
    <section className="mb-4 sm:mb-10">
      {/* Section Header */}
      <div className="flex items-center justify-between gap-2 mb-3 sm:mb-4">
        <div className="flex items-center gap-2 text-[#112F43]">
          <div className="flex items-center justify-center w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-br from-[#0E75BC] to-[#0A5A93] shadow-md">
            <Map className="h-4 w-4 sm:h-5 sm:w-5 text-white" />
          </div>
          <div>
            <h3 className="font-bold text-[15px] sm:text-lg leading-tight">Visualisasi Rute Perjalanan</h3>
            <p className="text-[10px] sm:text-xs text-[#557083] font-medium">Rute driving aktual antar destinasi</p>
          </div>
        </div>

        {hasRoutes && (
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* View All Button */}
            <button
              onClick={handleViewAll}
              className={`flex items-center gap-1 px-2.5 py-1.5 sm:px-3 sm:py-2 rounded-lg text-[10px] sm:text-xs font-semibold transition-all ${
                safeActiveSegmentIndex === -1
                  ? 'bg-[#0E75BC] text-white shadow-md'
                  : 'bg-white border border-slate-200 text-[#557083] hover:border-[#0E75BC] hover:text-[#0E75BC]'
              }`}
            >
              <Locate className="w-3 h-3" />
              <span className="hidden sm:inline">Semua</span>
            </button>
          </div>
        )}
      </div>

      {/* Map Container */}
      <div className="relative w-full rounded-[16px] sm:rounded-[24px] bg-slate-100 overflow-hidden shadow-lg border border-[#CFE5F2] route-map-container">
        {/* Map */}
        <div className="w-full h-[280px] sm:h-[450px]">
          <DynamicMap
            points={points}
            segments={segments}
            activeSegmentIndex={safeActiveSegmentIndex}
            onMarkerClick={handleMarkerClick}
            isLoading={isLoading}
          />
        </div>

        {/* Active Segment Info Overlay (top-left) */}
        {activeSeg && !isLoading && (
          <div className="absolute top-3 left-3 sm:top-4 sm:left-4 z-20 route-info-overlay">
            <div className="bg-white/90 backdrop-blur-xl rounded-2xl shadow-xl border border-white/50 p-3 sm:p-4 max-w-[260px] sm:max-w-[300px]">
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="w-3 h-3 rounded-full shrink-0"
                  style={{ backgroundColor: SEGMENT_COLORS[safeActiveSegmentIndex % SEGMENT_COLORS.length] }}
                />
                <span className="text-[10px] sm:text-[11px] font-bold text-[#557083] uppercase tracking-wide">
                  Rute {safeActiveSegmentIndex + 1} / {segments.length}
                </span>
              </div>

              <div className="flex items-center gap-1.5 mb-2.5">
                <span className="text-[12px] sm:text-[13px] font-bold text-[#112F43] truncate">
                  {activeSeg.from.name}
                </span>
                <ArrowRight className="w-3 h-3 text-[#0E75BC] shrink-0" />
                <span className="text-[12px] sm:text-[13px] font-bold text-[#112F43] truncate">
                  {activeSeg.to.name}
                </span>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1">
                  <Route className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[11px] sm:text-[12px] font-semibold text-[#112F43]">
                    {formatDistance(activeSeg.distance)}
                  </span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[11px] sm:text-[12px] font-semibold text-[#112F43]">
                    {formatDuration(activeSeg.duration)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Step Navigation (bottom) */}
        {hasRoutes && !isLoading && (
          <div className="absolute bottom-3 left-1/2 -translate-x-1/2 z-20">
            <div className="flex items-center gap-2 bg-white/90 backdrop-blur-xl rounded-full shadow-xl border border-white/50 px-2 py-1.5 sm:px-3 sm:py-2">
              <button
                onClick={handlePrev}
                disabled={safeActiveSegmentIndex <= 0}
                className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#F2FAFE] text-[#0E75BC] hover:bg-[#0E75BC] hover:text-white transition-all disabled:opacity-30 disabled:hover:bg-[#F2FAFE] disabled:hover:text-[#0E75BC]"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <div className="flex items-center gap-1 px-1.5 sm:px-3">
                {segments.map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setActiveSegmentIndex(i)}
                    className="transition-all"
                    style={{
                      width: i === safeActiveSegmentIndex ? 20 : 8,
                      height: 8,
                      borderRadius: 4,
                      backgroundColor: i === safeActiveSegmentIndex
                        ? SEGMENT_COLORS[i % SEGMENT_COLORS.length]
                        : '#CBD5E1',
                      transition: 'all 0.3s ease',
                    }}
                  />
                ))}
              </div>

              <button
                onClick={handleNext}
                disabled={safeActiveSegmentIndex >= segments.length - 1}
                className="flex items-center justify-center w-7 h-7 sm:w-8 sm:h-8 rounded-full bg-[#F2FAFE] text-[#0E75BC] hover:bg-[#0E75BC] hover:text-white transition-all disabled:opacity-30 disabled:hover:bg-[#F2FAFE] disabled:hover:text-[#0E75BC]"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}

        {/* Total Summary Badge (top-right) */}
        {hasRoutes && !isLoading && (
          <div className="absolute top-3 right-3 sm:top-4 sm:right-4 z-20">
            <div className="bg-white/90 backdrop-blur-xl rounded-xl shadow-lg border border-white/50 px-3 py-2 sm:px-4 sm:py-2.5">
              <div className="flex items-center gap-2 sm:gap-3">
                <div className="flex items-center gap-1">
                  <Navigation className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[10px] sm:text-xs font-bold text-[#112F43]">
                    {formatDistance(totalDistance)}
                  </span>
                </div>
                <div className="w-px h-3 bg-slate-200" />
                <div className="flex items-center gap-1">
                  <Clock className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[10px] sm:text-xs font-bold text-[#112F43]">
                    {formatDuration(totalDuration)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Warning for items missing coordinates */}
      {missingCoordItems.length > 0 && (
        <div className="mt-2.5 sm:mt-3 flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2.5 sm:px-4 sm:py-3">
          <span className="text-amber-500 text-sm mt-0.5 shrink-0">⚠️</span>
          <div>
            <p className="text-[11px] sm:text-[12px] font-semibold text-amber-800">
              {missingCoordItems.length} lokasi tidak memiliki data koordinat:
            </p>
            <p className="text-[10px] sm:text-[11px] text-amber-700 mt-0.5">
              {missingCoordItems.join(', ')} — tidak ditampilkan di peta
            </p>
          </div>
        </div>
      )}

      {error && points.length >= 2 && (
        <div className="mt-2.5 sm:mt-3 rounded-xl border border-sky-200 bg-sky-50 px-3 py-2.5 text-[11px] font-semibold text-sky-800 sm:px-4 sm:py-3 sm:text-[12px]">
          {error}
        </div>
      )}

      {/* Route Legend Panel */}
      {hasRoutes && !isLoading && (
        <div className="mt-3 sm:mt-4 rounded-[16px] sm:rounded-[20px] border border-[#CFE5F2] bg-gradient-to-br from-white via-white to-[#F2FAFE] p-3 sm:p-5 shadow-sm">
          <div className="flex items-center justify-between mb-3 sm:mb-4">
            <h4 className="text-[12px] sm:text-[14px] font-bold text-[#112F43] flex items-center gap-2">
              <Route className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-[#0E75BC]" />
              Detail Rute Perjalanan
            </h4>
            <div className="text-[10px] sm:text-[11px] font-semibold text-[#557083] bg-[#F2FAFE] px-2.5 py-1 rounded-full">
              {segments.length} segment
            </div>
          </div>

          <div className="space-y-2 sm:space-y-2.5">
            {segments.map((seg, i) => {
              const isActive = i === safeActiveSegmentIndex;
              const color = SEGMENT_COLORS[i % SEGMENT_COLORS.length];

              return (
                <button
                  key={i}
                  onClick={() => setActiveSegmentIndex(i)}
                  className={`w-full flex items-center gap-3 sm:gap-4 p-2.5 sm:p-3.5 rounded-xl sm:rounded-2xl transition-all text-left group ${
                    isActive
                      ? 'bg-white shadow-md border-2 scale-[1.01]'
                      : 'bg-white/60 border border-transparent hover:bg-white hover:shadow-sm hover:border-slate-100'
                  }`}
                  style={isActive ? { borderColor: color } : {}}
                >
                  {/* Segment indicator */}
                  <div className="flex flex-col items-center gap-0.5 shrink-0">
                    <div
                      className="w-6 h-6 sm:w-7 sm:h-7 rounded-full flex items-center justify-center text-white text-[10px] sm:text-[11px] font-bold shadow-sm"
                      style={{ backgroundColor: color }}
                    >
                      {i + 1}
                    </div>
                    <div
                      className="w-0.5 h-3 sm:h-4 rounded-full"
                      style={{ backgroundColor: isActive ? color : '#E2E8F0' }}
                    />
                  </div>

                  {/* Segment Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-1.5 mb-0.5">
                      <span className={`text-[11px] sm:text-[13px] font-bold truncate ${isActive ? 'text-[#112F43]' : 'text-[#557083]'}`}>
                        {seg.from.name}
                      </span>
                      <ArrowRight className="w-3 h-3 text-slate-300 shrink-0" />
                      <span className={`text-[11px] sm:text-[13px] font-bold truncate ${isActive ? 'text-[#112F43]' : 'text-[#557083]'}`}>
                        {seg.to.name}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 sm:gap-3 mt-0.5">
                      <span className={`text-[10px] sm:text-[11px] font-semibold flex items-center gap-0.5 ${isActive ? 'text-[#0E75BC]' : 'text-slate-400'}`}>
                        <Route className="w-2.5 h-2.5" />
                        {formatDistance(seg.distance)}
                      </span>
                      <span className={`text-[10px] sm:text-[11px] font-semibold flex items-center gap-0.5 ${isActive ? 'text-[#0E75BC]' : 'text-slate-400'}`}>
                        <Clock className="w-2.5 h-2.5" />
                        {formatDuration(seg.duration)}
                      </span>
                    </div>
                  </div>

                  {/* Active indicator */}
                  <div className={`w-2 h-2 rounded-full shrink-0 transition-all ${isActive ? 'scale-100' : 'scale-0 group-hover:scale-75'}`}
                    style={{ backgroundColor: color }}
                  />
                </button>
              );
            })}
          </div>

          {/* Total Summary Bar */}
          <div className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-[#CFE5F2]">
            <div className="flex items-center justify-between">
              <span className="text-[11px] sm:text-[13px] font-bold text-[#112F43]">Total Perjalanan</span>
              <div className="flex items-center gap-3 sm:gap-4">
                <div className="flex items-center gap-1.5 bg-[#F2FAFE] px-3 py-1.5 rounded-full">
                  <Navigation className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[11px] sm:text-[12px] font-bold text-[#0E75BC]">
                    {formatDistance(totalDistance)}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 bg-[#F2FAFE] px-3 py-1.5 rounded-full">
                  <Clock className="w-3 h-3 text-[#0E75BC]" />
                  <span className="text-[11px] sm:text-[12px] font-bold text-[#0E75BC]">
                    {formatDuration(totalDuration)}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Loading State for Legend */}
      {isLoading && points.length >= 2 && (
        <div className="mt-3 sm:mt-4 rounded-[16px] sm:rounded-[20px] border border-[#CFE5F2] bg-white p-4 sm:p-5">
          <div className="flex items-center gap-3">
            <div className="route-spinner" />
            <div>
              <p className="text-[12px] sm:text-[13px] font-semibold text-[#112F43]">Menghitung rute optimal...</p>
              <p className="text-[10px] sm:text-[11px] text-[#557083]">Mengambil data jarak dan waktu tempuh</p>
            </div>
          </div>
        </div>
      )}

      {/* No route data message */}
      {!isLoading && points.length < 2 && (
        <div className="mt-3 sm:mt-4 rounded-[16px] sm:rounded-[20px] border border-dashed border-[#CFE5F2] bg-[#F9FCFE] p-4 sm:p-6 text-center">
          <Map className="w-8 h-8 mx-auto text-[#CFE5F2] mb-2" />
          <p className="text-[12px] sm:text-[13px] font-semibold text-[#557083]">
            {destinations.length + accommodations.length >= 2
              ? 'Koordinat lokasi belum lengkap'
              : 'Tambahkan minimal 2 lokasi'}
          </p>
          <p className="text-[10px] sm:text-[11px] text-[#8DA3B2]">
            {destinations.length + accommodations.length >= 2
              ? 'Peta hanya menampilkan wisata atau penginapan dengan koordinat valid'
              : 'untuk melihat rute perjalanan'}
          </p>
        </div>
      )}
    </section>
  );
}
