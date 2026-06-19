"use client";

import { useEffect, useState, useCallback, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { RouteSegment } from './useRouteData';

// Fix for default marker icons in Next.js
type LeafletDefaultIconPrototype = L.Icon.Default & { _getIconUrl?: unknown };

delete (L.Icon.Default.prototype as LeafletDefaultIconPrototype)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// ─── Custom Marker Icons ─────────────────────────────────────────────────

function createNumberedIcon(number: number, isActive: boolean = false) {
  const size = isActive ? 36 : 28;
  const fontSize = isActive ? 14 : 12;
  const shadow = isActive
    ? '0 0 0 4px rgba(14,117,188,0.25), 0 4px 12px rgba(14,117,188,0.4)'
    : '0 2px 6px rgba(0,0,0,0.3)';
  const bg = isActive
    ? 'linear-gradient(135deg, #0E75BC 0%, #0A5A93 100%)'
    : 'linear-gradient(135deg, #0E75BC 0%, #1A8DD8 100%)';
  const pulseRing = isActive
    ? `<div style="position:absolute;top:-6px;left:-6px;width:${size + 12}px;height:${size + 12}px;border-radius:50%;border:2px solid rgba(14,117,188,0.4);animation:marker-pulse 2s ease-out infinite;"></div>`
    : '';

  return L.divIcon({
    className: 'custom-marker-icon',
    html: `
      <div style="position:relative;display:flex;align-items:center;justify-content:center;">
        ${pulseRing}
        <div style="
          background: ${bg};
          color: white;
          width: ${size}px;
          height: ${size}px;
          display: flex;
          justify-content: center;
          align-items: center;
          border-radius: 50%;
          border: 3px solid white;
          font-weight: 800;
          font-size: ${fontSize}px;
          box-shadow: ${shadow};
          transition: all 0.3s ease;
          position: relative;
          z-index: 2;
          font-family: 'Inter', sans-serif;
        ">${number}</div>
      </div>
    `,
    iconSize: [size + 12, size + 12],
    iconAnchor: [(size + 12) / 2, (size + 12) / 2],
  });
}

function createHotelIcon(isActive: boolean = false) {
  const size = isActive ? 36 : 28;
  const shadow = isActive
    ? '0 0 0 4px rgba(233,75,53,0.25), 0 4px 12px rgba(233,75,53,0.4)'
    : '0 2px 6px rgba(0,0,0,0.3)';
  const bg = isActive
    ? 'linear-gradient(135deg, #E94B35 0%, #C73425 100%)'
    : 'linear-gradient(135deg, #E94B35 0%, #F06050 100%)';
  const pulseRing = isActive
    ? `<div style="position:absolute;top:-6px;left:-6px;width:${size + 12}px;height:${size + 12}px;border-radius:50%;border:2px solid rgba(233,75,53,0.4);animation:marker-pulse 2s ease-out infinite;"></div>`
    : '';

  return L.divIcon({
    className: 'custom-marker-icon',
    html: `
      <div style="position:relative;display:flex;align-items:center;justify-content:center;">
        ${pulseRing}
        <div style="
          background: ${bg};
          color: white;
          width: ${size}px;
          height: ${size}px;
          display: flex;
          justify-content: center;
          align-items: center;
          border-radius: 50%;
          border: 3px solid white;
          font-weight: 800;
          font-size: ${isActive ? 16 : 13}px;
          box-shadow: ${shadow};
          transition: all 0.3s ease;
          position: relative;
          z-index: 2;
        ">🏨</div>
      </div>
    `,
    iconSize: [size + 12, size + 12],
    iconAnchor: [(size + 12) / 2, (size + 12) / 2],
  });
}

// ─── Segment Colors ──────────────────────────────────────────────────────

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

function getSegmentColor(index: number): string {
  return SEGMENT_COLORS[index % SEGMENT_COLORS.length];
}

// ─── Map Controller (handles all dynamic map updates) ────────────────────

function MapController({
  points,
  segments,
  activeSegmentIndex,
}: {
  points: MapPoint[];
  segments: RouteSegment[];
  activeSegmentIndex: number;
}) {
  const map = useMap();
  const prevActiveRef = useRef(activeSegmentIndex);

  useEffect(() => {
    if (!map) return;

    // Only fit bounds if active segment changed or on first render
    if (activeSegmentIndex >= 0 && activeSegmentIndex < segments.length) {
      const seg = segments[activeSegmentIndex];
      if (seg.geometry.length > 0) {
        const bounds = L.latLngBounds(seg.geometry);
        map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15, animate: true, duration: 0.8 });
      }
    } else if (points.length > 0) {
      // Show all points
      const allCoords = points.map(p => [p.lat, p.lng] as [number, number]);
      const bounds = L.latLngBounds(allCoords);
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15, animate: true, duration: 0.8 });
    }

    prevActiveRef.current = activeSegmentIndex;
  }, [map, activeSegmentIndex, segments, points]);

  return null;
}

