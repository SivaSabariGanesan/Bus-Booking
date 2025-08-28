import React, { useEffect, useState } from 'react'
import Navbar from './Navbar'
import { getCurrentBooking, cancelBooking } from '../services/api'
import type { Booking } from '../types'
import BookingCard from './BookingCard'

const MyBooking: React.FC = () => {
  const [booking, setBooking] = useState<Booking | null>(null)
  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(false)

  const load = async () => {
    try {
      setLoading(true)
      const b = await getCurrentBooking()
      setBooking(b)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <div>
      <Navbar />
      <div className="max-w-5xl mx-auto pt-28 px-4">
        <h1 className="text-2xl font-bold mb-4">My Booking</h1>
        {loading ? (
          <div className="text-gray-600">Loading...</div>
        ) : booking ? (
          <BookingCard booking={booking} onCancel={async () => { setActionLoading(true); await cancelBooking(); await load(); setActionLoading(false) }} loading={actionLoading} />
        ) : (
          <div className="bg-white p-6 rounded-xl border shadow-sm text-gray-600">No active booking.</div>
        )}
      </div>
    </div>
  )
}

export default MyBooking
