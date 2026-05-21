import { Server, RefreshCw, Clock } from 'lucide-react'
import { useHealth } from '../hooks/useHealth'
import Spinner from './Spinner'
import StatusBadge from './StatusBadge'

export default function HealthPanel() {
  const { health, loading, error, refetch } = useHealth()

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-base font-semibold text-white flex items-center gap-2">
          <Server size={16} className="text-yellow-500" />
          System Status
        </h2>
        <button
          onClick={refetch}
          disabled={loading}
          className="text-gray-500 hover:text-gray-300 transition-colors disabled:opacity-50"
          title="Refresh"
        >
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {loading && !health ? (
        <div className="flex items-center gap-2 text-gray-500 text-sm">
          <Spinner size="sm" />
          <span>Checking connectivity...</span>
        </div>
      ) : error ? (
        <div className="text-xs text-red-400">
          <StatusBadge variant="error">Error</StatusBadge>
          <p className="mt-2 text-gray-500">{error}</p>
        </div>
      ) : health ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Binance Testnet</span>
            <StatusBadge
              variant={health.binance_connected ? 'success' : 'error'}
              pulse={health.binance_connected}
            >
              {health.binance_connected ? 'Connected' : 'Offline'}
            </StatusBadge>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">App Version</span>
            <span className="text-xs text-gray-300 mono">{health.version}</span>
          </div>

          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">API Status</span>
            <StatusBadge variant={health.status === 'ok' ? 'success' : 'warning'}>
              {health.status}
            </StatusBadge>
          </div>

          <div className="flex items-start gap-1.5 mt-2 bg-[#1e2433] rounded-lg p-2.5">
            <Clock size={12} className="text-gray-500 mt-0.5 flex-shrink-0" />
            <p className="text-xs text-gray-400">{health.message}</p>
          </div>
        </div>
      ) : null}
    </div>
  )
}