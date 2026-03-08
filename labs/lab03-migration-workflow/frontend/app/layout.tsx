import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Migration Workflow Agent',
  description: 'AI-powered multi-step code migration between frameworks',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gradient-to-br from-slate-50 to-indigo-50 min-h-screen">
        <header className="bg-white border-b border-slate-200 shadow-sm">
          <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
              </svg>
            </div>
            <div>
              <h1 className="text-lg font-bold text-slate-800">Migration Workflow Agent</h1>
              <p className="text-xs text-slate-500">AI-powered code migration across frameworks</p>
            </div>
          </div>
        </header>
        {children}
      </body>
    </html>
  )
}
