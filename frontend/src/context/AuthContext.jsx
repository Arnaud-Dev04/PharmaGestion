import { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/authService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on mount
  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('token');

      if (savedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setToken(savedToken);
        } catch (error) {
          console.error('Failed to fetch user:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    const data = await authService.login(username, password);
    
    const accessToken = data.access_token;
    setToken(accessToken);
    localStorage.setItem('token', accessToken);
    
    // Fetch user details immediately after login to get the Role
    try {
        const userData = await authService.getCurrentUser();
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
        console.error("Error fetching user details after login", error);
        // Fallback or re-throw? 
        // If we can't get user, we might be in inconsistent state.
    }
    
    return data;
  };

  const logout = () => {
    authService.logout();
    setToken(null);
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const value = {
    user,
    token,
    isAuthenticated: !!token,
    isLoading,
    login,
    logout,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
