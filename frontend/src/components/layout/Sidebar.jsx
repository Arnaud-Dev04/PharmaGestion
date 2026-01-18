import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Package, 
  ShoppingCart, 
  History, 
  Truck,
  FileText,
  Pill,
  Settings,
  Users,
  LogOut,
  Shield
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { ThemeToggle } from '../common/ThemeToggle';

const navigation = [
  { name: 'dashboard', to: '/dashboard', icon: LayoutDashboard },
  { name: 'stock', to: '/stock', icon: Package },
  { name: 'pos', to: '/pos', icon: ShoppingCart },
  { name: 'salesHistory', to: '/sales-history', icon: History },
  { name: 'suppliers', to: '/suppliers', icon: Truck },
  { name: 'users', to: '/users', icon: Users, adminOnly: true },
  { name: 'reports', to: '/reports', icon: FileText },
  { name: 'settings', to: '/settings', icon: Settings },
  { name: 'superAdmin', to: '/super-admin', icon: Shield, superAdminOnly: true },
];

export const Sidebar = () => {
  const { logout, user } = useAuth();
  const { t } = useLanguage();

  const isSuperAdmin = user?.role === 'super_admin';
  const isAdmin = user?.role?.toLowerCase() === 'admin' || isSuperAdmin;

  const filteredNavigation = navigation.filter(item => {
    if (isSuperAdmin) return true; // Super admin sees everything (including admin only)
    if (isAdmin) return !item.superAdminOnly; // Admin sees everything except super admin only
    
    // Pharmacist access
    const pharmacistAllowed = ['/pos', '/stock', '/sales-history'];
    return pharmacistAllowed.includes(item.to);
  });

  return (
    <aside className="w-64 bg-white dark:bg-gray-900 border-r border-border flex flex-col">
      {/* Logo & Brand */}
      <div className="h-16 flex items-center px-6 border-b border-border">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <Pill className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">Pharmac+</h1>
            <p className="text-xs text-gray-500">
               {isAdmin ? t('adminMode') : t('pharmacistMode')}
            </p>
          </div>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {filteredNavigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-white'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span>{t(item.name)}</span>
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Bottom Actions */}
      <div className="p-3 border-t border-border space-y-2">

        
        <button
          onClick={logout}
          className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-danger hover:bg-danger-50 transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span>{t('logout')}</span>
        </button>
      </div>
    </aside>
  );
};
