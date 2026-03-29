import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'
import { ScoreChart } from '../components/ScoreChart'

export function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()
  const { data: experiment, isLoading } = useQuery({
    queryKey: ['experiment', id],
    queryFn: () => api.experiments.get(id!),
    enabled: !!id,
  })

  if (isLoading) return <p>Loading...</p>
  if (!experiment) return <p>Experiment not found.</p>

  const hasImage = !!experiment.best_image_asset_version_id

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">{experiment.name}</h1>
        <StatusBadge status={experiment.status} />
      </div>
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Asset Type</div>
          <div className="font-semibold">{experiment.asset_type}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Best Score</div>
          <div className="text-xl font-bold">{experiment.best_score !== null ? experiment.best_score.toFixed(2) : '—'}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Max Iterations</div>
          <div className="font-semibold">{(experiment.config as Record<string, unknown>)?.max_iterations as number || '—'}</div>
        </div>
        {experiment.total_cost !== null && experiment.total_cost !== undefined ? (
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Total Cost</div>
            <div className="font-semibold">${experiment.total_cost.toFixed(4)}</div>
          </div>
        ) : (
          <div className="bg-white rounded-lg border p-4">
            <div className="text-sm text-gray-500">Created</div>
            <div className="font-semibold">{new Date(experiment.created_at).toLocaleDateString()}</div>
          </div>
        )}
      </div>

      {hasImage && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-4">Best Generated Image</h2>
          <img
            src={api.assets.getImageUrl(experiment.best_image_asset_version_id!)}
            alt="Best generated image"
            className="max-w-lg rounded-lg border"
            loading="lazy"
          />
        </div>
      )}

      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-4">Score Progression</h2>
        <ScoreChart data={[]} />
      </div>

      {experiment.description && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Description</h2>
          <p className="text-gray-600">{experiment.description}</p>
        </div>
      )}
    </div>
  )
}
