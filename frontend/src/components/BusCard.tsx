"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Bus, MapPin, Clock } from "lucide-react"
import type { Bus as BusType, Stop } from "../types"

interface BusCardProps {
  bus: BusType
  onBook: (pickupStopId: number) => void
  loading: boolean
  isBooked: boolean
  activeFilter?: "from_rec" | "to_rec"
  hasConfirmedBooking?: boolean
}

const BusCard: React.FC<BusCardProps> = ({ bus, onBook, loading, isBooked, activeFilter, hasConfirmedBooking }) => {
  const [selectedStopId, setSelectedStopId] = useState<number | null>(null)
  const [showStopSelection, setShowStopSelection] = useState(false)

  const handleBookClick = () => {
    console.log("Book clicked for bus:", bus.bus_no, "Filter:", activeFilter, "Stops:", bus.stops)
    setShowStopSelection(true)
    
    const stops: Stop[] = Array.isArray(bus.stops) ? bus.stops : []
    if (stops.length > 0) {
      console.log("Available stops:", stops.map(s => ({
        id: s.id,
        name: s.display_name,
        location: s.location,
        is_pickup: s.is_pickup,
        is_dropoff: s.is_dropoff
      })))
      console.log("ℹ️ No auto-selection - user will manually select pickup and dropoff stops")
    }
  }

  const handleStopSelect = (stopId: string) => {
    const stopIdNum = parseInt(stopId)
    const stops: Stop[] = Array.isArray(bus.stops) ? bus.stops : []
    const selectedStop = stops.find(s => s.id === stopIdNum)
    console.log("Stop selected:", {
      stopId,
      stopIdNum,
      stopName: selectedStop?.display_name,
      stopLocation: selectedStop?.location
    })
    setSelectedStopId(stopIdNum)
  }

  const stopsArr: Stop[] = Array.isArray(bus.stops) ? bus.stops : []
  const activeStops = stopsArr.filter(stop => stop.is_active)
  
  const pickupStops = activeStops.filter(stop => stop.is_pickup)
  const dropoffStops = activeStops.filter(stop => stop.is_dropoff)

  const getStatusColor = () => {
    if (isBooked) return "ring-2 ring-purple-500 bg-purple-50/30"
    if (bus.is_full) return "ring-2 ring-red-200 bg-red-50/30"
    if (!bus.is_booking_open) return "ring-2 ring-gray-200 bg-gray-50/30"
    return "ring-1 ring-gray-200 hover:ring-2 hover:ring-purple-300 hover:shadow-lg"
  }

  const getButtonText = () => {
    if (loading) return "Booking..."
    if (isBooked) return "Booked"
    if (bus.is_full) return "Full"
    if (!bus.is_booking_open) return "Closed"
    if (hasConfirmedBooking) return "Unavailable"
    return "Book Now"
  }

  const getButtonVariant = () => {
    if (isBooked) return "outline"
    if (bus.is_full || !bus.is_booking_open) return "secondary"
    return "default"
  }

  return (
    <Card className={`transition-all duration-200 ${getStatusColor()}`}>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2 text-lg font-semibold">
            <div className="flex items-center justify-center w-8 h-8 bg-purple-100 rounded-lg">
              <Bus className="h-4 w-4 text-purple-600" />
            </div>
            <span className="text-gray-900">{bus.route_name}</span>
          </CardTitle>
          <div className="flex items-center gap-2">
            {!bus.is_booking_open && (
              <Badge variant="secondary" className="text-xs">Closed</Badge>
            )}
            {bus.is_full && (
              <Badge variant="destructive" className="text-xs">Full</Badge>
            )}
                          {isBooked && (
                <Badge variant="default" className="bg-purple-600 text-xs">Booked</Badge>
              )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Route Info */}
        <div className="flex items-center gap-2 text-sm text-gray-600 bg-gray-50 px-3 py-2 rounded-lg">
          <MapPin className="h-4 w-4 text-purple-500" />
          <span className="font-medium">{bus.from_location}</span>
          <span className="text-purple-400">→</span>
          <span className="font-medium">{bus.to_location}</span>
        </div>

        {/* Stop Selection or Booking Button */}
        {!showStopSelection ? (
          <Button 
            onClick={handleBookClick} 
            disabled={loading || bus.is_full || isBooked || !bus.is_booking_open || hasConfirmedBooking} 
            variant={getButtonVariant()}
            className="w-full h-10 font-medium" 
            size="sm"
          >
            {getButtonText()}
          </Button>
        ) : (
          <div className="space-y-4 border-t pt-4">
            {/* Stop Selection */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-gray-700">
                Select your pickup stop:
              </label>
              <Select onValueChange={handleStopSelect} value={selectedStopId?.toString() || ""}>
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="Choose your stop" />
                </SelectTrigger>
                <SelectContent>
                  {activeStops.length > 0 ? (
                    activeStops.map((stop) => (
                      <SelectItem key={stop.id} value={stop.id.toString()}>
                        {stop.location}
                      </SelectItem>
                    ))
                  ) : (
                    <SelectItem value="no-stops" disabled>
                      No stops available
                    </SelectItem>
                  )}
                </SelectContent>
              </Select>
            </div>

            {/* Journey Preview */}
            {selectedStopId && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="text-xs text-blue-800 font-medium mb-1">Your Journey:</div>
                <div className="text-sm text-blue-700">
                  {bus.from_location} → {stopsArr.find(s => s.id === selectedStopId)?.location} → {bus.to_location}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowStopSelection(false)
                  setSelectedStopId(null)
                }}
                className="flex-1"
                size="sm"
              >
                Cancel
              </Button>
              <Button
                onClick={() => {
                  if (selectedStopId) {
                    onBook(selectedStopId)
                    setShowStopSelection(false)
                    setSelectedStopId(null)
                  }
                }}
                disabled={!selectedStopId || loading}
                className="flex-1"
                size="sm"
              >
                {loading ? "Booking..." : "Confirm Booking"}
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default BusCard
