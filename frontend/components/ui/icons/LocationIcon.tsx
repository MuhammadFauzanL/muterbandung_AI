interface LocationIconProps {
  className?: string;
  size?: number;
}

export function LocationIcon({ className, size = 24 }: LocationIconProps) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className || 'h-3.5 w-3.5 text-[#0E75BC]'}
      fill="none"
      width={size}
      height={size}
      aria-hidden="true"
    >
      <path
        d="M12 13.5A2.5 2.5 0 1 0 12 8.5A2.5 2.5 0 0 0 12 13.5Z"
        stroke="currentColor"
        strokeWidth="1.8"
      />
      <path
        d="M19 10.5C19 15.75 12 21 12 21C12 21 5 15.75 5 10.5A7 7 0 1 1 19 10.5Z"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
