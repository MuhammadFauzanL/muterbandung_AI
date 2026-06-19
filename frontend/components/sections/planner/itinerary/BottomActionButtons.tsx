"use client";
import { useState, useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, Heart, Check, Loader2 } from 'lucide-react';
import { usePlanner } from '@/context/PlannerContext';
import { useToast } from '@/context/ToastContext';
import { saveItinerary } from '@/services/savedItineraries';
import type { PlannerDestination, PlannerAccommodation } from '@/context/PlannerContext';

interface BottomActionButtonsProps {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  totalBudget: number;
  durationDays: number;
  durationNights: number;
  guestCount: number;
  durationString: string;
  /** Ref to the itinerary content area for PDF capture */
  contentRef?: React.RefObject<HTMLElement | null>;
}

export function BottomActionButtons({
  destinations,
  accommodations,
  totalBudget,
  durationDays,
  durationNights,
  guestCount,
  durationString,
  contentRef,
}: BottomActionButtonsProps) {
  const { showToast } = useToast();

  const [isSaving, setIsSaving] = useState(false);
  const [isSaved, setIsSaved] = useState(false);

  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloaded, setIsDownloaded] = useState(false);

  const [isSharing, setIsSharing] = useState(false);
  const [isShared, setIsShared] = useState(false);

  // ─── Simpan ke Profil ────────────────────────────────
  const handleSave = () => {
    if (isSaving || isSaved) return;
    if (destinations.length === 0 && accommodations.length === 0) {
      showToast('Tambahkan destinasi atau penginapan terlebih dahulu', 'error');
      return;
    }

    setIsSaving(true);
    // Small delay for UX feel
    setTimeout(() => {
      saveItinerary({
        destinations,
        accommodations,
        totalBudget,
        durationDays,
        durationNights,
        guestCount,
      });
      setIsSaving(false);
      setIsSaved(true);
      showToast('Itinerary berhasil disimpan ke profil!', 'success');
      setTimeout(() => setIsSaved(false), 4000);
    }, 600);
  };

  // ─── Download PDF ────────────────────────────────────
  const handleDownload = async () => {
    if (isDownloading || isDownloaded) return;
    if (destinations.length === 0 && accommodations.length === 0) {
      showToast('Tambahkan destinasi terlebih dahulu', 'error');
      return;
    }

    setIsDownloading(true);

    try {
      // Dynamic import to avoid SSR issues
      const [{ default: jsPDF }, { default: html2canvas }] = await Promise.all([
        import('jspdf'),
        import('html2canvas'),
      ]);

      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      const margin = 15;
      let yPos = margin;

      // ── Header Band ──
      pdf.setFillColor(14, 117, 188); // #0E75BC
      pdf.rect(0, 0, pageWidth, 35, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text('MuterBandung', margin, 15);
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text('AI-Powered Travel Planner', margin, 22);
      pdf.setFontSize(9);
      pdf.text(`Dibuat: ${new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}`, margin, 29);

      yPos = 45;

      // ── Title ──
      pdf.setTextColor(17, 47, 67); // #112F43
      pdf.setFontSize(18);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Itinerary Perjalanan Bandung', margin, yPos);
      yPos += 10;

      // ── Summary Chips ──
      pdf.setFillColor(234, 246, 252); // #EAF6FC
      pdf.roundedRect(margin, yPos, pageWidth - margin * 2, 18, 3, 3, 'F');
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(85, 112, 131);
      const summaryItems = [
        `📍 ${destinations.length} Destinasi`,
        `🏨 ${accommodations.length > 0 ? accommodations[0].name : 'Belum dipilih'}`,
        `📅 ${durationString}`,
        `👥 ${guestCount} Orang`,
        `💰 Rp${totalBudget.toLocaleString('id-ID')}`,
      ];
      const chipX = margin + 5;
      summaryItems.forEach((item, i) => {
        pdf.text(item, chipX + (i * 34), yPos + 10);
      });
      yPos += 28;

      // ── Destinations Section ──
      if (destinations.length > 0) {
        pdf.setTextColor(14, 117, 188);
        pdf.setFontSize(13);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Destinasi Wisata', margin, yPos);
        yPos += 8;

        let startHour = 8;
        destinations.forEach((dest, index) => {
          // Check if we need a new page
          if (yPos > pageHeight - 30) {
            pdf.addPage();
            yPos = margin;
          }

          // Time badge
          const timeStr = `${startHour.toString().padStart(2, '0')}:00`;
          pdf.setFillColor(14, 117, 188);
          pdf.roundedRect(margin, yPos - 4, 18, 7, 2, 2, 'F');
          pdf.setTextColor(255, 255, 255);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'bold');
          pdf.text(timeStr, margin + 2.5, yPos + 1);

          // Destination name
          pdf.setTextColor(17, 47, 67);
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          pdf.text(`${index + 1}. ${dest.title}`, margin + 22, yPos + 1);

          // Category
          const cat = dest.category || dest.primaryIntent || '';
          if (cat) {
            pdf.setTextColor(85, 112, 131);
            pdf.setFontSize(8);
            pdf.setFont('helvetica', 'normal');
            pdf.text(`Kategori: ${cat}`, margin + 22, yPos + 7);
          }

          // Divider line
          yPos += 14;
          if (index < destinations.length - 1) {
            pdf.setDrawColor(207, 229, 242);
            pdf.setLineWidth(0.3);
            pdf.line(margin + 22, yPos - 3, pageWidth - margin, yPos - 3);
          }
          startHour += 2;
        });
        yPos += 5;
      }

      // ── Accommodation Section ──
      if (accommodations.length > 0) {
        if (yPos > pageHeight - 40) {
          pdf.addPage();
          yPos = margin;
        }

        pdf.setTextColor(233, 75, 53); // #E94B35
        pdf.setFontSize(13);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Penginapan', margin, yPos);
        yPos += 8;

        accommodations.forEach((acc) => {
          pdf.setFillColor(254, 243, 242);
          pdf.roundedRect(margin, yPos - 4, pageWidth - margin * 2, 22, 3, 3, 'F');

          pdf.setTextColor(17, 47, 67);
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          pdf.text(`🏨 ${acc.name}`, margin + 5, yPos + 2);

          pdf.setTextColor(85, 112, 131);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'normal');
          const accDetails = [
            acc.rating ? `⭐ ${acc.rating}` : '',
            acc.location ? `📍 ${acc.location}` : '',
            `📅 Check-in: ${acc.checkIn} — Check-out: ${acc.checkOut}`,
          ].filter(Boolean).join('  |  ');
          pdf.text(accDetails, margin + 5, yPos + 9);

          pdf.setTextColor(14, 117, 188);
          pdf.setFontSize(9);
          pdf.setFont('helvetica', 'bold');
          pdf.text(`Rp${acc.totalPrice.toLocaleString('id-ID')}`, margin + 5, yPos + 15);

          yPos += 28;
        });
      }

      // ── Budget Summary ──
      if (yPos > pageHeight - 35) {
        pdf.addPage();
        yPos = margin;
      }
      yPos += 5;
      pdf.setFillColor(17, 47, 67);
      pdf.roundedRect(margin, yPos - 4, pageWidth - margin * 2, 14, 3, 3, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Total Estimasi Budget', margin + 5, yPos + 4);
      pdf.text(`Rp${totalBudget.toLocaleString('id-ID')}`, pageWidth - margin - 5, yPos + 4, { align: 'right' });

      // ── Footer ──
      const footerY = pageHeight - 10;
      pdf.setTextColor(170, 170, 170);
      pdf.setFontSize(7);
      pdf.setFont('helvetica', 'normal');
      pdf.text('Dibuat dengan ❤️ oleh MuterBandung AI Planner — muterbandung.com', pageWidth / 2, footerY, { align: 'center' });

      pdf.save(`itinerary-bandung-${new Date().toISOString().slice(0, 10)}.pdf`);

      setIsDownloading(false);
      setIsDownloaded(true);
      showToast('PDF berhasil didownload!', 'success');
      setTimeout(() => setIsDownloaded(false), 4000);
    } catch (err) {
      console.error('PDF generation failed:', err);
      setIsDownloading(false);
      showToast('Gagal membuat PDF. Coba lagi.', 'error');
    }
  };

  // ─── Bagikan ─────────────────────────────────────────
  const handleShare = async () => {
    if (isSharing || isShared) return;
    if (destinations.length === 0 && accommodations.length === 0) {
      showToast('Tambahkan destinasi terlebih dahulu', 'error');
      return;
    }

    setIsSharing(true);

    // Build share text
    const destList = destinations.map((d, i) => `${i + 1}. ${d.title}`).join('\n');
    const accName = accommodations.length > 0 ? accommodations[0].name : 'Belum dipilih';
    const shareText = [
      '🗺️ Itinerary Bandung — MuterBandung\n',
      '📍 Destinasi:',
      destList,
      '',
      `🏨 Penginapan: ${accName}`,
      `📅 Durasi: ${durationString}`,
      `👥 ${guestCount} Orang`,
      `💰 Total Budget: Rp${totalBudget.toLocaleString('id-ID')}`,
      '',
      '✨ Rencanakan perjalananmu di MuterBandung!',
      typeof window !== 'undefined' ? window.location.origin + '/planner' : '',
    ].join('\n');

    try {
      // Try Web Share API first (mobile & supported desktop browsers)
      if (typeof navigator !== 'undefined' && navigator.share) {
        await navigator.share({
          title: 'Itinerary Bandung — MuterBandung',
          text: shareText,
        });
        setIsSharing(false);
        setIsShared(true);
        showToast('Berhasil dibagikan!', 'success');
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(shareText);
        setIsSharing(false);
        setIsShared(true);
        showToast('Teks itinerary berhasil disalin ke clipboard!', 'success');
      }
    } catch (err: any) {
      // User cancelled share or clipboard failed
      if (err?.name !== 'AbortError') {
        // Try clipboard as last resort
        try {
          await navigator.clipboard.writeText(shareText);
          showToast('Teks itinerary berhasil disalin ke clipboard!', 'success');
          setIsShared(true);
        } catch {
          showToast('Gagal membagikan. Coba copy manual.', 'error');
        }
      }
      setIsSharing(false);
    }
    setTimeout(() => setIsShared(false), 4000);
  };

  return (
    <div className="mt-4 sm:mt-16 flex flex-col sm:flex-row flex-wrap items-center justify-between gap-4 py-5 sm:py-8 bg-[#F8F9FA] rounded-[24px] sm:rounded-[32px] px-4 sm:px-8">
      {/* Mobile grid for the 3 main actions */}
      <div className="flex flex-col sm:flex-row w-full sm:w-auto items-center gap-2.5 sm:gap-4 order-1 sm:order-2">
        
        {/* Simpan Button */}
        <button 
          onClick={handleSave}
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
            onClick={handleDownload}
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
            onClick={handleShare}
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
