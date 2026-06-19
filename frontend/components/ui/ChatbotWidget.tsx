'use client';

import { useState, useEffect } from 'react';
import type { FormEvent } from 'react';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { apiFetch } from '@/services/api';

type ChatMessage = {
  id: string;
  role: 'assistant' | 'user';
  content: string;
};

type CepotChatResponse = {
  data?: {
    answer?: string;
  };
  message?: string;
};

const initialMessages: ChatMessage[] = [
  {
    id: 'welcome',
    role: 'assistant',
    content: 'Sampurasun! Mau saya bantu susun rute Bandung yang sesuai budget?',
  },
];

function SendIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" aria-hidden="true">
      <path
        d="m4 11 16-7-7 16-2-7-7-2Z"
        stroke="currentColor"
        strokeLinejoin="round"
        strokeWidth="1.8"
      />
    </svg>
  );
}

function CloseIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-5 w-5" fill="none" aria-hidden="true">
      <path
        d="M6 18L18 6M6 6l12 12"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg viewBox="0 0 24 24" className="h-6 w-6" fill="none" aria-hidden="true">
      <path
        d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
        stroke="currentColor"
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeWidth="2"
      />
    </svg>
  );
}

export function ChatbotWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    const handleOpenChat = () => setIsOpen(true);
    window.addEventListener('open-chat', handleOpenChat);
    return () => window.removeEventListener('open-chat', handleOpenChat);
  }, []);

  // Hide chatbot on auth pages
  if (pathname === '/register' || pathname === '/login') {
    return null;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = inputValue.trim();
    if (!message || isSending) return;

    const userMessage: ChatMessage = {
      id: `${Date.now()}-user`,
      role: 'user',
      content: message,
    };
    setMessages((current) => [...current, userMessage]);
    setInputValue('');
    setIsSending(true);

    try {
      const response = await apiFetch<CepotChatResponse>('/recommendations/cepot-chat', {
        method: 'POST',
        body: JSON.stringify({ message, top_k: 3 }),
      });
      const answer = response.data?.answer || response.message || 'Cepot belum bisa menjawab pertanyaan itu.';
      setMessages((current) => [
        ...current,
        { id: `${Date.now()}-assistant`, role: 'assistant', content: answer },
      ]);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Gagal menghubungi Cepot AI.';
      setMessages((current) => [
        ...current,
        { id: `${Date.now()}-error`, role: 'assistant', content: errorMessage },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <>
      {/* Expanded Chatbot Modal */}
      {isOpen && (
        <section
          aria-label="Cepot AI Chat"
          className="fixed inset-x-4 bottom-4 z-50 overflow-hidden rounded-2xl border border-[#CBE2EF] bg-white shadow-[0_24px_60px_rgba(15,23,42,0.22)] animate-in slide-in-from-bottom-4 fade-in duration-300 sm:inset-x-auto sm:bottom-6 sm:right-6 sm:w-[390px]"
        >
          <div className="flex items-center justify-between bg-[#0E75BC] px-4 py-3 text-white">
            <div className="flex items-center gap-3">
              <Image
                src="/images/welcome-cepot.png"
                alt="Cepot AI"
                width={42}
                height={42}
                className="h-10 w-10 rounded-full object-cover object-top bg-white/10"
              />
              <div>
                <h2 className="text-sm font-semibold">Cepot AI</h2>
                <p className="text-xs text-white/80">Online di MuterBandung</p>
              </div>
            </div>
            <button
              type="button"
              onClick={() => setIsOpen(false)}
              className="rounded-full p-1.5 transition-colors hover:bg-white/20"
              aria-label="Tutup obrolan"
            >
              <CloseIcon />
            </button>
          </div>

          <div className="flex h-[360px] flex-col">
            <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
              {messages.map((message) => (
                <p
                  key={message.id}
                  className={`max-w-[290px] rounded-2xl px-4 py-3 text-sm leading-6 ${
                    message.role === 'user'
                      ? 'ml-auto rounded-tr-sm bg-[#0E75BC] text-white'
                      : 'rounded-tl-sm bg-[#F0F7FC] text-slate-700'
                  }`}
                >
                  {message.content}
                </p>
              ))}
              {isSending && (
                <p className="max-w-[220px] rounded-2xl rounded-tl-sm bg-[#F0F7FC] px-4 py-3 text-sm leading-6 text-slate-500">
                  Cepot sedang mengetik...
                </p>
              )}
            </div>
            <form onSubmit={handleSubmit} className="m-4 mt-0 flex items-center gap-2 rounded-xl border border-[#D9E8F3] px-3 py-2">
              <label className="sr-only" htmlFor="global-cepot-message">
                Pesan untuk Cepot AI
              </label>
              <input
                id="global-cepot-message"
                name="message"
                type="text"
                value={inputValue}
                onChange={(event) => setInputValue(event.target.value)}
                placeholder="Tanya apa saja tentang Bandung..."
                disabled={isSending}
                className="min-w-0 flex-1 bg-transparent text-sm text-black outline-none placeholder:text-slate-400 disabled:text-slate-500"
              />
              <button
                type="submit"
                aria-label="Kirim pesan"
                disabled={isSending || inputValue.trim().length === 0}
                className="inline-flex h-9 w-9 items-center justify-center rounded-full bg-[#0E75BC] text-white transition-colors hover:bg-[#095f99] disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                <SendIcon />
              </button>
            </form>
          </div>
        </section>
      )}

      {/* FAB Button */}
      {!isOpen && (
        <button
          type="button"
          onClick={() => setIsOpen(true)}
          aria-label="Buka Chatbot Cepot AI"
          className="group fixed bottom-4 right-4 z-40 flex h-14 w-14 items-center justify-center overflow-hidden rounded-full border-4 border-white bg-[#0E75BC] shadow-[0_16px_34px_rgba(15,23,42,0.22)] transition-transform active:scale-95 sm:bottom-6 sm:right-6 sm:hover:scale-105 cursor-pointer"
        >
          <div className="absolute inset-0 flex items-center justify-center transition-opacity duration-300 group-hover:opacity-0 pointer-events-none">
            <Image
              src="/images/welcome-cepot.png"
              alt="Cepot AI"
              width={56}
              height={56}
              className="h-full w-full object-cover object-top"
            />
          </div>
          <div className="absolute inset-0 flex items-center justify-center text-white opacity-0 transition-opacity duration-300 group-hover:opacity-100">
            <ChatIcon />
          </div>
        </button>
      )}
    </>
  );
}
