"use client";
import { useMemo, useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Download, Share2, Heart, Check, Loader2 } from 'lucide-react';
import { useToast } from '@/context/ToastContext';
import { saveItinerary } from '@/services/savedItineraries';
import type { PlannerDestination, PlannerAccommodation } from '@/context/PlannerContext';
import { getRouteCalculation, type RoutePoint, type RouteSegment } from './useRouteData';

interface BottomActionButtonsProps {
  destinations: PlannerDestination[];
  accommodations: PlannerAccommodation[];
  totalBudget: number;
  durationDays: number;
  durationNights: number;
  guestCount: number;
  durationString: string;
}

type PdfDoc = InstanceType<typeof import('jspdf').default>;

const PAGE_MARGIN = 15;

function formatCurrency(value: number): string {
  return `Rp${value.toLocaleString('id-ID')}`;
}

function formatDistance(meters: number): string {
  if (!Number.isFinite(meters) || meters <= 0) return '-';
  if (meters >= 1000) return `${(meters / 1000).toFixed(1)} km`;
  return `${Math.round(meters)} m`;
}

function formatDuration(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds <= 0) return 'Estimasi';
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} menit`;
  const hours = Math.floor(minutes / 60);
  const remainingMinutes = minutes % 60;
  return remainingMinutes ? `${hours} jam ${remainingMinutes} menit` : `${hours} jam`;
}

function getValidCoordinates(latitude?: number, longitude?: number): { lat: number; lng: number } | null {
  if (
    typeof latitude !== 'number' ||
    typeof longitude !== 'number' ||
    !Number.isFinite(latitude) ||
    !Number.isFinite(longitude) ||
    latitude < -90 ||
    latitude > 90 ||
    longitude < -180 ||
    longitude > 180
  ) {
    return null;
  }

  return { lat: latitude, lng: longitude };
}

function buildRoutePoints(
  destinations: PlannerDestination[],
  accommodations: PlannerAccommodation[],
): RoutePoint[] {
  const points: RoutePoint[] = [];

  destinations.forEach((destination, index) => {
    const coordinates = getValidCoordinates(destination.latitude, destination.longitude);
    if (!coordinates) return;

    points.push({
      name: destination.title,
      lat: coordinates.lat,
      lng: coordinates.lng,
      type: 'destination',
      index: index + 1,
    });
  });

  accommodations.forEach((accommodation) => {
    const coordinates = getValidCoordinates(accommodation.latitude, accommodation.longitude);
    if (!coordinates) return;

    points.push({
      name: accommodation.name,
      lat: coordinates.lat,
      lng: coordinates.lng,
      type: 'accommodation',
    });
  });

  return points;
}

function getGoogleDirectionsUrl(points: RoutePoint[]): string | null {
  if (points.length < 2) return null;

  const origin = `${points[0].lat},${points[0].lng}`;
  const destination = `${points[points.length - 1].lat},${points[points.length - 1].lng}`;
  const waypoints = points
    .slice(1, -1)
    .map((point) => `${point.lat},${point.lng}`)
    .join('|');

  const params = new URLSearchParams({
    api: '1',
    origin,
    destination,
    travelmode: 'driving',
  });

  if (waypoints) params.set('waypoints', waypoints);
  return `https://www.google.com/maps/dir/?${params.toString()}`;
}

function addWrappedText(
  pdf: PdfDoc,
  text: string,
  x: number,
  y: number,
  maxWidth: number,
  lineHeight: number,
): number {
  const lines = pdf.splitTextToSize(text, maxWidth) as string[];
  pdf.text(lines, x, y);
  return y + Math.max(lines.length, 1) * lineHeight;
}

function ensureSpace(pdf: PdfDoc, yPos: number, neededHeight: number): number {
  const pageHeight = pdf.internal.pageSize.getHeight();
  if (yPos + neededHeight <= pageHeight - PAGE_MARGIN) return yPos;

  pdf.addPage();
  return PAGE_MARGIN;
}

function addSectionTitle(pdf: PdfDoc, title: string, yPos: number): number {
  const y = ensureSpace(pdf, yPos, 12);
  pdf.setTextColor(14, 117, 188);
  pdf.setFontSize(13);
  pdf.setFont('helvetica', 'bold');
  pdf.text(title, PAGE_MARGIN, y);
  return y + 8;
}

function getAllRouteCoordinates(segments: RouteSegment[], points: RoutePoint[]): [number, number][] {
  const coordinates = segments.flatMap((segment) => segment.geometry);
  if (coordinates.length > 0) return coordinates;
  return points.map((point) => [point.lat, point.lng] as [number, number]);
}

