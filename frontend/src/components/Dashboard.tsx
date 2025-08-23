import React, { useState, useEffect } from 'react';
import { LogOut, Bus, Clock, Users, CheckCircle, XCircle } from 'lucide-react';
import { Bus as BusType, Booking } from '../types';
import { logout, getBuses, getCurrentBooking, createBooking, cancelBooking } from '../services/api';
import { useAuth } from '../context/AuthContext';
import BusCard from './BusCard';
import BookingCard from './BookingCard';

const Dashboard: React.FC = () => {
  const { user, logout: authLogout } = useAuth();
  const [buses, setBuses] = useState<BusType[]>([]);
  const [currentBooking, setCurrentBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [bookingLoading, setBookingLoading] = useState(false);
  const [selectedBus, setSelectedBus] = useState<BusType | null>(null);

  // Load data on component mount
  useEffect(() => {
    console.log('Dashboard useEffect - user:', user);
    if (user) {
      console.log('User is authenticated, loading data...');
      loadData();
    } else {
      console.log('No user, skipping data load');
    }
  }, [user]);

  const loadData = async () => {
    try {
      console.log('Starting to load data...');
      console.log('Current user:', user);
      console.log('User ID:', user?.id);
      
      if (!user || !user.id) {
        console.error('No user or user ID available');
        setError('User not properly authenticated');
        return;
      }
      
      setLoading(true);
      const [busesData, bookingData] = await Promise.all([
        getBuses(),
        getCurrentBooking()
      ]);
      console.log('Data loaded successfully:', { buses: busesData, booking: bookingData });
      setBuses(busesData);
      setCurrentBooking(bookingData);
    } catch (err) {
      console.error('Failed to load data:', err);
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      authLogout();
    } catch (err) {
      console.error('Logout failed:', err);
      authLogout();
    }
  };

  const handleBookBus = async (busId: number) => {
    if (!user) return;
    
    // Check if user already has a current booking
    if (currentBooking) {
      setError('You already have an active booking. Please cancel it first.');
      return;
    }
    
    // Find the selected bus
    const bus = buses.find(b => b.id === busId);
    if (!bus) {
      setError('Bus not found');
      return;
    }
    
    // Check if bus is available for the selected trip type
    if (!bus.trip_types || bus.trip_types.length === 0) {
      setError('This bus is not available for any trip type');
      return;
    }
    
    // Check if bus is full
    if (bus.is_full) {
      setError('This bus is full. Please select another bus.');
      return;
    }
    
    // Use the first available trip type, or default to RETURN
    const tripType = bus.trip_types.includes('RETURN') ? 'RETURN' : bus.trip_types[0];
    
    // Calculate a future date based on trip type
    const today = new Date();
    let tripDate: Date;
    
    if (tripType === 'WEEKEND') {
      // Find next Saturday
      const daysUntilSaturday = (6 - today.getDay() + 7) % 7;
      tripDate = new Date(today);
      tripDate.setDate(today.getDate() + daysUntilSaturday);
    } else {
      // For return trips, use next Monday
      const daysUntilMonday = (1 - today.getDay() + 7) % 7;
      tripDate = new Date(today);
      tripDate.setDate(today.getDate() + daysUntilMonday);
    }
    
    // Format date as YYYY-MM-DD
    const tripDateStr = tripDate.toISOString().split('T')[0];
    
    // Set appropriate times based on trip type
    const departureTime = '08:00';
    const returnTime = tripType === 'RETURN' ? '18:00' : null;
    
    setBookingLoading(true);
    try {
      console.log('Creating booking with data:', {
        busId,
        tripType,
        tripDate: tripDateStr,
        departureTime,
        returnTime,
        fromLocation: bus.from_location || '',
        toLocation: bus.to_location || ''
      });
      
      const booking = await createBooking(
        busId,
        tripType,
        tripDateStr,
        departureTime,
        returnTime,
        bus.from_location || '',
        bus.to_location || ''
      );
      
      console.log('Booking created successfully:', booking);
      setCurrentBooking(booking);
      setSelectedBus(null);
      // Refresh buses to update available seats
      loadData();
    } catch (error) {
      console.error('Failed to book bus:', error);
      setError(error instanceof Error ? error.message : 'Failed to book bus');
    } finally {
      setBookingLoading(false);
    }
  };

  const handleBusSelect = (bus: BusType) => {
    setSelectedBus(bus);
  };

  const handleCancelBooking = async () => {
    try {
      setBookingLoading(true);
      await cancelBooking();
      setCurrentBooking(null);
      await loadData(); // Refresh data to update available seats
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Cancellation failed');
    } finally {
      setBookingLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">User not found. Please login again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="bg-blue-600 p-2 rounded-lg mr-3">
                <Bus className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">College Transport</h1>
                <p className="text-sm text-gray-600">Welcome, {user.first_name}!</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center px-4 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-md transition duration-150 ease-in-out"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
            <div className="flex items-center">
              <XCircle className="h-5 w-5 mr-2" />
              {error}
            </div>
          </div>
        )}

        {/* User Info */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Student Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm font-medium text-gray-500">Name</p>
              <p className="text-sm text-gray-900">{user.first_name} {user.last_name}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Roll No</p>
              <p className="text-sm text-gray-900">{user.roll_no}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500">Department</p>
              <p className="text-sm text-gray-900">{user.dept} - Year {user.year}</p>
            </div>
          </div>
        </div>

        {/* Current Booking */}
        {currentBooking && (
          <div className="mb-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
              Current Booking
            </h2>
            <BookingCard 
              booking={currentBooking} 
              onCancel={handleCancelBooking}
              loading={bookingLoading}
            />
          </div>
        )}

        {/* Available Buses Section */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <div className="flex items-center mb-6">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
              <Bus className="h-5 w-5 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Available Buses</h2>
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
              />
            ))}
          </div>
        </div>

        {currentBooking && (
          <div className="text-center py-8">
            <div className="bg-blue-50 rounded-lg p-6 max-w-md mx-auto">
              <CheckCircle className="h-12 w-12 text-blue-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Booking Active</h3>
              <p className="text-gray-600">
                You have an active booking. You can only have one booking at a time.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;