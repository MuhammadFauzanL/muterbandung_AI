'use client';

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/auth';

export function LoginForm() {
  const router = useRouter();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false,
  });

  const row1Ref = useRef<HTMLDivElement>(null);
  const row2Ref = useRef<HTMLDivElement>(null);
  const [scroll1, setScroll1] = useState({ start: true, end: false });
  const [scroll2, setScroll2] = useState({ start: true, end: false });

  const handleScroll = (ref: React.RefObject<HTMLDivElement | null>, setScroll: React.Dispatch<React.SetStateAction<{start: boolean, end: boolean}>>) => {
    if (ref.current) {
      const { scrollLeft, scrollWidth, clientWidth } = ref.current;
      setScroll({
        start: scrollLeft <= 10,
        end: Math.ceil(scrollLeft + clientWidth) >= scrollWidth - 5
      });
    }
  };

  useEffect(() => {
    handleScroll(row1Ref, setScroll1);
    handleScroll(row2Ref, setScroll2);
  }, []);

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
    setIsLoading(true);

    try {
      const response = await authService.login(formData.email, formData.password);
      
      const successTxt = 'Login berhasil! Mengarahkan ke halaman utama...';
      setSuccessMsg(successTxt);
      
      // Update state login dan simpan token
      login(response.access_token, response.user);
      
      // Redirect ke home after a short delay
      setTimeout(() => {
        router.push('/');
      }, 1000);

    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Terjadi kesalahan. Silakan coba lagi.';
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col lg:grid lg:grid-cols-2 bg-[#F7F9FF] relative overflow-hidden">
      {/* Tombol Kembali ke Beranda */}
      <div className="absolute top-4 left-4 sm:top-6 sm:left-6 lg:top-8 lg:left-8 z-50">
        <Link href="/" className="flex items-center gap-2 text-[14px] font-medium text-[#40484D] hover:text-[#0E75BC] transition-all bg-white/70 hover:bg-white backdrop-blur-md px-4 py-2 rounded-full border border-slate-200 shadow-[0_2px_8px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.08)]">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
          Kembali
        </Link>
      </div>

      {/* Ornamen Latar Belakang (Desktop Only) */}
      <div className="absolute inset-0 pointer-events-none hidden lg:block overflow-hidden">
        <div className="absolute -left-20 -top-20 h-96 w-96 rounded-full border border-blue-100/50 bg-radial from-blue-50/20 to-transparent" />
        <div className="absolute right-0 bottom-0 h-[500px] w-[500px] rounded-full border border-blue-100/40 bg-radial from-blue-50/30 to-transparent" />
      </div>

      {/* PART 1: Maskot & Heading (Mobile: Top, Desktop: Left Top) */}
      <div className="order-1 lg:col-start-1 lg:row-start-1 flex flex-col justify-end px-6 pt-6 pb-2 sm:px-12 lg:px-24 lg:pt-16 lg:pb-2 relative z-10">
        <div className="mx-auto w-full max-w-[540px] flex flex-col items-center text-center lg:items-start lg:text-left">
          {/* Maskot Cepot */}
          <div className="mb-2 lg:mb-6 flex justify-center lg:justify-start">
            <Image
              src="/images/welcome-cepot.png"
              alt="Maskot Cepot MuterBandung"
              width={120}
              height={140}
              priority
              className="object-contain drop-shadow-md w-[100px] h-[116px] lg:w-[140px] lg:h-[160px]"
            />
          </div>

          {/* Heading */}
          <h1 className="text-[17px] min-[375px]:text-[19px] sm:text-[28px] lg:text-[48px] font-bold leading-[28px] sm:leading-[40px] lg:leading-[60px] text-[#051D2E] tracking-[-0.02em] whitespace-nowrap lg:whitespace-normal">
            Sampurasun,<span className="hidden lg:inline"> </span><br className="hidden lg:block" />
            <span className="lg:hidden"> </span>Siap Muter Bandung?
          </h1>
        </div>
      </div>

      {/* PART 2: Form (Mobile: Middle, Desktop: Right Full Height) */}
      <div className="order-2 lg:col-start-2 lg:row-span-2 flex flex-col items-center justify-center bg-transparent lg:bg-[#ECF4FF] px-4 py-4 sm:py-10 sm:px-6 lg:px-8 relative z-20 shadow-[-10px_0_30px_rgba(0,0,0,0.02)]">
        <div className="w-full max-w-[500px] rounded-[24px] bg-white p-6 sm:p-10 shadow-[0_4px_12px_0_rgba(10,34,51,0.06)] border border-slate-200/50">
          {/* Tab Switcher */}
          <div className="flex rounded-[12px] bg-[#E2EFFF] p-1 max-w-[280px] mx-auto mb-4">
            <button
              className="flex flex-1 items-center justify-center rounded-[8px] bg-white py-2 text-[13px] font-medium text-[#00526E] shadow-[0_1px_2px_0_rgba(0,0,0,0.05)] border border-white/10"
            >
              Masuk
            </button>
            <Link
              href="/register"
              className="flex flex-1 items-center justify-center rounded-[8px] py-2 text-[13px] font-medium text-[#40484D] transition-colors hover:text-[#00526E]"
            >
              Daftar
            </Link>
          </div>

          {/* Form Header */}
          <div className="text-center">
            <h2 className="text-[20px] leading-[28px] font-semibold text-[#051D2E]">Selamat Datang Kembali</h2>
            <p className="mt-1 text-[14px] leading-[20px] text-[#40484D]">
              Lanjutkan rencana liburanmu bersama Cepot AI
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
          <form className="mt-4 space-y-2" onSubmit={handleSubmit}>
            {/* Input Email */}
            <div>
              <label htmlFor="email" className="block text-[14px] font-medium text-[#40484D] mb-2">
                Alamat Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                placeholder="contoh@email.com"
                className="w-full rounded-[12px] border border-[#BFC8CE] bg-white px-5 py-[10px] text-[15px] text-slate-800 placeholder-[#6B7280] outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
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
                  placeholder="••••••••"
                  className="w-full rounded-[12px] border border-[#BFC8CE] bg-white pl-5 pr-12 py-[10px] text-[15px] text-slate-800 placeholder-[#6B7280] tracking-widest outline-none transition-all focus:border-[#00526E] focus:ring-1 focus:ring-[#00526E]"
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

            {/* Tambahan Login: Ingat saya & Lupa sandi */}
            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center">
                <input
                  id="rememberMe"
                  name="rememberMe"
                  type="checkbox"
                  checked={formData.rememberMe}
                  onChange={handleChange}
                  className="h-5 w-5 rounded-[4px] border-[#BFC8CE] bg-white text-[#00526E] focus:ring-[#00526E]/20 transition-all cursor-pointer"
                />
                <label htmlFor="rememberMe" className="ml-2 block text-[14px] font-medium text-[#40484D] cursor-pointer">
                  Ingat saya
                </label>
              </div>
              <div className="text-[14px]">
                <Link href="/forgot-password" className="font-medium text-[#00526E] hover:text-[#00415C] hover:underline">
                  Lupa kata sandi?
                </Link>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`mt-4 w-full rounded-[12px] bg-[#00526E] py-[12px] text-[16px] font-semibold text-white shadow-[0_4px_12px_0_rgba(0,82,110,0.2)] transition-all hover:bg-[#003d52] hover:shadow-[0_6px_16px_0_rgba(0,82,110,0.3)] ${isLoading ? 'opacity-70 cursor-not-allowed' : ''}`}
            >
              {isLoading ? 'Sedang Masuk...' : 'Masuk ke MuterBandung'}
            </button>
          </form>

          {/* Footer Form */}
          <div className="mt-8 text-center text-[14px] text-[#62778C]">
            Belum punya akun?{' '}
            <Link href="/register" className="font-semibold text-[#0E75BC] hover:text-[#0A5F9E] hover:underline">
              Daftar sekarang
            </Link>
          </div>
        </div>
      </div>

      {/* PART 3: Deskripsi & Fitur (Mobile: Bottom, Desktop: Left Bottom) */}
      <div className="order-3 lg:col-start-1 lg:row-start-2 flex flex-col justify-start px-6 pb-12 pt-6 sm:px-12 lg:px-24 lg:pb-16 lg:pt-0 relative z-10">
        <div className="mx-auto w-full max-w-[540px] flex flex-col items-center text-center lg:items-start lg:text-left">
          <p className="text-[15px] sm:text-[18px] leading-[24px] sm:leading-[28px] text-[#40484D]">
            Mulai perjalananmu dan temukan wisata, Penginapan, serta pengalaman seru di Bandung bersama MuterBandung.
          </p>

          {/* Baris 1: Kategori Wisata Chips */}
          <div className="relative self-stretch -mx-6 lg:mx-0 mt-6 lg:mt-8">
            <div 
              ref={row1Ref}
              onScroll={() => handleScroll(row1Ref, setScroll1)}
              className="px-6 scroll-px-6 lg:scroll-px-0 lg:px-0 flex gap-4 overflow-x-auto pb-2 lg:flex-wrap lg:overflow-visible lg:pb-0 snap-x hide-scrollbar [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
            >
              <div className="flex shrink-0 snap-start items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#00526e]/10 text-[#00526e]">⛰️</span>
                <span className="text-[16px] font-normal text-[#051D2E]">Wisata Alam</span>
              </div>
              <div className="flex shrink-0 snap-start items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#00526e]/10 text-[#00526e]">🛏️</span>
                <span className="text-[16px] font-normal text-[#051D2E]">Penginapan</span>
              </div>
              <div className="flex shrink-0 snap-start items-center gap-4 rounded-xl border border-slate-200/50 bg-white px-4 py-4 shadow-[0_1px_2px_0_rgba(0,0,0,0.05)]">
                <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-[#9D0015]/10 text-[#9D0015]">🤖</span>
                <span className="text-[16px] font-normal text-[#051D2E]">Itinerary AI</span>
              </div>
              <div className="w-2 shrink-0 lg:hidden"></div>
            </div>
            {!scroll1.start && (
              <div className="absolute left-0 top-0 bottom-2 flex w-16 items-center justify-start pointer-events-none lg:hidden bg-gradient-to-r from-[#F7F9FF] via-[#F7F9FF]/80 to-transparent pl-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/60 shadow-sm backdrop-blur-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M15 18l-6-6 6-6"/></svg>
                </div>
              </div>
            )}
            {!scroll1.end && (
              <div className="absolute right-0 top-0 bottom-2 flex w-16 items-center justify-end pointer-events-none lg:hidden bg-gradient-to-l from-[#F7F9FF] via-[#F7F9FF]/80 to-transparent pr-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/60 shadow-sm backdrop-blur-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M9 18l6-6-6-6"/></svg>
                </div>
              </div>
            )}
          </div>

          {/* Baris 2: Fitur Highlight Cards */}
          <div className="relative self-stretch -mx-6 lg:mx-0 mt-4 lg:mt-8">
            <div 
              ref={row2Ref}
              onScroll={() => handleScroll(row2Ref, setScroll2)}
              className="px-6 scroll-px-6 lg:scroll-px-0 lg:px-0 flex gap-4 overflow-x-auto pb-4 snap-x lg:flex-col lg:overflow-visible lg:pb-0 hide-scrollbar [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]"
            >
              <div className="flex w-[260px] shrink-0 snap-start lg:w-auto items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#3B82F6]">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 3v16M8 5v12M4 8v6M16 6v10M20 9v4"/></svg>
                </div>
                <div>
                  <h4 className="text-[15px] font-semibold text-[#0A2540]">AI Recommendation</h4>
                  <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Cepot membantu menemukan destinasi sesuai preferensimu.</p>
                </div>
              </div>

              <div className="flex w-[260px] shrink-0 snap-start lg:w-auto items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#3B82F6]">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg>
                </div>
                <div>
                  <h4 className="text-[15px] font-semibold text-[#0A2540]">Nearby Destination</h4>
                  <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Temukan tempat menarik di sekitar lokasi pilihanmu.</p>
                </div>
              </div>

              <div className="flex w-[260px] shrink-0 snap-start lg:w-auto items-start gap-4 rounded-2xl border border-slate-100 bg-white p-5 shadow-[0_6px_16px_rgba(0,0,0,0.02)]">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#EEF5FC] text-[#E54545]">
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
                </div>
                <div>
                  <h4 className="text-[15px] font-semibold text-[#0A2540]">Smart Itinerary</h4>
                  <p className="mt-1 text-[13px] leading-relaxed text-[#62778C]">Susun perjalanan yang efisien secara otomatis.</p>
                </div>
              </div>
              <div className="w-2 shrink-0 lg:hidden"></div>
            </div>
            {!scroll2.start && (
              <div className="absolute left-0 top-0 bottom-4 flex w-16 items-center justify-start pointer-events-none lg:hidden bg-gradient-to-r from-[#F7F9FF] via-[#F7F9FF]/80 to-transparent pl-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/60 shadow-sm backdrop-blur-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M15 18l-6-6 6-6"/></svg>
                </div>
              </div>
            )}
            {!scroll2.end && (
              <div className="absolute right-0 top-0 bottom-4 flex w-16 items-center justify-end pointer-events-none lg:hidden bg-gradient-to-l from-[#F7F9FF] via-[#F7F9FF]/80 to-transparent pr-2">
                <div className="flex h-6 w-6 items-center justify-center rounded-full bg-white/60 shadow-sm backdrop-blur-sm">
                  <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#0E75BC" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="animate-pulse"><path d="M9 18l6-6-6-6"/></svg>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
