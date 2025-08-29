const API_BASE = import.meta.env.VITE_API_BASE;

// Import the existing API functions from services/api.ts
export { login, logout, getCurrentUser, getBuses, getCurrentBooking, createBooking, cancelBooking } from '../services/api';

// Create a simple API client for additional endpoints
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const url = `${API_BASE}${endpoint}`;
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  
  // Add any additional headers from options
  if (options.headers) {
    Object.assign(headers, options.headers);
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};

const api = {
  get: (endpoint: string) => apiCall(endpoint),
  
  post: (endpoint: string, data: any) => apiCall(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  }),
  
  put: (endpoint: string, data: any) => apiCall(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  }),
  
  delete: (endpoint: string) => apiCall(endpoint, {
    method: 'DELETE',
  }),
};

export default api;
