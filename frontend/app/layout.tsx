import type { Metadata } from "next";
import "./globals.css";
import { ChatbotWidget } from "@/components";

export const metadata: Metadata = {
  title: "MuterBandung - Jelajahi Bandung dengan AI",
  description: "Temukan destinasi wisata, kuliner, dan penginapan terbaik di Bandung dengan panduan kecerdasan buatan yang berbudaya. Sampurasun!",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col font-sans">
        {children}
        <ChatbotWidget />
      </body>
    </html>
  );
}
