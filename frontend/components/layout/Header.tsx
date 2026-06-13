"use client";

/**
 * Header Component
 *
 * Top navigation bar with logo and menu items.
 * Renamed from Navigation for semantic clarity.
 */
import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { NAVIGATION_ITEMS } from '@/constants';
import type { NavigationItem } from '@/types';
import { ChevronDown, User, LogOut, Menu, X } from 'lucide-react';
import { useAuth } from '@/context/AuthContext';

interface HeaderProps {
  activeItem?: NavigationItem['key'];
}

export function Header({ activeItem = 'home' }: HeaderProps) {
  const { isLoggedIn, login, logout } = useAuth();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  return (
    <header className="relative z-20 border-b border-slate-200 bg-white">
      <div className="mx-auto flex h-[68px] max-w-[1180px] items-center justify-between px-3 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-2.5 text-[#14528E]">
          <Image
            src="/images/logo.png"
            alt="Logo MuterBandung"
            width={42}
            height={42}
            className="h-[42px] w-[42px] object-contain"
            preload
          />
          <span className="text-[18px] font-semibold tracking-normal">
            MuterBandung
          </span>
        </Link>

        <nav className="hidden items-center gap-10 md:flex">
          {NAVIGATION_ITEMS.map((item) => (
            <Link
              key={item.label}
              href={item.href}
              aria-current={item.key === activeItem ? 'page' : undefined}
              className={`border-b-2 pb-1 text-[15px] transition-colors ${
                item.key === activeItem
                  ? 'border-[#0E75BC] font-semibold text-[#0E75BC]'
                  : 'border-transparent font-medium text-[#23689A] hover:text-[#0E75BC]'
              }`}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Auth Section */}
        {isLoggedIn ? (
          <div className="hidden md:block relative group z-50">
            <button className="flex items-center gap-2 rounded-full border border-[#0E75BC] p-1 pr-3 bg-white hover:bg-slate-50 transition-colors shadow-sm">
              <div className="h-8 w-8 rounded-full bg-[#EAF6FC] overflow-hidden border border-[#0E75BC]/20">
                <Image src="/images/welcome-cepot.png" alt="Avatar" width={32} height={32} className="object-cover object-top" />
              </div>
              <ChevronDown className="h-4 w-4 text-[#0E75BC]" />
            </button>
            
            <div className="absolute right-0 top-full mt-2 w-48 rounded-xl border border-slate-200 bg-white py-2 shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 transform origin-top-right">
              <Link href="/profile" className="flex items-center gap-3 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 hover:text-[#0E75BC]">
                <User className="h-4 w-4" /> Lihat Profil
              </Link>
              <button onClick={logout} className="w-full flex items-center gap-3 px-4 py-2 text-sm font-bold text-red-500 hover:bg-red-50">
                <LogOut className="h-4 w-4" /> Logout
              </button>
            </div>
          </div>
        ) : (
          <div className="hidden md:flex items-center gap-3">
            <button
              onClick={login}
              className="rounded-full border border-[#0E75BC] px-6 py-2 text-sm font-semibold text-[#0E75BC] transition-colors hover:bg-[#EEF7FD]"
            >
              Masuk
            </button>
            <button
              onClick={login}
              className="rounded-full bg-[#0E75BC] px-6 py-2 text-sm font-semibold text-white transition-colors hover:bg-[#095f99]"
            >
              Daftar
            </button>
          </div>
        )}

        {/* Mobile Menu Toggle Button */}
        <button
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 text-[#14528E] md:hidden"
          onClick={() => setIsMobileMenuOpen(true)}
          aria-label="Buka menu"
        >
          <Menu className="h-5 w-5" />
        </button>

        {/* Mobile Drawer Overlay */}
        {isMobileMenuOpen && (
          <div className="fixed inset-0 z-[100] md:hidden">
            {/* Backdrop */}
            <div 
              className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity"
              onClick={() => setIsMobileMenuOpen(false)}
            />
            
            {/* Drawer */}
            <div className="absolute inset-y-0 right-0 w-[280px] bg-white shadow-2xl animate-in slide-in-from-right flex flex-col">
              <div className="flex items-center justify-between border-b border-slate-100 p-4">
                <span className="text-[16px] font-bold text-[#14528E]">Menu</span>
                <button
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="rounded-full p-2 text-slate-500 hover:bg-slate-100 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto py-4">
                {/* Mobile Auth Header */}
                <div className="px-5 pb-6 border-b border-slate-100 mb-4">
                  {isLoggedIn ? (
                    <div className="flex items-center gap-3">
                      <div className="h-10 w-10 rounded-full bg-[#EAF6FC] overflow-hidden border border-[#0E75BC]/20">
                        <Image src="/images/welcome-cepot.png" alt="Avatar" width={40} height={40} className="object-cover object-top" />
                      </div>
                      <div>
                        <p className="text-[14px] font-bold text-slate-800">Halo, Pengguna</p>
                        <Link href="/profile" onClick={() => setIsMobileMenuOpen(false)} className="text-[12px] font-medium text-[#0E75BC] hover:underline">Lihat Profil</Link>
                      </div>
                    </div>
                  ) : (
                    <div className="flex flex-col gap-3">
                      <button
                        onClick={() => { login(); setIsMobileMenuOpen(false); }}
                        className="w-full rounded-full bg-[#0E75BC] px-6 py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#095f99]"
                      >
                        Daftar / Masuk
                      </button>
                    </div>
                  )}
                </div>

                {/* Mobile Navigation Links */}
                <nav className="flex flex-col px-3">
                  {NAVIGATION_ITEMS.map((item) => (
                    <Link
                      key={item.label}
                      href={item.href}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`block rounded-xl px-4 py-3 text-[15px] transition-colors ${
                        item.key === activeItem
                          ? 'bg-[#EEF7FD] font-semibold text-[#0E75BC]'
                          : 'font-medium text-[#23689A] hover:bg-slate-50'
                      }`}
                    >
                      {item.label}
                    </Link>
                  ))}
                </nav>
              </div>

              {/* Mobile Auth Footer */}
              {isLoggedIn && (
                <div className="border-t border-slate-100 p-4">
                  <button
                    onClick={() => { logout(); setIsMobileMenuOpen(false); }}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-red-50 py-3 text-[14px] font-bold text-red-600 transition-colors hover:bg-red-100"
                  >
                    <LogOut className="h-4 w-4" /> Logout
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
