import "./globals.css";
import { ReactNode } from "react";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "KOFFI - Agent IA",
  description: "Agent IA spécialisé en recherche internet avec reconnaissance vocale",
  icons: {
    icon: "/digitalization.png",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}