// ─── Animated Polyline ───────────────────────────────────────────────────

function AnimatedSegment({
  geometry,
  color,
  isActive,
  segmentIndex,
}: {
  geometry: [number, number][];
  color: string;
  isActive: boolean;
  segmentIndex: number;
}) {
  const [visiblePoints, setVisiblePoints] = useState<[number, number][]>([]);
  const animRef = useRef<number>(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (geometry.length === 0) {
      queueMicrotask(() => setVisiblePoints([]));
      return;
    }

    // Animate the route drawing
    const totalPoints = geometry.length;
    const animDuration = 800; // ms
    let currentIndex = 0;

    // Stagger start based on segment index
    const startDelay = segmentIndex * 300;

    timeoutRef.current = setTimeout(() => {
      function step() {
        currentIndex = Math.min(currentIndex + Math.ceil(totalPoints / (animDuration / 16)), totalPoints);
        setVisiblePoints(geometry.slice(0, currentIndex));

        if (currentIndex < totalPoints) {
          animRef.current = requestAnimationFrame(step);
        }
      }
      step();
    }, startDelay);

    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [geometry, segmentIndex]);

  if (visiblePoints.length < 2) return null;

  return (
    <>
      {/* Shadow line underneath for depth */}
      <Polyline
        positions={visiblePoints}
        color="rgba(0,0,0,0.15)"
        weight={isActive ? 8 : 5}
        opacity={0.5}
        lineCap="round"
        lineJoin="round"
      />
      {/* Main route line */}
      <Polyline
        positions={visiblePoints}
        color={color}
        weight={isActive ? 6 : 4}
        opacity={isActive ? 1 : 0.45}
        lineCap="round"
        lineJoin="round"
        dashArray={isActive ? undefined : "8, 6"}
      />
    </>
  );
}

// ─── Animated Moving Marker ──────────────────────────────────────────────

function MovingMarker({ geometry, color }: { geometry: [number, number][]; color: string }) {
  const [position, setPosition] = useState<[number, number] | null>(null);
  const animRef = useRef<number>(0);

  useEffect(() => {
    if (geometry.length < 2) {
      queueMicrotask(() => setPosition(null));
      return;
    }

    let idx = 0;
    const speed = Math.max(1, Math.floor(geometry.length / 120)); // ~2s loop

    function step() {
      setPosition(geometry[idx]);
      idx = (idx + speed) % geometry.length;
      animRef.current = requestAnimationFrame(step);
    }

    // Small initial delay
    const timeout = setTimeout(() => {
      step();
    }, 200);

    return () => {
      clearTimeout(timeout);
      if (animRef.current) cancelAnimationFrame(animRef.current);
    };
  }, [geometry]);

  if (!position) return null;

  const icon = L.divIcon({
    className: 'custom-marker-icon',
    html: `
      <div style="position:relative;">
        <div style="
          width: 14px;
          height: 14px;
          background: ${color};
          border: 3px solid white;
          border-radius: 50%;
          box-shadow: 0 0 8px ${color}88, 0 2px 6px rgba(0,0,0,0.3);
        "></div>
        <div style="
          position: absolute;
          top: -4px; left: -4px;
          width: 22px; height: 22px;
          border: 2px solid ${color}66;
          border-radius: 50%;
          animation: marker-pulse 1.5s ease-out infinite;
        "></div>
      </div>
    `,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  });

  return <Marker position={position} icon={icon} interactive={false} />;
}

// ─── Main Map Component ──────────────────────────────────────────────────

export interface MapPoint {
  name: string;
  lat: number;
  lng: number;
  type: 'destination' | 'accommodation';
  index?: number;
}

interface InteractiveRouteMapProps {
  points: MapPoint[];
  segments: RouteSegment[];
  activeSegmentIndex: number;
  onMarkerClick?: (pointIndex: number) => void;
  isLoading?: boolean;
}

