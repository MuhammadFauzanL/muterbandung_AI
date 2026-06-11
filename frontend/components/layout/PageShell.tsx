import type { ReactNode } from 'react';
import { cn } from '@/lib';
import type { NavigationItem } from '@/types';
import { Footer } from './Footer';
import { Header } from './Header';

interface PageShellProps {
  activeItem?: NavigationItem['key'];
  backgroundClassName?: string;
  children: ReactNode;
  footerVariant?: 'default' | 'compact';
  showFooter?: boolean;
}

export function PageShell({
  activeItem = 'home',
  backgroundClassName = 'bg-white',
  children,
  footerVariant = 'default',
  showFooter = true,
}: PageShellProps) {
  return (
    <div
      className={cn(
        'relative min-h-screen text-slate-950',
        backgroundClassName,
      )}
    >
      <Header activeItem={activeItem} />
      {children}
      {showFooter && <Footer variant={footerVariant} />}
    </div>
  );
}