function drawRouteSketch(
  pdf: PdfDoc,
  segments: RouteSegment[],
  points: RoutePoint[],
  yPos: number,
  contentWidth: number,
): number {
  if (points.length < 2) return yPos;

  const boxHeight = 62;
  const y = ensureSpace(pdf, yPos, boxHeight + 8);
  const x = PAGE_MARGIN;
  const innerPadding = 7;
  const mapWidth = contentWidth;
  const mapHeight = boxHeight;
  const coordinates = getAllRouteCoordinates(segments, points);
  const lats = coordinates.map((coord) => coord[0]);
  const lngs = coordinates.map((coord) => coord[1]);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const latSpan = Math.max(maxLat - minLat, 0.0001);
  const lngSpan = Math.max(maxLng - minLng, 0.0001);

  const project = ([lat, lng]: [number, number]): [number, number] => {
    const px = x + innerPadding + ((lng - minLng) / lngSpan) * (mapWidth - innerPadding * 2);
    const py = y + innerPadding + ((maxLat - lat) / latSpan) * (mapHeight - innerPadding * 2);
    return [px, py];
  };

  pdf.setFillColor(242, 250, 254);
  pdf.setDrawColor(207, 229, 242);
  pdf.roundedRect(x, y, mapWidth, mapHeight, 4, 4, 'FD');

  segments.forEach((segment, index) => {
    const geometry = segment.geometry.length >= 2
      ? segment.geometry
      : [[segment.from.lat, segment.from.lng], [segment.to.lat, segment.to.lng]] as [number, number][];
    const step = Math.max(1, Math.ceil(geometry.length / 90));
    const reduced = geometry.filter((_, pointIndex) => pointIndex % step === 0);
    const routeGeometry = reduced[reduced.length - 1] === geometry[geometry.length - 1]
      ? reduced
      : [...reduced, geometry[geometry.length - 1]];

    pdf.setDrawColor(index % 2 === 0 ? 14 : 16, index % 2 === 0 ? 117 : 185, index % 2 === 0 ? 188 : 129);
    pdf.setLineWidth(index === 0 ? 1.2 : 0.9);
    for (let i = 0; i < routeGeometry.length - 1; i += 1) {
      const [x1, y1] = project(routeGeometry[i]);
      const [x2, y2] = project(routeGeometry[i + 1]);
      pdf.line(x1, y1, x2, y2);
    }
  });

  points.forEach((point, index) => {
    const [markerX, markerY] = project([point.lat, point.lng]);
    const isAccommodation = point.type === 'accommodation';
    pdf.setFillColor(isAccommodation ? 233 : 14, isAccommodation ? 75 : 117, isAccommodation ? 53 : 188);
    pdf.circle(markerX, markerY, 3, 'F');
    pdf.setTextColor(255, 255, 255);
    pdf.setFontSize(6);
    pdf.setFont('helvetica', 'bold');
    pdf.text(isAccommodation ? 'H' : String(point.index || index + 1), markerX, markerY + 1.5, { align: 'center' });

    pdf.setTextColor(17, 47, 67);
    pdf.setFontSize(6);
    pdf.setFont('helvetica', 'normal');
    const label = pdf.splitTextToSize(point.name, 35) as string[];
    pdf.text(label.slice(0, 2), Math.min(markerX + 4, x + mapWidth - 38), markerY - 2);
  });

  return y + boxHeight + 8;
}

function addFooter(pdf: PdfDoc): void {
  const pageCount = pdf.getNumberOfPages();
  const pageWidth = pdf.internal.pageSize.getWidth();
  const pageHeight = pdf.internal.pageSize.getHeight();

  for (let page = 1; page <= pageCount; page += 1) {
    pdf.setPage(page);
    pdf.setDrawColor(225, 235, 242);
    pdf.line(PAGE_MARGIN, pageHeight - 14, pageWidth - PAGE_MARGIN, pageHeight - 14);
    pdf.setTextColor(140, 155, 166);
    pdf.setFontSize(7);
    pdf.setFont('helvetica', 'normal');
    pdf.text(`MuterBandung AI Planner - Halaman ${page} dari ${pageCount}`, pageWidth / 2, pageHeight - 8, { align: 'center' });
  }
}

