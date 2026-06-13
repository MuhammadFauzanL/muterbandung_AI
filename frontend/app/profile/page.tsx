import type { Metadata } from 'next';
import { ProfilePageContent } from '@/components/sections/profile/ProfilePageContent';

export const metadata: Metadata = {
  title: 'Profile - MuterBandung',
  description: 'Pengaturan akun dan profil MuterBandung Anda.',
};

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-[#F5F8FC] text-slate-950 flex flex-col">
      <div className="flex-1">
        <ProfilePageContent />
      </div>
    </div>
  );
}
