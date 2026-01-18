import { useState, useEffect } from 'react';
import { useLanguage } from '../../context/LanguageContext';
import { adminService } from '../../services/adminService';
import { Save, Shield, Calendar, AlertTriangle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const SuperAdminPage = () => {
  const { t } = useLanguage();
  const { user, isLoading: authLoading } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [licenseInfo, setLicenseInfo] = useState({
    expiry_date: '',
    is_valid: false,
    days_remaining: 0
  });

  useEffect(() => {
    // Wait until auth is done loading
    if (authLoading) return;

    // Basic protection (also handled by backend)
    if (user?.role !== 'super_admin') {
      navigate('/dashboard');
      return;
    }
    fetchLicense();
  }, [user, navigate, authLoading]);

  const fetchLicense = async () => {
    try {
      const data = await adminService.getLicense();
      setLicenseInfo(data);
    } catch (error) {
      console.error('Error fetching license:', error);
      alert('Erreur lors du chargement de la licence');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdate = async (e) => {
    e.preventDefault();
    setUpdating(true);
    try {
      const data = await adminService.updateLicense(licenseInfo.expiry_date);
      setLicenseInfo(data);
      alert('Licence mise à jour avec succès');
    } catch (error) {
      console.error('Error updating license:', error);
      alert('Erreur lors de la mise à jour');
    } finally {
      setUpdating(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center">Chargement...</div>;
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-3">
        <Shield className="w-8 h-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Super Admin</h1>
          <p className="text-gray-600 dark:text-gray-400">Gestion de la licence logicielle</p>
        </div>
      </div>

      <div className="card p-6">
        <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-500 mt-0.5" />
            <div>
              <h3 className="font-medium text-gray-900 dark:text-white mb-1">État actuel de la licence</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Expire le : <span className="font-semibold">{licenseInfo.expiry_date}</span>
              </p>
              <p className={`text-sm font-medium mt-1 ${licenseInfo.is_valid ? 'text-green-600' : 'text-red-600'}`}>
                {licenseInfo.is_valid ? 'VALIDE' : 'EXPIRÉE'} 
                {licenseInfo.is_valid && ` (${licenseInfo.days_remaining} jours restants)`}
              </p>
            </div>
          </div>
        </div>

        <form onSubmit={handleUpdate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Nouvelle date d'expiration
            </label>
            <div className="relative">
              <input
                type="date"
                value={licenseInfo.expiry_date}
                onChange={(e) => setLicenseInfo({...licenseInfo, expiry_date: e.target.value})}
                className="input pl-10"
                required
              />
              <Calendar className="w-4 h-4 text-gray-400 absolute left-3 top-3" />
            </div>
          </div>

          <button
            type="submit"
            disabled={updating}
            className="btn btn-primary w-full flex items-center justify-center gap-2"
          >
            <Save className="w-4 h-4" />
            {updating ? 'Mise à jour...' : 'Mettre à jour la licence'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default SuperAdminPage;
