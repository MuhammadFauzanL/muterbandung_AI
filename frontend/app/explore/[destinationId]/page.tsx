import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { destinationsService } from '@/services/destinations';
import type { DestinationDetail } from '@/types';
import { DestinationDetailPageContent } from '@/components';

interface DestinationDetailPageProps {
  params: Promise<{
    destinationId: string;
  }>;
}

async function getDestination(destinationId: string) {
  try {
    // Karena URL backend API menggunakan 'slug' dan Next.js menggunakan params 'destinationId',
    // kita asumsikan destinationId == slug.
    return await destinationsService.getBySlug(destinationId);
  } catch (error) {
    console.error(`Failed to fetch destination ${destinationId}:`, error);
    return null;
  }
}

// Kita menghapus generateStaticParams() agar halaman ini bisa me-render dinamis 
// (Server-Side Rendering) untuk setiap slug yang dipanggil, karena data di backend bisa bertambah sewaktu-waktu.

export async function generateMetadata({
  params,
}: DestinationDetailPageProps): Promise<Metadata> {
  const { destinationId } = await params;
  const destination = await getDestination(destinationId);

  if (!destination) {
    return {
      title: 'Detail Wisata - MuterBandung AI',
    };
  }

  return {
    title: `${destination.title} - MuterBandung AI`,
    description: destination.description || `Jelajahi keindahan ${destination.title}`,
  };
}

export default async function DestinationDetailPage({
  params,
}: DestinationDetailPageProps) {
  const { destinationId } = await params;
  const destination = await getDestination(destinationId);

  if (!destination) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-[#F3F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <DestinationDetailPageContent destination={destination} />
      </div>
    </div>
  );
}
