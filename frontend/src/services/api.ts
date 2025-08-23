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
  console.log('Basic auth set:', basicAuth ? 'Yes' : 'No');
};

export const getBasicAuth = () => {
  return basicAuth;
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
    console.error('API call failed:', endpoint, response.status, response.statusText);
    throw new ApiError(response.status, `HTTP error! status: ${response.status}`);
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
  basicAuth = null;
  return apiCall('/logout/', { method: 'POST' });
};

export const getCurrentUser = async () => {
  return apiCall('/user/');
};

export const getBuses = async () => {
  return apiCall('/buses/');
};

export const createBooking = async (busId: number, tripType: 'RETURN' | 'WEEKEND', tripDate: string, departureTime: string, returnTime: string | null, fromLocation: string, toLocation: string) => {
  try {
    const response = await apiCall('/bookings/', {
      method: 'POST',
      body: JSON.stringify({ 
        bus_id: busId, 
        trip_type: tripType, 
        trip_date: tripDate, 
        departure_time: departureTime, 
        return_time: returnTime, 
        from_location: fromLocation, 
        to_location: toLocation 
      }),
    });
    
    if (response.success) {
      return response.booking;
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