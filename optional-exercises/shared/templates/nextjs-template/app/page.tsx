import ChatInterface from '@/components/ChatInterface';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Next.js AI Chat
          </h1>
          <p className="text-gray-600">
            Production-ready template with Claude integration
          </p>
        </header>

        {/* Chat Interface */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <ChatInterface />
        </div>

        {/* Footer */}
        <footer className="text-center mt-8 text-sm text-gray-500">
          <p>
            Built with Next.js 14, TypeScript, and Tailwind CSS
          </p>
          <p className="mt-1">
            Powered by{' '}
            <a
              href="https://www.anthropic.com"
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
            >
              Anthropic Claude
            </a>
          </p>
        </footer>
      </div>
    </div>
  );
}
