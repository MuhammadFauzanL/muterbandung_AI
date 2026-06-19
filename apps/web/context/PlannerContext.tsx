"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type PlannerDestination = {
  id: string;
  title: string;
  slug?: string;
  latitude?: number;
  longitude?: number;
  category?: string;
  primaryIntent?: string;
  image?: string;
  distanceKm?: number;
};

export type PlannerAccommodation = {
  name: string;
  basePrice: number;
  guests: number;
  rooms: number;
  nights: number;
  totalPrice: number;
  checkIn: string;
  checkOut: string;
  image?: string;
  rating?: number;
  distance?: string;
  location?: string;
  latitude?: number;
  longitude?: number;
};

const STORAGE_KEY = 'muterbandung_planner_state';

interface StoredPlannerState {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
}

function readStoredPlannerState(): StoredPlannerState {
  if (typeof window === 'undefined') return { destinations: [], accommodations: [] };
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as StoredPlannerState;
      return {
        destinations: Array.isArray(parsed.destinations) ? parsed.destinations : [],
        accommodations: Array.isArray(parsed.accommodations) ? parsed.accommodations : [],
      };
    }
  } catch {
    // ignore corrupt data
  }
  return { destinations: [], accommodations: [] };
}

function writePlannerState(state: StoredPlannerState): void {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // ignore quota errors
  }
}

interface PlannerContextType {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  userLat?: number;
  userLng?: number;
  setUserLocation: (lat: number, lng: number) => void;
  addDestination: (dest: PlannerDestination) => void;
  removeDestination: (id: string) => void;
  addAccommodation: (acc: PlannerAccommodation) => void;
  removeAccommodation: (name: string) => void;
  clearPlanner: () => void;
}

const PlannerContext = createContext<PlannerContextType | undefined>(undefined);

function readStoredLocation(): { lat?: number; lng?: number } {
  if (typeof window === 'undefined') return {};
  try {
    const raw = window.sessionStorage.getItem('muterbandung_location');
    if (raw) {
      const parsed = JSON.parse(raw);
      if (parsed.lat && parsed.lng) return parsed;
    }
  } catch {
    // ignore
  }
  return {};
}

export function PlannerProvider({ children }: { children: ReactNode }) {
  // Initialize from localStorage
  const [destinations, setDestinations] = useState<PlannerDestination[]>([]);
  const [accommodations, setAccommodationsState] = useState<PlannerAccommodation[]>([]);
  const [isHydrated, setIsHydrated] = useState(false);

  // Hydrate from localStorage on mount (client only)
  useEffect(() => {
    const stored = readStoredPlannerState();
    if (stored.destinations.length > 0) {
      setDestinations(stored.destinations);
    }
    if (stored.accommodations.length > 0) {
      setAccommodationsState(stored.accommodations);
    }
    setIsHydrated(true);
  }, []);

  // Persist to localStorage whenever state changes (after hydration)
  useEffect(() => {
    if (!isHydrated) return;
    writePlannerState({ destinations, accommodations });
  }, [destinations, accommodations, isHydrated]);

  // Initialize user location from sessionStorage (set by explore page)
  const stored = readStoredLocation();
  const [userLat, setUserLat] = useState<number | undefined>(stored.lat);
  const [userLng, setUserLng] = useState<number | undefined>(stored.lng);

  const setUserLocation = (lat: number, lng: number) => {
    setUserLat(lat);
    setUserLng(lng);
  };

  const addDestination = (dest: PlannerDestination) => {
    setDestinations((prev) => {
      if (prev.find((d) => d.id === dest.id)) return prev;
      return [...prev, dest];
    });
  };

  const removeDestination = (id: string) => {
    setDestinations((prev) => prev.filter((d) => d.id !== id));
  };

  const addAccommodation = (acc: PlannerAccommodation) => {
    setAccommodationsState((prev) => [...prev, acc]);
  };

  const removeAccommodation = (name: string) => {
    setAccommodationsState((prev) => prev.filter((a) => a.name !== name));
  };

  const clearPlanner = () => {
    setDestinations([]);
    setAccommodationsState([]);
  };

  return (
    <PlannerContext.Provider
      value={{
        destinations,
        accommodations,
        userLat,
        userLng,
        setUserLocation,
        addDestination,
        removeDestination,
        addAccommodation,
        removeAccommodation,
        clearPlanner,
      }}
    >
      {children}
    </PlannerContext.Provider>
  );
}

export function usePlanner() {
  const context = useContext(PlannerContext);
  if (context === undefined) {
    throw new Error('usePlanner must be used within a PlannerProvider');
  }
  return context;
}
