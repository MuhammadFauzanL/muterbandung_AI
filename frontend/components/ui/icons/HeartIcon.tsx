/**
 * Heart Icon Component
 *
 * Reusable SVG icon for favorite/like actions.
 */

interface HeartIconProps {
  className?: string;
  size?: number;
  filled?: boolean;
}

export function HeartIcon({ className, size = 24, filled = false }: HeartIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className || 'h-5 w-5 text-slate-500'}
      fill={filled ? 'currentColor' : 'none'}
      width={size}
      height={size}
      aria-hidden="true"
    >
      <path
        d="M12.1 20.3L12 20.4L11.9 20.3C7.14 16 4 13.16 4 9.67C4 7.2 5.94 5.25 8.4 5.25C9.79 5.25 11.12 5.9 12 6.92C12.88 5.9 14.21 5.25 15.6 5.25C18.06 5.25 20 7.2 20 9.67C20 13.16 16.86 16 12.1 20.3Z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
      />
    </svg>
  );
}
