import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { QueryProvider } from "@/lib/query-provider";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "LeakSight - Tech Leak Intelligence",
  description: "AI-Powered Tech Leak Intelligence Platform",
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <head>
        <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet" />
      </head>
      <body className={`${inter.className} font-display bg-obsidian text-slate-400 antialiased selection:bg-accent-lime/30 overflow-hidden`}>
        <QueryProvider>
          <div className="flex flex-col h-screen overflow-hidden">
            <Header />
            <main className="flex-1 overflow-y-auto custom-scrollbar p-4 lg:p-6">
              {children}
            </main>
            <Footer />
          </div>
        </QueryProvider>
      </body>
    </html>
  );
}
