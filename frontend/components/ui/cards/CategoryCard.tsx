/**
 * Category Card Component
 *
 * Displays a destination category with overlay text on an image.
 * Used in the Category Highlights section of the landing page.
 */
import Image from 'next/image';
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
      <div className="relative h-full min-h-[236px] w-full lg:min-h-0">
        <Image
          src={image}
          alt={title}
          fill
          sizes="(min-width: 1024px) 50vw, (min-width: 640px) 50vw, 100vw"
          className="object-cover"
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(15,23,42,0.03)_15%,rgba(15,23,42,0.72)_100%)]" />
      </div>

      <div className="absolute inset-x-0 bottom-0 p-6 text-white">
        <h3 className="text-[26px] font-medium leading-tight">{title}</h3>
        {description ? (
          <p className="mt-3 max-w-[88%] text-[15px] leading-7 text-white/82">
            {description}
          </p>
        ) : null}
      </div>
    </article>
  );
}
