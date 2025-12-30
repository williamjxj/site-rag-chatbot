import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { Header } from "@/components/header";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Site RAG Chatbot",
  description: "Chatbot powered by RAG for website content",
  icons: {
    icon: "/favicon.svg",
    type: "image/svg+xml",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full flex flex-col`}>
        <Header />
        <div className="flex-1 min-h-0">
          {children}
        </div>
      </body>
    </html>
  );
}
