import { useState } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Save, Building2, Phone, CreditCard, Image as ImageIcon, Users, UserPlus, Key, Trash2, X, ShieldAlert } from 'lucide-react';
import { useForm } from 'react-hook-form';
import settingsService from '../../services/settingsService';
import userService from '../../services/userService';
import { adminService } from '../../services/adminService';
import { Badge } from '../../components/common/Badge';

export const SettingsPage = () => {
  const { t } = useLanguage();
  const [activeTab, setActiveTab] = useState('general');
  // Modal states
  const [showUserModal, setShowUserModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);

  const queryClient = useQueryClient();

  // ==============================================================================
  // GENERAL SETTINGS
  // ==============================================================================
  const { data: settings, isLoading: isLoadingSettings } = useQuery({
    queryKey: ['settings'],
    queryFn: settingsService.getSettings,
  });

  const updateSettingsMutation = useMutation({
    mutationFn: settingsService.updateSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(['settings'], data);
      alert(t('settingsUpdated'));
    },
    onError: (error) => {
      alert(t('errorUpdating'));
    },
  });

  const handleGeneralSubmit = (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    // Convert bonus to number roughly
    if (data.bonus_percentage) {
        data.bonus_percentage = parseFloat(data.bonus_percentage);
    }

    updateSettingsMutation.mutate(data);
  };

  // ==============================================================================
  // USER MANAGEMENT
  // ==============================================================================
  const { data: users, isLoading: isLoadingUsers } = useQuery({
    queryKey: ['users'],
    queryFn: userService.getAll,
    enabled: activeTab === 'users', // Only fetch when tab is active
  });

  const createUserMutation = useMutation({
    mutationFn: userService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setShowUserModal(false);
      alert(t('userCreated'));
    },
    onError: (error) => {
      alert(`${t('errorPrefix')}: ${error.response?.data?.detail || error.message}`);
    },
  });

  const deleteUserMutation = useMutation({
    mutationFn: userService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      alert(t('userDeleted'));
    },
    onError: (error) => {
      alert(`${t('errorPrefix')}: ${error.response?.data?.detail || error.message}`);
    },
  });

  const updatePasswordMutation = useMutation({
    mutationFn: ({ userId, password }) => userService.updatePassword(userId, password),
    onSuccess: () => {
      setShowPasswordModal(false);
      setSelectedUser(null);
      alert(t('passwordChanged'));
    },
    onError: (error) => {
        alert(`${t('errorPrefix')}: ${error.response?.data?.detail || error.message}`);
    }
  });

  // ==============================================================================
  // RENDER
  // ==============================================================================

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('settings')}</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">{t('settingsSubtitle')}</p>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-border space-x-4">
        <button
          onClick={() => setActiveTab('general')}
          className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'general'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:text-gray-300'
          }`}
        >
          <Building2 className="w-4 h-4" />
          {t('general')}
        </button>

        <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'users'
                ? 'border-primary text-primary'
                : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:text-gray-300'
            }`}
        >
            <Users className="w-4 h-4" />
            {t('userList') || "Utilisateurs"}
        </button>

        <button
          onClick={() => setActiveTab('administration')}
          className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors flex items-center gap-2 ${
            activeTab === 'administration'
              ? 'border-primary text-primary'
              : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:text-gray-300'
          }`}
        >
          <ShieldAlert className="w-4 h-4" />
          {t('administration')}
        </button>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'general' ? (
          /* GENERAL SETTINGS FORM */
           <div className="card max-w-2xl">
             {isLoadingSettings ? (
               <div className="p-8 text-center text-gray-500 dark:text-gray-400">{t('loading')}</div>
            ) : (
              <form onSubmit={handleGeneralSubmit} className="p-6 space-y-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Building2 className="w-5 h-5 text-gray-400" />
                    {t('pharmacyIdentity')}
                  </h3>
                  
                  <div className="grid gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('pharmacyName')}
                      </label>
                      <input
                        type="text"
                        name="pharmacy_name"
                        defaultValue={settings?.pharmacy_name}
                        className="input"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('address')}
                      </label>
                      <textarea
                        name="pharmacy_address"
                        defaultValue={settings?.pharmacy_address}
                        rows="2"
                        className="input"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('phone')}
                      </label>
                      <div className="relative">
                        <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="tel"
                          name="pharmacy_phone"
                          defaultValue={settings?.pharmacy_phone}
                          className="input pl-10"
                        />
                      </div>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('logoPath')}
                      </label>
                      <div className="relative">
                        <ImageIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                        <input
                          type="text"
                          name="logo_url"
                          defaultValue={settings?.logo_url}
                          placeholder="/logo.png"
                          className="input pl-10"
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                          {t('logoHelp')}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="border-t border-border pt-6 space-y-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <CreditCard className="w-5 h-5 text-gray-400" />
                    {t('salesConfig')}
                  </h3>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        {t('currency')}
                      </label>
                      <input
                        type="text"
                        name="currency"
                        defaultValue={settings?.currency}
                        className="input"
                      />
                    </div>
                    {/* Note: Bonus percentage is now per item in sales, this global setting might be default or deprecated */}
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-border">
                  <button
                    type="submit"
                    disabled={updateSettingsMutation.isPending}
                    className="btn btn-primary flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {updateSettingsMutation.isPending ? t('saving') : t('save')}
                  </button>
                </div>
              </form>
            )}
          </div>
        ) : activeTab === 'users' ? (
          /* USERS MANAGEMENT */
          <div className="card">
            <div className="p-4 border-b border-border flex justify-between items-center">
                <h3 className="font-semibold text-gray-900 dark:text-white">{t('userList')}</h3>
                <button 
                    onClick={() => setShowUserModal(true)}
                    className="btn btn-primary btn-sm flex items-center gap-2"
                >
                    <UserPlus className="w-4 h-4" />
                    {t('add')}
                </button>
            </div>
            
            <div className="overflow-x-auto">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-900/50 text-left text-sm font-medium text-gray-500 dark:text-gray-400">
                        <tr>
                            <th className="px-6 py-3">{t('user')}</th>
                            <th className="px-6 py-3">{t('role')}</th>
                            <th className="px-6 py-3">{t('status')}</th>
                            <th className="px-6 py-3 text-right">{t('actions')}</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-border">
                        {users?.map(user => (
                            <tr key={user.id} className="hover:bg-gray-50 dark:bg-gray-900/50">
                                <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">{user.username}</td>
                                <td className="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                                    <Badge variant={user.role === 'admin' ? 'primary' : 'secondary'}>
                                        {user.role}
                                    </Badge>
                                </td>
                                <td className="px-6 py-4 text-sm">
                                    <Badge variant={user.is_active ? 'success' : 'danger'}>
                                        {user.is_active ? t('active') : t('inactive')}
                                    </Badge>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="flex justify-end gap-2">
                                        <button 
                                            onClick={() => {
                                                setSelectedUser(user);
                                                setShowPasswordModal(true);
                                            }}
                                            className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-primary hover:bg-primary-50 dark:bg-primary-900/30 rounded"
                                            title="Changer mot de passe"
                                        >
                                            <Key className="w-4 h-4" />
                                        </button>
                                        <button 
                                            onClick={() => {
                                                if(window.confirm('Supprimer cet utilisateur ?')) {
                                                    deleteUserMutation.mutate(user.id);
                                                }
                                            }}
                                            className="p-1.5 text-gray-500 dark:text-gray-400 hover:text-danger hover:bg-danger-50 dark:bg-danger-900/30 rounded"
                                            title="Supprimer"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
          </div>
        ) : (
          /* ADMINISTRATION - DATA RESET */
          <div className="space-y-6">
             {/* LICENSE WARNING CONFIGURATION */}
             <div className="card max-w-2xl">
                <form onSubmit={handleGeneralSubmit} className="p-6 space-y-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                        <ShieldAlert className="w-5 h-5 text-yellow-500" />
                        {t('licenseNotificationConfig') || "Configuration Notification Licence"}
                    </h3>

                    <div className="grid gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                {t('triggerDaysBeforeExpiry')}
                            </label>
                            <input
                                type="number"
                                name="license_warning_bdays"
                                defaultValue={settings?.license_warning_bdays ?? 60}
                                className="input"
                            />
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Durée d'affichage (Secondes)
                            </label>
                            <input
                                type="number"
                                name="license_warning_duration"
                                defaultValue={settings?.license_warning_duration ?? 30}
                                className="input"
                            />
                        </div>
                        <div>
                             <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                Message d'alerte
                            </label>
                            <textarea
                                name="license_warning_message"
                                defaultValue={settings?.license_warning_message}
                                rows="3"
                                className="input"
                            />
                        </div>
                    </div>

                    <div className="flex justify-end pt-4 border-t border-border">
                        <button
                            type="submit"
                            disabled={updateSettingsMutation.isPending}
                            className="btn btn-primary flex items-center gap-2"
                        >
                            <Save className="w-4 h-4" />
                            {updateSettingsMutation.isPending ? t('saving') : t('save')}
                        </button>
                    </div>
                </form>
             </div>

             {/* DATA RESET ZONE */}
             <div className="card max-w-2xl bg-red-50 dark:bg-red-900/10 border-red-200 dark:border-red-800">
             <div className="p-6">
                <h3 className="text-lg font-bold text-red-700 dark:text-red-400 flex items-center gap-2 mb-4">
                  <ShieldAlert className="w-6 h-6" />
                  Zone de Danger - Réinitialisation
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300 mb-6">
                  Cochez les données que vous souhaitez supprimer définitivement. Cette action est irréversible.
                </p>

                <form onSubmit={(e) => {
                  e.preventDefault();
                  if (!window.confirm("ÊTES-VOUS SÛR ? Cette action est irréversible !")) return;
                  
                  const fd = new FormData(e.target);
                  const data = {
                    sales: fd.get('sales') === 'on',
                    products: fd.get('products') === 'on',
                    users: fd.get('users') === 'on'
                  };
                  
                  if (!data.sales && !data.products && !data.users) {
                    alert("Veuillez sélectionner au moins une option.");
                    return;
                  }

                  adminService.resetData(data).then(res => {
                    alert(`Réinitialisation effectuée :\nVentes : ${res.deleted.sales || 0}\nProduits : ${res.deleted.products || 0}\nUtilisateurs : ${res.deleted.users || 0}`);
                  }).catch(err => {
                       alert("Erreur lors de la réinitialisation: " + err.message);
                  });
                }}>
                  <div className="space-y-4 mb-6">
                    <label className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                      <input type="checkbox" name="sales" className="form-checkbox h-5 w-5 text-red-600" />
                      <span className="text-gray-700 dark:text-gray-300 font-medium">Vider l'historique des ventes</span>
                    </label>
                    <label className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                      <input type="checkbox" name="products" className="form-checkbox h-5 w-5 text-red-600" />
                      <span className="text-gray-700 dark:text-gray-300 font-medium">Vider le stock (Tous les médicaments)</span>
                    </label>
                    <label className="flex items-center space-x-3 p-3 bg-white dark:bg-gray-800 rounded border border-gray-200 dark:border-gray-700">
                      <input type="checkbox" name="users" className="form-checkbox h-5 w-5 text-red-600" />
                      <span className="text-gray-700 dark:text-gray-300 font-medium">Supprimer tous les utilisateurs (Sauf Super Admins)</span>
                    </label>
                  </div>

                  <button type="submit" className="w-full btn bg-red-600 hover:bg-red-700 text-white font-bold py-3">
                    CONFIRMER LA SUPPRESSION
                  </button>
                </form>
             </div>
          </div>
        </div>
        )}
      </div>

      {/* ADD USER MODAL */}
      {showUserModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold">{t('newUser')}</h3>
                    <button onClick={() => setShowUserModal(false)}><X className="w-5 h-5" /></button>
                </div>
                <form onSubmit={(e) => {
                    e.preventDefault();
                    const fd = new FormData(e.target);
                    createUserMutation.mutate(Object.fromEntries(fd));
                }}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('username')}</label>
                            <input name="username" type="text" required className="input mt-1" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('password')}</label>
                            <input name="password" type="password" required minLength="4" className="input mt-1" />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('role')}</label>
                            <select name="role" className="input mt-1">
                                <option value="pharmacist">{t('pharmacist')}</option>
                                <option value="admin">{t('admin')}</option>
                            </select>
                        </div>
                    </div>
                    <div className="mt-6 flex justify-end gap-3">
                        <button type="button" onClick={() => setShowUserModal(false)} className="btn btn-secondary">{t('cancel')}</button>
                        <button type="submit" className="btn btn-primary" disabled={createUserMutation.isPending}>{t('add')}</button>
                    </div>
                </form>
            </div>
        </div>
      )}

      {/* CHANGE PASSWORD MODAL */}
      {showPasswordModal && selectedUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full p-6">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-lg font-bold">{t('changePassword')} : {selectedUser.username}</h3>
                    <button onClick={() => setShowPasswordModal(false)}><X className="w-5 h-5" /></button>
                </div>
                <form onSubmit={(e) => {
                    e.preventDefault();
                    const fd = new FormData(e.target);
                    updatePasswordMutation.mutate({
                        userId: selectedUser.id,
                        password: fd.get('password')
                    });
                }}>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">{t('newPassword')}</label>
                            <input name="password" type="password" required minLength="4" className="input mt-1" />
                        </div>
                    </div>
                    <div className="mt-6 flex justify-end gap-3">
                        <button type="button" onClick={() => setShowPasswordModal(false)} className="btn btn-secondary">{t('cancel')}</button>
                        <button type="submit" className="btn btn-primary" disabled={updatePasswordMutation.isPending}>{t('save')}</button>
                    </div>
                </form>
            </div>
        </div>
      )}
    </div>
  );
};
