"use client"
import { useCallback, useEffect, useState } from 'react'
import { Bot, Plus, RefreshCw, Trash2, X } from 'lucide-react'
import type { AgentCreateRequest, AgentDef, AgentsListResponse } from '@/types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function AgentsPanel() {
  const [agents, setAgents] = useState<AgentDef[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState<AgentCreateRequest>({ name: '', system_prompt: '', description: '' })
  const [submitting, setSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const fetchAgents = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await fetch(`${API_BASE}/agents`)
      if (!res.ok) throw new Error(`Failed to fetch agents (${res.status})`)
      const data: AgentsListResponse = await res.json()
      setAgents(data.agents)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchAgents()
  }, [fetchAgents])

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setFormError(null)
    try {
      const res = await fetch(`${API_BASE}/agents`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || `Error ${res.status}`)
      setAgents((prev) => [...prev, data])
      setShowForm(false)
      setForm({ name: '', system_prompt: '', description: '' })
    } catch (err) {
      setFormError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(name: string) {
    if (!confirm(`Delete agent "${name}"?`)) return
    try {
      const res = await fetch(`${API_BASE}/agents/${encodeURIComponent(name)}`, { method: 'DELETE' })
      const data = await res.json()
      if (!res.ok) throw new Error(data.detail || `Error ${res.status}`)
      setAgents((prev) => prev.filter((a) => a.name !== name))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-indigo-600" />
          <h2 className="text-lg font-semibold text-gray-800">Agent Registry</h2>
          <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
            {agents.length} agent{agents.length !== 1 ? 's' : ''}
          </span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={fetchAgents}
            disabled={loading}
            title="Refresh"
            className="p-1.5 text-gray-400 hover:text-gray-600 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={() => { setShowForm((v) => !v); setFormError(null) }}
            title="Register new agent"
            className="p-1.5 text-indigo-500 hover:text-indigo-700 transition-colors"
          >
            {showForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {error && (
        <p className="text-sm text-red-600 bg-red-50 rounded px-3 py-2 border border-red-200">{error}</p>
      )}

      {/* New agent form */}
      {showForm && (
        <form onSubmit={handleCreate} className="space-y-3 bg-indigo-50 rounded-lg p-4 border border-indigo-100">
          <p className="text-sm font-semibold text-indigo-800">Register new agent</p>
          {formError && (
            <p className="text-xs text-red-600 bg-red-50 rounded px-2 py-1 border border-red-200">{formError}</p>
          )}
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-0.5">
              Name <span className="text-gray-400">(letters, digits, hyphens; start with letter)</span>
            </label>
            <input
              value={form.name}
              onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
              pattern="^[A-Za-z][A-Za-z0-9-]{0,31}$"
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Editor"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-0.5">Description</label>
            <input
              value={form.description}
              onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
              required
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="Polishes prose for grammar, clarity, and conciseness"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-700 mb-0.5">System prompt</label>
            <textarea
              value={form.system_prompt}
              onChange={(e) => setForm((f) => ({ ...f, system_prompt: e.target.value }))}
              required
              rows={4}
              className="w-full border border-gray-300 rounded px-2 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-400"
              placeholder="You are an expert editor. Your job is to..."
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              disabled={submitting}
              className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold px-4 py-1.5 rounded transition-colors"
            >
              {submitting ? 'Registering…' : 'Register'}
            </button>
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5 rounded transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      )}

      {/* Agent list */}
      <ul className="space-y-2">
        {agents.map((agent) => (
          <li key={agent.name} className="flex items-start justify-between gap-3 border border-gray-100 rounded-lg px-4 py-3 bg-gray-50">
            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-gray-800 text-sm">{agent.name}</span>
                {agent.builtin && (
                  <span className="text-xs bg-gray-200 text-gray-600 px-1.5 py-0.5 rounded">built-in</span>
                )}
              </div>
              <p className="text-xs text-gray-500 mt-0.5 truncate">{agent.description}</p>
            </div>
            {!agent.builtin && (
              <button
                onClick={() => handleDelete(agent.name)}
                title={`Delete ${agent.name}`}
                className="shrink-0 p-1 text-red-300 hover:text-red-600 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            )}
          </li>
        ))}
        {agents.length === 0 && !loading && (
          <p className="text-sm text-gray-400 text-center py-3">No agents registered.</p>
        )}
      </ul>
    </div>
  )
}
