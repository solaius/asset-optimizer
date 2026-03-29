import { BrowserRouter, Routes, Route, Link } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Dashboard } from './pages/Dashboard'
import { ExperimentList } from './pages/ExperimentList'
import { ExperimentDetail } from './pages/ExperimentDetail'
import { EvaluationList } from './pages/EvaluationList'
import { ProviderSettings } from './pages/ProviderSettings'

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

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/experiments" element={<ExperimentList />} />
            <Route path="/experiments/:id" element={<ExperimentDetail />} />
            <Route path="/evaluations" element={<EvaluationList />} />
            <Route path="/providers" element={<ProviderSettings />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
