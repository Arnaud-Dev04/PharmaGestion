import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { X } from 'lucide-react';
import supplierService from '../../services/supplierService';
import { useLanguage } from '../../context/LanguageContext';

export const SupplierModal = ({ supplier, onClose, onSuccess }) => {
  const { t } = useLanguage();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    defaultValues: supplier || {},
  });

  useEffect(() => {
    if (supplier) {
      reset(supplier);
    }
  }, [supplier, reset]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (supplier) {
        return supplierService.updateSupplier(supplier.id, data);
      } else {
        return supplierService.createSupplier(data);
      }
    },
    onSuccess: () => {
      onSuccess();
    },
    onError: (error) => {
      alert(`${t('errorPrefix')}: ${error.response?.data?.detail || error.message}`);
    },
  });

  const onSubmit = (data) => {
    mutation.mutate(data);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-lg w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {supplier ? t('editSupplier') : t('addSupplier')}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6">
          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('name')} <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                {...register('name', { required: t('nameRequired') })}
                className="input"
                placeholder="Pharmadis"
              />
              {errors.name && (
                <p className="text-sm text-danger mt-1">{errors.name.message}</p>
              )}
            </div>

            {/* Contact Person */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('contactPerson')}
              </label>
              <input
                type="text"
                {...register('contact')}
                className="input"
                placeholder="Jean Dupont"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('phone')}</label>
              <input
                type="tel"
                {...register('phone')}
                className="input"
                placeholder="+225 XX XX XX XX"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('email')}</label>
              <input
                type="email"
                {...register('email')}
                className="input"
                placeholder="contact@supplier.com"
              />
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('address')}</label>
              <textarea
                {...register('address')}
                className="input"
                rows="3"
                placeholder={t('fullAddress')}
              />
            </div>
          </div>

          {/* Footer */}
          <div className="flex items-center justify-end gap-3 mt-6 pt-4 border-t border-border">
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary"
              disabled={isSubmitting}
            >
              {t('cancel')}
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? t('saving') : supplier ? t('update') : t('create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
