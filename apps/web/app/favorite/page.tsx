import type { Metadata } from 'next';
import { FavoritePageContent } from '@/components/sections/favorite/FavoritePageContent';

export const metadata: Metadata = {
  title: 'Favorite - MuterBandung',
  description: 'Koleksi destinasi, penginapan, dan itinerary favorit Anda.',
};

export default function FavoritePage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <FavoritePageContent />
      </div>
    </div>
  );
}
