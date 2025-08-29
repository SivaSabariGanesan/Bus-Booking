"use client"

import type React from "react"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select"
import { Bus, MapPin } from "lucide-react"
import type { Bus as BusType, Stop } from "../types"

interface BusCardProps {
  bus: BusType
  onBook: (pickupStopId: number) => void
  loading: boolean
  isBooked: boolean
  activeFilter?: "from_rec" | "to_rec"
}

const BusCard: React.FC<BusCardProps> = ({ bus, onBook, loading, isBooked, activeFilter }) => {
  const [selectedStopId, setSelectedStopId] = useState<number | null>(null)
  const [showStopSelection, setShowStopSelection] = useState(false)
  


  const handleBookClick = () => {
    console.log("Book clicked for bus:", bus.bus_no, "Filter:", activeFilter, "Stops:", bus.stops)
    
    // Always show stop selection first, regardless of filter or stops configuration
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
      
      // No auto-selection - user will manually select all stops
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
  
  // Always show all available stops in dropdowns, regardless of filter
  const pickupStops = activeStops.filter(stop => stop.is_pickup)
  const dropoffStops = activeStops.filter(stop => stop.is_dropoff)

  return (
    <Card className={`transition-all hover:shadow-md ${isBooked ? "ring-2 ring-primary" : ""}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Bus className="h-4 w-4" />
          {bus.route_name}
          {!bus.is_booking_open && (
            <Badge variant="secondary" className="ml-2">Closed</Badge>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <MapPin className="h-3 w-3" />
            <span className="truncate">{bus.from_location}</span>
            <span>→</span>
            <span className="truncate">{bus.to_location}</span>
          </div>
          
          {/* Show route with selected stops when available */}
          {showStopSelection && (selectedStopId) && (
            <div className="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded border border-blue-200">
              <span className="font-medium">Bus Route:</span>{" "}
              <span className="font-medium">{bus.from_location} → {bus.to_location}</span>
              <br />
              <span className="font-medium">Your Journey:</span>{" "}
              {selectedStopId ? (
                <>
                  <span className="font-medium">{stopsArr.find(s => s.id === selectedStopId)?.location || "Selected Stop"}</span>
                  <span> → </span>
                  <span className="font-medium">{bus.to_location}</span>
                </>
              ) : (
                "Select your main stop for your journey"
              )}
            </div>
          )}
        </div>

        {!showStopSelection ? (
          <Button 
            onClick={handleBookClick} 
            disabled={loading || bus.is_full || isBooked || !bus.is_booking_open} 
            className="w-full" 
            size="sm"
          >
            {loading ? "Booking..." : isBooked ? "Booked" : bus.is_full ? "Full" : (!bus.is_booking_open ? "Closed" : "Book Now")}
          </Button>
        ) : (
          <div className="space-y-3">
    <div className="text-sm font-medium text-gray-700">
      Pickup: {bus.from_location} | Dropoff: {bus.to_location}
      <br />
      <span className="text-xs text-gray-600">Select your main stop for your journey:</span>
    </div>
    {/* Single Stop Selection Dropdown */}
    <div className="space-y-2">
      <label className="text-xs font-medium text-gray-600">
        Your Stop: ({activeStops.length} options)
      </label>
      <Select onValueChange={handleStopSelect} value={selectedStopId?.toString() || ""}>
        <SelectTrigger>
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
    {/* Show selected stop summary */}
    {selectedStopId && (
      <div className="text-sm text-green-600 bg-green-50 px-3 py-2 rounded border border-green-200">
        <div className="text-xs text-green-700">
          <span className="font-medium">Bus Route:</span> {bus.from_location} → {bus.to_location}
        </div>
        <div className="text-xs text-green-700 mt-1">
          <span className="font-medium">Your Journey:</span> {bus.from_location} → {stopsArr.find(s => s.id === selectedStopId)?.location} → {bus.to_location}
        </div>
      </div>
    )}
    {/* Journey Preview */}
    {selectedStopId && (
      <div className="text-sm text-blue-600 bg-blue-50 px-3 py-2 rounded border border-blue-200">
        🚌 Journey Preview:
        <div className="text-xs text-blue-700 mt-1">
          {bus.from_location} → {stopsArr.find(s => s.id === selectedStopId)?.location} → {bus.to_location}
        </div>
      </div>
    )}
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
