import React from 'react';
import { Clock, MapPin, Calendar, ArrowRight, XCircle } from 'lucide-react';
import { Booking } from '../types';

interface BookingCardProps {
  booking: Booking;
  onCancel: () => void;
  loading: boolean;
}

const BookingCard: React.FC<BookingCardProps> = ({ booking, onCancel, loading }) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex justify-between items-start mb-6">
        <div>
          <h3 className="text-xl font-semibold text-gray-900">{booking.bus.bus_no}</h3>
          <div className="flex items-center text-gray-600 mt-1">
            <MapPin className="h-4 w-4 mr-1" />
            <span>{booking.bus.route_name}</span>
          </div>
        </div>
        <div className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
          Confirmed
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="space-y-4">
          <div className="flex items-center text-gray-600">
            <Clock className="h-5 w-5 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Departure Time</p>
              <p className="text-sm">{booking.departure_time}</p>
            </div>
          </div>
          {booking.trip_type === 'RETURN' && booking.return_time && (
            <div className="flex items-center text-gray-600">
              <Clock className="h-5 w-5 mr-3" />
              <div>
                <p className="font-medium text-gray-900">Return Time</p>
                <p className="text-sm">{booking.return_time}</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="space-y-4">
          <div className="flex items-center text-gray-600">
            <Calendar className="h-5 w-5 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Trip Date</p>
              <p className="text-sm">{new Date(booking.trip_date).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}</p>
            </div>
          </div>
          <div className="flex items-center text-gray-600">
            <Calendar className="h-5 w-5 mr-3" />
            <div>
              <p className="font-medium text-gray-900">Booking Date</p>
              <p className="text-sm">{formatDate(booking.booking_date)}</p>
            </div>
          </div>
          <div className="flex items-center text-gray-600">
            <div className="w-5 h-5 mr-3 flex items-center justify-center">
              ↔️
            </div>
            <div>
              <p className="font-medium text-gray-900">Trip Type</p>
              <p className="text-sm">
                {booking.trip_type === 'RETURN' ? 'Return Trip' : 'Weekend Trip'}
              </p>
            </div>
          </div>
          <div className="flex items-center text-gray-600">
            <MapPin className="h-5 w-5 mr-3" />
            <div>
              <p className="font-medium text-gray-900">From</p>
              <p className="text-sm">{booking.from_location}</p>
            </div>
          </div>
          <div className="flex items-center text-gray-600">
            <MapPin className="h-5 w-5 mr-3" />
            <div>
              <p className="font-medium text-gray-900">To</p>
              <p className="text-sm">{booking.to_location}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
        <p className="text-blue-800 text-sm">
          <strong>Important:</strong> Please arrive at the pickup point 10 minutes before departure time. 
          A confirmation email has been sent to your registered email address.
        </p>
      </div>

      <button
        onClick={onCancel}
        disabled={loading}
        className="w-full md:w-auto flex items-center justify-center px-6 py-2 border border-red-300 text-red-700 hover:bg-red-50 rounded-md font-medium transition duration-150 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? (
          <>
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-700 mr-2"></div>
            Cancelling...
          </>
        ) : (
          <>
            <XCircle className="h-4 w-4 mr-2" />
            Cancel Booking
          </>
        )}
      </button>
    </div>
  );
};

export default BookingCard;