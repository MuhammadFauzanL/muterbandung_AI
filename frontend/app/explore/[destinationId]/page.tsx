import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { DESTINATION_DETAILS } from '@/constants';
import { DestinationDetailPageContent, PageShell } from '@/components';

interface DestinationDetailPageProps {
  params: Promise<{
    destinationId: string;
  }>;
}

function getDestination(destinationId: string) {
  return DESTINATION_DETAILS.find(
    (destination) => destination.id === destinationId,
  );
}

export function generateStaticParams() {
  return DESTINATION_DETAILS.map((destination) => ({
    destinationId: destination.id,
  }));
}

export async function generateMetadata({
  params,
}: DestinationDetailPageProps): Promise<Metadata> {
  const { destinationId } = await params;
  const destination = getDestination(destinationId);

  if (!destination) {
    return {
      title: 'Detail Wisata - MuterBandung AI',
    };
  }

  return {
    title: `${destination.title} - MuterBandung AI`,
    description: destination.description,
  };
}

export default async function DestinationDetailPage({
  params,
}: DestinationDetailPageProps) {
  const { destinationId } = await params;
  const destination = getDestination(destinationId);

  if (!destination) {
    notFound();
  }

  return (
    <PageShell
      activeItem="explore"
      backgroundClassName="bg-[#F3F8FC]"
      showFooter={false}
    >
      <DestinationDetailPageContent destination={destination} />
    </PageShell>
  );
}
