import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white border-b border-gray-200 px-6 py-3">
        <div className="flex items-center gap-6">
          <Link to="/" className="text-lg font-semibold text-gray-900">Asset Optimizer</Link>
          <Link to="/experiments" className="text-gray-600 hover:text-gray-900">Experiments</Link>
          <Link to="/evaluations" className="text-gray-600 hover:text-gray-900">Evaluations</Link>
          <Link to="/providers" className="text-gray-600 hover:text-gray-900">Providers</Link>
        </div>
      </nav>
      <main className="p-6">{children}</main>
    </div>
  )
}

function Dashboard() {
  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-4">Dashboard</h1>
      <p className="text-gray-600">Welcome to Asset Optimizer.</p>
    </div>
  )
}

function Placeholder({ title }: { title: string }) {
  return <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/experiments" element={<Placeholder title="Experiments" />} />
            <Route path="/evaluations" element={<Placeholder title="Evaluations" />} />
            <Route path="/providers" element={<Placeholder title="Providers" />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
