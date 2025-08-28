export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  year: string;
  roll_no: string;
  dept: string;
  gender: string;
  student_type: string;
  degree_type: string;
}

export interface Stop {
  id: number;
  stop_name: string;
  location: string;
  is_pickup: boolean;
  is_dropoff: boolean;
  is_active: boolean;
  display_name: string;
}

export interface Bus {
  id: number;
  bus_no: string;
  route_name: string;
  from_location: string;
  to_location: string;
  route_display: string;
  departure_date: string;
  departure_time: string;
  capacity: number;
  available_seats: number;
  is_full: boolean;
  stops: Stop[];
}

export interface Booking {
  id: number;
  student: User;
  bus: Bus;
  booking_date: string;
  trip_date: string;
  departure_time: string;
  from_location: string;
  to_location: string;
  status: string;
}