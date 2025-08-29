const API_BASE = 'http://localhost:8000/api';

let basicAuth: string | null = null;

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export const setBasicAuth = (email: string, password: string) => {
  basicAuth = 'Basic ' + btoa(`${email}:${password}`);
  // Store credentials in localStorage for persistence
  localStorage.setItem('basicAuth', basicAuth);
  localStorage.setItem('userEmail', email);
  console.log('Basic auth set and stored:', basicAuth ? 'Yes' : 'No');
};

export const getBasicAuth = () => {
  return basicAuth;
};

export const restoreBasicAuth = () => {
  const storedAuth = localStorage.getItem('basicAuth');
  if (storedAuth) {
    basicAuth = storedAuth;
    console.log('Basic auth restored from localStorage');
    return true;
  }
  return false;
};

export const clearBasicAuth = () => {
  basicAuth = null;
  localStorage.removeItem('basicAuth');
  localStorage.removeItem('userEmail');
  console.log('Basic auth cleared');
};

const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add any additional headers from options
  if (options.headers) {
    Object.assign(headers, options.headers);
  }
  
  if (basicAuth) {
    headers['Authorization'] = basicAuth;
    console.log('Adding Authorization header for:', endpoint);
  } else {
    console.log('No basicAuth available for:', endpoint);
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `HTTP error! status: ${response.status}`;
    try {
      const data = await response.json();
      if (data && data.errors) {
        errorMessage = Object.values(data.errors).flat().join(', ');
      } else if (data && data.detail) {
        errorMessage = data.detail;
      }
    } catch (e) {
      // ignore JSON parse errors, keep default errorMessage
    }
    throw new ApiError(response.status, errorMessage);
  }

  return response.json();
};

export const login = async (email: string, password: string) => {
  setBasicAuth(email, password);
  const response = await apiCall('/login/', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
  if (response.success) {
    return response.user;
  } else {
    basicAuth = null; // clear on failure
    throw new Error(Object.values(response.errors).flat().join(', '));
  }
};

export const logout = async () => {
  try {
    await apiCall('/logout/', { method: 'POST' });
  } catch (error) {
    console.log('Logout API call failed, but clearing local auth anyway');
  } finally {
    clearBasicAuth();
  }
};

export const getCurrentUser = async () => {
  return apiCall('/user/');
};

export const getBuses = async () => {
  return apiCall('/buses/');
};

export const getBusAvailableDates = async (busId: number, tripType: 'RETURN' | 'WEEKEND') => {
  return apiCall(`/buses/${busId}/available-dates/?trip_type=${tripType}`);
};

export const debugRequest = async (data: any) => {
  try {
    const response = await apiCall('/debug-request/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    
    console.log('Debug response:', response);
    return response;
  } catch (error) {
    console.error('Debug error:', error);
    throw error;
  }
};

export const testBookingData = async (busId: number, tripDate: string, departureTime: string, fromLocation: string, toLocation: string) => {
  try {
    const response = await apiCall('/test-booking-data/', {
      method: 'POST',
      body: JSON.stringify({ 
        bus_id: busId, 
        trip_date: tripDate, 
        departure_time: departureTime, 
        from_location: fromLocation, 
        to_location: toLocation 
      }),
    });
    
    console.log('Test response:', response);
    return response;
  } catch (error) {
    console.error('Test error:', error);
    throw error;
  }
};

export const createBooking = async (
  busId: number,
  tripDate: string,
  departureTime: string,
  fromLocation: string,
  toLocation: string,
  selectedStopId: number
) => {
  try {
    const response = await apiCall('/bookings/', {
      method: 'POST',
      body: JSON.stringify({ 
        bus_id: busId, 
        trip_date: tripDate, 
        departure_time: departureTime, 
        from_location: fromLocation, 
        to_location: toLocation,
        selected_stop_id: selectedStopId
      }),
    });
    if (response.success) {
      return response;
    } else {
      // Show more detailed error information
      const errorMessage = response.errors ? Object.values(response.errors).flat().join(', ') : 'Failed to create booking';
      throw new Error(errorMessage);
    }
  } catch (error) {
    console.error('createBooking error details:', error);
    if (error instanceof ApiError) {
      // Try to get the response body for more details
      console.error('API Error status:', error.status);
      throw error;
    }
    throw error;
  }
};

export const getCurrentBooking = async () => {
  const response = await apiCall('/bookings/current/');
  return response.booking;
};

export const cancelBooking = async () => {
  const response = await apiCall('/bookings/cancel/', {
    method: 'DELETE',
  });
  if (!response.success) {
    throw new Error(response.message || 'Failed to cancel booking');
  }
  return response;
};

export const verifyBookingOtp = async (pendingBookingId: number, otp: string) => {
  const response = await apiCall('/bookings/verify-otp/', {
    method: 'POST',
    body: JSON.stringify({ pending_booking_id: pendingBookingId, otp }),
  });
  return response;
};

export const resendOtp = async (bookingId: number) => {
  const response = await apiCall('/bookings/resend-otp/', {
    method: 'POST',
    body: JSON.stringify({ booking_id: bookingId }),
  });
  return response;
};