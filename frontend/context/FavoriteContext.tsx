"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from 'react';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { userFavoritesService } from '@/services/userFavorites';
import { trackFavoriteAdd, trackFavoriteRemove } from '@/services/userEvents';

interface FavoriteContextType {
  /** Set of favorited destination external IDs (LOC-xxx) */
  favoriteIds: Set<string>;
  /** Whether favorites are still loading from the server */
  isLoading: boolean;
  /** Toggle a destination's favorite status (optimistic) */
  toggleFavorite: (destinationId: string) => Promise<void>;
  /** Check if a destination is favorited */
  isFavorite: (destinationId: string) => boolean;
}

const FavoriteContext = createContext<FavoriteContextType | undefined>(undefined);

export function FavoriteProvider({ children }: { children: ReactNode }) {
  const { isLoggedIn, isLoading: authLoading } = useAuth();
  const { showToast } = useToast();
  const [favoriteIds, setFavoriteIds] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(false);

  // Fetch favorite IDs when user logs in
  useEffect(() => {
    if (authLoading) return;

    let cancelled = false;
    const timeoutId = window.setTimeout(() => {
      if (!isLoggedIn) {
        setFavoriteIds(new Set());
        setIsLoading(false);
        return;
      }

      setIsLoading(true);
      userFavoritesService
        .getFavoriteIds()
        .then((ids) => {
          if (!cancelled) setFavoriteIds(ids);
        })
        .catch(() => {
          // Silently fail because favorites are non-critical.
        })
        .finally(() => {
          if (!cancelled) setIsLoading(false);
        });
    }, 0);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [isLoggedIn, authLoading]);

  const isFavorite = useCallback(
    (destinationId: string) => favoriteIds.has(destinationId),
    [favoriteIds],
  );

  const toggleFavorite = useCallback(
    async (destinationId: string) => {
      if (!isLoggedIn) {
        showToast('Silakan login terlebih dahulu untuk menyimpan favorit', 'error');
        return;
      }

      const wasAlreadyFavorite = favoriteIds.has(destinationId);

      // Optimistic update
      setFavoriteIds((prev) => {
        const next = new Set(prev);
        if (wasAlreadyFavorite) {
          next.delete(destinationId);
        } else {
          next.add(destinationId);
        }
        return next;
      });

      try {
        if (wasAlreadyFavorite) {
          await userFavoritesService.removeFavorite(destinationId);
          trackFavoriteRemove(destinationId);
        } else {
          await userFavoritesService.addFavorite(destinationId);
          trackFavoriteAdd(destinationId);
          showToast('Ditambahkan ke favorit! ❤️', 'success');
        }
      } catch {
        // Rollback on failure
        setFavoriteIds((prev) => {
          const next = new Set(prev);
          if (wasAlreadyFavorite) {
            next.add(destinationId);
          } else {
            next.delete(destinationId);
          }
          return next;
        });
        showToast('Gagal memperbarui favorit. Coba lagi.', 'error');
      }
    },
    [isLoggedIn, favoriteIds, showToast],
  );

  return (
    <FavoriteContext.Provider value={{ favoriteIds, isLoading, toggleFavorite, isFavorite }}>
      {children}
    </FavoriteContext.Provider>
  );
}

export function useFavorite() {
  const context = useContext(FavoriteContext);
  if (context === undefined) {
    throw new Error('useFavorite must be used within a FavoriteProvider');
  }
  return context;
}
