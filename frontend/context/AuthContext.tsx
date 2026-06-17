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

  const fetchUser = useCallback(async () => {
    try {
      const userData = await authService.getMe();
      setUser(userData);
      setIsLoggedIn(true);
    } catch (error) {
      console.error('Gagal mengambil data user:', error);
      // Jika token expired atau invalid, otomatis logout
      logout();
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Load state from localStorage on mount
  useEffect(() => {
    const token = localStorage.getItem('muterbandung_token');
    if (token) {
      fetchUser();
    } else {
      setIsLoading(false);
    }
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

  const logout = () => {
    setIsLoggedIn(false);
    setUser(null);
    localStorage.removeItem('muterbandung_token');
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
