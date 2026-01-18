import { useEffect } from 'react';
import { useError } from '../../context/ErrorContext';
import { useLanguage } from '../../context/LanguageContext';
import api from '../../services/api';
import { mapErrorToTranslationKey } from '../../utils/errorMapping';

const AxiosInterceptor = () => {
  const { showError } = useError();
  const { t } = useLanguage();

  useEffect(() => {
    // Add a response interceptor
    const interceptor = api.interceptors.response.use(
      (response) => response,
      (error) => {
        const status = error.response ? error.response.status : null;
        
        if (status === 400 || status === 401 || status === 403 || status === 500) {
          // Get backend error message
          let backendMessage = null;
          
          if (error.response?.data) {
            const data = error.response.data;
            backendMessage = data.detail || data.message || data.error;
            
            // If detail is an array (validation errors), take first message
            if (Array.isArray(data.detail) && data.detail.length > 0) {
              backendMessage = data.detail[0].msg || data.detail[0].message;
            }
          }
          
          // Map backend message to translation key
          const translationKey = mapErrorToTranslationKey(backendMessage, status);
          const message = t(translationKey);

          showError(message, status);
        } else if (!status) {
           // Network error
           showError(t('errorGeneric'), 0);
        }

        return Promise.reject(error);
      }
    );

    // Eject interceptor on unmount
    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [showError, t]);

  return null;
};

export default AxiosInterceptor;
