"use client";
import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, Heart, Check, Loader2 } from 'lucide-react';

export function BottomActionButtons() {
  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloaded, setIsDownloaded] = useState(false);

  const [isSharing, setIsSharing] = useState(false);
  const [isShared, setIsShared] = useState(false);

  const handleAction = (
    setLoading: (v: boolean) => void,
    setSuccess: (v: boolean) => void
  ) => {
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000); // Reset after 3s
    }, 1200); // Fake delay
  };

  return (
    <div className="mt-4 sm:mt-16 flex flex-col sm:flex-row flex-wrap items-center justify-between gap-4 py-5 sm:py-8 bg-[#F8F9FA] rounded-[24px] sm:rounded-[32px] px-4 sm:px-8">
      {/* Mobile grid for the 3 main actions */}
      <div className="flex flex-col sm:flex-row w-full sm:w-auto items-center gap-2.5 sm:gap-4 order-1 sm:order-2">
        
        {/* Simpan Button */}
        <button 
          onClick={() => !isSaving && !isSaved && handleAction(setIsSaving, setIsSaved)}
          className={`flex w-full sm:w-auto justify-center items-center gap-2 rounded-full border px-6 py-2.5 sm:py-3.5 text-[12px] sm:text-[13px] font-bold transition shadow-sm
            ${isSaved 
              ? 'bg-green-50 text-green-600 border-green-200' 
              : 'border-slate-300 bg-white text-[#E94B35] hover:bg-slate-50'
            }`}
        >
          {isSaving ? <Loader2 className="h-4 w-4 animate-spin" /> 
           : isSaved ? <Check className="h-4 w-4" /> 
           : <Heart className="h-4 w-4" />}
          {isSaving ? 'Menyimpan...' : isSaved ? 'Tersimpan!' : 'Simpan ke Profil'}
        </button>

        <div className="grid grid-cols-2 gap-2.5 w-full sm:w-auto">
          {/* Download Button */}
          <button 
            onClick={() => !isDownloading && !isDownloaded && handleAction(setIsDownloading, setIsDownloaded)}
            className={`flex w-full justify-center items-center gap-1.5 sm:gap-2 rounded-full px-3 py-2.5 sm:px-6 sm:py-3.5 text-[11px] sm:text-[13px] font-bold text-white transition shadow-sm
              ${isDownloaded ? 'bg-green-600' : 'bg-[#0B5C73] hover:bg-[#084354]'}`}
          >
            {isDownloading ? <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
             : isDownloaded ? <Check className="h-3 w-3 sm:h-4 sm:w-4" />
             : <Download className="h-3 w-3 sm:h-4 sm:w-4" />}
            {isDownloading ? 'Proses...' : isDownloaded ? 'Selesai!' : 'Download'}
          </button>

          {/* Share Button */}
          <button 
            onClick={() => !isSharing && !isShared && handleAction(setIsSharing, setIsShared)}
            className={`flex w-full justify-center items-center gap-1.5 sm:gap-2 rounded-full px-3 py-2.5 sm:px-6 sm:py-3.5 text-[11px] sm:text-[13px] font-bold text-white transition shadow-sm
              ${isShared ? 'bg-green-600' : 'bg-[#08748C] hover:bg-[#065b6e]'}`}
          >
            {isSharing ? <Loader2 className="h-3 w-3 sm:h-4 sm:w-4 animate-spin" />
             : isShared ? <Check className="h-3 w-3 sm:h-4 sm:w-4" />
             : <Share2 className="h-3 w-3 sm:h-4 sm:w-4" />}
            {isSharing ? 'Memuat...' : isShared ? 'Tersalin!' : 'Bagikan'}
          </button>
        </div>
      </div>

      {/* Left Action (Moved to bottom on mobile) */}
      <Link 
        href="/planner" 
        className="flex w-full sm:w-auto justify-center items-center gap-2 rounded-full px-6 py-2 sm:py-3.5 text-[11px] sm:text-[13px] font-bold text-[#557083] transition hover:text-[#112F43] order-2 sm:order-1"
      >
        <ArrowLeft className="h-4 w-4" />
        Kembali ke AI Planner
      </Link>
    </div>
  );
}
