/**
 * Saved Itineraries Service
 * 
 * CRUD operations for saved itineraries stored in localStorage.
 */

import type { PlannerDestination, PlannerAccommodation } from '@/context/PlannerContext';

const STORAGE_KEY = 'muterbandung_saved_itineraries';

export interface SavedItinerary {
  id: string;
  title: string;
  savedAt: string;
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  totalBudget: number;
  durationDays: number;
  durationNights: number;
  guestCount: number;
}

function generateId(): string {
  return `itn_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

function formatDate(date: Date): string {
  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
    'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des',
  ];
  return `${date.getDate()} ${months[date.getMonth()]} ${date.getFullYear()}`;
}

export function getSavedItineraries(): SavedItinerary[] {
  if (typeof window === 'undefined') return [];
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : [];
    }
  } catch {
    // ignore
  }
  return [];
}

export function saveItinerary(params: {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  totalBudget: number;
  durationDays: number;
  durationNights: number;
  guestCount: number;
}): SavedItinerary {
  const existing = getSavedItineraries();
  
  const newItinerary: SavedItinerary = {
    id: generateId(),
    title: `Perjalanan Bandung — ${formatDate(new Date())}`,
    savedAt: new Date().toISOString(),
    ...params,
  };
  
  existing.unshift(newItinerary); // newest first
  
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(existing));
  } catch {
    // ignore quota errors
  }
  
  return newItinerary;
}

export function deleteItinerary(id: string): void {
  const existing = getSavedItineraries();
  const filtered = existing.filter((item) => item.id !== id);
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch {
    // ignore
  }
}

export function getItineraryCount(): number {
  return getSavedItineraries().length;
}