function formatDistance(meters: number): string {
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

function formatDuration(seconds: number): string {
  if (seconds <= 0) return '-';
  const mins = Math.round(seconds / 60);
  if (mins < 60) return `${mins} mnt`;
  const hours = Math.floor(mins / 60);
  const remainMins = mins % 60;
  return `${hours} jam ${remainMins} mnt`;
}

export default function InteractiveRouteMap({
  points,
  segments,
  activeSegmentIndex,
  onMarkerClick,
  isLoading = false,
}: InteractiveRouteMapProps) {
  // Calculate initial bounds for MapContainer (only used on first render)
  const getInitialBounds = useCallback((): L.LatLngBoundsExpression | undefined => {
    if (points.length > 0) {
      return L.latLngBounds(points.map(p => [p.lat, p.lng] as [number, number]));
    }
    return undefined;
  }, [points]);

  const initialBounds = getInitialBounds();

  // Active segment for the moving marker
  const activeSeg = activeSegmentIndex >= 0 && activeSegmentIndex < segments.length
    ? segments[activeSegmentIndex]
    : null;

  // Empty state
  if (points.length === 0) {
    return (
      <MapContainer
        center={[-6.9175, 107.6191]}
        zoom={12}
        style={{ height: '100%', width: '100%', zIndex: 10 }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
      </MapContainer>
    );
  }

  return (
    <MapContainer
      center={initialBounds ? undefined : [-6.9175, 107.6191]}
      bounds={initialBounds}
      zoom={initialBounds ? undefined : 12}
      style={{ height: '100%', width: '100%', zIndex: 10 }}
      zoomControl={false}
    >
      {/* Premium map tiles — CARTO Voyager for clean look */}
      <TileLayer
        attribution='&copy; <a href="https://carto.com">CARTO</a>'
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
      />

      {/* Dynamic map controller — handles fitBounds on segment changes */}
      <MapController
        points={points}
        segments={segments}
        activeSegmentIndex={activeSegmentIndex}
      />

      {/* Render route segments */}
      {segments.map((seg, i) => (
        <AnimatedSegment
          key={`seg-${i}`}
          geometry={seg.geometry}
          color={getSegmentColor(i)}
          isActive={i === activeSegmentIndex}
          segmentIndex={i}
        />
      ))}

      {/* Moving marker on active segment */}
      {activeSeg && activeSeg.geometry.length > 2 && (
        <MovingMarker
          geometry={activeSeg.geometry}
          color={getSegmentColor(activeSegmentIndex)}
        />
      )}

      {/* Render markers */}
      {points.map((point, i) => {
        const isActive = (
          activeSegmentIndex >= 0 &&
          (i === activeSegmentIndex || i === activeSegmentIndex + 1)
        );

        const icon = point.type === 'accommodation'
          ? createHotelIcon(isActive)
          : createNumberedIcon(point.index || i + 1, isActive);

        return (
          <Marker
            key={`marker-${i}`}
            position={[point.lat, point.lng]}
            icon={icon}
            eventHandlers={{
              click: () => onMarkerClick?.(i),
            }}
          >
            <Popup>
              <div style={{ minWidth: 160 }}>
                <div style={{ fontWeight: 700, fontSize: 14, color: '#112F43', marginBottom: 4 }}>
                  {point.type === 'destination' ? `${point.index || i + 1}. ` : '🏨 '}{point.name}
                </div>
                <div style={{ fontSize: 11, color: '#557083', textTransform: 'capitalize' }}>
                  {point.type === 'destination' ? 'Destinasi Wisata' : 'Penginapan'}
                </div>
                {/* Show distance to next if this is not the last point and segment data exists */}
                {i < segments.length && (
                  <div style={{
                    marginTop: 8,
                    padding: '6px 8px',
                    background: '#F2FAFE',
                    borderRadius: 8,
                    fontSize: 11,
                    color: '#0E75BC',
                    fontWeight: 600,
                  }}>
                    → {segments[i].to.name}: {formatDistance(segments[i].distance)} • {formatDuration(segments[i].duration)}
                  </div>
                )}
              </div>
            </Popup>
          </Marker>
        );
      })}

      {/* Loading overlay */}
      {isLoading && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(255,255,255,0.6)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          pointerEvents: 'none',
        }}>
          <div style={{
            background: 'white',
            padding: '12px 20px',
            borderRadius: 12,
            boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
            fontSize: 13,
            fontWeight: 600,
            color: '#0E75BC',
            display: 'flex',
            alignItems: 'center',
            gap: 8,
          }}>
            <div className="route-spinner" />
            Memuat rute...
          </div>
        </div>
      )}
    </MapContainer>
  );
}
