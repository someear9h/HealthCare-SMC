import { parseISO, differenceInHours } from 'date-fns'

export function aggregateByIndicator(records = [], facilityFilter = 'All') {
  const now = new Date()
  const map = new Map()

  records.forEach((r) => {
    try {
      // Normalize keys to handle different backend naming conventions
      const indicator = r.indicatorname || r.indicator || 'Unknown'
      const facility = (r.facility_type || r.facilityType || 'Unknown')
      const total = Number(r.total_cases || 0)
      
      // ########################################################################
      // BUG FIX: Ensure vaccination_count is captured correctly from payload
      // ########################################################################
      const vaccination = Number(r.vaccination_count || 0)
      
      const ts = r.timestamp ? new Date(r.timestamp) : now

      // Filter for last 24 hours
      const hours = differenceInHours(now, ts)
      if (hours > 24) return

      // ########################################################################
      // BUG FIX: Robust Facility Filtering
      // Ensures "Hospital" matches "Hospitals" filter correctly
      // ########################################################################
      if (facilityFilter !== 'All') {
        const lowerFacility = facility.toLowerCase();
        if (facilityFilter === 'Hospitals' && !lowerFacility.includes('hospital')) return
        if (facilityFilter === 'Labs' && !lowerFacility.includes('lab')) return
        if (facilityFilter === 'Ambulance' && !lowerFacility.includes('ambulance')) return
      }

      const key = indicator
      if (!map.has(key)) {
        map.set(key, { 
          indicator: key, 
          total: 0, 
          vaccination_count: 0, 
          breakdown: {} 
        })
      }
      
      const entry = map.get(key)
      
      // ########################################################################
      // HUGE CHANGE: SUMMING VACCINATIONS
      // This ensures the value 85 from your payload is added to the 
      // green bar's dataKey in the BarChart.
      // ########################################################################
      entry.total += total
      entry.vaccination_count += vaccination
      
      // Track which facility type contributed to the cases
      entry.breakdown[facility] = (entry.breakdown[facility] || 0) + total
      
    } catch (e) {
      console.error("Aggregation error:", e)
    }
  })

  // Sort by total cases descending
  const arr = Array.from(map.values()).sort((a, b) => b.total - a.total)
  return arr
}
