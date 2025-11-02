import "./globals.css";
import { ReactNode } from "react";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <title>Agent Koffi - Assistant IA</title>
        <meta name="description" content="Assistant IA spécialisé en recherche internet" />
      </head>
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}