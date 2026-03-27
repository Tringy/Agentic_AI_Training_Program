import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Football Game Review Assistant",
  description: "Multi-agent AI analysis of football matches",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen">
        <div className="bg-gradient-to-b from-pitch-green to-grass">
          <header className="border-b border-goal-yellow">
            <div className="max-w-6xl mx-auto px-4 py-6">
              <h1 className="text-4xl font-bold text-white">⚽ Football Game Review</h1>
              <p className="text-goal-yellow mt-2">Multi-Agent AI Analysis System</p>
            </div>
          </header>
        </div>
        <main className="max-w-6xl mx-auto px-4 py-8">
          {children}
        </main>
        <footer className="border-t border-gray-700 mt-12 py-6">
          <div className="max-w-6xl mx-auto px-4 text-center text-gray-400">
            <p>Football Game Review Assistant © 2026</p>
          </div>
        </footer>
      </body>
    </html>
  );
}
