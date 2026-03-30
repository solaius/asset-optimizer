import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'
import type { IterationData } from '../api/client'
import { StatusBadge } from '../components/StatusBadge'
import { ScoreChart } from '../components/ScoreChart'

function IterationCard({ iteration }: { iteration: IterationData }) {
  const outputVersion = iteration.asset_versions.find(av => av.role === 'output' || av.role === 'AssetVersionRole.OUTPUT')
  const hasImage = outputVersion?.file_path != null
  const accepted = iteration.status === 'improved' || iteration.status === 'IterationStatus.IMPROVED'
  const avgScore = iteration.scores.length > 0
    ? iteration.scores.reduce((sum, s) => sum + s.value, 0) / iteration.scores.length
    : 0

  return (
    <div className={`bg-white rounded-lg border p-4 ${accepted ? 'border-green-200' : 'border-gray-200'}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-lg">Iteration {iteration.number}</span>
          <span className={`text-xs px-2 py-0.5 rounded-full ${accepted ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>
            {accepted ? 'accepted' : 'rejected'}
          </span>
        </div>
        <div className="text-right">
          <div className="text-xl font-bold">{avgScore.toFixed(1)}</div>
          <div className="text-xs text-gray-400">avg score</div>
        </div>
      </div>

      {/* Score bars */}
      <div className="space-y-2 mb-4">
        {iteration.scores.map(s => (
          <div key={s.criterion_name}>
            <div className="flex justify-between text-sm mb-0.5">
              <span className="text-gray-600">{s.criterion_name.replace(/_/g, ' ')}</span>
              <span className="font-mono">{s.value.toFixed(1)}/{s.max_value.toFixed(0)}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${s.value >= 8 ? 'bg-green-500' : s.value >= 5 ? 'bg-yellow-500' : 'bg-red-400'}`}
                style={{ width: `${(s.value / s.max_value) * 100}%` }}
              />
            </div>
            {s.details?.reasoning && (
              <p className="text-xs text-gray-400 mt-0.5 line-clamp-2">{s.details.reasoning}</p>
            )}
          </div>
        ))}
      </div>

      {/* Generated image */}
      {hasImage && outputVersion && (
        <div className="mb-3">
          <img
            src={api.assets.getImageUrl(outputVersion.id)}
            alt={`Iteration ${iteration.number}`}
            className="w-full rounded-lg border"
            loading="lazy"
          />
        </div>
      )}

      {/* Prompt text */}
      {outputVersion?.content && (
        <details className="text-sm">
          <summary className="cursor-pointer text-gray-500 hover:text-gray-700">View prompt</summary>
          <pre className="mt-2 p-3 bg-gray-50 rounded text-xs whitespace-pre-wrap">{outputVersion.content}</pre>
        </details>
      )}

      {iteration.duration_ms && (
        <div className="text-xs text-gray-400 mt-2">
          Duration: {(iteration.duration_ms / 1000).toFixed(1)}s
        </div>
      )}
    </div>
  )
}

export function ExperimentDetail() {
  const { id } = useParams<{ id: string }>()

  const { data: experiment, isLoading: loadingExp } = useQuery({
    queryKey: ['experiment', id],
    queryFn: () => api.experiments.get(id!),
    enabled: !!id,
  })

  const { data: iterations, isLoading: loadingIter } = useQuery({
    queryKey: ['iterations', id],
    queryFn: () => api.experiments.iterations(id!),
    enabled: !!id,
  })

  if (loadingExp) return <p>Loading...</p>
  if (!experiment) return <p>Experiment not found.</p>

  // Build score chart data from iterations
  const chartData = (iterations || []).map(it => {
    const point: Record<string, number> = { iteration: it.number }
    for (const s of it.scores) {
      point[s.criterion_name.replace(/_/g, ' ')] = s.value
    }
    // Add average
    if (it.scores.length > 0) {
      point['average'] = it.scores.reduce((sum, s) => sum + s.value, 0) / it.scores.length
    }
    return point
  })

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <h1 className="text-2xl font-bold text-gray-900">{experiment.name}</h1>
        <StatusBadge status={experiment.status} />
      </div>

      {/* Stats cards */}
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
          <div className="text-sm text-gray-500">Iterations</div>
          <div className="font-semibold">{iterations?.length ?? '—'}</div>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <div className="text-sm text-gray-500">Created</div>
          <div className="font-semibold">{new Date(experiment.created_at).toLocaleDateString()}</div>
        </div>
      </div>

      {experiment.description && (
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-2">Description</h2>
          <p className="text-gray-600">{experiment.description}</p>
        </div>
      )}

      {/* Score progression chart */}
      <div className="bg-white rounded-lg border p-4">
        <h2 className="font-semibold mb-4">Score Progression</h2>
        {loadingIter ? <p>Loading scores...</p> : <ScoreChart data={chartData} />}
      </div>

      {/* Iteration cards */}
      <div>
        <h2 className="font-semibold text-lg mb-3">Iterations</h2>
        {loadingIter ? (
          <p>Loading iterations...</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {(iterations || []).map(it => (
              <IterationCard key={it.id} iteration={it} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
