import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Link from 'next/link'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Codebase RAG System',
  description: 'AI-powered codebase Q&A with evaluation',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gray-50 flex flex-col">
          <nav className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-16">
                <div className="flex items-center gap-8">
                  <Link href="/" className="font-bold text-xl text-violet-600">
                    RAG System
                  </Link>
                  <div className="flex gap-6 text-sm font-medium text-gray-600">
                    <Link href="/" className="hover:text-violet-600 transition-colors">
                      Index
                    </Link>
                    <Link href="/query" className="hover:text-violet-600 transition-colors">
                      Query
                    </Link>
                    <Link href="/evaluate" className="hover:text-violet-600 transition-colors">
                      Evaluate
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </nav>
          {children}
        </div>
      </body>
    </html>
  )
}
