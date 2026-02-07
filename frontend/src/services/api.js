import axios from 'axios'

const BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000'

export async function getRecentLogs() {
  const url = `${BASE}/logs/recent`
  const res = await axios.get(url, { timeout: 5000 })
  return res.data
}
