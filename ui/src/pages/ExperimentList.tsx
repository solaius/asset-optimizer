import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'

export function ExperimentList() {
  const { data: experiments, isLoading } = useQuery({ queryKey: ['experiments'], queryFn: api.experiments.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Experiments</h1>
      <div className="bg-white rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Best Score</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {experiments?.map(exp => (
              <tr key={exp.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link to={`/experiments/${exp.id}`} className="text-blue-600 hover:underline font-medium">{exp.name}</Link>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{exp.asset_type}</td>
                <td className="px-4 py-3"><StatusBadge status={exp.status} /></td>
                <td className="px-4 py-3 text-sm font-mono">{exp.best_score !== null ? exp.best_score.toFixed(2) : '—'}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(exp.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
