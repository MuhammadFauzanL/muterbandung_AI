import { FOOTER_LINKS } from '@/constants';
import { cn } from '@/lib';

interface FooterProps {
  variant?: 'default' | 'compact';
}

export function Footer({ variant = 'default' }: FooterProps) {
  const currentYear = new Date().getFullYear();
  const isCompact = variant === 'compact';

  return (
    <footer
      className={cn(
        'border-t bg-white',
        isCompact ? 'border-[#D9E8F3]' : 'border-[#8FCCF4]',
      )}
    >
      <div
        className={cn(
          'mx-auto flex max-w-[1180px] flex-col sm:px-8',
          isCompact
            ? 'gap-1 px-4 py-5 text-sm text-slate-500'
            : 'gap-3 px-5 py-6',
        )}
      >
        <h2
          className={cn(
            'font-semibold text-slate-950',
            isCompact ? 'text-sm' : 'text-[20px]',
          )}
        >
          MuterBandung
        </h2>
        <p className={isCompact ? undefined : 'text-[16px] text-slate-700'}>
          © {currentYear} MuterBandung. Sampurasun! Powered by Cepot AI.
        </p>
        {!isCompact && (
          <div className="flex flex-wrap gap-5 pt-1">
            {FOOTER_LINKS.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="text-sm font-medium text-slate-500 transition-colors hover:text-[#0E75BC]"
              >
                {link.label}
              </a>
            ))}
          </div>
        )}
      </div>
    </footer>
  );
}
