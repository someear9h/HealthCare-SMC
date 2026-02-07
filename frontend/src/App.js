import React, { useEffect, useState, useCallback } from 'react'
import { getRecentLogs } from './services/api'
import BarChartComponent from './components/BarChartComponent'
import TimeSeriesComponent from './components/TimeSeriesComponent'
import MapPanel from './components/MapPanel'
import { aggregateByIndicator } from './utils/format'
import { format } from 'date-fns'

const FILTERS = [
  { key: 'All', label: 'All facilities' },
  { key: 'Hospitals', label: 'Hospitals only' },
  { key: 'Labs', label: 'Labs only' },
  { key: 'Ambulance', label: 'Ambulance/Other' }
]

function ToggleGroup({ value, onChange }) {
  return (
    <div className="flex gap-4 items-center">
      {FILTERS.map((f) => (
        <button
          key={f.key}
          onClick={() => onChange(f.key)}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${value === f.key ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
        >
          {f.label}
        </button>
      ))}
    </div>
  )
}

export default function App() {
  const [records, setRecords] = useState([])
  const [filter, setFilter] = useState('All')
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState(null)

  const fetch = useCallback(async () => {
    setLoading(true)
    try {
      const recs = await getRecentLogs()
      setRecords(recs || [])
      setLastUpdated(new Date())
    } catch (e) {
      setRecords([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const id = setInterval(fetch, 30000)
    return () => clearInterval(id)
  }, [fetch])

  useEffect(() => {
    const agg = aggregateByIndicator(records, filter)
    setData(agg)
  }, [records, filter])

  // small synthetic timeseries for demo
  const timeseries = data.slice(0,5).map((d, i) => ({ time: `T-${i}`, value: d.total }))

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold">🏥 Solapur Municipal Corporation - Live Health Analytics</h1>
          <p className="text-sm text-gray-500">SMC Smart Health Dashboard</p>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold">Cases per Medical Condition (last 24 hours)</h2>
          <div className="text-sm text-gray-600">Last updated: {lastUpdated ? format(lastUpdated, 'PPpp') : 'Never'}</div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow mb-6">
          <div className="flex items-center justify-between mb-4">
            <ToggleGroup value={filter} onChange={setFilter} />
            <div className="text-sm text-gray-600">{loading ? 'Loading...' : `${data.length} conditions`}</div>
          </div>

          {loading ? (
            <div className="w-full flex items-center justify-center py-20">
              <div className="spinner" />
            </div>
          ) : data.length === 0 ? (
            <div className="py-16 text-center text-gray-500">No recent health data available.</div>
          ) : (
            <BarChartComponent data={data} />
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-medium mb-2">Timeseries (sample)</h3>
            <TimeSeriesComponent data={timeseries} />
          </div>

          <div className="bg-white p-4 rounded-lg shadow">
            <h3 className="font-medium mb-2">Map Summary</h3>
            <MapPanel data={data} />
          </div>
        </div>
      </main>
    </div>
  )
}
