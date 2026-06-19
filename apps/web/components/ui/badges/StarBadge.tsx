/**
 * Star Badge Component
 *
 * Reusable badge for displaying rating values with a star icon.
 */
import { Star } from 'lucide-react';

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
      <Star className="h-3.5 w-3.5 fill-[#FBBF24] text-[#FBBF24]" />
      {rating}
    </div>
  );
}
