import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin } from '../services/api';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Check if user is already logged in from localStorage
    console.log('AuthContext: Checking localStorage for existing user...');
    const storedUser = localStorage.getItem('user');
    console.log('AuthContext: Stored user from localStorage:', storedUser);
    
    if (storedUser) {
      try {
        const parsedUser = JSON.parse(storedUser);
        console.log('AuthContext: Parsed user from localStorage:', parsedUser);
        
        // For security, we don't store passwords in localStorage
        // So we can't restore the basicAuth. Clear the user and force re-login
        console.log('AuthContext: Cannot restore authentication from localStorage, clearing user state');
        localStorage.removeItem('user');
        setUser(null);
      } catch (error) {
        console.error('AuthContext: Error parsing stored user:', error);
        localStorage.removeItem('user');
      }
    } else {
      console.log('AuthContext: No stored user found in localStorage');
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      console.log('Attempting login with:', email);
      const userData = await apiLogin(email, password);
      console.log('Login successful, user data:', userData);
      setUser(userData);
      console.log('User state updated');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('Logging out user');
    setUser(null);
    localStorage.removeItem('user');
  };

  const value: AuthContextType = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
