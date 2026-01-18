import { createContext, useContext, useState, useCallback } from 'react';

const ErrorContext = createContext();

export const ErrorProvider = ({ children }) => {
  const [error, setError] = useState({
    visible: false,
    message: '',
    status: null
  });

  const showError = useCallback((message, status = null) => {
    setError({
      visible: true,
      message,
      status
    });
  }, []);

  const hideError = useCallback(() => {
    setError(prev => ({ ...prev, visible: false }));
  }, []);

  return (
    <ErrorContext.Provider value={{ error, showError, hideError }}>
      {children}
    </ErrorContext.Provider>
  );
};

export const useError = () => useContext(ErrorContext);
