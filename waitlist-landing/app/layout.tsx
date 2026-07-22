import type { Metadata, Viewport } from "next";
import { Fraunces, Inter } from "next/font/google";
import { site } from "@/lib/site";
import Analytics from "@/components/Analytics";
import "./globals.css";

const display = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  axes: ["opsz"],
});

const sans = Inter({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  metadataBase: new URL(site.url),
  title: `${site.brandName} — ${site.tagline}`,
  description: site.description,
  openGraph: {
    title: `${site.brandName} — ${site.tagline}`,
    description: site.description,
    url: site.url,
    siteName: site.brandName,
    locale: "en_NZ",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: `${site.brandName} — ${site.tagline}`,
    description: site.description,
  },
};

export const viewport: Viewport = {
  themeColor: "#FAFAF7",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en-NZ" className={`${display.variable} ${sans.variable}`}>
      <body className="font-sans">
        {children}
        <Analytics />
      </body>
    </html>
  );
}
