import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MuterBandung - Jelajahi Bandung dengan AI",
  description: "Temukan destinasi wisata, kuliner, dan penginapan terbaik di Bandung dengan panduan kecerdasan buatan yang berbudaya. Sampurasun!",
};

import { ChatbotWidget } from "@/components/ui/ChatbotWidget";

import { PlannerProvider } from "@/context/PlannerContext";
import { AuthProvider } from "@/context/AuthContext";
import { ToastProvider } from "@/context/ToastContext";
import { ClientLayoutWrapper } from "@/components/layout/ClientLayoutWrapper";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col font-sans" suppressHydrationWarning>
        <ToastProvider>
          <AuthProvider>
            <PlannerProvider>
              <ClientLayoutWrapper>
                {children}
              </ClientLayoutWrapper>
              <ChatbotWidget />
            </PlannerProvider>
          </AuthProvider>
        </ToastProvider>
      </body>
    </html>
  );
}
