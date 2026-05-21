import { History, TrendingUp, TrendingDown } from 'lucide-react'
import { clsx } from 'clsx'
import { formatQty, formatPrice, getSideColor, getStatusColor } from '../utils/formatters'

export default function OrderHistory({ orders = [] }) {
  if (orders.length === 0) {
    return (
      <div className="card">
        <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
          <History size={16} className="text-yellow-500" />
          Recent Orders
        </h2>
        <div className="flex flex-col items-center justify-center py-8 text-center">
          <History size={32} className="text-gray-700 mb-2" />
          <p className="text-sm text-gray-600">No orders placed yet</p>
          <p className="text-xs text-gray-700 mt-1">Your orders will appear here</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h2 className="text-base font-semibold text-white mb-4 flex items-center gap-2">
        <History size={16} className="text-yellow-500" />
        Recent Orders
        <span className="ml-auto text-xs text-gray-500 font-normal">{orders.length} this session</span>
      </h2>

      <div className="space-y-2 max-h-72 overflow-y-auto">
        {[...orders].reverse().map((result, i) => {
          const order = result.order
          const summary = result.request_summary
          return (
            <div
              key={i}
              className={clsx(
                'rounded-lg p-3 border text-xs',
                result.success
                  ? 'bg-green-500/5 border-green-500/10'
                  : 'bg-red-500/5 border-red-500/10',
              )}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  {summary?.side === 'BUY' ? (
                    <TrendingUp size={12} className="text-green-400" />
                  ) : (
                    <TrendingDown size={12} className="text-red-400" />
                  )}
                  <span className="font-semibold text-white">{summary?.symbol}</span>
                  <span className={clsx('font-medium', getSideColor(summary?.side))}>
                    {summary?.side}
                  </span>
                  <span className="text-gray-500">{summary?.type}</span>
                </div>

                {order ? (
                  <span className={clsx('font-medium', getStatusColor(order.status))}>
                    {order.status}
                  </span>
                ) : (
                  <span className="text-red-400">FAILED</span>
                )}
              </div>

              <div className="flex items-center justify-between text-gray-500">
                <span>
                  Qty: <span className="text-gray-300 mono">{formatQty(summary?.quantity, 6)}</span>
                </span>
                {order?.avgPrice && order.avgPrice !== '0' && (
                  <span>
                    Avg:{' '}
                    <span className="text-gray-300 mono">${formatPrice(order.avgPrice)}</span>
                  </span>
                )}
                {order?.orderId && (
                  <span className="text-gray-600 mono">#{order.orderId}</span>
                )}
              </div>

              {!result.success && result.error && (
                <p className="mt-1 text-red-400 text-xs truncate">{result.error}</p>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}