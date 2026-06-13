"use client";

/**
 * Hero Section Component
 *
 * Main landing page hero with Bandung backdrop and mascot panel.
 * Includes call-to-action buttons for user engagement.
 */
import Image from 'next/image';
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
        <div className="grid flex-1 items-center gap-7 sm:gap-8 lg:grid-cols-[minmax(0,1fr)_470px]">
          <div className="min-w-0 max-w-[560px] text-white">
            <h1 className="text-[32px] font-bold leading-[1.15] md:text-[48px]">
              <span className="block text-white">Wilujeng Sumping</span>
              <span className="mt-1 block text-[#4FC4FF]">
                Di Muter Bandung
              </span>
            </h1>

            <p className="mt-5 max-w-[520px] text-[16px] font-normal leading-[1.55] text-white/90">
              Cepot akan menyiapkan rekomendasi destinasi berdasarkan preferensi wisata yang kamu pilih. Masuk/Daftar untuk membuat rekomendasi sesuai kesukaan dan pencarianmu.
            </p>

            <div className="mt-8 flex flex-col gap-4 sm:mt-9 sm:flex-row">
              <a
                href={isLoggedIn ? "#foryou" : "#explore"}
                className="inline-flex items-center justify-center rounded-full bg-[#2C6E7E]/80 backdrop-blur-[6px] border border-[#5CA4B5]/60 px-5 py-3 md:px-7 md:py-[14px] text-[15px] md:text-[17px] font-medium text-white transition-transform hover:-translate-y-0.5"
              >
                {isLoggedIn ? 'Lihat Destinasi Untukmu' : 'Lihat Destinasi Populer'}
              </a>
              <a
                href="/explore"
                className="inline-flex items-center justify-center rounded-full bg-[#E54545] px-5 py-3 md:px-7 md:py-[14px] text-[15px] md:text-[17px] font-medium text-white transition-transform hover:-translate-y-0.5"
              >
                Mulai Menjelajah
                <span className="ml-2 text-xl leading-none">↗</span>
              </a>
            </div>
          </div>

          <div className="relative w-full max-w-[340px] mx-auto flex items-center justify-center pt-8 sm:pt-0 group">
            {/* Soft glowing aura behind the mascot to make it pop and look professional */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[280px] h-[280px] bg-[#4FC4FF]/25 rounded-full blur-[70px] pointer-events-none transition-all duration-700 group-hover:bg-[#4FC4FF]/40 group-hover:w-[300px] group-hover:h-[300px]" />
            
            {/* Floating mascot image */}
            <Image
              src="/images/welcome-cepot.png"
              alt="Maskot MuterBandung"
              width={340}
              height={382}
              preload
              sizes="(min-width: 640px) 340px, 250px"
              className="relative drop-shadow-[0_24px_30px_rgba(0,0,0,0.3)] object-contain animate-float transition-transform duration-500 group-hover:scale-105"
              style={{ width: '100%', height: 'auto' }}
            />
          </div>
        </div>
      </div>
    </section>
  );
}
