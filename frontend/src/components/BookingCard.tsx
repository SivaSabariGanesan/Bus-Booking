"use client"

import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Calendar, Clock, MapPin, Bus } from "lucide-react"
import type { Booking } from "../types"

interface BookingCardProps {
  booking: Booking
}

const BookingCard: React.FC<BookingCardProps> = ({ booking }) => {
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

          <div className="text-xs text-muted-foreground">Booked on {formatDate(booking.created_at)}</div>
        </div>


      </CardContent>
    </Card>
  )
}

export default BookingCard
