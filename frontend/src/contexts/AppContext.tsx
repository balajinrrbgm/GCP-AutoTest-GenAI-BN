import React, { createContext, useContext, useState, ReactNode } from 'react';

// Types for application state
interface AppState {
  loading: boolean;
  error: string | null;
  notifications: Notification[];
  preferences: UserPreferences;
}

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
}

interface UserPreferences {
  theme: 'light' | 'dark';
  language: string;
  itemsPerPage: number;
  autoSave: boolean;
}

interface AppContextType {
  state: AppState;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp'>) => void;
  removeNotification: (id: string) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
}

// Default state
const defaultState: AppState = {
  loading: false,
  error: null,
  notifications: [],
  preferences: {
    theme: 'light',
    language: 'en',
    itemsPerPage: 10,
    autoSave: true,
  },
};

// Create context
const AppContext = createContext<AppContextType | undefined>(undefined);

// App provider component
export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, setState] = useState<AppState>(defaultState);

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, loading }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const addNotification = (notification: Omit<Notification, 'id' | 'timestamp'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
    };
    
    setState(prev => ({
      ...prev,
      notifications: [...prev.notifications, newNotification],
    }));

    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      removeNotification(newNotification.id);
    }, 5000);
  };

  const removeNotification = (id: string) => {
    setState(prev => ({
      ...prev,
      notifications: prev.notifications.filter(n => n.id !== id),
    }));
  };

  const updatePreferences = (preferences: Partial<UserPreferences>) => {
    setState(prev => ({
      ...prev,
      preferences: { ...prev.preferences, ...preferences },
    }));
  };

  const contextValue: AppContextType = {
    state,
    setLoading,
    setError,
    addNotification,
    removeNotification,
    updatePreferences,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};

// Hook to use app context
export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};