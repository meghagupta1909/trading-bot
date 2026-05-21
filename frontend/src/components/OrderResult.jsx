import { CheckCircle, XCircle, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react'
import { useState } from 'react'
import { clsx } from 'clsx'
import { formatQty, formatPrice, formatTimestamp, getSideColor, getStatusColor } from '../utils/formatters'

const Row = ({ label, value, className }) =>
  value && value !== '—' ? (
    <div className="flex justify-between items-center py-1.5 border-b border-gray-800/50 last:border-0">
      <span className="text-xs text-gray-500">{label}</span>
      <span className={clsx('text-xs font-medium mono', className || 'text-white')}>{value}</span>
    </div>
  ) : null

export default function OrderResult({ result }) {
  const [expanded, setExpanded] = useState(true)
  if (!result) return null

  const { success, message, request_summary, order, error } = result

  return (
    <div
      className={clsx(
        'rounded-xl border p-4 animate-slide-up',
        success
          ? 'bg-green-500/5 border-green-500/20'
          : 'bg-red-500/5 border-red-500/20',
      )}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          {success ? (
            <CheckCircle size={18} className="text-green-400 flex-shrink-0" />
          ) : (
            <XCircle size={18} className="text-red-400 flex-shrink-0" />
          )}
          <div>
            <p className={clsx('text-sm font-semibold', success ? 'text-green-400' : 'text-red-400')}>
              {success ? 'Order Placed' : 'Order Failed'}
            </p>
            <p className="text-xs text-gray-400 mt-0.5">{message}</p>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-gray-500 hover:text-gray-300 transition-colors"
        >
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </button>
      </div>

      {expanded && (
        <div className="space-y-3 mt-3">
          {/* Request Summary */}
          {request_summary && (
            <div className="bg-[#161c2c] rounded-lg p-3">
              <p className="text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Request Summary
              </p>
              <div>
                <Row label="Symbol" value={request_summary.symbol} />
                <Row
                  label="Side"
                  value={request_summary.side}
                  className={getSideColor(request_summary.side)}
                />
                <Row label="Type" value={request_summary.type} />
                <Row label="Quantity" value={request_summary.quantity} />
                {request_summary.price !== 'N/A' && (
                  <Row label="Price" value={request_summary.price} />
                )}
                {request_summary.stop_price !== 'N/A' && (
                  <Row label="Stop Price" value={request_summary.stop_price} />
                )}
              </div>
            </div>
          )}

          {/* Order Details */}
          {order && (
            <div className="bg-[#161c2c] rounded-lg p-3">
              <p className="text-xs font-medium text-gray-400 mb-2 uppercase tracking-wide">
                Order Response
              </p>
              <Row label="Order ID" value={order.orderId?.toString()} />
              <Row label="Client Order ID" value={order.clientOrderId} />
              <Row
                label="Status"
                value={order.status}
                className={getStatusColor(order.status)}
              />
              <Row label="Executed Qty" value={formatQty(order.executedQty)} />
              <Row label="Avg Price" value={formatPrice(order.avgPrice)} />
              {order.price && order.price !== '0' && (
                <Row label="Limit Price" value={formatPrice(order.price)} />
              )}
              {order.stopPrice && order.stopPrice !== '0' && (
                <Row label="Stop Price" value={formatPrice(order.stopPrice)} />
              )}
              <Row label="Updated At" value={formatTimestamp(order.updateTime)} />
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="bg-red-500/5 border border-red-500/20 rounded-lg p-3">
              <p className="text-xs font-medium text-red-400 mb-1">Error Details</p>
              <p className="text-xs text-gray-300 mono">{error}</p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}