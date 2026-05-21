import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { toast } from 'react-hot-toast'
import { Send, AlertCircle } from 'lucide-react'
import { clsx } from 'clsx'
import { placeOrder } from '../services/api'
import Spinner from './Spinner'

const ORDER_TYPES = ['MARKET', 'LIMIT', 'STOP_LIMIT']
const SIDES = ['BUY', 'SELL']
const TIF_OPTIONS = ['GTC', 'IOC', 'FOK', 'GTX']

const POPULAR_SYMBOLS = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT']

export default function OrderForm({ onOrderPlaced }) {
  const [loading, setLoading] = useState(false)
  const [selectedSide, setSelectedSide] = useState('BUY')
  const [selectedType, setSelectedType] = useState('MARKET')

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors },
  } = useForm({
    defaultValues: {
      symbol: 'BTCUSDT',
      side: 'BUY',
      type: 'MARKET',
      quantity: '',
      price: '',
      stop_price: '',
      time_in_force: 'GTC',
      reduce_only: false,
    },
  })

  const needsPrice = selectedType === 'LIMIT' || selectedType === 'STOP_LIMIT'
  const needsStopPrice = selectedType === 'STOP_LIMIT'

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      const payload = {
        symbol: data.symbol.toUpperCase(),
        side: selectedSide,
        type: selectedType,
        quantity: data.quantity,
        time_in_force: data.time_in_force,
        reduce_only: data.reduce_only,
      }

      if (needsPrice) payload.price = data.price
      if (needsStopPrice) payload.stop_price = data.stop_price

      const result = await placeOrder(payload)

      if (result.success) {
        toast.success(result.message || 'Order placed successfully!')
        onOrderPlaced?.(result)
        reset()
        setSelectedSide('BUY')
        setSelectedType('MARKET')
      } else {
        toast.error(result.error || 'Order failed')
      }
    } catch (err) {
      toast.error(err.userMessage || 'Request failed. Check your API credentials.')
    } finally {
      setLoading(false)
    }
  }

  const FieldError = ({ name }) =>
    errors[name] ? (
      <p className="mt-1 text-xs text-red-400 flex items-center gap-1">
        <AlertCircle size={10} />
        {errors[name].message}
      </p>
    ) : null

  return (
    <div className="card animate-fade-in">
      <h2 className="text-base font-semibold text-white mb-5 flex items-center gap-2">
        <Send size={16} className="text-yellow-500" />
        Place Order
      </h2>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* BUY / SELL toggle */}
        <div className="grid grid-cols-2 gap-2">
          {SIDES.map((side) => (
            <button
              key={side}
              type="button"
              onClick={() => {
                setSelectedSide(side)
                setValue('side', side)
              }}
              className={clsx(
                'py-2.5 rounded-lg text-sm font-bold transition-all duration-150',
                selectedSide === side && side === 'BUY'
                  ? 'bg-[#0ecb81] text-black shadow-lg shadow-green-500/20'
                  : selectedSide === side && side === 'SELL'
                    ? 'bg-[#f6465d] text-white shadow-lg shadow-red-500/20'
                    : 'bg-[#1e2433] text-gray-400 hover:bg-[#252d40] border border-gray-700',
              )}
            >
              {side}
            </button>
          ))}
        </div>

        {/* Symbol */}
        <div>
          <label className="label">Symbol</label>
          <input
            {...register('symbol', {
              required: 'Symbol is required',
              pattern: { value: /^[A-Za-z0-9]{2,20}$/, message: 'Invalid symbol (e.g. BTCUSDT)' },
            })}
            className={clsx('input-base', errors.symbol && 'input-error')}
            placeholder="BTCUSDT"
            style={{ textTransform: 'uppercase' }}
          />
          <div className="mt-1.5 flex flex-wrap gap-1">
            {POPULAR_SYMBOLS.map((sym) => (
              <button
                key={sym}
                type="button"
                onClick={() => setValue('symbol', sym)}
                className="text-xs px-2 py-0.5 rounded bg-[#1e2433] text-gray-400 hover:text-yellow-400 hover:bg-yellow-500/10 border border-gray-700 transition-colors"
              >
                {sym}
              </button>
            ))}
          </div>
          <FieldError name="symbol" />
        </div>

        {/* Order Type */}
        <div>
          <label className="label">Order Type</label>
          <div className="grid grid-cols-3 gap-1.5">
            {ORDER_TYPES.map((type) => (
              <button
                key={type}
                type="button"
                onClick={() => {
                  setSelectedType(type)
                  setValue('type', type)
                }}
                className={clsx(
                  'py-2 rounded-lg text-xs font-medium transition-all duration-150 border',
                  selectedType === type
                    ? 'bg-yellow-500/10 border-yellow-500/40 text-yellow-400'
                    : 'bg-[#1e2433] border-gray-700 text-gray-400 hover:border-gray-600',
                )}
              >
                {type.replace('_', '-')}
              </button>
            ))}
          </div>
        </div>

        {/* Quantity */}
        <div>
          <label className="label">Quantity</label>
          <input
            {...register('quantity', {
              required: 'Quantity is required',
              validate: (v) => parseFloat(v) > 0 || 'Must be greater than 0',
            })}
            type="number"
            step="any"
            min="0"
            className={clsx('input-base mono', errors.quantity && 'input-error')}
            placeholder="0.01"
          />
          <FieldError name="quantity" />
        </div>

        {/* Price (LIMIT / STOP_LIMIT) */}
        {needsPrice && (
          <div>
            <label className="label">
              Price{' '}
              <span className="text-yellow-500 normal-case tracking-normal font-normal">
                (Limit Price)
              </span>
            </label>
            <input
              {...register('price', {
                required: needsPrice ? 'Price is required for this order type' : false,
                validate: (v) => !needsPrice || parseFloat(v) > 0 || 'Must be greater than 0',
              })}
              type="number"
              step="any"
              min="0"
              className={clsx('input-base mono', errors.price && 'input-error')}
              placeholder="65000.00"
            />
            <FieldError name="price" />
          </div>
        )}

        {/* Stop Price (STOP_LIMIT) */}
        {needsStopPrice && (
          <div>
            <label className="label">
              Stop Price{' '}
              <span className="text-orange-400 normal-case tracking-normal font-normal">
                (Trigger Price)
              </span>
            </label>
            <input
              {...register('stop_price', {
                required: needsStopPrice ? 'Stop price is required for STOP_LIMIT' : false,
                validate: (v) => !needsStopPrice || parseFloat(v) > 0 || 'Must be greater than 0',
              })}
              type="number"
              step="any"
              min="0"
              className={clsx('input-base mono', errors.stop_price && 'input-error')}
              placeholder="64500.00"
            />
            <FieldError name="stop_price" />
          </div>
        )}

        {/* Time In Force */}
        <div>
          <label className="label">Time In Force</label>
          <select {...register('time_in_force')} className="input-base">
            {TIF_OPTIONS.map((t) => (
              <option key={t} value={t}>
                {t} —{' '}
                {t === 'GTC'
                  ? 'Good Till Cancel'
                  : t === 'IOC'
                    ? 'Immediate or Cancel'
                    : t === 'FOK'
                      ? 'Fill or Kill'
                      : 'Post Only'}
              </option>
            ))}
          </select>
        </div>

        {/* Reduce Only */}
        <div className="flex items-center gap-2.5">
          <input
            {...register('reduce_only')}
            type="checkbox"
            id="reduce_only"
            className="w-4 h-4 rounded border-gray-600 bg-[#1e2433] text-yellow-500 focus:ring-yellow-500/40"
          />
          <label htmlFor="reduce_only" className="text-xs text-gray-400 cursor-pointer">
            Reduce Only (close existing position only)
          </label>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className={clsx(
            'w-full py-3 rounded-lg font-bold text-sm transition-all duration-150 flex items-center justify-center gap-2',
            selectedSide === 'BUY'
              ? 'bg-[#0ecb81] hover:bg-[#12e090] text-black disabled:opacity-50 disabled:cursor-not-allowed'
              : 'bg-[#f6465d] hover:bg-[#ff5a72] text-white disabled:opacity-50 disabled:cursor-not-allowed',
          )}
        >
          {loading ? (
            <>
              <Spinner size="sm" />
              Placing Order...
            </>
          ) : (
            <>
              <Send size={14} />
              {selectedSide} {selectedType.replace('_', '-')}
            </>
          )}
        </button>
      </form>
    </div>
  )
}