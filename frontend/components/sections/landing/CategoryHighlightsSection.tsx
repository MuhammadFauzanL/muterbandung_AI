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
        <div className="mb-8">
          <h2 className="text-[24px] sm:text-[28px] font-bold text-[#14528E] mb-1">
            Temukan Tempat lainnya
          </h2>
          <p className="text-[15px] text-slate-500">
            Cari dan temukan tempat lainnya yang ada di Bandung
          </p>
        </div>
        <div className="grid gap-5 lg:grid-cols-[1.05fr_1fr]">
          <CategoryCard
            {...CATEGORY_HIGHLIGHTS[0]}
            containerClassName="min-h-[494px]"
          />

          <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-2">
            <div className="sm:col-span-2 h-full">
              <CategoryCard
                {...CATEGORY_HIGHLIGHTS[1]}
                containerClassName="h-full min-h-[236px]"
              />
            </div>
            <CategoryCard
              {...CATEGORY_HIGHLIGHTS[2]}
              containerClassName="min-h-[236px]"
            />
            <CategoryCard
              {...CATEGORY_HIGHLIGHTS[3]}
              containerClassName="min-h-[236px]"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
