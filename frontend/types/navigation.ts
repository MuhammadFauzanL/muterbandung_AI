export interface NavigationItem {
  key: 'home' | 'explore' | 'planner';
  label: string;
  href: string;
}

export interface FooterLink {
  label: string;
  href: string;
}

export type NavigationList = readonly NavigationItem[];
export type FooterLinkList = readonly FooterLink[];
