import { useState, useEffect, useCallback } from 'react'
import { getHealth } from '../services/api'

export function useHealth(pollIntervalMs = 30000) {
  const [health, setHealth] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetch = useCallback(async () => {
    try {
      setError(null)
      const data = await getHealth()
      setHealth(data)
    } catch (err) {
      setError(err.userMessage || 'Health check failed')
      setHealth(null)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetch()
    const interval = setInterval(fetch, pollIntervalMs)
    return () => clearInterval(interval)
  }, [fetch, pollIntervalMs])

  return { health, loading, error, refetch: fetch }
}