/**
 * Star Icon Component
 *
 * Reusable SVG icon for ratings and favorites.
 */

interface StarIconProps {
  className?: string;
  size?: number;
  filled?: boolean;
}

export function StarIcon({ className, size = 20, filled = true }: StarIconProps) {
  return (
    <svg
      viewBox="0 0 20 20"
      className={className || 'h-3.5 w-3.5 text-[#F0A22E]'}
      fill={filled ? 'currentColor' : 'none'}
      width={size}
      height={size}
      aria-hidden="true"
    >
      <path d="M10 2.2L12.15 6.56L16.96 7.26L13.48 10.66L14.3 15.45L10 13.19L5.7 15.45L6.52 10.66L3.04 7.26L7.85 6.56L10 2.2Z" />
    </svg>
  );
}
