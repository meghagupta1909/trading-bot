import { useState, useEffect, useRef } from 'react'
import { Terminal, RefreshCw, ChevronDown } from 'lucide-react'
import { clsx } from 'clsx'
import { useLogs } from '../hooks/useLogs'
import { getLogLevel } from '../utils/formatters'
import Spinner from './Spinner'

const lineColors = {
  error: 'text-red-400',
  warning: 'text-yellow-400',
  info: 'text-gray-200',
  debug: 'text-gray-500',
  default: 'text-gray-400',
}

export default function LogViewer() {
  const { logs, logFiles, loading, error, fetchLogs, fetchLogFiles } = useLogs()
  const [selectedFile, setSelectedFile] = useState('trading_bot.log')
  const [lineCount, setLineCount] = useState(100)
  const [autoScroll, setAutoScroll] = useState(true)
  const scrollRef = useRef(null)

  useEffect(() => {
    fetchLogFiles()
    fetchLogs(selectedFile, lineCount)
  }, [])

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const handleRefresh = () => fetchLogs(selectedFile, lineCount)

  const handleFileChange = (e) => {
    setSelectedFile(e.target.value)
    fetchLogs(e.target.value, lineCount)
  }

  return (
    <div className="card flex flex-col h-[480px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 flex-shrink-0">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <Terminal size={16} className="text-yellow-500" />
          Log Viewer
          {logs && (
            <span className="text-xs text-gray-500 font-normal">
              ({logs.total_lines} total lines)
            </span>
          )}
        </h2>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoScroll(!autoScroll)}
            className={clsx(
              'text-xs px-2 py-1 rounded border transition-colors',
              autoScroll
                ? 'bg-yellow-500/10 border-yellow-500/30 text-yellow-400'
                : 'bg-[#1e2433] border-gray-700 text-gray-500',
            )}
          >
            <ChevronDown size={12} className="inline mr-1" />
            Auto
          </button>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="text-gray-500 hover:text-gray-300 transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          </button>
        </div>
      </div>

      {/* Controls */}
      <div className="flex gap-2 mb-3 flex-shrink-0">
        <select
          value={selectedFile}
          onChange={handleFileChange}
          className="input-base text-xs py-1.5 flex-1"
        >
          {logFiles.length > 0
            ? logFiles.map((f) => (
                <option key={f} value={f}>
                  {f}
                </option>
              ))
            : <option value="trading_bot.log">trading_bot.log</option>}
        </select>
        <select
          value={lineCount}
          onChange={(e) => {
            setLineCount(Number(e.target.value))
            fetchLogs(selectedFile, Number(e.target.value))
          }}
          className="input-base text-xs py-1.5 w-24"
        >
          {[50, 100, 200, 500].map((n) => (
            <option key={n} value={n}>
              {n} lines
            </option>
          ))}
        </select>
      </div>

      {/* Log output */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto bg-[#090e18] rounded-lg p-3 min-h-0"
      >
        {loading && !logs ? (
          <div className="flex items-center gap-2 text-gray-500 text-xs p-2">
            <Spinner size="sm" />
            Loading logs...
          </div>
        ) : error ? (
          <p className="text-red-400 text-xs">{error}</p>
        ) : logs?.lines.length === 0 ? (
          <p className="text-gray-600 text-xs italic">No log entries found.</p>
        ) : (
          <div className="space-y-0.5">
            {logs?.lines.map((line, i) => (
              <p
                key={i}
                className={clsx(
                  'text-xs mono leading-5 whitespace-pre-wrap break-all',
                  lineColors[getLogLevel(line)],
                )}
              >
                {line}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}