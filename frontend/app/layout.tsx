import "./globals.css";

export const metadata = {
  title: "TikTok Structure Cloner",
  description: "Clone la formule d'une vidéo TikTok sur un nouveau sujet",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body className="bg-neutral-950 text-white min-h-screen">{children}</body>
    </html>
  );
}
