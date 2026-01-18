import { useEffect } from 'react';
import { useError } from '../../context/ErrorContext';
import { useLanguage } from '../../context/LanguageContext';
import { XCircle, AlertTriangle, ShieldAlert, ServerCrash } from 'lucide-react';

const GlobalErrorModal = () => {
  const { error, hideError } = useError();
  const { t } = useLanguage();

  if (!error.visible) return null;

  // Determine icon and title based on status
  const getErrorContent = (status) => {
    switch (status) {
      case 400:
        return {
          icon: <AlertTriangle size={48} className="text-orange-500 mb-4" />,
          title: t('error'),
          defaultMessage: t('error400')
        };
      case 401:
        return {
          icon: <ShieldAlert size={48} className="text-red-500 mb-4" />,
          title: t('error'),
          defaultMessage: t('error401')
        };
      case 403:
        return {
          icon: <ShieldAlert size={48} className="text-red-600 mb-4" />,
          title: t('error'),
          defaultMessage: t('error403')
        };
      case 500:
        return {
          icon: <ServerCrash size={48} className="text-red-700 mb-4" />,
          title: t('error'),
          defaultMessage: t('error500')
        };
      default:
        return {
          icon: <XCircle size={48} className="text-red-500 mb-4" />,
          title: t('error'),
          defaultMessage: t('errorGeneric')
        };
    }
  };

  const content = getErrorContent(error.status);
  
  // Use custom message if provided and it's not just the status text, otherwise use translation
  const displayMessage = error.message && error.message !== 'Error' ? error.message : content.defaultMessage;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-8 max-w-md w-full mx-4 transform transition-all scale-100 animate-in zoom-in-95 duration-200 text-center relative">
        <div className="flex flex-col items-center">
          {content.icon}
          
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            {content.title}
          </h2>
          
          <p className="text-gray-600 dark:text-gray-300 mb-6 leading-relaxed">
            {displayMessage}
          </p>

          <button
            onClick={hideError}
            className="px-6 py-2.5 bg-gray-900 dark:bg-gray-700 hover:bg-gray-800 dark:hover:bg-gray-600 text-white rounded-lg font-medium transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
          >
            {t('close')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default GlobalErrorModal;
