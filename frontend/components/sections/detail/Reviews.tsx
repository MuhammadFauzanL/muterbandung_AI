import { StarIcon } from '@/components/ui/icons';
import type { DestinationDetail } from '@/types';

export function Reviews({ reviews }: { reviews: DestinationDetail['reviews'] }) {
  return (
    <section className="rounded-2xl border border-[#D9E8F3] bg-white p-5 shadow-[0_12px_28px_rgba(15,23,42,0.05)]">
      <div className="flex items-center justify-between gap-4">
        <h2 className="text-[22px] font-semibold text-slate-950">
          Ulasan Pengunjung
        </h2>
        <a
          href="#reviews"
          className="text-sm font-semibold text-[#0E75BC] hover:text-[#095f99]"
        >
          Lihat Semua
        </a>
      </div>
      <div id="reviews" className="mt-4 grid gap-3 md:grid-cols-3">
        {reviews.map((review) => (
          <article
            key={review.name}
            className="rounded-2xl border border-[#E1EEF6] bg-[#F8FBFE] p-4"
          >
            <div className="flex items-center justify-between gap-3">
              <div>
                <h3 className="text-sm font-semibold text-slate-950">
                  {review.name}
                </h3>
                <p className="text-xs text-slate-500">{review.role}</p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-[#FFF3E2] px-2.5 py-1 text-xs font-semibold text-[#A96916]">
                <StarIcon className="h-4 w-4" size={16} />
                {review.rating}
              </span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              {review.comment}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
