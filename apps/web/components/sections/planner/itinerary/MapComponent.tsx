"use client";

import { useEffect, useState, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Next.js
const defaultIconPrototype = L.Icon.Default.prototype as L.Icon.Default & {
  _getIconUrl?: unknown;
};
delete defaultIconPrototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// ─── Custom Marker Icons ───────────────────────────────────────
const createNumberedIcon = (number: number) => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `
      <div style="
        position: relative;
        background: linear-gradient(135deg, #0E75BC 0%, #0B5C73 100%);
        color: white;
        width: 32px; height: 32px;
        display: flex; justify-content: center; align-items: center;
        border-radius: 50%;
        border: 3px solid white;
        font-weight: 800; font-size: 14px;
        box-shadow: 0 3px 8px rgba(14,117,188,0.45), 0 0 0 3px rgba(14,117,188,0.15);
        font-family: system-ui, sans-serif;
      ">${number}</div>
    `,
    iconSize: [32, 32],
    iconAnchor: [16, 16],
  });
};

const createHotelIcon = () => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `
      <div style="
        position: relative;
        background: linear-gradient(135deg, #E94B35 0%, #C93A28 100%);
        color: white;
        width: 36px; height: 36px;
        display: flex; justify-content: center; align-items: center;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 3px 8px rgba(233,75,53,0.45), 0 0 0 3px rgba(233,75,53,0.15);
      "><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 21V7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v14"/><path d="M3 11h18"/><path d="M9 21V11"/></svg></div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
};

const createStartIcon = () => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `
      <div style="
        position: relative;
        background: linear-gradient(135deg, #10B981 0%, #059669 100%);
        color: white;
        width: 36px; height: 36px;
        display: flex; justify-content: center; align-items: center;
        border-radius: 50%;
        border: 3px solid white;
        font-weight: 800; font-size: 14px;
        box-shadow: 0 3px 8px rgba(16,185,129,0.45), 0 0 0 3px rgba(16,185,129,0.15);
        font-family: system-ui, sans-serif;
      ">1</div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
  });
};

// ─── OSRM Road Route Fetcher ────────────────────────────────────
async function fetchOSRMRoute(
  waypoints: { lat: number; lng: number }[]
): Promise<[number, number][] | null> {
  if (waypoints.length < 2) return null;

  // Build OSRM coordinates string: lng,lat;lng,lat;...
  const coords = waypoints
    .map((wp) => `${wp.lng},${wp.lat}`)
    .join(';');

  const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=full&geometries=geojson`;

  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const data = await res.json();

    if (data.code !== 'Ok' || !data.routes?.[0]) return null;

    // OSRM returns [lng, lat], Leaflet expects [lat, lng]
    const coordinates: [number, number][] = data.routes[0].geometry.coordinates.map(
      (coord: [number, number]) => [coord[1], coord[0]]
    );

    return coordinates;
  } catch {
    return null;
  }
}

// ─── Extract route metadata from OSRM ──────────────────────────
async function fetchRouteMetadata(
  waypoints: { lat: number; lng: number }[]
): Promise<{ totalDistanceKm: number; totalDurationMin: number } | null> {
  if (waypoints.length < 2) return null;

  const coords = waypoints.map((wp) => `${wp.lng},${wp.lat}`).join(';');
  const url = `https://router.project-osrm.org/route/v1/driving/${coords}?overview=false`;

  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const data = await res.json();
    if (data.code !== 'Ok' || !data.routes?.[0]) return null;

    return {
      totalDistanceKm: Math.round((data.routes[0].distance / 1000) * 10) / 10,
      totalDurationMin: Math.round(data.routes[0].duration / 60),
    };
  } catch {
    return null;
  }
}

// ─── Animated Route Drawing ─────────────────────────────────────
function AnimatedRoute({ routeCoords }: { routeCoords: [number, number][] }) {
  const [visibleCoords, setVisibleCoords] = useState<[number, number][]>([]);
  const animRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (routeCoords.length === 0) return;

    // Animate drawing the route progressively
    const totalPoints = routeCoords.length;
    const step = Math.max(1, Math.floor(totalPoints / 60)); // ~60 frames
    let current = 0;

    const animate = () => {
      current = Math.min(current + step, totalPoints);
      setVisibleCoords(routeCoords.slice(0, current));

      if (current < totalPoints) {
        animRef.current = setTimeout(animate, 16); // ~60fps
      }
    };

    animate();

    return () => {
      if (animRef.current) clearTimeout(animRef.current);
    };
  }, [routeCoords]);

  if (visibleCoords.length < 2) return null;

  return (
    <>
      {/* Shadow line (underneath) */}
      <Polyline
        positions={visibleCoords}
        color="#0B5C73"
        weight={7}
        opacity={0.2}
        lineCap="round"
        lineJoin="round"
      />
      {/* Main route line */}
      <Polyline
        positions={visibleCoords}
        color="#0E75BC"
        weight={4}
        opacity={0.9}
        lineCap="round"
        lineJoin="round"
      />
    </>
  );
}

// ─── Straight-line Fallback ──────────────────────────────────────
function StraightLineFallback({ points }: { points: [number, number][] }) {
  if (points.length < 2) return null;
  return (
    <Polyline
      positions={points}
      color="#0E75BC"
      weight={3}
      dashArray="8, 12"
      opacity={0.6}
      lineCap="round"
    />
  );
}

