import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface ScoreDataPoint {
  iteration: number
  score: number
  [key: string]: number
}

export function ScoreChart({ data }: { data: ScoreDataPoint[] }) {
  if (!data.length) return <p className="text-gray-500">No data yet.</p>

  const keys = Object.keys(data[0]).filter(k => k !== 'iteration')
  const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="iteration" />
        <YAxis domain={[0, 10]} />
        <Tooltip />
        <Legend />
        {keys.map((key, i) => (
          <Line key={key} type="monotone" dataKey={key} stroke={colors[i % colors.length]} strokeWidth={2} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
