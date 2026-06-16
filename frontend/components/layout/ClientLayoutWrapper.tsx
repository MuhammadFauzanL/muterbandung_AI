"use client";

import { usePathname } from 'next/navigation';
import { Header } from '@/components/layout/Header';
import { Footer } from '@/components/layout/Footer';

export function ClientLayoutWrapper({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  
  // Rute yang tidak menggunakan layout utama (Header & Footer)
  const noLayoutRoutes = ['/login', '/register', '/forgot-password', '/reset-password'];
  
  const isNoLayoutRoute = noLayoutRoutes.includes(pathname);

  return (
    <>
      {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
      {!isNoLayoutRoute && <Header activeItem={pathname === '/' ? 'home' : pathname.split('/')[1] as any} />}
      
      {/* Konten Utama */}
      <div className="flex-1 flex flex-col">
        {children}
      </div>

      {!isNoLayoutRoute && <Footer />}
    </>
  );
}
