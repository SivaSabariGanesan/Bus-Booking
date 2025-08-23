import React from 'react';
import { Clock, Users, MapPin } from 'lucide-react';
import { Bus } from '../types';

interface BusCardProps {
  bus: Bus;
  onBook: () => void;
  onSelect: () => void;
  loading: boolean;
  selected: boolean;
}

const BusCard: React.FC<BusCardProps> = ({ bus, onBook, onSelect, loading, selected }) => {
  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition duration-150 ease-in-out cursor-pointer ${
        selected ? 'ring-2 ring-blue-500 border-blue-300' : ''
      }`}
      onClick={onSelect}
    >
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">{bus.bus_no}</h3>
          <div className="flex items-center text-gray-600 mt-1">
            <MapPin className="h-4 w-4 mr-1" />
            <span className="text-sm">{bus.route_name}</span>
          </div>
        </div>
        <div className={`px-2 py-1 rounded-full text-xs font-medium ${
          bus.available_seats > 5 
            ? 'bg-green-100 text-green-800'
            : bus.available_seats > 0
            ? 'bg-yellow-100 text-yellow-800'
            : 'bg-red-100 text-red-800'
        }`}>
          {bus.available_seats} seats left
        </div>
      </div>

      <div className="space-y-3 mb-6">
        <div className="flex items-center text-gray-600">
          <Clock className="h-4 w-4 mr-2" />
          <div className="text-sm">
            <span className="font-medium">Departure:</span> {bus.departure_time}
          </div>
        </div>
        <div className="flex items-center text-gray-600">
          <Clock className="h-4 w-4 mr-2" />
          <div className="text-sm">
            <span className="font-medium">Return:</span> {bus.return_time}
          </div>
        </div>
        <div className="flex items-center text-gray-600">
          <Users className="h-4 w-4 mr-2" />
          <div className="text-sm">
            <span className="font-medium">Capacity:</span> {bus.capacity} seats
          </div>
        </div>
        
        {/* Available Dates Section */}
        {bus.weekend_dates && bus.weekend_dates.length > 0 && (
          <div className="flex items-start text-gray-600">
            <div className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0">
              📅
            </div>
            <div className="text-sm">
              <span className="font-medium">Weekend Dates:</span>
              <div className="mt-1 space-y-1">
                {bus.weekend_dates.map((date, index) => (
                  <div key={index} className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">
                    {new Date(date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {bus.return_dates && bus.return_dates.length > 0 && (
          <div className="flex items-start text-gray-600">
            <div className="w-4 h-4 mr-2 mt-0.5 flex-shrink-0">
              📅
            </div>
            <div className="text-sm">
              <span className="font-medium">Return Trip Dates:</span>
              <div className="mt-1 space-y-1">
                {bus.return_dates.map((date, index) => (
                  <div key={index} className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded">
                    {new Date(date).toLocaleDateString('en-US', {
                      weekday: 'short',
                      month: 'short',
                      day: 'numeric',
                      year: 'numeric'
                    })}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      <button
        onClick={onBook}
        disabled={loading || bus.is_full}
        className={`w-full py-2 px-4 rounded-md font-medium transition duration-150 ease-in-out ${
          bus.is_full
            ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
            : loading
            ? 'bg-blue-400 text-white cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700 text-white focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
        }`}
      >
        {loading ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Booking...
          </div>
        ) : bus.is_full ? (
          'Bus Full'
        ) : (
          'Book Now'
        )}
      </button>
    </div>
  );
};

export default BusCard;