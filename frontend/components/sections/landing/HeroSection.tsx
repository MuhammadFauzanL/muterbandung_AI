"use client";

/**
 * Hero Section Component
 *
 * Main landing page hero with Bandung backdrop and mascot panel.
 * Includes call-to-action buttons for user engagement.
 */
import Image from 'next/image';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';

export function HeroSection() {
  const { isLoggedIn } = useAuth();

  return (
    <section
      id="home"
      className="relative min-h-[calc(100vh-68px)] overflow-hidden"
    >
      <Image
        src="/images/background.png"
        alt="Ilustrasi Gedung Sate Bandung"
        fill
        preload
        sizes="100vw"
        className="object-cover"
      />
      <div className="absolute inset-0 bg-[linear-gradient(90deg,rgba(10,33,52,0.84)_0%,rgba(20,58,92,0.58)_50%,rgba(44,104,189,0.22)_100%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_82%_12%,rgba(132,172,255,0.42),transparent_28%)]" />

      <div className="relative mx-auto flex min-h-[calc(100svh-68px)] max-w-[1180px] flex-col justify-between px-4 pb-14 pt-8 sm:px-8 sm:pb-20 sm:pt-10 lg:px-8">
        <div className="grid flex-1 items-center gap-4 sm:gap-8 lg:grid-cols-[minmax(0,1fr)_470px] mt-6 sm:mt-0">
          <div className="min-w-0 max-w-[560px] text-white text-center sm:text-left z-10">
            <h1 className="text-[34px] sm:text-[48px] font-extrabold leading-[1.1] tracking-tight">
              <span className="block text-white drop-shadow-md">Wilujeng Sumping</span>
              <span className="mt-1 sm:mt-2 block text-[#4FC4FF] drop-shadow-md">
                Di Muter Bandung
              </span>
            </h1>

            <p className="mt-4 sm:mt-6 mx-auto sm:mx-0 max-w-[480px] text-[13px] sm:text-[16px] font-medium leading-relaxed text-white/90 drop-shadow-sm">
              Cepot akan menyiapkan rekomendasi destinasi berdasarkan preferensi wisata yang kamu pilih. Masuk/Daftar untuk membuat rekomendasi sesuai kesukaan dan pencarianmu.
            </p>

            <div className="mt-6 sm:mt-9 flex flex-col sm:flex-row gap-3 sm:gap-4 items-center justify-center sm:justify-start">
              <Link
                href={isLoggedIn ? "#foryou" : "#explore"}
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-full bg-white/10 backdrop-blur-md border border-white/30 px-6 py-3 sm:px-7 sm:py-[14px] text-[13px] sm:text-[16px] font-bold text-white transition-all hover:bg-white/20"
              >
                {isLoggedIn ? 'Destinasi Untukmu' : 'Destinasi Populer'}
              </Link>
              <Link
                href="/explore"
                className="inline-flex w-full sm:w-auto items-center justify-center rounded-full bg-[#E54545] px-6 py-3 sm:px-7 sm:py-[14px] text-[13px] sm:text-[16px] font-bold text-white transition-transform hover:-translate-y-0.5 shadow-lg shadow-[#E54545]/40"
              >
                Mulai Menjelajah
                <span className="ml-1.5 text-lg leading-none">↗</span>
              </Link>
            </div>
          </div>

          <div className="relative w-full max-w-[200px] sm:max-w-[340px] mx-auto flex items-center justify-center pt-2 sm:pt-0 group z-0">
            {/* Soft glowing aura behind the mascot to make it pop and look professional */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] sm:w-[280px] h-[200px] sm:h-[280px] bg-[#4FC4FF]/30 rounded-full blur-[60px] sm:blur-[70px] pointer-events-none transition-all duration-700 group-hover:bg-[#4FC4FF]/40 group-hover:w-[220px] sm:group-hover:w-[300px] group-hover:h-[220px] sm:group-hover:h-[300px]" />
            
            {/* Floating mascot image */}
            <Image
              src="/images/welcome-cepot.png"
              alt="Maskot MuterBandung"
              width={340}
              height={382}
              preload={true}
              sizes="(max-width: 640px) 200px, 340px"
              className="relative drop-shadow-[0_24px_30px_rgba(0,0,0,0.3)] object-contain animate-float transition-transform duration-500 group-hover:scale-105"
              style={{ width: '100%', height: 'auto' }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
