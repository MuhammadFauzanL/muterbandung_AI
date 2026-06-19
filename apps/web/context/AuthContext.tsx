"use client";

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { authService, User } from '@/services/auth';

interface AuthContextType {
  isLoggedIn: boolean;
  user: User | null;
  isLoading: boolean;
  login: (token: string, userData?: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const logout = useCallback(() => {
    setIsLoggedIn(false);
    setUser(null);
    localStorage.removeItem('muterbandung_token');
  }, []);

  const fetchUser = useCallback(async () => {
    try {
      const userData = await authService.getMe();
      setUser(userData);
      setIsLoggedIn(true);
    } catch {
      // Hanya log sebagai warning karena token expired adalah siklus wajar
      console.warn('Sesi telah berakhir atau tidak valid. Melakukan logout otomatis...');
      // Jika token expired atau invalid, otomatis logout
      logout();
    } finally {
      setIsLoading(false);
    }
  }, [logout]);

  // Load state from localStorage on mount
  useEffect(() => {
    const timeoutId = window.setTimeout(() => {
      const token = localStorage.getItem('muterbandung_token');
      if (token) {
        void fetchUser();
      } else {
        setIsLoading(false);
      }
    }, 0);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [fetchUser]);

  const login = (token: string, userData?: User) => {
    localStorage.setItem('muterbandung_token', token);
    setIsLoggedIn(true);
    if (userData) {
      setUser(userData);
    } else {
      // Ambil data user jika belum disediakan saat login
      fetchUser();
    }
  };

  return (
    <AuthContext.Provider value={{ isLoggedIn, user, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
