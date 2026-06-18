import Image from 'next/image';
import { Send } from 'lucide-react';

export function AIChatPromoSection() {
  return (
    <section className="bg-[#F3F8FC] py-6 overflow-hidden relative">
      {/* Decorative Blob */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-[#EAF6FC] rounded-full blur-3xl opacity-50 pointer-events-none" />

      <div className="relative mx-auto max-w-[1180px] px-5 sm:px-8">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          
          {/* Left Content */}
          <div className="max-w-xl">
            <div className="inline-flex items-center rounded-full bg-[#14528E] px-3 py-1 mb-6 shadow-sm">
              <span className="text-[10px] font-bold tracking-wider text-white uppercase">
                Fitur Unggulan
              </span>
            </div>
            
            <h2 className="text-[32px] sm:text-[40px] font-bold text-[#14528E] leading-[1.15] mb-6">
              Bicara dengan Cepot, AI Personal Concierge Anda
            </h2>
            
            <p className="text-[16px] text-slate-600 leading-relaxed mb-10 italic border-l-4 border-[#0E75BC] pl-4">
              &quot;Cepot, saya ingin liburan keluarga ke Lembang. Saya suka pemandangan alam tapi anak saya ingin tempat bermain yang seru. Ada saran?&quot;
            </p>

            <div className="flex items-center gap-4">
              <div className="flex -space-x-3">
                <div className="w-10 h-10 rounded-full bg-blue-100 border-2 border-[#F3F8FC] overflow-hidden relative"><Image src="/images/background.webp" alt="User 1" fill className="object-cover" /></div>
                <div className="w-10 h-10 rounded-full bg-blue-200 border-2 border-[#F3F8FC] overflow-hidden relative"><Image src="/images/welcome-cepot.png" alt="User 2" fill className="object-cover object-top" /></div>
                <div className="w-10 h-10 rounded-full bg-blue-300 border-2 border-[#F3F8FC] overflow-hidden relative"><Image src="/images/background.webp" alt="User 3" fill className="object-cover" /></div>
              </div>
              <p className="text-[13px] text-slate-500 font-medium">
                Dibuat oleh AI, divalidasi oleh para Traveler
              </p>
            </div>
          </div>

          {/* Right Content - Chat Mockup */}
          <div className="relative mx-auto w-full max-w-[440px]">
            {/* Soft Glow Behind Mockup */}
            <div className="absolute inset-0 bg-[#0E75BC]/10 blur-2xl rounded-[32px] transform scale-105" />
            
            <div className="relative bg-white rounded-[24px] border border-slate-200 shadow-[0_24px_48px_rgba(14,117,188,0.12)] overflow-hidden flex flex-col h-[480px]">
              
              {/* Chat Header */}
              <div className="bg-[#14528E] px-5 py-4 flex items-center gap-3">
                <div className="relative w-10 h-10 rounded-full bg-white/10 overflow-hidden flex items-center justify-center shrink-0 border border-white/20">
                  <Image src="/images/welcome-cepot.png" alt="Cepot Avatar" width={32} height={32} className="object-contain" />
                </div>
                <div>
                  <h3 className="text-[15px] font-bold text-white">Cepot - AI Planner</h3>
                  <p className="text-[12px] text-blue-200">Online & Siap Membantu</p>
                </div>
              </div>

              {/* Chat Body */}
              <div className="flex-1 p-5 overflow-y-auto bg-[#F8FAFC] flex flex-col gap-5">
                
                {/* User Message */}
                <div className="flex justify-end">
                  <div className="bg-[#EEF7FD] text-[#0A3D6B] font-medium rounded-2xl rounded-tr-sm px-4 py-3 max-w-[85%] text-[14px] leading-relaxed shadow-sm border border-[#D9E8F3]">
                    Halo Cepot! Mau jalan-jalan ke favorit wisatawan Bandung bareng temen kantor, ada saran?
                  </div>
                </div>

                {/* Bot Message */}
                <div className="flex justify-start">
                  <div className="bg-[#0E75BC] text-white rounded-2xl rounded-tl-sm px-4 py-3 max-w-[90%] text-[14px] leading-relaxed shadow-sm">
                    Wilujeng sumping! Untuk rombongan kantor, saya sarankan Glamping di Orchid Forest atau Gathering di Floating Market. Mending kamu langsung gabung ke muterbandung aja.
                  </div>
                </div>
                
              </div>

              {/* Chat Input */}
              <div className="p-4 bg-white border-t border-slate-100">
                <div className="relative">
                  <input 
                    type="text" 
                    placeholder="Tulis pesan ke Cepot..." 
                    className="w-full bg-[#F3F8FC] border border-[#D9E8F3] rounded-full pl-5 pr-12 py-3 text-[14px] text-slate-900 placeholder:text-slate-500 font-medium outline-none focus:border-[#0E75BC] transition-colors"
                    readOnly
                  />
                  <button className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-[#14528E] text-white rounded-full hover:bg-[#0E75BC] transition-colors">
                    <Send className="w-4 h-4 ml-0.5" />
                  </button>
                </div>
              </div>

            </div>
          </div>

        </div>
      </div>
    </section>
  );
}
