"use client";

import Image from 'next/image';
import { Camera, Lock, Mail, MapPin, Heart, Map, Building, Eye, EyeOff, X, Mountain, Utensils, ShoppingBag, Landmark, Home, PawPrint, Castle, GraduationCap, Leaf, PersonStanding, Rocket, Users, Smile, TreePine, Moon } from 'lucide-react';
import { useState } from 'react';

// --- CONSTANTS FOR PREFERENCES ---
const FAVORITE_PLACES = [
  { id: 'alam', label: 'Alam', icon: Mountain },
  { id: 'kuliner', label: 'Kuliner', icon: Utensils },
  { id: 'belanja', label: 'Belanja', icon: ShoppingBag },
  { id: 'sejarah', label: 'Sejarah', icon: Landmark },
  { id: 'budaya', label: 'Budaya', icon: Home },
  { id: 'satwa', label: 'Satwa', icon: PawPrint },
  { id: 'religi', label: 'Religi', icon: Castle },
  { id: 'edukasi', label: 'Edukasi', icon: GraduationCap },
];

const FAVORITE_ACTIVITIES = [
  { id: 'santai', label: 'Santai / Healing', desc: 'Tenangkan pikiran & jiwa.', icon: Leaf },
  { id: 'foto', label: 'Spot Foto', desc: 'Estetik dan hits.', icon: Camera },
  { id: 'petualangan', label: 'Petualangan', desc: 'Eksplorasi medan menantang.', icon: PersonStanding },
  { id: 'wahana', label: 'Wahana Ekstrem', desc: 'Adrenalin tinggi & seru.', icon: Rocket },
];

const TARGET_VISITORS = [
  { id: 'keluarga', label: 'Keluarga', icon: Users },
  { id: 'ramah_anak', label: 'Ramah Anak', icon: Smile },
];

const ATMOSPHERES = [
  { id: 'indoor', label: 'Indoor', icon: Building },
  { id: 'outdoor', label: 'Outdoor', icon: TreePine },
  { id: 'malam', label: 'Malam / City Light', icon: Moon },
];