// ─── Auto-Zoom to Bounds ─────────────────────────────────────────
function MapBoundsUpdater({ bounds }: { bounds: L.LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [60, 60], maxZoom: 15 });
    }
  }, [bounds, map]);
  return null;
}

// ─── Main Component ─────────────────────────────────────────────
interface Point {
  name: string;
  lat: number;
  lng: number;
  type: 'destination' | 'accommodation';
  index?: number;
}

interface MapComponentProps {
  points: Point[];
}

export default function MapComponent({ points }: MapComponentProps) {
  const [routeCoords, setRouteCoords] = useState<[number, number][] | null>(null);
  const [routeMeta, setRouteMeta] = useState<{ totalDistanceKm: number; totalDurationMin: number } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch road route from OSRM when points change
  useEffect(() => {
    let active = true;

    if (points.length < 2) {
      void Promise.resolve().then(() => {
        if (!active) return;
        setRouteCoords(null);
        setRouteMeta(null);
        setIsLoading(false);
      });
      return () => {
        active = false;
      };
    }

    void Promise.resolve().then(() => {
      if (active) setIsLoading(true);
    });

    const waypoints = points.map((p) => ({ lat: p.lat, lng: p.lng }));

    Promise.all([
      fetchOSRMRoute(waypoints),
      fetchRouteMetadata(waypoints),
    ])
      .then(([coords, meta]) => {
        if (!active) return;
        setRouteCoords(coords);
        setRouteMeta(meta);
      })
      .finally(() => {
        if (active) setIsLoading(false);
      });

    return () => {
      active = false;
    };
  }, [points]);

  // Empty state
  if (points.length === 0) {
    return (
      <div className="relative h-full w-full">
        <MapContainer
          center={[-6.9175, 107.6191]}
          zoom={12}
          style={{ height: '100%', width: '100%', zIndex: 10 }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | <a href="https://carto.com">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
          />
        </MapContainer>
        <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none">
          <div className="bg-white/90 backdrop-blur-md px-4 py-3 rounded-xl shadow-lg text-center">
            <p className="text-sm font-bold text-[#112F43]">Belum ada rute</p>
            <p className="text-xs text-slate-500 mt-0.5">Tambahkan destinasi untuk melihat rute perjalanan</p>
          </div>
        </div>
      </div>
    );
  }

  // Calculate bounds
  const polylineCoords: [number, number][] = points.map((p) => [p.lat, p.lng]);
  const bounds = L.latLngBounds(polylineCoords);

  return (
    <div className="relative h-full w-full">
      <MapContainer
        bounds={bounds}
        style={{ height: '100%', width: '100%', zIndex: 10 }}
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> | <a href="https://carto.com">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />

        {/* Route: prefer road route, fallback to straight line */}
        {routeCoords ? (
          <AnimatedRoute routeCoords={routeCoords} />
        ) : (
          <StraightLineFallback points={polylineCoords} />
        )}

        {/* Markers */}
        {points.map((point, i) => {
          const isFirst = i === 0 && point.type === 'destination';
          const icon = point.type === 'accommodation'
            ? createHotelIcon()
            : isFirst
              ? createStartIcon()
              : createNumberedIcon(point.index || i + 1);

          return (
            <Marker key={i} position={[point.lat, point.lng]} icon={icon}>
              <Popup>
                <div style={{ minWidth: 140 }}>
                  <div style={{ fontWeight: 700, fontSize: 14, color: '#112F43', marginBottom: 2 }}>
                    {point.type === 'destination' ? `${point.index || i + 1}. ` : ''}{point.name}
                  </div>
                  <div style={{ fontSize: 11, color: '#557083', textTransform: 'capitalize' }}>
                    {point.type === 'accommodation' ? 'Check-in Hotel' : `Destinasi ke-${point.index || i + 1}`}
                  </div>
                </div>
              </Popup>
            </Marker>
          );
        })}

        <MapBoundsUpdater bounds={bounds} />
      </MapContainer>

      {/* Route Info Overlay */}
      {routeMeta && (
        <div className="absolute bottom-3 right-3 sm:bottom-4 sm:right-4 bg-white/95 backdrop-blur-md px-3 py-2 sm:px-4 sm:py-2.5 rounded-xl shadow-lg border border-slate-200 z-20 pointer-events-none">
          <div className="flex items-center gap-3 sm:gap-4 text-[10px] sm:text-xs">
            <div className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5 text-[#0E75BC]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/></svg>
              <span className="font-bold text-[#112F43]">{routeMeta.totalDistanceKm} km</span>
            </div>
            <div className="w-px h-3 bg-slate-300" />
            <div className="flex items-center gap-1.5">
              <svg className="w-3.5 h-3.5 text-[#0E75BC]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              <span className="font-bold text-[#112F43]">
                {routeMeta.totalDurationMin >= 60
                  ? `${Math.floor(routeMeta.totalDurationMin / 60)}j ${routeMeta.totalDurationMin % 60}m`
                  : `${routeMeta.totalDurationMin} menit`
                }
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {isLoading && (
        <div className="absolute inset-0 bg-white/30 backdrop-blur-[1px] flex items-center justify-center z-20 pointer-events-none">
          <div className="bg-white/95 px-4 py-2.5 rounded-xl shadow-lg flex items-center gap-2.5">
            <div className="w-4 h-4 border-2 border-[#0E75BC] border-t-transparent rounded-full animate-spin" />
            <span className="text-xs font-bold text-[#112F43]">Menghitung rute jalan...</span>
          </div>
        </div>
      )}
    </div>
  );
}
