import { useState } from 'react';
import { Bell, Sun, Moon, Globe } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useTheme } from '../../context/ThemeContext';
import { useLanguage } from '../../context/LanguageContext';
import { format } from 'date-fns';
import { fr, enUS } from 'date-fns/locale';

export const Header = () => {
  const { user } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const { language, setLanguage } = useLanguage();
  
  const [showNotifications, setShowNotifications] = useState(false);
  const [showLanguageMenu, setShowLanguageMenu] = useState(false);

  // Mock Notifications
  const notifications = [
    { id: 1, title: 'Stock faible', message: 'Paracétamol 500mg (10 boîtes restantes)', time: '2 min' },
    { id: 2, title: 'Nouvelle vente', message: 'Vente #1234 validée', time: '15 min' },
    { id: 3, title: 'Rapport généré', message: 'Rapport journalier disponible', time: '1h' },
  ];

  const currentDate = format(new Date(), 'EEEE d MMMM yyyy', { 
    locale: language === 'en' ? enUS : fr 
  });

  return (
    <header className="h-16 bg-card border-b border-border px-6 flex items-center justify-between relative z-20">
      {/* Left Section - Date and User Role */}
      <div>
        <p className="text-sm text-gray-600 dark:text-gray-400 capitalize">{currentDate}</p>
        <p className="text-xs font-medium text-primary">
          {user?.role === 'admin' ? 'Mode Administrateur' : 'Mode Pharmacien'}
        </p>
      </div>

      {/* Right Section - Actions */}
      <div className="flex items-center gap-4">
        
        {/* Notifications Dropdown */}
        <div className="relative">
            <button 
                onClick={() => {
                    setShowNotifications(!showNotifications);
                    setShowLanguageMenu(false);
                }}
                className="relative p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                title="Notifications"
            >
                <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full"></span>
            </button>
            
            {showNotifications && (
                <div className="absolute top-full right-0 mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-border overflow-hidden ring-1 ring-black ring-opacity-5">
                    <div className="p-3 border-b border-border bg-gray-50 dark:bg-gray-900/50 flex justify-between items-center">
                        <h3 className="font-semibold text-sm text-gray-900 dark:text-white">Notifications</h3>
                        <span className="text-xs text-primary cursor-pointer hover:underline">Tout marquer comme lu</span>
                    </div>
                    <div className="max-h-80 overflow-y-auto">
                        {notifications.map(notif => (
                            <div key={notif.id} className="p-3 border-b border-border last:border-0 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer transition-colors">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-sm font-medium text-gray-900 dark:text-white">{notif.title}</span>
                                    <span className="text-xs text-gray-500 dark:text-gray-400">{notif.time}</span>
                                </div>
                                <p className="text-xs text-gray-600 dark:text-gray-400">{notif.message}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title={theme === 'light' ? 'Passer en mode sombre' : 'Passer en mode clair'}
        >
          {theme === 'light' ? (
            <Moon className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          ) : (
            <Sun className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          )}
        </button>

        {/* Language Selector Dropdown */}
         <div className="relative">
            <button 
                onClick={() => {
                    setShowLanguageMenu(!showLanguageMenu);
                    setShowNotifications(false);
                }}
                className="flex items-center gap-2 px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            >
                <Globe className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    {language === 'fr' ? 'Français' : 'English'}
                </span>
            </button>

            {showLanguageMenu && (
                <div className="absolute top-full right-0 mt-2 w-40 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-border overflow-hidden ring-1 ring-black ring-opacity-5">
                    <button 
                        onClick={() => { setLanguage('fr'); setShowLanguageMenu(false); }}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-between ${language === 'fr' ? 'bg-primary-50 dark:bg-primary-900/20 text-primary' : 'text-gray-700 dark:text-gray-300'}`}
                    >
                        Français
                    </button>
                    <button 
                        onClick={() => { setLanguage('en'); setShowLanguageMenu(false); }}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center justify-between ${language === 'en' ? 'bg-primary-50 dark:bg-primary-900/20 text-primary' : 'text-gray-700 dark:text-gray-300'}`}
                    >
                        English
                    </button>
                </div>
            )}
         </div>

        {/* User Info */}
        <div className="flex items-center gap-3 pl-4 border-l border-border">
          <div className="text-right">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{user?.username || 'Admin'}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">{user?.email || 'admin@pharmac.com'}</p>
          </div>
          <div className="w-9 h-9 bg-primary rounded-full flex items-center justify-center">
            <span className="text-sm font-semibold text-white">
              {user?.username?.charAt(0).toUpperCase() || 'A'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
};
