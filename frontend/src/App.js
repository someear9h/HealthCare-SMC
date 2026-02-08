import React, { useEffect, useState, useCallback } from 'react'
import { getRecentLogs } from './services/api'
import BarChartComponent from './components/BarChartComponent'
import TimeSeriesComponent from './components/TimeSeriesComponent'
import MapPanel from './components/MapPanel'
import KPIStrip from './components/KPIStrip'
import BedPredictionPanel from './components/BedPredictionPanel'
import WardHeatmap from './components/WardHeatmap'
import AmbulanceTracker from './components/AmbulanceTracker'
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
  const [tab, setTab] = useState('dashboard') // 'dashboard' or 'cases'

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

  const timeseries = data.slice(0, 5).map((d, i) => ({ time: `T-${i}`, value: d.total }))

  return (
    <div className="min-h-screen bg-slate-900 text-gray-100">
      <header className="bg-gradient-to-r from-slate-900 to-slate-800 shadow-lg border-b border-slate-700">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold">🏥 Solapur Municipal Corporation - Command Center</h1>
          <p className="text-sm text-gray-400">Smart Public Health Management System</p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex gap-8">
            <button
              onClick={() => setTab('dashboard')}
              className={`py-4 px-4 border-b-2 font-medium transition-colors ${
                tab === 'dashboard'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              📊 Command Dashboard
            </button>
            <button
              onClick={() => setTab('cases')}
              className={`py-4 px-4 border-b-2 font-medium transition-colors ${
                tab === 'cases'
                  ? 'border-blue-500 text-blue-400'
                  : 'border-transparent text-gray-400 hover:text-white'
              }`}
            >
              📈 Cases & Conditions
            </button>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* DASHBOARD TAB */}
        {tab === 'dashboard' && (
          <div className="space-y-6">
            {/* Critical KPIs Strip */}
            <KPIStrip />

            {/* Bed Prediction */}
            <BedPredictionPanel />

            {/* Ward Risk Heatmap */}
            <WardHeatmap />

            {/* Ambulance Tracker */}
            <AmbulanceTracker />

            {/* Footer */}
            <div className="text-center text-sm text-gray-500 pt-4">
              Last updated: {lastUpdated ? format(lastUpdated, 'PPpp') : 'Never'} • Auto-refresh: 10s
            </div>
          </div>
        )}

        {/* CASES TAB */}
        {tab === 'cases' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-semibold text-white">Cases per Medical Condition (last 24 hours)</h2>
              <div className="text-sm text-gray-400">Last updated: {lastUpdated ? format(lastUpdated, 'PPpp') : 'Never'}</div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow border border-slate-700">
              <div className="flex items-center justify-between mb-4">
                <ToggleGroup value={filter} onChange={setFilter} />
                <div className="text-sm text-gray-400">{loading ? 'Loading...' : `${data.length} conditions`}</div>
              </div>

              {loading ? (
                <div className="w-full flex items-center justify-center py-20">
                  <div className="text-gray-400">Loading...</div>
                </div>
              ) : data.length === 0 ? (
                <div className="py-16 text-center text-gray-500">No recent health data available.</div>
              ) : (
                <BarChartComponent data={data} />
              )}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-800 p-6 rounded-lg shadow border border-slate-700">
                <h3 className="font-medium text-white mb-4">Timeseries (sample)</h3>
                <TimeSeriesComponent data={timeseries} />
              </div>

              <div className="bg-slate-800 p-6 rounded-lg shadow border border-slate-700">
                <h3 className="font-medium text-white mb-4">Map Summary</h3>
                <MapPanel data={data} />
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
