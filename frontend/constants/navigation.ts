/**
 * Navigation Constants
 *
 * Static data for navigation bar and footer links.
 */
import type { NavigationItem, FooterLink } from '@/types';

export const NAVIGATION_ITEMS: readonly NavigationItem[] = [
  { key: 'home', label: 'Home', href: '/' },
  { key: 'explore', label: 'Explore', href: '/explore' },
  { key: 'planner', label: 'AI Planner', href: '/planner' },
] as const;

export const FOOTER_LINKS: readonly FooterLink[] = [
  { label: 'Privasi', href: '#' },
  { label: 'Syarat & Ketentuan', href: '#' },
  { label: 'Hubungi Kami', href: '#' },
] as const;
