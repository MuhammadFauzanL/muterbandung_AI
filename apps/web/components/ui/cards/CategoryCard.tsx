/**
 * Category Card Component
 *
 * Displays a destination category with overlay text on an image.
 * Used in the Category Highlights section of the landing page.
 */
import { SafeImage } from '@/components/ui/SafeImage';
import type { Category } from '@/types';

interface CategoryCardProps extends Category {
  /** Additional Tailwind classes for layout control (e.g., min-height). */
  containerClassName?: string;
}

export function CategoryCard({
  title,
  description,
  image,
  containerClassName,
}: CategoryCardProps) {
  return (
    <article
      className={`group relative overflow-hidden rounded-[26px] ${containerClassName ?? ''}`}
    >
      <div className="relative h-full w-full">
        <SafeImage
          src={image}
          alt={title}
          fill
          sizes="(min-width: 1024px) 50vw, (min-width: 640px) 50vw, 100vw"
          className="object-cover"
          category={title}
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(15,23,42,0.03)_15%,rgba(15,23,42,0.72)_100%)]" />
      </div>

      <div className="absolute inset-x-0 bottom-0 p-2.5 sm:p-6 text-white">
        <h3 className="text-[13px] sm:text-[26px] font-bold sm:font-medium leading-tight line-clamp-1">{title}</h3>
        {description ? (
          <p className="mt-0.5 sm:mt-3 max-w-[98%] sm:max-w-[88%] text-[9px] sm:text-[15px] leading-[1.3] sm:leading-7 text-white/90 line-clamp-2 sm:line-clamp-none">
            {description}
          </p>
        ) : null}
      </div>
    </article>
  );
}