export function BottomActionButtons({
  destinations,
  accommodations,
  totalBudget,
  durationDays,
  durationNights,
  guestCount,
  durationString,
}: BottomActionButtonsProps) {
  const { showToast } = useToast();
  const routePoints = useMemo(
    () => buildRoutePoints(destinations, accommodations),
    [destinations, accommodations],
  );

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
      const { default: jsPDF } = await import('jspdf');
      const routeCalculation = await getRouteCalculation(routePoints);
      const routeSegments = routeCalculation.segments;
      const routeTotalDistance = routeCalculation.totalDistance;
      const routeTotalDuration = routeCalculation.totalDuration;
      const routeError = routeCalculation.error;

      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const contentWidth = pageWidth - PAGE_MARGIN * 2;
      let yPos = PAGE_MARGIN;

      // ── Header Band ──
      pdf.setFillColor(14, 117, 188); // #0E75BC
      pdf.rect(0, 0, pageWidth, 35, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text('MuterBandung', PAGE_MARGIN, 15);
      pdf.setFontSize(10);
      pdf.setFont('helvetica', 'normal');
      pdf.text('AI-Powered Travel Planner', PAGE_MARGIN, 22);
      pdf.setFontSize(9);
      pdf.text(`Dibuat: ${new Date().toLocaleDateString('id-ID', { day: 'numeric', month: 'long', year: 'numeric' })}`, PAGE_MARGIN, 29);

      yPos = 45;

      // ── Title ──
      pdf.setTextColor(17, 47, 67); // #112F43
      pdf.setFontSize(18);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Itinerary Perjalanan Bandung', PAGE_MARGIN, yPos);
      yPos += 10;

      // ── Summary Box ──
      pdf.setFillColor(234, 246, 252); // #EAF6FC
      pdf.roundedRect(PAGE_MARGIN, yPos, contentWidth, 28, 3, 3, 'F');
      const summaryItems = [
        `${destinations.length} destinasi wisata`,
        `${accommodations.length} penginapan`,
        `Durasi: ${durationString}`,
        `Tamu: ${guestCount} orang`,
        `Budget: ${formatCurrency(totalBudget)}`,
        routeSegments.length > 0 ? `Rute: ${formatDistance(routeTotalDistance)} / ${formatDuration(routeTotalDuration)}` : 'Rute: belum tersedia',
      ];
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(85, 112, 131);
      summaryItems.forEach((item, i) => {
        const col = i % 2;
        const row = Math.floor(i / 2);
        pdf.text(item, PAGE_MARGIN + 5 + col * 85, yPos + 8 + row * 7);
      });
      yPos += 38;

      // ── Destinations Section ──
      if (destinations.length > 0) {
        yPos = addSectionTitle(pdf, 'Destinasi Wisata Terpilih', yPos);

        let startHour = 8;
        destinations.forEach((dest, index) => {
          yPos = ensureSpace(pdf, yPos, 22);

          // Time badge
          const timeStr = `${startHour.toString().padStart(2, '0')}:00`;
          pdf.setFillColor(14, 117, 188);
          pdf.roundedRect(PAGE_MARGIN, yPos - 4, 18, 7, 2, 2, 'F');
          pdf.setTextColor(255, 255, 255);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'bold');
          pdf.text(timeStr, PAGE_MARGIN + 2.5, yPos + 1);

          // Destination name
          pdf.setTextColor(17, 47, 67);
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          yPos = addWrappedText(pdf, `${index + 1}. ${dest.title}`, PAGE_MARGIN + 22, yPos + 1, contentWidth - 22, 5);

          // Category
          const cat = dest.category || dest.primaryIntent || '';
          const coordinates = getValidCoordinates(dest.latitude, dest.longitude);
          const details = [
            cat ? `Kategori: ${cat}` : undefined,
            coordinates ? `Koordinat: ${coordinates.lat.toFixed(6)}, ${coordinates.lng.toFixed(6)}` : 'Koordinat: belum tersedia',
          ].filter(Boolean).join(' | ');
          pdf.setTextColor(85, 112, 131);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'normal');
          yPos = addWrappedText(pdf, details, PAGE_MARGIN + 22, yPos + 1, contentWidth - 22, 4);

          // Divider line
          yPos += 4;
          if (index < destinations.length - 1) {
            pdf.setDrawColor(207, 229, 242);
            pdf.setLineWidth(0.3);
            pdf.line(PAGE_MARGIN + 22, yPos - 2, pageWidth - PAGE_MARGIN, yPos - 2);
          }
          startHour += 2;
        });
        yPos += 5;
      }

      // ── Accommodation Section ──
      if (accommodations.length > 0) {
        yPos = addSectionTitle(pdf, 'Penginapan', yPos);

        accommodations.forEach((acc) => {
          yPos = ensureSpace(pdf, yPos, 30);
          pdf.setFillColor(254, 243, 242);
          pdf.roundedRect(PAGE_MARGIN, yPos - 4, contentWidth, 25, 3, 3, 'F');

          pdf.setTextColor(17, 47, 67);
          pdf.setFontSize(11);
          pdf.setFont('helvetica', 'bold');
          yPos = addWrappedText(pdf, acc.name, PAGE_MARGIN + 5, yPos + 2, contentWidth - 10, 5);

          pdf.setTextColor(85, 112, 131);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'normal');
          const coordinates = getValidCoordinates(acc.latitude, acc.longitude);
          const accDetails = [
            acc.rating ? `Rating: ${acc.rating}` : '',
            acc.location ? `Lokasi: ${acc.location}` : '',
            coordinates ? `Koordinat: ${coordinates.lat.toFixed(6)}, ${coordinates.lng.toFixed(6)}` : '',
            `Check-in: ${acc.checkIn} - Check-out: ${acc.checkOut}`,
          ].filter(Boolean).join('  |  ');
          yPos = addWrappedText(pdf, accDetails, PAGE_MARGIN + 5, yPos + 1, contentWidth - 10, 4);

          pdf.setTextColor(14, 117, 188);
          pdf.setFontSize(9);
          pdf.setFont('helvetica', 'bold');
          pdf.text(formatCurrency(acc.totalPrice), PAGE_MARGIN + 5, yPos + 2);

          yPos += 10;
        });
      }

      // ── Route Section ──
      yPos = addSectionTitle(pdf, 'Rute Perjalanan', yPos);
      yPos = ensureSpace(pdf, yPos, 30);
      pdf.setTextColor(85, 112, 131);
      pdf.setFontSize(8);
      pdf.setFont('helvetica', 'normal');

      if (routeSegments.length > 0) {
        const routeNote = routeError
          ? `${routeError}.`
          : 'Jarak dan durasi memakai data rute berkendara OSRM.';
        yPos = addWrappedText(pdf, routeNote, PAGE_MARGIN, yPos, contentWidth, 4);
        yPos += 2;

        yPos = drawRouteSketch(pdf, routeSegments, routePoints, yPos, contentWidth);

        routeSegments.forEach((segment: RouteSegment, index) => {
          yPos = ensureSpace(pdf, yPos, 14);
          pdf.setTextColor(17, 47, 67);
          pdf.setFontSize(9);
          pdf.setFont('helvetica', 'bold');
          yPos = addWrappedText(
            pdf,
            `${index + 1}. ${segment.from.name} -> ${segment.to.name}`,
            PAGE_MARGIN,
            yPos,
            contentWidth,
            5,
          );

          pdf.setTextColor(85, 112, 131);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'normal');
          pdf.text(`${formatDistance(segment.distance)} | ${formatDuration(segment.duration)}`, PAGE_MARGIN + 4, yPos);
          yPos += 7;
        });

        const mapsUrl = getGoogleDirectionsUrl(routePoints);
        if (mapsUrl) {
          yPos = ensureSpace(pdf, yPos + 2, 18);
          pdf.setTextColor(14, 117, 188);
          pdf.setFontSize(8);
          pdf.setFont('helvetica', 'bold');
          pdf.textWithLink('Buka rute lengkap di Google Maps', PAGE_MARGIN, yPos, { url: mapsUrl });
          yPos += 8;
        }
      } else {
        yPos = addWrappedText(pdf, routeError || 'Rute belum tersedia karena kurang dari 2 lokasi dengan koordinat valid.', PAGE_MARGIN, yPos, contentWidth, 4);
        yPos += 6;
      }

      // ── Budget Summary ──
      yPos = ensureSpace(pdf, yPos, 60);
      yPos += 5;
      pdf.setTextColor(14, 117, 188);
      pdf.setFontSize(13);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Rincian Budget', PAGE_MARGIN, yPos);
      yPos += 8;

      const totalAccommodationCost = accommodations.reduce((sum, acc) => sum + acc.totalPrice, 0);
      const totalDestinationCost = destinations.length * 25000;
      const budgetRows = [
        ['Estimasi tiket/aktivitas', formatCurrency(totalDestinationCost)],
        ['Estimasi penginapan', formatCurrency(totalAccommodationCost)],
      ];
      pdf.setTextColor(85, 112, 131);
      pdf.setFontSize(9);
      pdf.setFont('helvetica', 'normal');
      budgetRows.forEach(([label, value]) => {
        pdf.text(label, PAGE_MARGIN, yPos);
        pdf.text(value, pageWidth - PAGE_MARGIN, yPos, { align: 'right' });
        yPos += 6;
      });

      pdf.setFillColor(17, 47, 67);
      pdf.roundedRect(PAGE_MARGIN, yPos - 4, contentWidth, 14, 3, 3, 'F');
      pdf.setTextColor(255, 255, 255);
      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Total Estimasi Budget', PAGE_MARGIN + 5, yPos + 4);
      pdf.text(formatCurrency(totalBudget), pageWidth - PAGE_MARGIN - 5, yPos + 4, { align: 'right' });

      addFooter(pdf);
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
    } catch (err: unknown) {
      // User cancelled share or clipboard failed
      if (!(err instanceof DOMException) || err.name !== 'AbortError') {
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
