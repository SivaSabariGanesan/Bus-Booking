"use client"

import type React from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Bus, MapPin, Users } from "lucide-react"
import type { Bus as BusType } from "../types"

interface BusCardProps {
  bus: BusType
  onBook: () => void
  loading: boolean
  isBooked: boolean
}

const BusCard: React.FC<BusCardProps> = ({ bus, onBook, loading, isBooked }) => {
  const availabilityColor = bus.is_full ? "destructive" : bus.available_seats < 10 ? "secondary" : "default"
  const availabilityText = bus.is_full ? "Full" : `${bus.available_seats} seats`

  return (
    <Card className={`transition-all hover:shadow-md ${isBooked ? "ring-2 ring-primary" : ""}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center justify-between text-lg">
          <div className="flex items-center gap-2">
            <Bus className="h-4 w-4" />
            {bus.bus_no}
          </div>
          <Badge variant={availabilityColor} className="text-xs">
            {availabilityText}
          </Badge>
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <h3 className="font-medium text-sm">{bus.route_name}</h3>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-3 w-3" />
            <span className="truncate">{bus.from_location}</span>
            <span>→</span>
            <span className="truncate">{bus.to_location}</span>
          </div>

          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Users className="h-3 w-3" />
            <span>
              {bus.available_seats}/{bus.total_seats} available
            </span>
          </div>
        </div>

        <Button onClick={onBook} disabled={loading || bus.is_full || isBooked} className="w-full" size="sm">
          {loading ? "Booking..." : isBooked ? "Booked" : bus.is_full ? "Full" : "Book Now"}
        </Button>
      </CardContent>
    </Card>
  )
}

export default BusCard
