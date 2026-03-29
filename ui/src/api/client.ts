const BASE_URL = '/api/v1'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!resp.ok) {
    throw new Error(`API error: ${resp.status} ${resp.statusText}`)
  }
  if (resp.status === 204) return undefined as T
  return resp.json()
}

export interface Evaluation {
  id: string
  name: string
  asset_type: string
  description: string
  criteria: Array<{ name: string; description: string; max_score: number; requires_image?: boolean }>
  scorer_config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface Experiment {
  id: string
  name: string
  description: string | null
  asset_type: string
  evaluation_id: string
  status: string
  config: Record<string, unknown>
  best_score: number | null
  best_image_asset_version_id: string | null
  total_cost: number | null
  created_at: string
  updated_at: string
}

export const api = {
  health: () => request<{ status: string; version: string }>('/health'),

  evaluations: {
    list: () => request<Evaluation[]>('/evaluations'),
    get: (id: string) => request<Evaluation>(`/evaluations/${id}`),
    create: (data: Partial<Evaluation>) => request<Evaluation>('/evaluations', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/evaluations/${id}`, { method: 'DELETE' }),
  },

  experiments: {
    list: () => request<Experiment[]>('/experiments'),
    get: (id: string) => request<Experiment>(`/experiments/${id}`),
    create: (data: Partial<Experiment>) => request<Experiment>('/experiments', { method: 'POST', body: JSON.stringify(data) }),
    delete: (id: string) => request<void>(`/experiments/${id}`, { method: 'DELETE' }),
  },

  providers: {
    list: () => request<{ text: string[]; image: string[] }>('/providers'),
  },

  assets: {
    getImageUrl: (assetVersionId: string) => `${BASE_URL}/assets/${assetVersionId}/image`,
  },
}
