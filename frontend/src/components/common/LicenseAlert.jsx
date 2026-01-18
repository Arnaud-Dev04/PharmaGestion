import { AlertTriangle, Lock } from 'lucide-react';

export const LicenseAlert = ({ status, daysRemaining, message, expirationDate }) => {
  if (status === 'valid') return null;

  if (status === 'expired') {
    return (
      <div className="fixed inset-0 z-[9999] bg-gray-900 bg-opacity-95 flex items-center justify-center p-4">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-2xl max-w-lg w-full p-8 text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Lock className="w-10 h-10 text-red-600" />
          </div>
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Licence Expirée</h2>
          <p className="text-gray-600 dark:text-gray-300 mb-6 text-lg">
            {message}
          </p>
          <div className="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg mb-8">
            <p className="text-sm text-gray-500 dark:text-gray-400">Date d'expiration</p>
            <p className="text-xl font-mono font-bold text-gray-900 dark:text-white">{expirationDate}</p>
          </div>
          <button 
            className="btn btn-primary w-full py-3 text-lg"
            onClick={() => window.location.reload()}
          >
            Actualiser
          </button>
        </div>
      </div>
    );
  }

  if (status === 'warning') {
    return (
      <div className="fixed bottom-4 right-4 z-[9999] max-w-sm w-full bg-white dark:bg-gray-800 rounded-lg shadow-xl border-l-4 border-yellow-500 p-4 animate-slide-in">
        <div className="flex gap-3">
            <div className="flex-shrink-0">
                <AlertTriangle className="w-6 h-6 text-yellow-500" />
            </div>
            <div>
                <h3 className="font-bold text-gray-900 dark:text-white">Licence expire bientôt</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                    {message}
                </p>
                <div className="mt-2 text-xs text-gray-400">
                    Expire le: {expirationDate}
                </div>
            </div>
        </div>
      </div>
    );
  }

  return null;
};
