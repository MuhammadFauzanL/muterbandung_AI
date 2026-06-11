/**
 * Header Component
 *
 * Top navigation bar with logo and menu items.
 * Renamed from Navigation for semantic clarity.
 */
import Image from 'next/image';
import Link from 'next/link';
import { NAVIGATION_ITEMS } from '@/constants';
import type { NavigationItem } from '@/types';

interface HeaderProps {
  activeItem?: NavigationItem['key'];
}

export function Header({ activeItem = 'home' }: HeaderProps) {
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

        <details className="group relative md:hidden">
          <summary
            className="inline-flex h-10 w-10 cursor-pointer list-none items-center justify-center rounded-xl border border-slate-200 text-[#14528E]"
            aria-label="Buka menu"
          >
            <span className="flex w-5 flex-col gap-1">
              <span className="h-0.5 rounded-full bg-current" />
              <span className="h-0.5 rounded-full bg-current" />
              <span className="h-0.5 rounded-full bg-current" />
            </span>
          </summary>
          <nav className="absolute right-0 top-12 w-48 overflow-hidden rounded-2xl border border-slate-200 bg-white py-2 shadow-[0_18px_35px_rgba(15,23,42,0.16)]">
            {NAVIGATION_ITEMS.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                aria-current={item.key === activeItem ? 'page' : undefined}
                className={`block px-4 py-2.5 text-sm transition-colors ${
                  item.key === activeItem
                    ? 'bg-[#EEF7FD] font-semibold text-[#0E75BC]'
                    : 'font-medium text-[#23689A] hover:bg-slate-50'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </details>
      </div>
    </header>
  );
}
