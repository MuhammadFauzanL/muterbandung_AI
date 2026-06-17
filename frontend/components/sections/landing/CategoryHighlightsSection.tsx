"use client";

/**
 * Category Highlights Section Component
 *
 * Displays a mosaic grid of destination categories.
 * Uses CategoryCard for each category item.
 */
import { useState, useEffect } from 'react';
import { CategoryCard } from '@/components/ui/cards';
import { destinationsService, HighlightCategory } from '@/services/destinations';

export function CategoryHighlightsSection() {
  const [highlights, setHighlights] = useState<HighlightCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchHighlights() {
      try {
        const data = await destinationsService.getHighlights(4);
        setHighlights(data);
      } catch (error) {
        console.error("Gagal mengambil data highlights:", error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchHighlights();
  }, []);

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
        {isLoading || highlights.length < 4 ? (
          // Skeleton Loading Layout
          <div className="grid gap-2 sm:gap-5 grid-cols-2 lg:grid-cols-[1.05fr_1fr]">
            <div className="col-span-2 lg:col-span-1 h-[140px] sm:h-[300px] lg:h-[494px] bg-slate-200 animate-pulse rounded-[16px] sm:rounded-[24px]"></div>
            <div className="col-span-2 lg:col-span-1 grid gap-2 sm:gap-5 grid-cols-2 grid-rows-2">
              <div className="col-span-1 row-span-2 bg-slate-200 animate-pulse rounded-[16px] sm:rounded-[24px]"></div>
              <div className="col-span-1 row-span-1 bg-slate-200 animate-pulse rounded-[16px] sm:rounded-[24px]"></div>
              <div className="col-span-1 row-span-1 bg-slate-200 animate-pulse rounded-[16px] sm:rounded-[24px]"></div>
            </div>
          </div>
        ) : (
          <div className="grid gap-2 sm:gap-5 grid-cols-2 lg:grid-cols-[1.05fr_1fr]">
            <div className="col-span-2 lg:col-span-1 h-full">
              <CategoryCard
                {...highlights[0]}
                containerClassName="h-full min-h-[140px] sm:min-h-[300px] lg:min-h-[494px]"
              />
            </div>

            <div className="col-span-2 lg:col-span-1 grid gap-2 sm:gap-5 grid-cols-2 grid-rows-2">
              {/* Caffe (Portrait on the left) */}
              <div className="col-span-1 row-span-2 h-full">
                <CategoryCard
                  {...highlights[1]}
                  containerClassName="h-full min-h-[200px] sm:min-h-[492px]"
                />
              </div>

              {/* Instagramable (Top right) */}
              <div className="col-span-1 row-span-1 h-full">
                 <CategoryCard
                   {...highlights[2]}
                   containerClassName="h-full min-h-[96px] sm:min-h-[236px]"
                 />
              </div>

              {/* Wisata Sejarah (Bottom right) */}
              <div className="col-span-1 row-span-1 h-full">
                 <CategoryCard
                   {...highlights[3]}
                   containerClassName="h-full min-h-[96px] sm:min-h-[236px]"
                 />
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
