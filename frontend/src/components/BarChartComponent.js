import React from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LabelList,
  CartesianGrid
} from 'recharts'

function CustomTooltip({ active, payload }) {
  if (!active || !payload || !payload.length) return null
  const d = payload[0].payload
  return (
    <div className="bg-white p-2 rounded shadow text-sm">
      <div className="font-semibold">{d.indicator}</div>
      <div>Total: {d.total}</div>
      <div className="mt-1">Breakdown:</div>
      <ul className="pl-4 list-disc">
        {Object.entries(d.breakdown).map(([k, v]) => (
          <li key={k}>{k}: {v}</li>
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
        <Bar dataKey="total" fill="#4f46e5" radius={[4,4,0,0]}>
          <LabelList dataKey="total" position="top" />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
