import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG Document Chat",
  description: "Chat with your PDF documents",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="vi">
      <body className="antialiased">{children}</body>
    </html>
  );
}
