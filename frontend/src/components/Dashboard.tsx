"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { Bus, Search, CheckCircle, XCircle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Alert, AlertDescription } from "../components/ui/alert"
import type { Bus as BusType, Booking } from "../types"
import { getBuses, createBooking, getCurrentBooking } from "../services/api"
import { useAuth } from "../context/AuthContext"
import BusCard from "./BusCard"
import { toast } from "sonner"
import Navbar from "./Navbar"

const Dashboard: React.FC = () => {
  const { user } = useAuth()
  const [buses, setBuses] = useState<BusType[]>([])
  const [currentBooking, setCurrentBooking] = useState<Booking | null>(null)
  const [hasPendingBooking, setHasPendingBooking] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [bookingLoading, setBookingLoading] = useState<number | null>(null)
  const [selectedTripDate, setSelectedTripDate] = useState("")
  const [selectedDepartureTime, setSelectedDepartureTime] = useState("")

  const [searchQuery, setSearchQuery] = useState("")
  const [activeFilter, setActiveFilter] = useState<"from_rec" | "to_rec">("from_rec")

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
      
      // Check if there's a pending booking
      if (bookingData && bookingData.status === 'pending') {
        setHasPendingBooking(true)
      } else {
        setHasPendingBooking(false)
      }
    } catch (err) {
      setError("Failed to load data")
    } finally {
      setLoading(false)
    }
  }

  const handleBookBus = async (busId: number, selectedStopId: number = 0) => {
    if (!user) return
    
    // Check if user already has a confirmed booking
    if (currentBooking && currentBooking.status === 'confirmed') {
      toast.error("You already have an active booking. You can only have one booking at a time.")
      return
    }

    // Check if user has a pending booking
    if (hasPendingBooking) {
      toast.error("You have a pending booking that requires OTP verification. Please complete your current booking first.")
      return
    }

    const bus = buses.find((b) => b.id === busId)
    if (!bus || bus.is_full) return

    // Get stop information
    const fromLocation = bus.from_location || ""
    const toLocation = bus.to_location || ""
    
    setBookingLoading(busId)
    try {
      const response = await createBooking(
        busId,
        selectedTripDate,
        selectedDepartureTime,
        fromLocation,
        toLocation,
        selectedStopId
      )

      if (response && response.otp_sent && response.pending_booking_id) {
        setCurrentBooking(response)
        toast.success("OTP sent to your email. Please go to 'My Booking' to verify your OTP and complete your booking.")
        loadData()
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
      setBookingLoading(null)
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
      activeFilter === "from_rec"
        ? bus.stops?.some(stop => stop.is_pickup && stop.location.toLowerCase().includes("rec")) || 
          (bus.from_location || "").toLowerCase().includes("rec")
        : activeFilter === "to_rec"
          ? bus.stops?.some(stop => stop.is_dropoff && stop.location.toLowerCase().includes("rec")) || 
            (bus.to_location || "").toLowerCase().includes("rec")
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

      <div className="container mx-auto px-4 pt-32 pb-8 space-y-6">
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
             { key: "from_rec", label: "From REC", description: "Buses departing from REC" },
             { key: "to_rec", label: "To REC", description: "Buses arriving at REC" },
           ].map(({ key, label, description }) => (
             <Button
               key={key}
               variant={activeFilter === key ? "default" : "outline"}
               size="sm"
               onClick={() => setActiveFilter(key as any)}
               title={description}
             >
               {label}
             </Button>
           ))}
         </div>
         
         <p className="text-sm text-muted-foreground">
           {activeFilter === "from_rec" 
             ? "Showing buses where REC is a pickup point. REC will be automatically selected as your pickup location."
             : "Showing buses where REC is a drop-off point. REC will be automatically selected as your drop-off location."
           }
         </p>

        {error && (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

                 {currentBooking && currentBooking.status === 'confirmed' && (
           <Alert>
             <CheckCircle className="h-4 w-4" />
             <AlertDescription>
               You have an active booking. You can only have one booking at a time. 
               View your booking details in the "My Booking" section.
             </AlertDescription>
           </Alert>
         )}

         {hasPendingBooking && (
           <Alert>
             <CheckCircle className="h-4 w-4" />
             <AlertDescription>
               You have a pending booking that requires OTP verification. 
               Please go to "My Booking" to complete your booking.
             </AlertDescription>
           </Alert>
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
                       onBook={(selectedStopId) => handleBookBus(bus.id, selectedStopId)}
                       loading={bookingLoading === bus.id}
                       isBooked={!!(currentBooking && currentBooking.status === 'confirmed')}
                       activeFilter={activeFilter}
                     />
                ))}
              </div>
            )}
          </CardContent>
        </Card>


      </div>

      
    </div>
  )
}

export default Dashboard
