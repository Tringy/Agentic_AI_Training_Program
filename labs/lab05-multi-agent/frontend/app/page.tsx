import AgentRunner from '@/components/AgentRunner'
import AgentsPanel from '@/components/AgentsPanel'
import MemoryPanel from '@/components/MemoryPanel'

export default function Home() {
  return (
    <main className="max-w-4xl mx-auto px-4 py-10 w-full space-y-8">
      <AgentRunner />
      <AgentsPanel />
      <MemoryPanel />
    </main>
  )
}
