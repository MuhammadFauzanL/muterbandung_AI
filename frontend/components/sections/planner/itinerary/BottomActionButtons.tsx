import Link from 'next/link';
import { ArrowLeft, Download, Share2, Heart } from 'lucide-react';

export function BottomActionButtons() {
  return (
    <div className="mt-16 flex flex-wrap items-center justify-between gap-4 py-8 bg-[#F8F9FA] rounded-[32px] px-8">
      {/* Left Action */}
      <Link 
        href="/planner" 
        className="flex items-center gap-2 rounded-full border border-slate-300 bg-white px-6 py-3 text-xs font-bold text-[#112F43] transition hover:bg-slate-50 shadow-sm"
      >
        <ArrowLeft className="h-4 w-4" />
        Kembali ke AI Planner
      </Link>

      {/* Right Actions */}
      <div className="flex flex-wrap items-center gap-4">
        <button className="flex items-center gap-2 rounded-full bg-[#0B5C73] px-6 py-3 text-xs font-bold text-white transition hover:bg-[#084354] shadow-sm">
          <Download className="h-4 w-4" />
          Download Itinerary
        </button>
        <button className="flex items-center gap-2 rounded-full bg-[#08748C] px-6 py-3 text-xs font-bold text-white transition hover:bg-[#065b6e] shadow-sm">
          <Share2 className="h-4 w-4" />
          Bagikan Perjalanan
        </button>
        <button className="flex items-center gap-2 rounded-full border border-slate-300 bg-white px-6 py-3 text-xs font-bold text-[#E94B35] transition hover:bg-slate-50 shadow-sm">
          <Heart className="h-4 w-4" />
          Simpan
        </button>
      </div>
    </div>
  );
}
