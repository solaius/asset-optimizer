import { useQuery } from '@tanstack/react-query'
import { api } from '../api/client'

export function ProviderSettings() {
  const { data: providers, isLoading } = useQuery({ queryKey: ['providers'], queryFn: api.providers.list })

  if (isLoading) return <p>Loading...</p>

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">Providers</h1>
      <div className="grid grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Text Providers</h2>
          <ul className="space-y-2">
            {providers?.text.map(name => (
              <li key={name} className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gray-300" />
                <span className="text-sm">{name}</span>
              </li>
            ))}
          </ul>
        </div>
        <div className="bg-white rounded-lg border p-4">
          <h2 className="font-semibold mb-3">Image Providers</h2>
          <ul className="space-y-2">
            {providers?.image.map(name => (
              <li key={name} className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-gray-300" />
                <span className="text-sm">{name}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}
