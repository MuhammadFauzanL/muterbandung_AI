"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';

export type PlannerDestination = {
  id: string;
  title: string;
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
};

interface PlannerContextType {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  addDestination: (dest: PlannerDestination) => void;
  removeDestination: (id: string) => void;
  addAccommodation: (acc: PlannerAccommodation) => void;
  removeAccommodation: (name: string) => void;
}

const PlannerContext = createContext<PlannerContextType | undefined>(undefined);

export function PlannerProvider({ children }: { children: ReactNode }) {
  // Initialize empty
  const [destinations, setDestinations] = useState<PlannerDestination[]>([]);
  const [accommodations, setAccommodationsState] = useState<PlannerAccommodation[]>([]);

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

  return (
    <PlannerContext.Provider
      value={{
        destinations,
        accommodations,
        addDestination,
        removeDestination,
        addAccommodation,
        removeAccommodation,
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
