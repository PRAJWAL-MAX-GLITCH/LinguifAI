import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";
import SessionProvider from "./SessionProvider";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata = {
  title: {
    default: "LinguifAI – AI Language Translation",
    template: "%s | LinguifAI",
  },
  description:
    "Translate across 100+ languages using GPT-4o, Gemini 1.5 Pro, and DeepSeek. Powered by AI with tone control, confidence scores, and full history.",
  keywords: ["AI translation", "language translation", "GPT-4o", "Gemini", "multilingual"],
  openGraph: {
    title: "LinguifAI – AI Language Translation",
    description:
      "Next-generation multilingual translation powered by GPT-4o, Gemini, and DeepSeek.",
    type: "website",
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        <SessionProvider>
          <Providers>{children}</Providers>
        </SessionProvider>
      </body>
    </html>
  );
}
