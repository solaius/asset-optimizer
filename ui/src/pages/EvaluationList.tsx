import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export function EvaluationList() {
  const { data: evaluations, isLoading } = useQuery({ queryKey: ['evaluations'], queryFn: api.evaluations.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-gray-900">Evaluations</h1>
      <div className="bg-white rounded-lg border">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Asset Type</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Criteria</th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {evaluations?.map(ev => (
              <tr key={ev.id} className="hover:bg-gray-50">
                <td className="px-4 py-3 font-medium">
                  <Link to={`/evaluations/${ev.id}`} className="text-blue-600 hover:underline">{ev.name}</Link>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500">{ev.asset_type}</td>
                <td className="px-4 py-3 text-sm text-gray-500">{ev.criteria.length} criteria</td>
                <td className="px-4 py-3 text-sm text-gray-500">{new Date(ev.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {(!evaluations || evaluations.length === 0) && (
          <p className="p-4 text-gray-500">No evaluations yet.</p>
        )}
      </div>
    </div>
  )
}
