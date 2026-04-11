import type { ReactNode } from "react";
import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, Michroma } from "next/font/google";
import { LenisProvider } from "@/components/lenis-provider";
import "./globals.css";

const display = Michroma({
  variable: "--font-display",
  subsets: ["latin"],
  weight: "400",
});

const mono = IBM_Plex_Mono({
  variable: "--font-mono-ui",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "smart-city-managment",
  description:
    "smart-city-managment landing page built with Next.js, Tailwind CSS, and Lenis.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${display.variable} ${mono.variable} h-full bg-canvas antialiased`}
    >
      <body className="min-h-full bg-canvas font-sans text-ink">
        <LenisProvider>{children}</LenisProvider>
      </body>
    </html>
  );
}
