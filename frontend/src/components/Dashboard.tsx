"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Bus, Search, CheckCircle, XCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Alert, AlertDescription } from "../components/ui/alert"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "../components/ui/dialog"
import type { Bus as BusType, Booking } from "../types"
import { getBuses, createBooking, getCurrentBooking, cancelBooking, verifyBookingOtp } from "../services/api"
import { useAuth } from "../context/AuthContext"
import BusCard from "./BusCard"
import BookingCard from "./BookingCard"
import { toast } from "sonner"
import Navbar from "./Navbar"

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [buses, setBuses] = useState<BusType[]>([])
  const [currentBooking, setCurrentBooking] = useState<Booking | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [bookingLoading, setBookingLoading] = useState(false)
  const [selectedTripDate, setSelectedTripDate] = useState("")
  const [selectedDepartureTime, setSelectedDepartureTime] = useState("")
  const [showOtpModal, setShowOtpModal] = useState(false)
  const [pendingBookingId, setPendingBookingId] = useState<number | null>(null)
  const [otpInput, setOtpInput] = useState("")
  const [otpError, setOtpError] = useState("")
  const [otpLoading, setOtpLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [activeFilter, setActiveFilter] = useState<"all" | "from_rec" | "to_rec">("all")

  useEffect(() => {
    const today = new Date()
    const daysUntilMonday = (1 - today.getDay() + 7) % 7
    const tripDate = new Date(today)
    tripDate.setDate(today.getDate() + daysUntilMonday)
    setSelectedTripDate(tripDate.toISOString().split("T")[0])
    setSelectedDepartureTime("08:00")
  }, [])

  useEffect(() => {
    if (user) {
      loadData()
    }
  }, [user])

  const loadData = async () => {
    try {
      setLoading(true)
      const [busesData, bookingData] = await Promise.all([getBuses(), getCurrentBooking()])
      setBuses(busesData)
      setCurrentBooking(bookingData)
    } catch (err) {
      setError("Failed to load data")
    } finally {
      setLoading(false)
    }
  }

  const handleBookBus = async (busId: number) => {
    if (!user || currentBooking) return

    const bus = buses.find((b) => b.id === busId)
    if (!bus || bus.is_full) return

    setBookingLoading(true)
    try {
      const response = await createBooking(
        busId,
        selectedTripDate,
        selectedDepartureTime,
        bus.from_location || "",
        bus.to_location || "",
      )

      if (response && response.otp_sent && response.pending_booking_id) {
        setPendingBookingId(response.pending_booking_id)
        setShowOtpModal(true)
        toast.success("OTP sent to your email")
      } else {
        setCurrentBooking(response)
        toast.success("Booking confirmed!")
        loadData()
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Failed to book bus"
      toast.error(errorMsg)
      setError(errorMsg)
    } finally {
      setBookingLoading(false)
    }
  }

  const handleCancelBooking = async () => {
    try {
      setBookingLoading(true)
      await cancelBooking()
      setCurrentBooking(null)
      await loadData()
      toast.success("Booking cancelled")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cancellation failed")
    } finally {
      setBookingLoading(false)
    }
  }

  const handleOtpVerification = async () => {
    if (!pendingBookingId) return

    setOtpLoading(true)
    setOtpError("")
    try {
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
  }

  const filteredBuses = buses.filter((bus) => {
    const query = searchQuery.trim().toLowerCase()
    const matchesQuery =
      !query ||
      bus.bus_no.toLowerCase().includes(query) ||
      bus.route_name.toLowerCase().includes(query) ||
      (bus.from_location || "").toLowerCase().includes(query) ||
      (bus.to_location || "").toLowerCase().includes(query)

    const matchesFilter =
      activeFilter === "all"
        ? true
        : activeFilter === "from_rec"
          ? (bus.from_location || "").toLowerCase().includes("rec")
          : activeFilter === "to_rec"
            ? (bus.to_location || "").toLowerCase().includes("rec")
            : true

    return matchesQuery && matchesFilter
  })

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Please login to continue</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <div className="container mx-auto px-4 pt-24 pb-8 space-y-6">
        <Card>
          <CardContent className="p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search buses and routes"
                className="pl-10"
              />
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-2">
          {[
            { key: "all", label: "All Buses" },
            { key: "from_rec", label: "From REC" },
            { key: "to_rec", label: "To REC" },
          ].map(({ key, label }) => (
            <Button
              key={key}
              variant={activeFilter === key ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveFilter(key as any)}
            >
              {label}
            </Button>
          ))}
        </div>

        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {currentBooking && (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600" />
                Current Booking
              </CardTitle>
            </CardHeader>
            <CardContent>
              <BookingCard booking={currentBooking} onCancel={handleCancelBooking} loading={bookingLoading} />
            </CardContent>
          </Card>
        )}

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Bus className="h-5 w-5" />
              Available Buses
            </CardTitle>
          </CardHeader>
          <CardContent>
            {filteredBuses.length === 0 ? (
              <p className="text-center text-muted-foreground py-8">No buses match your search criteria</p>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredBuses.map((bus) => (
                  <BusCard
                    key={bus.id}
                    bus={bus}
                    onBook={() => handleBookBus(bus.id)}
                    loading={bookingLoading}
                    isBooked={!!(currentBooking && currentBooking.bus && currentBooking.bus.id === bus.id)}
                  />
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {currentBooking && (
          <Card>
            <CardContent className="text-center py-8">
              <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">Booking Active</h3>
              <p className="text-muted-foreground">
                You have an active booking. You can only have one booking at a time.
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      <Dialog open={showOtpModal} onOpenChange={setShowOtpModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Enter OTP</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <p className="text-sm text-muted-foreground">
              An OTP has been sent to your email. Please enter it below to confirm your booking.
            </p>
            <Input
              type="text"
              value={otpInput}
              onChange={(e) => setOtpInput(e.target.value)}
              placeholder="Enter 6-digit OTP"
              maxLength={6}
            />
            {otpError && <p className="text-sm text-destructive">{otpError}</p>}
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowOtpModal(false)
                  setOtpInput("")
                  setOtpError("")
                }}
                disabled={otpLoading}
              >
                Cancel
              </Button>
              <Button onClick={handleOtpVerification} disabled={otpLoading || otpInput.length !== 6}>
                {otpLoading ? "Verifying..." : "Verify"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default Dashboard
