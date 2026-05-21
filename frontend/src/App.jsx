import { useState } from 'react'
import Navbar from './components/Navbar'
import OrderForm from './components/OrderForm'
import OrderResult from './components/OrderResult'
import OrderHistory from './components/OrderHistory'
import HealthPanel from './components/HealthPanel'
import LogViewer from './components/LogViewer'

export default function App() {
  const [lastResult, setLastResult] = useState(null)
  const [orderHistory, setOrderHistory] = useState([])

  const handleOrderPlaced = (result) => {
    setLastResult(result)
    setOrderHistory((prev) => [...prev, result])
  }

  return (
    <div className="min-h-screen bg-[#0d1117]">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Page header */}
        <div className="mb-6">
          <h1 className="text-xl font-bold text-white">
            Futures Trading Dashboard
          </h1>
          <p className="text-sm text-gray-500 mt-0.5">
            Binance Futures Testnet (USDT-M) — place MARKET, LIMIT and STOP-LIMIT orders
          </p>
        </div>

        {/* Main grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">

          {/* Left column — Order form + result */}
          <div className="lg:col-span-1 space-y-4">
            <OrderForm onOrderPlaced={handleOrderPlaced} />
            {lastResult && <OrderResult result={lastResult} />}
          </div>

          {/* Right columns — Health + History + Logs */}
          <div className="lg:col-span-2 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <HealthPanel />
              <OrderHistory orders={orderHistory} />
            </div>
            <LogViewer />
          </div>

        </div>
      </main>
    </div>
  )
}