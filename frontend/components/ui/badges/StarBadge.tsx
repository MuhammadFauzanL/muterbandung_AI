/**
 * Star Badge Component
 *
 * Reusable badge for displaying rating values with a star icon.
 */
import { StarIcon } from '@/components/ui/icons';

interface StarBadgeProps {
  rating: string;
  className?: string;
}

export function StarBadge({ rating, className }: StarBadgeProps) {
  return (
    <div
      className={
        className ||
        'inline-flex items-center gap-1 rounded-full bg-[#FFF3E2] px-2.5 py-1 text-xs font-semibold text-[#5B4630] shadow-sm'
      }
    >
      <StarIcon />
      {rating}
    </div>
  );
}
