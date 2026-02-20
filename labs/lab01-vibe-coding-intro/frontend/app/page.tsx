'use client'

import { useState } from 'react'
import URLShortener from '@/components/URLShortener'

export default function Home() {
  return (
    <main className="flex items-center justify-center min-h-[calc(100vh-64px)] px-4 py-8">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-lg shadow-lg p-8 space-y-2">
          <h1 className="text-4xl font-bold text-center text-gray-800 mb-2">
            URL Shortener
          </h1>
          <p className="text-center text-gray-600 mb-8">
            Transform long URLs into short, shareable links
          </p>
          <URLShortener />
        </div>
      </div>
    </main>
  )
}

