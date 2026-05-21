import { useState, useCallback } from 'react'
import { getRecentLogs, getLogFiles } from '../services/api'

export function useLogs() {
  const [logs, setLogs] = useState(null)
  const [logFiles, setLogFiles] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchLogs = useCallback(async (logFile = 'trading_bot.log', lines = 100) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getRecentLogs(logFile, lines)
      setLogs(data)
    } catch (err) {
      setError(err.userMessage || 'Failed to load logs')
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchLogFiles = useCallback(async () => {
    try {
      const data = await getLogFiles()
      setLogFiles(data.files || [])
    } catch {
      setLogFiles([])
    }
  }, [])

  return { logs, logFiles, loading, error, fetchLogs, fetchLogFiles }
}