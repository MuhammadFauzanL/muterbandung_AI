'use client';

import { useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useToast } from '@/context/ToastContext';

export function RegisterForm() {
  const router = useRouter();
  const { showToast } = useToast();
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    agreeToTerms: false,
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setSuccessMsg('');

    // Validasi Frontend Dasar
    if (formData.password !== formData.confirmPassword) {
      const msg = 'Kata sandi dan konfirmasi kata sandi tidak cocok.';
      setErrorMsg(msg);
      showToast(msg, 'error');
      return;
    }

    if (formData.password.length < 8) {
      const msg = 'Kata sandi harus terdiri dari minimal 8 karakter.';
      setErrorMsg(msg);
      showToast(msg, 'error');
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'ngrok-skip-browser-warning': 'true'
        },
        body: JSON.stringify({
          name: formData.fullName,
          email: formData.email,
          password: formData.password
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        
        // Membedah pesan error dari API jika bentuknya array (khas FastAPI)
        let errMsg = 'Terjadi kesalahan saat registrasi.';
        if (Array.isArray(errorData?.detail)) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          errMsg = errorData.detail.map((err: any) => err.msg).join(', ');
        } else if (typeof errorData?.detail === 'string') {
          errMsg = errorData.detail;
        }

        throw new Error(errMsg);
      }

      const successTxt = 'Registrasi berhasil! Mengarahkan ke halaman login...';
      setSuccessMsg(successTxt);
      showToast(successTxt, 'success');
      
      // Redirect to login after a short delay
      setTimeout(() => {
        router.push('/login');
      }, 500);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    } catch (err: any) {
      setErrorMsg(err.message || 'Gagal terhubung ke server.');
      showToast(err.message || 'Gagal terhubung ke server.', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col lg:flex-row bg-[#F7F9FF]">
      {/* KIRI - Panel Welcome & Highlight Fitur */}
      <div className="relative flex flex-1 flex-col justify-center px-6 py-12 sm:px-12 lg:py-16 xl:px-24 bg-[#F7F9FF] overflow-hidden">
        {/* Ornamen Latar Belakang */}
        <div className="absolute -left-20 -top-20 h-96 w-96 rounded-full border border-blue-100/50 bg-radial from-blue-50/20 to-transparent" />
        <div className="absolute right-0 bottom-0 h-[500px] w-[500px] rounded-full border border-blue-100/40 bg-radial from-blue-50/30 to-transparent" />

        <div className="relative mx-auto w-full max-w-[540px]">
          {/* Maskot Cepot */}
          <div className="mb-6 flex justify-start">
            <Image
              src="/images/welcome-cepot.png"
              alt="Maskot Cepot MuterBandung"
              width={140}
              height={160}
              priority
              className="object-contain drop-shadow-md"
            />
          </div>

          {/* Heading */}
          <h1 className="text-[32px] sm:text-[48px] font-bold leading-[60px] text-[#051D2E] tracking-[-0.02em]">
            Sampurasun,<br />
            Siap Muter Bandung?
          </h1>

          <p className="mt-4 text-[16px] sm:text-[18px] leading-[28px] text-[#40484D]">
            Mulai perjalananmu dan temukan wisata, Penginapan, serta pengalaman seru di Bandung bersama MuterBandung.
          </p>

          {/* Baris 1: Kategori Wisata Chips */}
          <div className="mt-8 flex flex-wrap gap-4">
            <div className="flex items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#00526e]/10 text-[#00526e]">⛰️</span>
              <span className="text-[16px] font-normal text-[#051D2E]">Wisata Alam</span>
            </div>
            <div className="flex items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#00526e]/10 text-[#00526e]">🛏️</span>
              <span className="text-[16px] font-normal text-[#051D2E]">Penginapan</span>
            </div>
            <div className="flex items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
              <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#9D0015]/10 text-[#9D0015]">🤖</span>
              <span className="text-[16px] font-normal text-[#051D2E]">Itinerary AI</span>
            </div>
          </div>

          {/* Baris 2: Fitur Highlight Cards */}
          <div className="mt-8 flex flex-col gap-4">
            <div className="flex items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#3B82F6]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v16M8 5v12M4 8v6M16 6v10M20 9v4"/></svg>
              </div>
              <div>
                <h4 className="text-[15px] font-semibold text-[#0A2540]">AI Recommendation</h4>
                <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Cepot membantu menemukan destinasi sesuai preferensimu.</p>
              </div>
            </div>

            <div className="flex items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#3B82F6]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
              </div>
              <div>
                <h4 className="text-[15px] font-semibold text-[#0A2540]">Nearby Destination</h4>
                <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Temukan tempat menarik di sekitar lokasi pilihanmu.</p>
              </div>
            </div>

            <div className="flex items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#E54545]">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
              </div>
              <div>
                <h4 className="text-[15px] font-semibold text-[#0A2540]">Smart Itinerary</h4>
                <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Susun perjalanan yang efisien secara otomatis.</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KANAN - Form Card Registrasi */}
      <div className="flex flex-1 flex-col items-center justify-center bg-[#ECF4FF] px-4 py-12 sm:px-6 lg:px-8">
        <div className="w-full max-w-[576px] rounded-[24px] bg-white p-8 sm:p-12 shadow-[0_4px_12px_0_rgba(10,34,51,0.06)] border border-slate-200/50">
          {/* Tab Switcher */}
          <div className="flex rounded-[12px] bg-[#E2EFFF] p-1">
            <Link
              href="/login"
              className="flex flex-1 items-center justify-center rounded-[8px] py-4 text-[14px] font-medium text-[#40484D] transition-colors"
            >
              Masuk
            </Link>
            <button
              className="flex flex-1 items-center justify-center rounded-[8px] bg-white py-4 text-[14px] font-medium text-[#00526E] shadow-[0_1px_2px_0_rgba(0,0,0,0.05)] border border-white/10"
            >
              Daftar
            </button>
          </div>

          {/* Form Header */}
          <div className="mt-6 text-center">
            <h2 className="text-[20px] leading-[28px] font-semibold text-[#051D2E]">Selamat Datang</h2>
            <p className="mt-1 text-[14px] leading-[20px] text-[#40484D]">
              Daftar dan mulai jelajahi Bandung bersama MuterBandung.
            </p>
          </div>

          {/* Alert Messages */}
          {errorMsg && (
            <div className="mt-4 rounded-lg bg-red-50 p-4 text-[14px] text-red-600 border border-red-100">
              {errorMsg}
            </div>
          )}
          {successMsg && (
            <div className="mt-4 rounded-lg bg-green-50 p-4 text-[14px] text-green-600 border border-green-100">
              {successMsg}
            </div>
          )}

          {/* Form */}
          <form className="mt-8 space-y-4" onSubmit={handleSubmit}>
            {/* Input Nama */}
            <div>
              <label htmlFor="fullName" className="block text-[14px] font-medium text-[#40484D] mb-2">
                Nama
              </label>
              <input
                id="fullName"
                name="fullName"
                type="text"
                required
                value={formData.fullName}
                onChange={handleChange}
                placeholder="Masukkan nama"
                className="w-full rounded-[12px] border border-[#BFC8CE] bg-white px-6 py-[13px] text-[16px] text-slate-800 placeholder-[#6B7280] outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
              />
            </div>

            {/* Input Email */}
            <div>
              <label htmlFor="email" className="block text-[14px] font-medium text-[#40484D] mb-2">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="contoh@email.com"
                className="w-full rounded-[12px] border border-[#BFC8CE] bg-white px-6 py-[13px] text-[16px] text-slate-800 placeholder-[#6B7280] outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
              />
            </div>

            {/* Input Kata Sandi */}
            <div>
              <label htmlFor="password" className="block text-[14px] font-medium text-[#40484D] mb-2">
                Kata Sandi
              </label>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  placeholder="Min. 8 karakter"
                  className="w-full rounded-[12px] border border-[#BFC8CE] bg-white pl-6 pr-12 py-[13px] text-[16px] text-slate-800 placeholder-[#6B7280] outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showPassword ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Input Konfirmasi Kata Sandi */}
            <div>
              <label htmlFor="confirmPassword" className="block text-[14px] font-medium text-[#40484D] mb-2">
                Konfirmasi Kata Sandi
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  name="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="Ulangi kata sandi"
                  className="w-full rounded-[12px] border border-[#BFC8CE] bg-white pl-6 pr-12 py-[13px] text-[16px] text-slate-800 placeholder-[#6B7280] outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  {showConfirmPassword ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  )}
                </button>
              </div>
            </div>

            {/* Checkbox Persetujuan */}
            <div className="flex items-start pt-2">
              <div className="flex h-5 items-center">
                <input
                  id="agreeToTerms"
                  name="agreeToTerms"
                  type="checkbox"
                  required
                  checked={formData.agreeToTerms}
                  onChange={handleChange}
                  className="h-5 w-5 rounded-[4px] border-[#BFC8CE] bg-white text-[#00526E] focus:ring-[#00526E]/20 transition-all cursor-pointer"
                />
              </div>
              <div className="ml-3 text-[14px] font-medium leading-[20px] text-[#40484D]">
                <label htmlFor="agreeToTerms" className="cursor-pointer">
                  Saya menyetujui <button type="button" onClick={() => showToast('Halaman S&K segera hadir!', 'info')} className="text-[#40484D] hover:underline">Syarat &amp; Ketentuan</button> dan <button type="button" onClick={() => showToast('Halaman Kebijakan Privasi segera hadir!', 'info')} className="text-[#40484D] hover:underline">Kebijakan Privasi</button>
                </label>
              </div>
            </div>

            {/* Button Submit */}
            <button
              type="submit"
              disabled={isLoading}
              className={`mt-6 w-full rounded-[12px] py-[16px] text-[14px] font-medium text-white transition-all shadow-md ${
                isLoading 
                  ? 'bg-slate-400 cursor-not-allowed' 
                  : 'bg-[#00526E] hover:bg-[#00415C] active:scale-[0.99]'
              }`}
            >
              {isLoading ? 'Sedang Memproses...' : 'Buat Akun MuterBandung'}
            </button>
          </form>

          {/* Footer Link */}
          <div className="mt-8 text-center text-[12px] font-semibold tracking-[0.05em] text-[#40484D]">
            Sudah punya akun?{' '}
            <Link href="/login" className="text-[#00526E] hover:underline">
              Masuk Sekarang
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
