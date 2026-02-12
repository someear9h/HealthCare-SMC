import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LabelList,
  CartesianGrid,
  Legend
} from 'recharts'

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-white p-3 rounded shadow text-sm">
      <div className="font-semibold text-gray-900">{d.indicator}</div>
      <div className="mt-1 space-y-1">
        <div className="text-indigo-600">Cases: {d.total}</div>
        {d.vaccination_count !== undefined && d.vaccination_count > 0 && (
          <div className="text-green-600">Vaccinations Administered: {d.vaccination_count}</div>
        )}
      </div>
      <div className="mt-2 text-xs text-gray-600">Breakdown by facility:</div>
      <ul className="pl-4 list-disc text-xs">
        {Object.entries(d.breakdown).map(([k, v]) => (
          <li key={k} className="text-gray-700">{k}: {v}</li>
        ))}
      </ul>
    </div>
  )
}

export default function BarChartComponent({ data = [] }) {
  return (
    <ResponsiveContainer width="100%" height={420}>
      <BarChart data={data} margin={{ top: 20, right: 24, left: 8, bottom: 64 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="indicator" interval={0} angle={-30} textAnchor="end" height={80} />
        <YAxis />
        <Tooltip content={<CustomTooltip />} />
        <Legend />
        <Bar dataKey="total" fill="#4f46e5" radius={[4,4,0,0]} name="Cases">
          <LabelList dataKey="total" position="top" />
        </Bar>
        <Bar dataKey="vaccination_count" fill="#10b981" radius={[4,4,0,0]} name="Vaccinations" />
      </BarChart>
    </ResponsiveContainer>
  )
}
