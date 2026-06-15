/**
 * Footer Component
 *
 * Site footer with branding and links.
 */
import { FOOTER_LINKS } from '@/constants';

export function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-[#8FCCF4] bg-white">
      <div className="mx-auto flex max-w-[1180px] flex-col gap-1.5 sm:gap-3 px-4 py-4 sm:px-8 sm:py-6">
        <h2 className="text-[15px] sm:text-[20px] font-semibold text-slate-950">MuterBandung</h2>
        <p className="text-[11px] sm:text-[16px] text-slate-700">
          © {currentYear} MuterBandung. Sampurasun! Powered by Cepot AI.
        </p>
        <div className="flex flex-wrap gap-3 sm:gap-5 pt-1">
          {FOOTER_LINKS.map((link) => (
            <a
              key={link.label}
              href={link.href}
              className="text-[10px] sm:text-sm font-medium text-slate-500 transition-colors hover:text-[#0E75BC]"
            >
              {link.label}
            </a>
          ))}
        </div>
      </div>
    </footer>
  );
}
