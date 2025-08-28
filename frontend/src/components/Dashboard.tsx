"use client"

import React, { useState, useEffect } from "react"
import { LogOut, Bus, CheckCircle, XCircle } from "lucide-react"
import type { Bus as BusType, Booking } from "../types"
import { logout, getBuses, createBooking, getCurrentBooking, cancelBooking, testBookingData, debugRequest, verifyBookingOtp } from '../services/api'
import { useAuth } from "../context/AuthContext"
import BusCard from "./BusCard"
import BookingCard from "./BookingCard"
import { toast } from "sonner"

const Dashboard: React.FC = () => {
  const { user, logout: authLogout } = useAuth()
  const [buses, setBuses] = useState<BusType[]>([])
  const [currentBooking, setCurrentBooking] = useState<Booking | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [bookingLoading, setBookingLoading] = useState(false)
  const [selectedBus, setSelectedBus] = useState<BusType | null>(null)
  const [selectedTripDate, setSelectedTripDate] = useState("")
  const [selectedDepartureTime, setSelectedDepartureTime] = useState("")
  const [showOtpModal, setShowOtpModal] = useState(false)
  const [pendingBookingId, setPendingBookingId] = useState<number | null>(null)
  const [otpInput, setOtpInput] = useState("")
  const [otpError, setOtpError] = useState("")
  const [otpLoading, setOtpLoading] = useState(false)

  // Calculate default trip date (next Monday) and set default departure time
  useEffect(() => {
    const today = new Date()
    const daysUntilMonday = (1 - today.getDay() + 7) % 7
    const tripDate = new Date(today)
    tripDate.setDate(today.getDate() + daysUntilMonday)
    setSelectedTripDate(tripDate.toISOString().split('T')[0])
    setSelectedDepartureTime("08:00")
  }, [])

  // Load data on component mount
  useEffect(() => {
    console.log("Dashboard useEffect - user:", user)
    if (user) {
      console.log("User is authenticated, loading data...")
      loadData()
    } else {
      console.log("No user, skipping data load")
    }
  }, [user])

  const loadData = async () => {
    try {
      console.log("Starting to load data...")
      console.log("Current user:", user)
      console.log("User ID:", user?.id)

      if (!user || !user.id) {
        console.error("No user or user ID available")
        setError("User not properly authenticated")
        return
      }

      setLoading(true)
      const [busesData, bookingData] = await Promise.all([getBuses(), getCurrentBooking()])
      console.log("Data loaded successfully:", { buses: busesData, booking: bookingData })
      setBuses(busesData)
      setCurrentBooking(bookingData)
    } catch (err) {
      console.error("Failed to load data:", err)
      setError("Failed to load data")
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      await logout()
      authLogout()
    } catch (err) {
      console.error("Logout failed:", err)
      authLogout()
    }
  }

  const handleBookBus = async (busId: number) => {
    if (!user) return

    // Check if user already has a current booking
    if (currentBooking) {
      setError("You already have an active booking. Please cancel it first.")
      return
    }

    // Find the selected bus
    const bus = buses.find((b) => b.id === busId)
    if (!bus) {
      setError("Bus not found")
      return
    }

    // Check if bus is full
    if (bus.is_full) {
      setError("This bus is full. Please select another bus.")
      return
    }

    // Check if trip date and departure time are selected
    if (!selectedTripDate) {
      setError("Please select a trip date first.")
      return
    }

    if (!selectedDepartureTime) {
      setError("Please select a departure time first.")
      return
    }

    // Use the selected trip date and departure time
    const tripDateStr = selectedTripDate
    const departureTime = selectedDepartureTime

    setBookingLoading(true)
    try {
      console.log("Creating booking with data:", {
        busId,
        tripDate: tripDateStr,
        departureTime,
        fromLocation: bus.from_location || "",
        toLocation: bus.to_location || "",
      })
      
      console.log("Selected trip date:", selectedTripDate)
      console.log("Selected departure time:", selectedDepartureTime)
      console.log("Bus details:", bus)

      // Test the data first
      console.log("Testing data with test endpoint...")
      const testResult = await testBookingData(
        busId,
        tripDateStr,
        departureTime,
        bus.from_location || "",
        bus.to_location || "",
      )
      console.log("Test result:", testResult)

      // Debug the raw request format
      console.log("Debugging raw request format...")
      try {
        const debugResult = await debugRequest({
          bus_id: busId,
          trip_date: tripDateStr,
          departure_time: departureTime,
          from_location: bus.from_location || "",
          to_location: bus.to_location || "",
        })
        console.log("Debug result:", debugResult)
      } catch (error) {
        console.log("Debug endpoint failed, continuing with booking...")
      }

      try {
        const response = await createBooking(
          busId,
          tripDateStr,
          departureTime,
          bus.from_location || "",
          bus.to_location || "",
        )
        if (response && response.otp_sent && response.pending_booking_id) {
          setPendingBookingId(response.pending_booking_id)
          setShowOtpModal(true)
          toast.success("OTP sent to your email. Please verify to confirm booking.")
        } else {
          // fallback for old flow
          setCurrentBooking(response)
          toast.success("Booking confirmed! Check your email for details.")
          setSelectedBus(null)
          loadData()
        }
      } catch (error) {
        let errorMsg = error instanceof Error ? error.message : String(error)
        // Extract the actual message if it's wrapped in a list/object
        const match = errorMsg.match(/'You already have an active booking'/)
        if (match) {
          errorMsg = "You already have an active booking"
        }
        if (errorMsg.includes("already have an active booking")) {
          toast.error("You already have an active booking.")
        } else {
          toast.error(errorMsg || "Failed to book bus")
        }
        setError(errorMsg)
      } finally {
        setBookingLoading(false)
      }
    } catch (error) {
      console.error("Failed to book bus:", error)
      setError(error instanceof Error ? error.message : "Failed to book bus")
    } finally {
      setBookingLoading(false)
    }
  }

  const handleBusSelect = (bus: BusType) => {
    setSelectedBus(bus)
  }

  const handleCancelBooking = async () => {
    try {
      setBookingLoading(true)
      await cancelBooking()
      setCurrentBooking(null)
      await loadData() // Refresh data to update available seats
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancellation failed")
    } finally {
      setBookingLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-white">
        <div className="text-center">
          <p className="text-gray-600">User not found. Please login again.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-white">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="bg-gradient-to-r from-purple-600 to-purple-700 p-3 rounded-xl mr-4 shadow-lg">
                <Bus className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">College Transport</h1>
                <p className="text-sm text-purple-600 font-medium">Welcome, {user.first_name}!</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center px-6 py-3 text-sm font-medium text-gray-700 hover:text-purple-700 hover:bg-purple-50 rounded-xl transition duration-200 ease-in-out border border-gray-200 hover:border-purple-200"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* User Info */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8 border border-purple-100">
          <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <div className="w-2 h-6 bg-gradient-to-b from-purple-600 to-purple-700 rounded-full mr-3"></div>
            Student Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-purple-50 p-4 rounded-xl">
              <p className="text-sm font-semibold text-purple-700 mb-1">Name</p>
              <p className="text-gray-900 font-medium">
                {user.first_name} {user.last_name}
              </p>
            </div>
            <div className="bg-purple-50 p-4 rounded-xl">
              <p className="text-sm font-semibold text-purple-700 mb-1">Roll No</p>
              <p className="text-gray-900 font-medium">{user.roll_no}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-xl">
              <p className="text-sm font-semibold text-purple-700 mb-1">Department</p>
              <p className="text-gray-900 font-medium">
                {user.dept} - Year {user.year}
              </p>
            </div>
          </div>
        </div>

        {/* Current Booking */}
        {currentBooking && (
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
              <CheckCircle className="h-6 w-6 mr-3 text-green-600" />
              Current Booking
            </h2>
            <BookingCard booking={currentBooking} onCancel={handleCancelBooking} loading={bookingLoading} />
          </div>
        )}

        {/* Available Buses Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 border border-purple-100">
          <div className="flex items-center mb-8">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-purple-700 rounded-xl flex items-center justify-center mr-4 shadow-lg">
              <Bus className="h-6 w-6 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Available Buses</h2>
              <p className="text-purple-600 text-sm font-medium">Choose your preferred bus for today</p>
            </div>
          </div>

          {/* Bus Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {buses.map((bus) => (
              <BusCard
                key={bus.id}
                bus={bus}
                onBook={() => handleBookBus(bus.id)}
                onSelect={() => handleBusSelect(bus)}
                loading={bookingLoading}
                selected={selectedBus?.id === bus.id}
                isBooked={!!(currentBooking && currentBooking.bus && currentBooking.bus.id === bus.id)}
              />  
            ))}
          </div>
        </div>

        {currentBooking && (
          <div className="text-center py-8">
            <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-2xl p-8 max-w-md mx-auto border border-purple-200 shadow-lg">
              <CheckCircle className="h-16 w-16 text-purple-600 mx-auto mb-4" />
              <h3 className="text-xl font-bold text-gray-900 mb-3">Booking Active</h3>
              <p className="text-gray-700 leading-relaxed">
                You have an active booking. You can only have one booking at a time.
              </p>
            </div>
          </div>
        )}
      </div>
      {showOtpModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-40 z-50">
          <div className="bg-white rounded-xl shadow-lg p-8 max-w-sm w-full">
            <h2 className="text-xl font-bold mb-4">Enter OTP</h2>
            <p className="mb-2 text-gray-600">An OTP has been sent to your email. Please enter it below to confirm your booking.</p>
            <input
              type="text"
              value={otpInput}
              onChange={e => setOtpInput(e.target.value)}
              className="w-full border border-gray-300 rounded-md px-4 py-2 mb-3 focus:outline-none focus:ring-2 focus:ring-purple-400"
              placeholder="Enter OTP"
              maxLength={6}
            />
            {otpError && <div className="text-red-600 mb-2">{otpError}</div>}
            <div className="flex justify-end space-x-2">
              <button
                className="px-4 py-2 rounded-md bg-gray-200 text-gray-700"
                onClick={() => { setShowOtpModal(false); setOtpInput(""); setOtpError(""); }}
                disabled={otpLoading}
              >Cancel</button>
              <button
                className="px-4 py-2 rounded-md bg-purple-600 text-white font-semibold"
                onClick={async () => {
                  setOtpLoading(true)
                  setOtpError("")
                  try {
                    if (!pendingBookingId) return
                    const result = await verifyBookingOtp(pendingBookingId, otpInput)
                    if (result.success) {
                      toast.success("Booking confirmed!")
                      setShowOtpModal(false)
                      setOtpInput("")
                      setPendingBookingId(null)
                      loadData()
                    } else {
                      setOtpError(result.error || "Invalid OTP")
                    }
                  } catch (err) {
                    setOtpError("Invalid or expired OTP")
                  } finally {
                    setOtpLoading(false)
                  }
                }}
                disabled={otpLoading || otpInput.length !== 6}
              >{otpLoading ? "Verifying..." : "Verify"}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
