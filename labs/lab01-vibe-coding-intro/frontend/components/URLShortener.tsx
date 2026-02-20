'use client'

import { useState, useRef } from 'react'

interface ShortenResponse {
  short_code: string
  short_url: string
}

export default function URLShortener() {
  const [url, setUrl] = useState('')
  const [customCode, setCustomCode] = useState('')
  const [expiresAt, setExpiresAt] = useState('')
  const [result, setResult] = useState<ShortenResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [showQRCode, setShowQRCode] = useState(false)
  const [qrCodeUrl, setQRCodeUrl] = useState<string | null>(null)
  const [qrLoading, setQRLoading] = useState(false)
  const copyTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Handle date selection (no time component)
  const handleExpiresAtChange = (value: string) => {
    setExpiresAt(value)
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setError(null)
    setResult(null)
    setCopied(false)

    // Validate input
    if (!url.trim()) {
      setError('Please enter a URL')
      return
    }

    // Basic URL validation
    try {
      new URL(url)
    } catch {
      setError('Please enter a valid URL (include http:// or https://)')
      return
    }

    setLoading(true)

    try {
      const body: any = { url }
      if (customCode.trim()) {
        body.custom_code = customCode.trim()
      }
      if (expiresAt) {
        // Convert date to datetime format for backend (YYYY-MM-DD -> YYYY-MM-DDT00:00)
        body.expires_at = expiresAt + 'T00:00'
      }

      const response = await fetch('/api/shorten', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to shorten URL')
      }

      const data: ShortenResponse = await response.json()
      setResult(data)
      setUrl('')
      setCustomCode('')
      setExpiresAt('')
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred'
      setError(errorMessage)
      console.error('Error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = async () => {
    if (!result) return

    try {
      await navigator.clipboard.writeText(result.short_url)
      setCopied(true)

      if (copyTimeoutRef.current) {
        clearTimeout(copyTimeoutRef.current)
      }

      copyTimeoutRef.current = setTimeout(() => {
        setCopied(false)
      }, 2000)
    } catch {
      setError('Failed to copy to clipboard')
    }
  }

  const handleShowQRCode = async () => {
    if (!result || showQRCode) {
      // Toggle off
      setShowQRCode(false)
      setQRCodeUrl(null)
      return
    }

    setQRLoading(true)
    try {
      const response = await fetch(`/api/qrcode/${result.short_code}`)
      if (!response.ok) {
        throw new Error('Failed to generate QR code')
      }
      const blob = await response.blob()
      const url = URL.createObjectURL(blob)
      setQRCodeUrl(url)
      setShowQRCode(true)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate QR code')
    } finally {
      setQRLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
            Enter your long URL
          </label>
          <input
            id="url"
            type="text"
            placeholder="https://example.com/very/long/url/path"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 disabled:bg-gray-50 disabled:text-gray-500"
          />
        </div>

        {/* Advanced Options Toggle */}
        <button
          type="button"
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="text-sm text-blue-600 hover:text-blue-700 font-medium"
        >
          {showAdvanced ? '▼ Hide' : '▶ Show'} Advanced Options
        </button>

        {/* Advanced Options */}
        {showAdvanced && (
          <div className="space-y-4 bg-blue-50 p-4 rounded-lg border border-blue-200">
            <div>
              <label htmlFor="customCode" className="block text-sm font-medium text-gray-700 mb-2">
                Custom Short Code (optional)
              </label>
              <input
                id="customCode"
                type="text"
                placeholder="e.g., mycode"
                value={customCode}
                onChange={(e) => setCustomCode(e.target.value)}
                disabled={loading}
                maxLength={20}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder-gray-400 disabled:bg-gray-50"
              />
              <p className="text-xs text-gray-600 mt-1">3-20 alphanumeric characters</p>
            </div>

            <div>
              <label htmlFor="expiresAt" className="block text-sm font-medium text-gray-700 mb-2">
                Expiration Date (optional)
              </label>
              <input
                id="expiresAt"
                type="date"
                value={expiresAt}
                onChange={(e) => handleExpiresAtChange(e.target.value)}
                disabled={loading}
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-50"
              />
              <p className="text-xs text-gray-600 mt-1">Select a date for link expiration (defaults to 00:00 UTC)</p>
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-semibold py-3 px-4 rounded-lg transition-colors duration-200 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              <span>Shortening...</span>
            </>
          ) : (
            <span>Shorten URL</span>
          )}
        </button>
      </form>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded">
          <p className="text-red-700 text-sm font-medium">Error</p>
          <p className="text-red-600 text-sm mt-1">{error}</p>
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-2">Your shortened URL:</p>
            <div className="flex items-center gap-2 bg-white border border-gray-300 rounded px-3 py-2">
              <code className="flex-1 text-sm text-gray-800 break-all font-mono">
                {result.short_url}
              </code>
            </div>
          </div>

          <button
            onClick={handleCopy}
            className={`w-full py-2 px-4 rounded-lg font-medium transition-colors duration-200 flex items-center justify-center gap-2 ${
              copied
                ? 'bg-green-500 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            {copied ? (
              <>
                <span>✓</span>
                <span>Copied!</span>
              </>
            ) : (
              <>
                <span>📋</span>
                <span>Copy to Clipboard</span>
              </>
            )}
          </button>

          <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded border border-blue-200">
            <p>
              <strong>Short code:</strong>{' '}
              <code className="bg-white px-2 py-1 rounded font-mono text-gray-800">
                {result.short_code}
              </code>
            </p>
          </div>

          <button
            onClick={handleShowQRCode}
            disabled={qrLoading}
            className="w-full bg-purple-100 text-purple-700 hover:bg-purple-200 disabled:opacity-50 disabled:cursor-not-allowed px-3 py-2 rounded text-center font-medium transition-colors"
          >
            {qrLoading ? '⏳ QR Loading...' : showQRCode ? '📱 Hide QR' : '📱 Show QR'}
          </button>

          {showQRCode && qrCodeUrl && (
            <div className="mt-4 p-4 bg-gray-50 border border-gray-200 rounded flex flex-col items-center gap-3">
              <p className="text-sm text-gray-700 font-medium">QR Code</p>
              <img
                src={qrCodeUrl}
                alt="QR Code"
                className="w-48 h-48 border-2 border-gray-300 rounded bg-white p-2"
              />
              <p className="text-xs text-gray-500 text-center">Scan to visit your shortened link</p>
            </div>
          )}
        </div>
      )}

      {/* Info Message */}
      {!result && !error && (
        <div className="text-center text-gray-500 text-sm py-4">
          <p>✨ Paste a long URL and click "Shorten URL" to get started</p>
        </div>
      )}
    </div>
  )
}