export function ProfilePageContent() {
  const [activeModal, setActiveModal] = useState<'editProfile' | 'changePassword' | 'editPreferences' | null>(null);

  return (
    <>
      <main className="mx-auto max-w-[1180px] px-4 py-8 sm:px-8 relative z-10">
        {/* Top Profile Card */}
        <section className="bg-white rounded-3xl border border-slate-200 p-8 flex flex-col sm:flex-row items-center justify-between shadow-sm mb-8">
          <div className="flex items-center gap-6">
            <div className="relative">
              <div className="h-24 w-24 rounded-full border-[3px] border-[#E94B35] overflow-hidden bg-slate-100">
                <Image 
                  src="/images/welcome-cepot.png" 
                  alt="Profile Avatar" 
                  width={96} 
                  height={96} 
                  className="object-cover object-top"
                />
              </div>
              <button className="absolute bottom-0 right-0 h-8 w-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-sm hover:bg-slate-50 text-[#0E75BC]">
                <Camera className="h-4 w-4" />
              </button>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[#112F43]">dudung</h1>
              <p className="text-sm text-slate-500 mt-1">Bergabung sejak 2025</p>
            </div>
          </div>
          <button 
            onClick={() => setActiveModal('editProfile')}
            className="mt-4 sm:mt-0 rounded-lg bg-[#0B5C73] px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-[#084354] shadow-sm"
          >
            Edit Profil
          </button>
        </section>

        <div className="grid gap-8 lg:grid-cols-[1fr_2fr] items-start">
          {/* Kolom Kiri: Informasi Akun */}
          <section>
            <h2 className="text-[15px] font-bold text-slate-500 mb-4 uppercase tracking-wide">Informasi Akun</h2>
            <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm">
              
              <div className="space-y-5 mb-8">
                {/* Username Field */}
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">Username</label>
                  <div className="flex items-center gap-3 bg-[#F8FAFC] border border-slate-200 rounded-xl px-4 py-3 opacity-80 cursor-not-allowed">
                    <span className="text-slate-400 font-bold">@</span>
                    <input type="text" value="andiwj" disabled className="bg-transparent border-none text-slate-700 w-full outline-none font-medium" />
                  </div>
                </div>

                {/* Email Field */}
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">Email Address</label>
                  <div className="flex items-center gap-3 bg-[#F8FAFC] border border-slate-200 rounded-xl px-4 py-3 opacity-80 cursor-not-allowed">
                    <Mail className="h-4 w-4 text-slate-400" />
                    <input type="email" value="andi.wijaya@example.com" disabled className="bg-transparent border-none text-slate-700 w-full outline-none font-medium" />
                  </div>
                </div>

                {/* Password Field */}
                <div>
                  <label className="block text-xs font-bold text-slate-500 mb-2 uppercase tracking-wide">Password</label>
                  <div className="flex items-center gap-3 bg-[#F8FAFC] border border-slate-200 rounded-xl px-4 py-3">
                    <Lock className="h-4 w-4 text-slate-400" />
                    <input type="password" value="password123456" disabled className="bg-transparent border-none text-slate-700 w-full outline-none font-medium tracking-[0.2em]" />
                    <button className="text-xs font-bold text-[#0E75BC] hover:underline">Lihat</button>
                  </div>
                </div>
              </div>

              <button 
                onClick={() => setActiveModal('changePassword')}
                className="w-full block text-center rounded-xl bg-[#D6EBF8] px-4 py-3.5 text-sm font-bold text-[#0B5C73] transition-colors hover:bg-[#c2e2f6]"
              >
                Ubah Password
              </button>
            </div>
          </section>

          {/* Kolom Kanan: Preferensi Wisata & Statistik */}
          <section>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-[15px] font-bold text-slate-500 uppercase tracking-wide">Preferensi Wisata</h2>
              <button onClick={() => setActiveModal('editPreferences')} className="text-sm font-bold text-[#0B5C73] hover:underline">
                Edit Preferensi
              </button>
            </div>

            {/* Preferences Card */}
            <div className="bg-white rounded-3xl border border-slate-200 p-6 shadow-sm mb-6">
              <div className="grid grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xs font-bold text-slate-600 mb-3 flex items-center gap-2"><MapPin className="h-4 w-4 text-[#0B5C73]" /> Tipe Tempat</h3>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Alam</span>
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Kuliner</span>
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Sejarah</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-slate-600 mb-3 flex items-center gap-2"><UsersIcon className="h-4 w-4 text-[#0B5C73]" /> Target & Suasana</h3>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Keluarga</span>
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Outdoor</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-slate-600 mb-3 flex items-center gap-2"><ActivityIcon className="h-4 w-4 text-[#0B5C73]" /> Aktivitas</h3>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Healing</span>
                    <span className="bg-[#7FE0F4] text-[#0B5C73] px-4 py-1.5 rounded-full text-xs font-bold">Spot Foto</span>
                  </div>
                </div>

                <div>
                  <h3 className="text-xs font-bold text-slate-600 mb-3 flex items-center gap-2"><WalletIcon className="h-4 w-4 text-[#0B5C73]" /> Budget Terpilih</h3>
                  <div className="flex flex-wrap gap-2">
                    <span className="bg-[#E8F3FB] text-[#0E75BC] border border-[#0E75BC] px-4 py-1.5 rounded-full text-xs font-bold">Gratis</span>
                  </div>
                </div>
              </div>
            </div>

            {/* 4 Stats Cards */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col items-center text-center shadow-sm">
                <MapPin className="h-6 w-6 text-[#0B5C73] mb-3" />
                <span className="text-2xl font-black text-[#112F43]">12</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Destinasi</span>
              </div>
              
              <div className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col items-center text-center shadow-sm">
                <Heart className="h-6 w-6 text-[#E94B35] mb-3 fill-[#FCD3D1]" />
                <span className="text-2xl font-black text-[#112F43]">8</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Wishlist</span>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col items-center text-center shadow-sm">
                <Map className="h-6 w-6 text-[#0B5C73] mb-3" />
                <span className="text-2xl font-black text-[#112F43]">5</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Itinerary</span>
              </div>

              <div className="bg-white rounded-3xl border border-slate-200 p-6 flex flex-col items-center text-center shadow-sm">
                <Building className="h-6 w-6 text-[#0B5C73] mb-3" />
                <span className="text-2xl font-black text-[#112F43]">3</span>
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mt-1">Penginapan</span>
              </div>
            </div>

          </section>
        </div>
      </main>

      {/* MODALS */}
      {activeModal === 'editProfile' && (
        <EditProfileModal onClose={() => setActiveModal(null)} />
      )}
      {activeModal === 'changePassword' && (
        <ChangePasswordModal onClose={() => setActiveModal(null)} />
      )}
      {activeModal === 'editPreferences' && (
        <EditPreferencesModal onClose={() => setActiveModal(null)} />
      )}
    </>
  );
}

// --- SUB COMPONENTS FOR MODALS ---

function EditProfileModal({ onClose }: { onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-[500px] rounded-[24px] bg-white p-8 shadow-xl relative animate-in zoom-in-95 duration-200">
        <button onClick={onClose} className="absolute top-4 right-4 h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200">
          <X className="h-4 w-4" />
        </button>
        <h2 className="text-xl font-bold text-[#112F43] mb-6">Edit Profil</h2>
        
        <div className="flex justify-center mb-6">
          <div className="relative">
            <div className="h-24 w-24 rounded-full border-[3px] border-[#E94B35] overflow-hidden bg-slate-100">
              <Image 
                src="/images/welcome-cepot.png" 
                alt="Profile Avatar" 
                width={96} 
                height={96} 
                className="object-cover object-top"
              />
            </div>
            <button className="absolute bottom-0 right-0 h-8 w-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-md hover:bg-slate-50 text-[#0E75BC]">
              <Camera className="h-4 w-4" />
            </button>
          </div>
        </div>

        <form className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Nama Lengkap</label>
            <input 
              type="text" 
              defaultValue="Dudung Hermawan" 
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 outline-none focus:border-[#0E75BC] focus:ring-1 focus:ring-[#0E75BC] font-medium" 
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Username</label>
            <div className="flex items-center gap-3 bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 opacity-80 cursor-not-allowed">
              <span className="text-slate-400 font-bold">@</span>
              <input type="text" value="andiwj" disabled className="bg-transparent border-none text-slate-700 w-full outline-none font-medium" />
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Email Address</label>
            <input 
              type="email" 
              defaultValue="andi.wijaya@example.com" 
              className="w-full bg-white border border-slate-200 rounded-xl px-4 py-2.5 text-slate-700 outline-none focus:border-[#0E75BC] focus:ring-1 focus:ring-[#0E75BC] font-medium" 
            />
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="rounded-full bg-white border border-slate-300 px-6 py-2.5 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-50">
              Batal
            </button>
            <button type="button" onClick={onClose} className="rounded-full bg-[#0E75BC] px-8 py-2.5 text-sm font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm">
              Simpan
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ChangePasswordModal({ onClose }: { onClose: () => void }) {
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="w-full max-w-[440px] rounded-[24px] bg-white p-8 shadow-xl relative animate-in zoom-in-95 duration-200">
        <button onClick={onClose} className="absolute top-4 right-4 h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200">
          <X className="h-4 w-4" />
        </button>
        <div className="mb-6 flex flex-col items-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#EAF6FC] mb-4">
            <Lock className="h-8 w-8 text-[#0E75BC]" />
          </div>
          <h2 className="text-xl font-bold text-[#112F43]">Ubah Password</h2>
        </div>

        <form className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Password Lama</label>
            <div className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-2.5 focus-within:border-[#0E75BC] focus-within:ring-1 focus-within:ring-[#0E75BC]">
              <input 
                type={showOld ? "text" : "password"} 
                placeholder="Masukkan password lama" 
                className="bg-transparent border-none text-slate-700 w-full outline-none font-medium text-sm" 
              />
              <button type="button" onClick={() => setShowOld(!showOld)} className="text-slate-400 hover:text-[#0E75BC]">
                {showOld ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Password Baru</label>
            <div className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-2.5 focus-within:border-[#0E75BC] focus-within:ring-1 focus-within:ring-[#0E75BC]">
              <input 
                type={showNew ? "text" : "password"} 
                placeholder="Masukkan password baru" 
                className="bg-transparent border-none text-slate-700 w-full outline-none font-medium text-sm" 
              />
              <button type="button" onClick={() => setShowNew(!showNew)} className="text-slate-400 hover:text-[#0E75BC]">
                {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold text-slate-500 mb-1.5 uppercase tracking-wide">Konfirmasi Password</label>
            <div className="flex items-center gap-3 bg-white border border-slate-200 rounded-xl px-4 py-2.5 focus-within:border-[#0E75BC] focus-within:ring-1 focus-within:ring-[#0E75BC]">
              <input 
                type={showNew ? "text" : "password"} 
                placeholder="Ulangi password baru" 
                className="bg-transparent border-none text-slate-700 w-full outline-none font-medium text-sm" 
              />
            </div>
          </div>

          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={onClose} className="rounded-full bg-white border border-slate-300 px-6 py-2.5 text-sm font-bold text-slate-700 transition-colors hover:bg-slate-50">
              Batal
            </button>
            <button type="button" onClick={onClose} className="rounded-full bg-[#0E75BC] px-6 py-2.5 text-sm font-bold text-white transition-colors hover:bg-[#095f99] shadow-sm">
              Perbarui Password
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function EditPreferencesModal({ onClose }: { onClose: () => void }) {
  const [places, setPlaces] = useState<string[]>(['alam', 'kuliner', 'sejarah']);
  const [activities, setActivities] = useState<string[]>(['santai', 'foto']);
  const [visitor, setVisitor] = useState('keluarga');
  const [atmospheres, setAtmospheres] = useState<string[]>(['outdoor']);
  const [isFree, setIsFree] = useState(true);

  const togglePlace = (id: string) => {
    setPlaces(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id]);
  };
  const toggleActivity = (id: string) => {
    setActivities(prev => prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]);
  };
  const toggleAtmosphere = (id: string) => {
    setAtmospheres(prev => prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id]);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-sm p-4 sm:p-8">
      <div className="w-full max-w-[700px] max-h-[90vh] flex flex-col rounded-[24px] bg-[#ECF4FF] shadow-2xl relative animate-in zoom-in-95 duration-200 overflow-hidden border border-slate-200/50">
        
        {/* Header */}
        <div className="shrink-0 flex items-center justify-between border-b border-slate-200/60 bg-white/95 px-6 py-4 backdrop-blur-md">
          <h2 className="text-[14px] font-bold tracking-[0.05em] text-[#051D2E]">EDIT PREFERENSI WISATA</h2>
          <button onClick={onClose} className="h-8 w-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200 transition-colors">
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Scrollable Body */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-8 custom-scrollbar">
          
          {/* 1. Tipe Tempat Favorit */}
          <section>
            <div className="mb-3">
              <h3 className="text-[15px] font-bold text-[#051D2E]">Tipe Tempat Favorit</h3>
            </div>
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
              {FAVORITE_PLACES.map((place) => {
                const isSelected = places.includes(place.id);
                const Icon = place.icon;
                return (
                  <button
                    key={place.id}
                    onClick={() => togglePlace(place.id)}
                    className={`flex flex-col items-center justify-center rounded-[12px] border p-3 transition-all active:scale-[0.98] ${
                      isSelected
                        ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                        : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                    }`}
                  >
                    <div className={`mb-2 rounded-lg p-2 ${isSelected ? 'bg-white' : 'bg-[#F7F9FF]'}`}>
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                    </div>
                    <span className={`text-[12px] font-medium ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`}>
                      {place.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          {/* 2. Aktivitas Favorit */}
          <section>
            <div className="mb-3">
              <h3 className="text-[15px] font-bold text-[#051D2E]">Aktivitas Favorit</h3>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {FAVORITE_ACTIVITIES.map((act) => {
                const isSelected = activities.includes(act.id);
                const Icon = act.icon;
                return (
                  <button
                    key={act.id}
                    onClick={() => toggleActivity(act.id)}
                    className={`flex items-start gap-3 rounded-[12px] border p-3 text-left transition-all active:scale-[0.98] ${
                      isSelected
                        ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                        : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                    }`}
                  >
                    <div className={`rounded-lg p-2 shrink-0 ${isSelected ? 'bg-white' : 'bg-[#F7F9FF]'}`}>
                      <Icon className={`h-5 w-5 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                    </div>
                    <div>
                      <span className={`block text-[13px] font-bold ${isSelected ? 'text-[#00526E]' : 'text-[#051D2E]'}`}>
                        {act.label}
                      </span>
                      <span className="mt-0.5 block text-[11px] text-[#6B7280]">
                        {act.desc}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          </section>

          {/* 3. Target Pengunjung */}
          <section>
            <div className="mb-3">
              <h3 className="text-[15px] font-bold text-[#051D2E]">Target Pengunjung</h3>
            </div>
            <div className="flex flex-wrap gap-3">
              {TARGET_VISITORS.map((v) => {
                const isSelected = visitor === v.id;
                const Icon = v.icon;
                return (
                  <button
                    key={v.id}
                    onClick={() => setVisitor(v.id)}
                    className={`flex items-center gap-2 rounded-full border px-4 py-2 transition-all active:scale-[0.98] ${
                      isSelected
                        ? 'border-[#00526E] bg-[#00526E] text-white shadow-sm'
                        : 'border-slate-200 bg-white text-[#051D2E] hover:bg-slate-50'
                    }`}
                  >
                    <Icon className="h-4 w-4" strokeWidth={2} />
                    <span className="text-[13px] font-semibold">{v.label}</span>
                  </button>
                );
              })}
            </div>
          </section>

          {/* 4. Suasana yang Disukai */}
          <section>
            <div className="mb-3">
              <h3 className="text-[15px] font-bold text-[#051D2E]">Suasana yang Disukai</h3>
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {ATMOSPHERES.map((atm) => {
                const isSelected = atmospheres.includes(atm.id);
                const Icon = atm.icon;
                return (
                  <button
                    key={atm.id}
                    onClick={() => toggleAtmosphere(atm.id)}
                    className={`flex flex-col items-center justify-center rounded-[12px] border p-3 transition-all active:scale-[0.98] ${
                      isSelected
                        ? 'border-[#00526E] bg-[#F0F7FC] shadow-sm'
                        : 'border-slate-200 bg-white hover:border-[#BFC8CE]'
                    }`}
                  >
                    <Icon className={`mb-2 h-5 w-5 ${isSelected ? 'text-[#00526E]' : 'text-[#40484D]'}`} strokeWidth={isSelected ? 2.5 : 1.5} />
                    <span className={`text-[12px] font-medium text-center ${isSelected ? 'text-[#00526E]' : 'text-[#051D2E]'}`}>
                      {atm.label}
                    </span>
                  </button>
                );
              })}
            </div>
          </section>

          {/* 5. Wisata Gratis */}
          <section>
            <div className="flex items-center justify-between rounded-[16px] bg-[#F0F4F8] p-4">
              <div className="flex items-center gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-white text-[#E54545]">
                  <span className="font-bold text-xs">Rp</span>
                </div>
                <div>
                  <h4 className="text-[13px] font-bold text-[#051D2E]">Wisata Gratis (Free)</h4>
                  <p className="mt-0.5 text-[11px] text-[#6B7280]">Tampilkan destinasi tanpa tiket masuk.</p>
                </div>
              </div>
              <button
                onClick={() => setIsFree(!isFree)}
                className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer items-center rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-[#00526E] ${
                  isFree ? 'bg-[#00526E]' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    isFree ? 'translate-x-5' : 'translate-x-0.5'
                  }`}
                />
              </button>
            </div>
          </section>

        </div>

        {/* Footer Actions */}
        <div className="shrink-0 flex items-center justify-end border-t border-slate-200/60 bg-white/95 px-6 py-4 backdrop-blur-md gap-3">
          <button
            onClick={onClose}
            className="text-[13px] font-bold text-[#40484D] hover:text-[#051D2E] transition-colors px-4"
          >
            Batal
          </button>
          <button
            onClick={onClose}
            className="flex items-center justify-center gap-2 rounded-full bg-[#00526E] px-6 py-2.5 text-[13px] font-semibold text-white transition-all hover:bg-[#00415C] active:scale-[0.98] shadow-md"
          >
            Simpan Preferensi
          </button>
        </div>

      </div>
      
      {/* Global style to hide scrollbar but keep functionality */}
      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: rgba(0,0,0,0.1);
          border-radius: 10px;
        }
      `}} />
    </div>
  );
}

// Inline Icons for those missing in lucide-react standard
function UsersIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
      <circle cx="9" cy="7" r="4" />
      <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
      <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </svg>
  );
}

function ActivityIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </svg>
  );
}

function WalletIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4" />
      <path d="M3 5v14a2 2 0 0 0 2 2h16v-5" />
      <path d="M18 12a2 2 0 0 0 0 4h4v-4Z" />
    </svg>
  );
}
