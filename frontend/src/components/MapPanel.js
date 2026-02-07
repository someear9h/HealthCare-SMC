import React from 'react'

export default function MapPanel({ data = [] }) {
  // Simple placeholder map visualization showing top wards/districts
  const top = data.slice(0,5)
  return (
    <div className="w-full h-64 bg-gradient-to-br from-green-50 to-blue-50 rounded-lg p-4">
      <h4 className="font-medium mb-2">Map (summary)</h4>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {top.map((t, i) => (
          <div key={t.indicator} className="bg-white p-2 rounded shadow text-sm">
            <div className="font-semibold">{t.indicator}</div>
            <div className="text-gray-600">Cases: {t.total}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
