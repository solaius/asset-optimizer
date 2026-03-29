import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'

export function Dashboard() {
  const { data: experiments } = useQuery({ queryKey: ['experiments'], queryFn: api.experiments.list })
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: api.health })

  const recent = experiments?.slice(0, 5) || []
  const active = experiments?.filter(e => e.status === 'running') || []

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="text-sm text-gray-500">
          {health ? `v${health.version} — ${health.status}` : 'Connecting...'}
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Total Experiments</div>
          <div className="text-2xl font-bold">{experiments?.length || 0}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Active</div>
          <div className="text-2xl font-bold text-blue-600">{active.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Completed</div>
          <div className="text-2xl font-bold text-green-600">
            {experiments?.filter(e => e.status === 'completed').length || 0}
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border">
        <div className="px-4 py-3 border-b">
          <h2 className="font-semibold">Recent Experiments</h2>
        </div>
        {recent.length === 0 ? (
          <p className="p-4 text-gray-500">No experiments yet. Create one to get started.</p>
        ) : (
          <ul className="divide-y">
            {recent.map(exp => (
              <li key={exp.id} className="px-4 py-3 flex items-center justify-between">
                <div>
                  <Link to={`/experiments/${exp.id}`} className="font-medium text-blue-600 hover:underline">
                    {exp.name}
                  </Link>
                  <span className="ml-2 text-sm text-gray-500">{exp.asset_type}</span>
                </div>
                <div className="flex items-center gap-3">
                  {exp.best_score !== null && (
                    <span className="text-sm font-mono">{exp.best_score.toFixed(2)}</span>
                  )}
                  <StatusBadge status={exp.status} />
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
