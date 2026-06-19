"use client";

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default marker icons in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icon creator for numbered markers
const createNumberedIcon = (number: number) => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: #0E75BC; color: white; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; border-radius: 50%; border: 2px solid white; font-weight: bold; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">${number}</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const createHotelIcon = () => {
  return L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: #E94B35; color: white; width: 24px; height: 24px; display: flex; justify-content: center; align-items: center; border-radius: 50%; border: 2px solid white; font-weight: bold; font-size: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.3);">🏨</div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

// Component to handle auto-zooming to fit all markers
function MapBoundsUpdater({ bounds }: { bounds: L.LatLngBoundsExpression }) {
  const map = useMap();
  useEffect(() => {
    if (bounds) {
      map.fitBounds(bounds, { padding: [50, 50] });
    }
  }, [bounds, map]);
  return null;
}

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
  if (points.length === 0) {
    return (
      <MapContainer 
        center={[-6.9175, 107.6191]} 
        zoom={12} 
        style={{ height: '100%', width: '100%', zIndex: 10 }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </MapContainer>
    );
  }

  // Calculate coordinates array for polyline
  const polylineCoords: [number, number][] = points.map(p => [p.lat, p.lng]);
  
  // Calculate bounds
  const bounds = L.latLngBounds(polylineCoords);

  return (
    <MapContainer 
      bounds={bounds}
      style={{ height: '100%', width: '100%', zIndex: 10 }}
      zoomControl={false}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        className="map-tiles-custom"
      />
      
      <Polyline 
        positions={polylineCoords} 
        color="#0E75BC" 
        weight={3} 
        dashArray="5, 10" 
        opacity={0.8}
      />

      {points.map((point, i) => (
        <Marker 
          key={i} 
          position={[point.lat, point.lng]}
          icon={point.type === 'accommodation' ? createHotelIcon() : createNumberedIcon(point.index || i + 1)}
        >
          <Popup>
            <div className="font-bold text-sm">{point.name}</div>
            <div className="text-xs text-gray-500 capitalize">{point.type}</div>
          </Popup>
        </Marker>
      ))}
      
      <MapBoundsUpdater bounds={bounds} />
    </MapContainer>
  );
}
