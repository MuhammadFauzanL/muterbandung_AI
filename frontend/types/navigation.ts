/**
 * Navigation Types
 *
 * Type definitions for navigation and footer links.
 */

export interface NavigationItem {
  key: 'home' | 'explore' | 'planner' | 'favorite' | 'profile';
  label: string;
  href: string;
}

export interface FooterLink {
  label: string;
  href: string;
}

export type NavigationList = readonly NavigationItem[];
export type FooterLinkList = readonly FooterLink[];
