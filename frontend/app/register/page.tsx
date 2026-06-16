import type { Metadata } from 'next';
import { RegisterForm } from '@/components/sections/register/RegisterForm';

export const metadata: Metadata = {
  title: 'Registrasi Akun - MuterBandung AI',
  description: 'Daftar akun MuterBandung untuk mulai merencanakan liburan terbaikmu di Bandung Raya dengan bantuan asisten AI Cepot.',
};

export default function RegisterPage() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <RegisterForm />
    </div>
  );
}
