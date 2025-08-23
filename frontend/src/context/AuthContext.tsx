import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { login as apiLogin, restoreBasicAuth, getCurrentUser } from '../services/api';
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
        
        // Try to restore basic auth
        if (restoreBasicAuth()) {
          console.log('AuthContext: Basic auth restored, validating user session...');
          // Validate the user session by making an API call
          getCurrentUser()
            .then(userData => {
              console.log('AuthContext: User session validated, user data:', userData);
              setUser(userData);
            })
            .catch(error => {
              console.log('AuthContext: User session invalid, clearing auth:', error);
              localStorage.removeItem('user');
              setUser(null);
            });
        } else {
          console.log('AuthContext: Could not restore basic auth, clearing user state');
          localStorage.removeItem('user');
          setUser(null);
        }
      } catch (error) {
        console.error('AuthContext: Error parsing stored user:', error);
        localStorage.removeItem('user');
        setUser(null);
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
      // Store user in localStorage for persistence
      localStorage.setItem('user', JSON.stringify(userData));
      console.log('User state updated and stored in localStorage');
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
