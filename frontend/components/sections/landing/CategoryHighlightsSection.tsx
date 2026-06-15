/**
 * Category Highlights Section Component
 *
 * Displays a mosaic grid of destination categories.
 * Uses CategoryCard for each category item.
 */
import { CATEGORY_HIGHLIGHTS } from '@/constants';
import { CategoryCard } from '@/components/ui/cards';

export function CategoryHighlightsSection() {
  return (
    <section className="bg-[#F8FBFE] pb-20 pt-16">
      <div className="mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="mb-5 sm:mb-8">
          <h2 className="text-[22px] sm:text-[28px] font-bold text-[#14528E] mb-0.5 sm:mb-1">
            Temukan Tempat lainnya
          </h2>
          <p className="text-[15px] text-slate-500">
            Cari dan temukan tempat lainnya yang ada di Bandung
          </p>
        </div>
        <div className="grid gap-2 sm:gap-5 grid-cols-2 lg:grid-cols-[1.05fr_1fr]">
          <div className="col-span-2 lg:col-span-1 h-full">
            <CategoryCard
              {...CATEGORY_HIGHLIGHTS[0]}
              containerClassName="h-full min-h-[140px] sm:min-h-[300px] lg:min-h-[494px]"
            />
          </div>

          <div className="col-span-2 lg:col-span-1 grid gap-2 sm:gap-5 grid-cols-2 grid-rows-2">
            {/* Caffe (Portrait on the left) */}
            <div className="col-span-1 row-span-2 h-full">
              <CategoryCard
                {...CATEGORY_HIGHLIGHTS[2]}
                containerClassName="h-full min-h-[200px] sm:min-h-[492px]"
              />
            </div>

            {/* Instagramable (Top right) */}
            <div className="col-span-1 row-span-1 h-full">
               <CategoryCard
                 {...CATEGORY_HIGHLIGHTS[1]}
                 containerClassName="h-full min-h-[96px] sm:min-h-[236px]"
               />
            </div>

            {/* Wisata Sejarah (Bottom right) */}
            <div className="col-span-1 row-span-1 h-full">
               <CategoryCard
                 {...CATEGORY_HIGHLIGHTS[3]}
                 containerClassName="h-full min-h-[96px] sm:min-h-[236px]"
               />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
