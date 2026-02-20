'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

export default function Navigation() {
  const pathname = usePathname()

  const isActive = (path: string) => pathname === path

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2 font-bold text-xl text-blue-600">
              <span>🔗</span>
              <span>URL Shortener</span>
            </Link>

            <div className="hidden md:flex gap-1">
              <Link
                href="/"
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/')
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Home
              </Link>
              <Link
                href="/analytics"
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/analytics')
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Analytics
              </Link>
              <Link
                href="/manage"
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  isActive('/manage')
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                Manage URLs
              </Link>
            </div>
          </div>

          {/* Mobile menu icon placeholder */}
          <div className="md:hidden flex items-center">
            <button className="text-gray-700 hover:text-gray-900">
              <span className="sr-only">Menu</span>
              ☰
            </button>
          </div>
        </div>
      </div>
    </nav>
  )
}
