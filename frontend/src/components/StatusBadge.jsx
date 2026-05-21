import { clsx } from 'clsx'

const variants = {
  success: 'bg-green-500/10 text-green-400 border-green-500/20',
  error: 'bg-red-500/10 text-red-400 border-red-500/20',
  warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  neutral: 'bg-gray-500/10 text-gray-400 border-gray-500/20',
}

const dots = {
  success: 'bg-green-400',
  error: 'bg-red-400',
  warning: 'bg-yellow-400',
  info: 'bg-blue-400',
  neutral: 'bg-gray-400',
}

export default function StatusBadge({ variant = 'neutral', children, pulse = false }) {
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border',
        variants[variant],
      )}
    >
      <span
        className={clsx(
          'w-1.5 h-1.5 rounded-full',
          dots[variant],
          pulse && variant === 'success' && 'animate-pulse',
        )}
      />
      {children}
    </span>
  )
}