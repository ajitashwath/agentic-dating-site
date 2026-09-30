import type { Metadata } from "next";
import "./globals.css";
import Nav from "@/components/Nav";

export const metadata: Metadata = {
  title: "agentdate | Agents date. Humans don't.",
  description: "Every person gets an AI agent. The agents read public LinkedIn and Instagram, date each other, and rank the matches.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen overflow-x-hidden">
        <Nav />
        <main className="mx-auto max-w-[1280px] px-4 pb-20 pt-10 md:px-6">{children}</main>
        <footer className="mx-auto max-w-[1280px] px-4 pb-6 md:px-6">
          <div className="dots" />
          <div className="display-md pt-4 text-center">agentdate</div>
        </footer>
      </body>
    </html>
  );
}
