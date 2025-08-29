"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Input } from "../components/ui/input"
import { Calendar, Clock, MapPin, Bus, AlertCircle, RefreshCw, CheckCircle, X } from "lucide-react"
import type { Booking } from "../types"
import { verifyBookingOtp, resendOtp, cancelBooking } from "../services/api"
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
  const [cancelLoading, setCancelLoading] = useState(false)

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      weekday: "short",
      month: "short",
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

  const getSelectedStop = () => {
    if (booking.bus.stops && booking.bus.stops.length > 0) {
      const intermediate = booking.bus.stops.find(
        s => s.location !== booking.from_location && s.location !== booking.to_location
      )
      return intermediate ? intermediate.location : booking.bus.stops[0].location
    }
    return "-"
  }

  const getStatusConfig = () => {
    switch (booking.status) {
      case 'confirmed':
        return { color: 'bg-green-50 border-green-200', icon: CheckCircle, textColor: 'text-green-700' }
      case 'pending':
        return { color: 'bg-amber-50 border-amber-200', icon: AlertCircle, textColor: 'text-amber-700' }
      default:
        return { color: 'bg-gray-50 border-gray-200', icon: AlertCircle, textColor: 'text-gray-700' }
    }
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

  const handleCancelBooking = async () => {
    if (!confirm("Are you sure you want to cancel this booking? This action cannot be undone.")) {
      return
    }

    setCancelLoading(true)
    try {
      await cancelBooking()
      toast.success("Booking cancelled successfully!")
      onBookingConfirmed?.() // Refresh the booking list
    } catch (err: any) {
      toast.error(err.message || "Failed to cancel booking")
    } finally {
      setCancelLoading(false)
    }
  }

  const statusConfig = getStatusConfig()
  const StatusIcon = statusConfig.icon

  return (
    <Card className={`border-2 ${statusConfig.color} transition-all duration-200 hover:shadow-md`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-3">
            <div className="flex items-center justify-center w-10 h-10 bg-white rounded-xl shadow-sm">
              <Bus className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <div className="text-lg font-semibold text-gray-900">Bus {booking.bus.bus_no}</div>
              <div className="text-sm text-gray-500">{booking.bus.route_name}</div>
            </div>
          </CardTitle>
          <Badge 
            variant="outline" 
            className={`border-current ${statusConfig.textColor} font-medium`}
          >
            {booking.status}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Journey Route */}
        <div className="bg-white rounded-lg p-3 border border-gray-100">
          <div className="flex items-center gap-2 text-sm text-gray-700 mb-2">
            <MapPin className="h-4 w-4 text-purple-500" />
            <span className="font-medium">Journey Route</span>
          </div>
          <div className="flex items-center gap-2 text-gray-600">
            <span className="font-medium">{booking.from_location}</span>
            <span className="text-purple-400">→</span>
            <span className="font-medium">{getSelectedStop()}</span>
            <span className="text-purple-400">→</span>
            <span className="font-medium">{booking.to_location}</span>
          </div>
        </div>

        {/* Trip Details */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white rounded-lg p-3 border border-gray-100">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Calendar className="h-4 w-4 text-purple-500" />
              <span className="text-xs font-medium">Date</span>
            </div>
            <div className="text-sm font-medium text-gray-900">{formatDate(booking.trip_date)}</div>
          </div>
          <div className="bg-white rounded-lg p-3 border border-gray-100">
            <div className="flex items-center gap-2 text-gray-600 mb-1">
              <Clock className="h-4 w-4 text-purple-500" />
              <span className="text-xs font-medium">Time</span>
            </div>
            <div className="text-sm font-medium text-gray-900">{formatTime(booking.departure_time)}</div>
          </div>
        </div>

        {/* Booking Date */}
        <div className="text-xs text-gray-500 text-center">
          Booked on {formatDate(booking.booking_date)}
        </div>

        {/* OTP Verification Section for Pending Bookings */}
        {booking.status === 'pending' && (
          <div className="border-t border-amber-200 pt-4">
            <div className="flex items-center gap-2 mb-4">
              <StatusIcon className="h-5 w-5 text-amber-600" />
              <span className="text-sm font-medium text-amber-800">
                OTP Verification Required
              </span>
            </div>
            
            {!showOtpInput ? (
              <div className="space-y-3">
                <Button 
                  onClick={() => setShowOtpInput(true)}
                  className="w-full bg-amber-600 hover:bg-amber-700 h-10"
                >
                  Verify OTP
                </Button>
                <Button 
                  onClick={handleResendOtp}
                  disabled={resendLoading}
                  variant="outline"
                  className="w-full border-amber-600 text-amber-700 hover:bg-amber-50 h-10"
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
                {/* Cancel Booking Button - Only for pending bookings */}
                <Button 
                  onClick={handleCancelBooking}
                  disabled={cancelLoading}
                  variant="outline"
                  className="w-full border-red-600 text-red-700 hover:bg-red-50 h-10"
                >
                  {cancelLoading ? (
                    <>
                      <X className="h-4 w-4 mr-2 animate-spin" />
                      Cancelling...
                    </>
                  ) : (
                    <>
                      <X className="h-4 w-4 mr-2" />
                      Cancel Booking
                    </>
                  )}
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="text-sm text-amber-800 bg-amber-50 p-3 rounded-lg border border-amber-200">
                  Enter the 6-digit OTP sent to your email to confirm your booking.
                </div>
                
                <Input
                  type="text"
                  value={otpInput}
                  onChange={(e) => setOtpInput(e.target.value)}
                  placeholder="Enter 6-digit OTP"
                  maxLength={6}
                  className="text-center text-lg tracking-widest border-amber-300 focus:border-amber-500"
                />
                
                {otpError && (
                  <p className="text-sm text-red-600 bg-red-50 p-2 rounded border border-red-200">
                    {otpError}
                  </p>
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
