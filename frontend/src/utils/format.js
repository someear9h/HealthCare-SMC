import { parseISO, differenceInHours } from 'date-fns'

export function aggregateByIndicator(records = [], facilityFilter = 'All') {
  const now = new Date()
  const map = new Map()

  records.forEach((r) => {
    try {
      const indicator = r.indicatorname || r.indicator || 'Unknown'
      const facility = (r.facility_type || r.facilityType || 'Unknown')
      const total = Number(r.total_cases || r.total_cases || 0)
      const vaccination = Number(r.vaccination_count || 0)
      const ts = r.timestamp ? new Date(r.timestamp) : now

      const hours = differenceInHours(now, ts)
      if (hours > 24) return

      if (facilityFilter !== 'All') {
        if (facilityFilter === 'Hospitals' && facility.toLowerCase().indexOf('hospital') === -1) return
        if (facilityFilter === 'Labs' && facility.toLowerCase().indexOf('lab') === -1) return
        if (facilityFilter === 'Ambulance' && facility.toLowerCase().indexOf('ambulance') === -1) return
      }

      const key = indicator
      if (!map.has(key)) map.set(key, { indicator: key, total: 0, vaccination_count: 0, breakdown: {} })
      const entry = map.get(key)
      entry.total += total
      entry.vaccination_count += vaccination
      entry.breakdown[facility] = (entry.breakdown[facility] || 0) + total
    } catch (e) {}
  })

  const arr = Array.from(map.values()).sort((a, b) => b.total - a.total)
  return arr
}
