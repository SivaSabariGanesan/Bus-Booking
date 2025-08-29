"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Input } from "../components/ui/input"
import { Calendar, Clock, MapPin, Bus, AlertCircle, RefreshCw } from "lucide-react"
import type { Booking } from "../types"
import { verifyBookingOtp, resendOtp } from "../services/api"
import { toast } from "sonner"

interface BookingCardProps {
  booking: Booking
  onBookingConfirmed?: () => void
}

const BookingCard: React.FC<BookingCardProps> = ({ booking, onBookingConfirmed }) => {
  const [showOtpInput, setShowOtpInput] = useState(false)
  const [otpInput, setOtpInput] = useState("")
  const [otpLoading, setOtpLoading] = useState(false)
  const [otpError, setOtpError] = useState("")
  const [resendLoading, setResendLoading] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    })
  }

  const formatTime = (timeString: string) => {
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    })
  }

  // Add this helper to get the selected stop for the booking
  const getSelectedStop = () => {
    // If booking has a stop_id or stop_name, use that (add logic if your backend provides it)
    // Otherwise, try to find a stop in the bus stops that is not from_location or to_location
    if (booking.bus.stops && booking.bus.stops.length > 0) {
      // Try to find a stop that is not from_location or to_location
      const intermediate = booking.bus.stops.find(
        s => s.location !== booking.from_location && s.location !== booking.to_location
      )
      return intermediate ? intermediate.location : booking.bus.stops[0].location
    }
    return "-"
  }

  const handleOtpVerification = async () => {
    if (!otpInput || otpInput.length !== 6) return

    setOtpLoading(true)
    setOtpError("")
    
    try {
      const result = await verifyBookingOtp(booking.id, otpInput)
      if (result.success) {
        toast.success("Booking confirmed!")
        setShowOtpInput(false)
        setOtpInput("")
        onBookingConfirmed?.()
      } else {
        setOtpError(result.error || "Invalid OTP")
      }
    } catch (err) {
      setOtpError("Invalid or expired OTP")
    } finally {
      setOtpLoading(false)
    }
  }

  const handleResendOtp = async () => {
    setResendLoading(true)
    setOtpError("")
    
    try {
      const result = await resendOtp(booking.id)
      if (result.success) {
        toast.success("New OTP sent to your email!")
        setShowOtpInput(true)
        setOtpInput("")
      } else {
        setOtpError(result.error || "Failed to resend OTP")
      }
    } catch (err: any) {
      setOtpError(err.message || "Failed to resend OTP")
    } finally {
      setResendLoading(false)
    }
  }

  return (
    <Card className="border-green-200 bg-green-50/50">
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bus className="h-4 w-4 text-green-600" />
            <span className="text-green-800">{booking.bus.bus_no}</span>
          </div>
          <Badge variant="outline" className="border-green-600 text-green-700">
            {booking.status}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm">
            <MapPin className="h-3 w-3 text-muted-foreground" />
            <span className="font-medium">{booking.from_location}</span>
            <span className="text-muted-foreground">→</span>
            <span className="font-medium">{getSelectedStop()}</span>
            <span className="text-muted-foreground">→</span>
            <span className="font-medium">{booking.to_location}</span>
          </div>

          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Calendar className="h-3 w-3 text-muted-foreground" />
              <span>{formatDate(booking.trip_date)}</span>
            </div>
            <div className="flex items-center gap-2">
              <Clock className="h-3 w-3 text-muted-foreground" />
              <span>{formatTime(booking.departure_time)}</span>
            </div>
          </div>

          <div className="text-xs text-muted-foreground">Booked on {formatDate(booking.booking_date)}</div>
        </div>

        {/* OTP Verification Section for Pending Bookings */}
        {booking.status === 'pending' && (
          <div className="border-t pt-4">
            <div className="flex items-center gap-2 mb-3">
              <AlertCircle className="h-4 w-4 text-amber-600" />
              <span className="text-sm font-medium text-amber-800">
                OTP Verification Required
              </span>
            </div>
            
            {!showOtpInput ? (
              <div className="space-y-3">
                <Button 
                  onClick={() => setShowOtpInput(true)}
                  className="w-full bg-amber-600 hover:bg-amber-700"
                >
                  Verify OTP
                </Button>
                <Button 
                  onClick={handleResendOtp}
                  disabled={resendLoading}
                  variant="outline"
                  className="w-full border-amber-600 text-amber-700 hover:bg-amber-50"
                >
                  {resendLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Resend OTP
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="text-sm text-amber-800">
                  Enter the 6-digit OTP sent to your email to confirm your booking.
                </div>
                <Input
                  type="text"
                  value={otpInput}
                  onChange={(e) => setOtpInput(e.target.value)}
                  placeholder="Enter 6-digit OTP"
                  maxLength={6}
                  className="text-center text-lg tracking-widest"
                />
                {otpError && (
                  <p className="text-sm text-red-600">{otpError}</p>
                )}
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowOtpInput(false)
                      setOtpInput("")
                      setOtpError("")
                    }}
                    disabled={otpLoading}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleOtpVerification}
                    disabled={otpLoading || otpInput.length !== 6}
                    className="flex-1 bg-amber-600 hover:bg-amber-700"
                  >
                    {otpLoading ? "Verifying..." : "Verify OTP"}
                  </Button>
                </div>
                <Button 
                  onClick={handleResendOtp}
                  disabled={resendLoading}
                  variant="outline"
                  size="sm"
                  className="w-full border-amber-600 text-amber-700 hover:bg-amber-50"
                >
                  {resendLoading ? (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                      Sending New OTP...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Resend OTP
                    </>
                  )}
                </Button>
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default BookingCard
