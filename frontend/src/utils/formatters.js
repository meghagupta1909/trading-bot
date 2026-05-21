/**
 * Format a unix millisecond timestamp to a readable local time string.
 */
export const formatTimestamp = (ms) => {
  if (!ms) return '—'
  return new Date(ms).toLocaleString()
}

/**
 * Format a decimal number with up to N significant decimal places.
 */
export const formatQty = (val, decimals = 8) => {
  if (!val && val !== 0) return '—'
  return parseFloat(parseFloat(val).toFixed(decimals)).toString()
}

/**
 * Format a price value with 2 decimal places.
 */
export const formatPrice = (val) => {
  if (!val || val === '0' || val === '0.00') return '—'
  return parseFloat(val).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 8,
  })
}

/**
 * Get colour class for an order side.
 */
export const getSideColor = (side) => {
  if (!side) return 'text-gray-400'
  return side.toUpperCase() === 'BUY' ? 'text-green-400' : 'text-red-400'
}

/**
 * Get colour class for an order status.
 */
export const getStatusColor = (status) => {
  switch (status?.toUpperCase()) {
    case 'FILLED':
      return 'text-green-400'
    case 'NEW':
    case 'PARTIALLY_FILLED':
      return 'text-yellow-400'
    case 'CANCELED':
    case 'REJECTED':
    case 'EXPIRED':
      return 'text-red-400'
    default:
      return 'text-gray-400'
  }
}

/**
 * Classify a log line into a severity level.
 */
export const getLogLevel = (line) => {
  if (line.includes('| ERROR') || line.includes('| CRITICAL')) return 'error'
  if (line.includes('| WARNING')) return 'warning'
  if (line.includes('| INFO')) return 'info'
  if (line.includes('| DEBUG')) return 'debug'
  return 'default'
}