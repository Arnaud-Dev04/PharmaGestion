import { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { X, Eye, EyeOff, Save } from 'lucide-react';

export const UserFormModal = ({ isOpen, onClose, onSubmit, user = null, isSubmitting = false }) => {
  const { t } = useLanguage();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    role: 'pharmacist',
  });
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isOpen) {
      if (user) {
        setFormData({
          username: user.username,
          password: '', // Don't show password on edit
          role: user.role,
        });
      } else {
        setFormData({
          username: '',
          password: '',
          role: 'pharmacist',
        });
      }
      setErrors({});
    }
  }, [isOpen, user]);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const newErrors = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Le nom d\'utilisateur est requis';
    }

    if (!user && !formData.password) {
      newErrors.password = 'Le mot de passe est requis pour un nouvel utilisateur';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Prepare data
    const dataToSubmit = {
      username: formData.username,
      role: formData.role,
    };
    
    // Only include password if provided
    if (formData.password) {
      dataToSubmit.password = formData.password;
    }

    onSubmit(dataToSubmit);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl w-full max-w-md overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-700">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white">
            {user ? 'Modifier l\'utilisateur' : 'Nouvel Utilisateur'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Nom d'utilisateur <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className={`input w-full ${errors.username ? 'border-red-500 focus:ring-red-500' : ''}`}
              placeholder="Ex: jean.dupont"
            />
            {errors.username && (
              <p className="mt-1 text-sm text-red-500">{errors.username}</p>
            )}
          </div>

          {/* Role */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Rôle
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({ ...formData, role: 'pharmacist' })}
                className={`flex items-center justify-center px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  formData.role === 'pharmacist'
                    ? 'bg-blue-50 border-blue-500 text-blue-700 dark:bg-blue-900/20 dark:text-blue-400'
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-300'
                }`}
              >
                Pharmacien
              </button>
              <button
                type="button"
                onClick={() => setFormData({ ...formData, role: 'admin' })}
                className={`flex items-center justify-center px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                  formData.role === 'admin'
                    ? 'bg-purple-50 border-purple-500 text-purple-700 dark:bg-purple-900/20 dark:text-purple-400'
                    : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-700 dark:text-gray-300 hover:border-gray-300'
                }`}
              >
                Administrateur
              </button>
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              {user ? 'Nouveau mot de passe (optionnel)' : 'Mot de passe *'}
            </label>
            <div className="relative">
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                className={`input w-full pr-10 ${errors.password ? 'border-red-500 focus:ring-red-500' : ''}`}
                placeholder={user ? 'Laisser vide pour ne pas changer' : '••••••••'}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {errors.password && (
              <p className="mt-1 text-sm text-red-500">{errors.password}</p>
            )}
            {user && (
              <p className="mt-1 text-xs text-gray-500">
                Laissez vide pour conserver le mot de passe actuel
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100 dark:border-gray-700 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              disabled={isSubmitting}
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary flex items-center gap-2"
            >
              {isSubmitting ? (
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{user ? 'Mettre à jour' : 'Créer'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
