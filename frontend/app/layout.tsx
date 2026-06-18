import type { Metadata } from "next";
import Script from "next/script";
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

const stripExtensionHydrationAttrsScript = `
(function () {
  var ATTRIBUTE = 'bis_skin_checked';
  function stripAttribute(root) {
    if (!root || root.nodeType !== 1) return;
    if (root.hasAttribute && root.hasAttribute(ATTRIBUTE)) {
      root.removeAttribute(ATTRIBUTE);
    }
    if (root.querySelectorAll) {
      root.querySelectorAll('[' + ATTRIBUTE + ']').forEach(function (node) {
        node.removeAttribute(ATTRIBUTE);
      });
    }
  }

  stripAttribute(document.documentElement);

  var observer = new MutationObserver(function (mutations) {
    mutations.forEach(function (mutation) {
      stripAttribute(mutation.target);
      mutation.addedNodes.forEach(stripAttribute);
    });
  });

  observer.observe(document.documentElement, {
    attributes: true,
    attributeFilter: [ATTRIBUTE],
    childList: true,
    subtree: true
  });

  window.addEventListener('load', function () {
    stripAttribute(document.documentElement);
    window.setTimeout(function () {
      observer.disconnect();
    }, 1000);
  }, { once: true });
})();
`;

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" translate="no" className="h-full antialiased scroll-smooth">
      <body className="min-h-full flex flex-col font-sans" suppressHydrationWarning>
        {process.env.NODE_ENV === "development" && (
          <Script
            id="strip-extension-hydration-attrs"
            strategy="beforeInteractive"
            dangerouslySetInnerHTML={{ __html: stripExtensionHydrationAttrsScript }}
          />
        )}
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
