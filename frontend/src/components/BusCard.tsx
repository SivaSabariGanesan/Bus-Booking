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
  onBook: (pickupStopId: number, dropoffStopId: number) => void
  loading: boolean
  isBooked: boolean
  activeFilter?: "from_rec" | "to_rec"
}

const BusCard: React.FC<BusCardProps> = ({ bus, onBook, loading, isBooked, activeFilter }) => {
  const [selectedPickupStopId, setSelectedPickupStopId] = useState<number | null>(null)
  const [selectedDropoffStopId, setSelectedDropoffStopId] = useState<number | null>(null)
  const [showStopSelection, setShowStopSelection] = useState(false)
  


  const handleBookClick = () => {
    console.log("Book clicked for bus:", bus.bus_no, "Filter:", activeFilter, "Stops:", bus.stops)
    
    // Always show stop selection first, regardless of filter or stops configuration
    setShowStopSelection(true)
    
    if (bus.stops && bus.stops.length > 0) {
      // If filter is active, automatically select REC stops
      if (activeFilter === "from_rec") {
        const recPickupStop = bus.stops.find(stop => 
          stop.is_pickup && stop.location.toLowerCase().includes("rec")
        )
        console.log("REC pickup stop found:", recPickupStop)
        if (recPickupStop) {
          // Automatically select REC as pickup
          setSelectedPickupStopId(recPickupStop.id)
        }
      } else if (activeFilter === "to_rec") {
        const recDropoffStop = bus.stops.find(stop => 
          stop.is_dropoff && stop.location.toLowerCase().includes("rec")
        )
        console.log("REC dropoff stop found:", recDropoffStop)
        if (recDropoffStop) {
          // Automatically select REC as drop-off
          setSelectedDropoffStopId(recDropoffStop.id)
        }
      }
    }
  }

  const handlePickupStopSelect = (stopId: string) => {
    console.log("Pickup stop selected:", stopId)
    setSelectedPickupStopId(parseInt(stopId))
  }

  const handleDropoffStopSelect = (stopId: string) => {
    console.log("Dropoff stop selected:", stopId)
    setSelectedDropoffStopId(parseInt(stopId))
  }

  const handleConfirmBooking = () => {
    // For from_rec: pickup is automatically selected, need dropoff
    // For to_rec: dropoff is automatically selected, need pickup
    // For all: need both pickup and dropoff
    const canConfirm = 
      (activeFilter === "from_rec" && selectedPickupStopId && selectedDropoffStopId) ||
      (activeFilter === "to_rec" && selectedPickupStopId && selectedDropoffStopId) ||
      (!activeFilter && selectedPickupStopId && selectedDropoffStopId)
    
    if (canConfirm) {
      onBook(selectedPickupStopId, selectedDropoffStopId)
      setShowStopSelection(false)
      setSelectedPickupStopId(null)
      setSelectedDropoffStopId(null)
    }
  }

  const activeStops = bus.stops?.filter(stop => stop.is_active) || []
  
  // Always show all available stops in dropdowns, regardless of filter
  // The filter only affects what gets automatically selected, not what's shown
  const pickupStops = activeStops.filter(stop => stop.is_pickup)
  const dropoffStops = activeStops.filter(stop => stop.is_dropoff)

  return (
    <Card className={`transition-all hover:shadow-md ${isBooked ? "ring-2 ring-primary" : ""}`}>
      <CardHeader className="pb-3">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Bus className="h-4 w-4" />
          {bus.route_name}
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
          
          
        </div>

        {!showStopSelection ? (
          <Button 
            onClick={handleBookClick} 
            disabled={loading || bus.is_full || isBooked} 
            className="w-full" 
            size="sm"
          >
            {loading ? "Booking..." : isBooked ? "Booked" : bus.is_full ? "Full" : "Book Now"}
          </Button>
        ) : (
          <div className="space-y-3">
            <div className="text-sm font-medium text-gray-700">
              {activeFilter === "from_rec" 
                ? "REC is automatically selected as your pickup point. Choose your drop-off location:"
                : activeFilter === "to_rec"
                ? "REC is automatically selected as your drop-off point. Choose your pickup location:"
                : "Select your pickup and drop-off stops:"
              }
            </div>
            
                         {/* Pickup Point - Show for "to_rec" filter (user selects pickup, REC is dropoff) */}
             {(activeFilter === "to_rec" || !activeFilter) && (
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-600">
                  Pickup Point: ({pickupStops.length} options)
                </label>
                <Select onValueChange={handlePickupStopSelect} value={selectedPickupStopId?.toString() || ""}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose pickup stop" />
                  </SelectTrigger>
                  <SelectContent>
                    {pickupStops.length > 0 ? (
                      pickupStops.map((stop) => (
                        <SelectItem key={stop.id} value={stop.id.toString()}>
                          {stop.display_name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="" disabled>
                        No pickup stops available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            )}

                         {/* Drop-off Point - Show for "from_rec" filter (user selects dropoff, REC is pickup) */}
             {(activeFilter === "from_rec" || !activeFilter) && (
              <div className="space-y-2">
                <label className="text-xs font-medium text-gray-600">
                  Drop-off Point: ({dropoffStops.length} options)
                </label>
                <Select onValueChange={handleDropoffStopSelect} value={selectedDropoffStopId?.toString() || ""}>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose drop-off stop" />
                  </SelectTrigger>
                  <SelectContent>
                    {dropoffStops.length > 0 ? (
                      dropoffStops.map((stop) => (
                        <SelectItem key={stop.id} value={stop.id.toString()}>
                          {stop.display_name}
                        </SelectItem>
                      ))
                    ) : (
                      <SelectItem value="" disabled>
                        No drop-off stops available
                      </SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            )}

            {/* Show automatically selected stops */}
            {activeFilter === "from_rec" && selectedPickupStopId && (
              <div className="text-sm text-green-600 bg-green-50 px-3 py-2 rounded border border-green-200">
                ✅ Pickup Point: {bus.stops?.find(s => s.id === selectedPickupStopId)?.display_name || "REC"}
              </div>
            )}
            
            {activeFilter === "to_rec" && selectedDropoffStopId && (
              <div className="text-sm text-green-600 bg-green-50 px-3 py-2 rounded border border-green-200">
                ✅ Drop-off Point: {bus.stops?.find(s => s.id === selectedDropoffStopId)?.display_name || "REC"}
              </div>
            )}
            
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => {
                  setShowStopSelection(false)
                  setSelectedPickupStopId(null)
                  setSelectedDropoffStopId(null)
                }}
                className="flex-1"
                size="sm"
              >
                Cancel
              </Button>
                             <Button
                 onClick={handleConfirmBooking}
                                   disabled={
                    (activeFilter === "from_rec" && !selectedDropoffStopId) ||
                    (activeFilter === "to_rec" && !selectedPickupStopId) ||
                    (!activeFilter && (!selectedPickupStopId || !selectedDropoffStopId)) ||
                    loading
                  }
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
