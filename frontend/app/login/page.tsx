import type { Metadata } from 'next';
import { LoginForm } from '@/components/sections/login';

export const metadata: Metadata = {
  title: 'Masuk Akun - MuterBandung AI',
  description: 'Masuk ke akun MuterBandung untuk melanjutkan perencanaan liburan terbaikmu di Bandung Raya.',
};

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <LoginForm />
    </div>
  );
}
