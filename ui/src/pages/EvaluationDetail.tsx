import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function EvaluationDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: evaluation, isLoading } = useQuery({
    queryKey: ['evaluation', id],
    queryFn: () => api.evaluations.get(id!),
    enabled: !!id,
  })

  if (isLoading) return <p>Loading...</p>
  if (!evaluation) return <p>Evaluation not found.</p>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">{evaluation.name}</h1>
        {evaluation.description && (
          <p className="text-gray-500 mt-1">{evaluation.description}</p>
        )}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Asset Type</div>
          <div className="font-semibold">{evaluation.asset_type}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Criteria Count</div>
          <div className="font-semibold">{evaluation.criteria.length}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Created</div>
          <div className="font-semibold">{new Date(evaluation.created_at).toLocaleDateString()}</div>
        </div>
      </div>

      <div className="bg-white rounded-lg border">
        <div className="px-4 py-3 border-b">
          <h2 className="font-semibold">Criteria</h2>
        </div>
        <div className="divide-y">
          {evaluation.criteria.map((c, i) => (
            <div key={i} className="p-4">
              <div className="flex items-center justify-between mb-1">
                <span className="font-medium">{c.name.replace(/_/g, ' ')}</span>
                <div className="flex items-center gap-2">
                  {(c as any).requires_image && (
                    <span className="text-xs bg-purple-100 text-purple-700 px-2 py-0.5 rounded-full">visual</span>
                  )}
                  <span className="text-sm text-gray-400">max: {c.max_score}</span>
                </div>
              </div>
              <p className="text-sm text-gray-600">{c.description}</p>
              {(c as any).rubric && (
                <pre className="mt-2 text-xs text-gray-400 whitespace-pre-wrap bg-gray-50 rounded p-2">{(c as any).rubric}</pre>
              )}
            </div>
          ))}
        </div>
      </div>

      {Object.keys(evaluation.scorer_config).length > 0 && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Scorer Configuration</h2>
          <pre className="text-sm text-gray-600 bg-gray-50 rounded p-3">
            {JSON.stringify(evaluation.scorer_config, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
