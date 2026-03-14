import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Multi-Agent System',
  description: 'Supervisor/worker multi-agent orchestration',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <nav className="bg-white border-b border-gray-200">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex items-center h-16 gap-3">
                <span className="font-bold text-xl text-indigo-600">Multi-Agent System</span>
                <span className="text-gray-400 text-sm">Supervisor · Researcher · Writer · Reviewer</span>
              </div>
            </div>
          </nav>
          {children}
        </div>
      </body>
    </html>
  )
}
