import { Activity, Cpu } from 'lucide-react'
import StatusBadge from './StatusBadge'
import { useHealth } from '../hooks/useHealth'

export default function Navbar() {
  const { health, loading } = useHealth()

  return (
    <nav className="sticky top-0 z-50 bg-[#0d1117]/95 backdrop-blur border-b border-gray-800/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-yellow-500/10 border border-yellow-500/30 flex items-center justify-center">
              <Cpu size={16} className="text-yellow-500" />
            </div>
            <div>
              <span className="font-bold text-white text-sm">FuturesBot</span>
              <span className="ml-2 text-xs text-gray-500 hidden sm:inline">Binance Testnet</span>
            </div>
          </div>

          {/* Status */}
          <div className="flex items-center gap-3">
            {loading ? (
              <StatusBadge variant="neutral">Checking...</StatusBadge>
            ) : health?.binance_connected ? (
              <StatusBadge variant="success" pulse>
                Connected
              </StatusBadge>
            ) : (
              <StatusBadge variant="error">Disconnected</StatusBadge>
            )}
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-gray-500">
              <Activity size={12} />
              <span>Testnet</span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}