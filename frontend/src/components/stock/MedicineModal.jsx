import { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useMutation } from '@tanstack/react-query';
import { X } from 'lucide-react';
import stockService from '../../services/stockService';
import { useLanguage } from '../../context/LanguageContext';

export const MedicineModal = ({ medicine, onClose, onSuccess }) => {
  const { t } = useLanguage();
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm({
    defaultValues: medicine || {},
  });

  useEffect(() => {
    if (medicine) {
      // Calculate display quantity based on the hierarchy
      // The input label says "Qté Initiale (Cartons)"
      // So we must convert the Total Units back to Cartons (or Boxes)
      
      const units_per_packaging = medicine.units_per_packaging || 1;
      const boxes_per_carton = medicine.boxes_per_carton || 1;
      const total_units_per_carton = units_per_packaging * boxes_per_carton;
      
      // We display the quantity in "Highest Unit" (Carton if > 1, else Box)
      // This is an approximation if there are broken units, but good enough for the "Initial/Edit" input.
      const displayQuantity = Math.floor(medicine.quantity / total_units_per_carton);

      reset({
        ...medicine,
        quantity: displayQuantity
      });
    }
  }, [medicine, reset]);

  const mutation = useMutation({
    mutationFn: (data) => {
      if (medicine) {
        return stockService.updateMedicine(medicine.id, data);
      } else {
        return stockService.createMedicine(data);
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
    // Convert number fields
    const formattedData = {
      ...data,
      price_buy: parseFloat(data.price_buy) || 0,
      price_sell: parseFloat(data.price_sell) || 0,
      // Handle Quantity: Input is in Cartons (or Boxes if Cartons=1), stored in Units
      quantity: (parseInt(data.quantity) || 0) * (parseInt(data.boxes_per_carton) || 1) * (parseInt(data.blisters_per_box) || 1) * (parseInt(data.units_per_blister) || 1),
      quantity: (parseInt(data.quantity) || 0) * (parseInt(data.boxes_per_carton) || 1) * (parseInt(data.blisters_per_box) || 1) * (parseInt(data.units_per_blister) || 1),
      min_stock_alert: parseInt(data.min_stock_alert) || 10,
      expiry_alert_threshold: parseInt(data.expiry_alert_threshold) || 30,
      family_id: data.family_id ? parseInt(data.family_id) : null,
      type_id: data.type_id ? parseInt(data.type_id) : null,
      boxes_per_carton: parseInt(data.boxes_per_carton) || 1,
      blisters_per_box: parseInt(data.blisters_per_box) || 1,
      units_per_blister: parseInt(data.units_per_blister) || 1,
      // units_per_packaging calculated by backend 
    };

    mutation.mutate(formattedData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {medicine ? t('editMedicine') : t('addMedicine')}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-600 dark:text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit(onSubmit)} className="p-6 overflow-y-auto max-h-[calc(90vh-140px)]">
          <div className="space-y-4">
            
            {/* NOTE: Code field removed as requested. It is auto-generated in backend. */}

            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('name')} <span className="text-danger">*</span>
              </label>
              <input
                type="text"
                {...register('name', { required: t('nameRequired') })}
                className="input"
                placeholder="Paracétamol 500mg"
              />
              {errors.name && (
                <p className="text-sm text-danger mt-1">{errors.name.message}</p>
              )}
            </div>

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('description')}</label>
              <textarea
                {...register('description')}
                className="input"
                rows="3"
                placeholder={`${t('description')}...`}
              />
            </div>

            {/* New Fields: Dosage Form, Packaging, Units */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('cartonName')}</label>
                <input
                  type="text"
                  {...register('carton_type')}
                  className="input"
                  placeholder="Carton"
                  defaultValue="Carton"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('boxesPerCarton')}</label>
                <input
                  type="number"
                  {...register('boxes_per_carton')}
                  className="input"
                  placeholder="Ex: 50"
                  defaultValue={1}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('dosageForm')}</label>
                <input 
                  list="dosage_forms_list" 
                  {...register('dosage_form')} 
                  className="input" 
                  placeholder={`Ex: ${t('tablet')}`}
                />
                <datalist id="dosage_forms_list">
                    <option value={t('tablet')} />
                    <option value={t('syrup')} />
                    <option value={t('injection')} />
                    <option value={t('capsule')} />
                    <option value={t('ointment')} />
                    <option value={t('sachet')} />
                </datalist>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('packagingType')}</label>
                <input 
                  list="packaging_list" 
                  {...register('packaging')} 
                  className="input" 
                  placeholder={`Ex: ${t('box')}`}
                />
                <datalist id="packaging_list">
                    <option value={t('box')} />
                    <option value={t('bottle')} />
                    <option value={t('tube')} />
                    <option value={t('sachet')} />
                </datalist>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('blistersPerBox')}</label>
                <input
                  type="number"
                  {...register('blisters_per_box')}
                  className="input"
                  placeholder="Ex: 10"
                  defaultValue={1}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{t('unitsPerBlister')}</label>
                <input
                  type="number"
                  {...register('units_per_blister')}
                  className="input"
                  placeholder="Ex: 6"
                  defaultValue={1}
                />
              </div>
            </div>

            {/* Prices - Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('buyPrice')} <span className="text-danger">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register('price_buy', { required: t('priceRequired'), min: 0 })}
                  className="input"
                  placeholder="0.00"
                />
                {errors.price_buy && (
                  <p className="text-sm text-danger mt-1">{errors.price_buy.message}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('sellPrice')} <span className="text-danger">*</span>
                </label>
                <input
                  type="number"
                  step="0.01"
                  {...register('price_sell', { required: t('priceRequired'), min: 0 })}
                  className="input"
                  placeholder="0.00"
                />
                {errors.price_sell && (
                  <p className="text-sm text-danger mt-1">{errors.price_sell.message}</p>
                )}
              </div>
            </div>

            {/* Quantity and Alert - Grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('initialQuantity')} <span className="text-danger">*</span>
                </label>
                <input
                  type="number"
                  {...register('quantity', { required: t('quantityRequired'), min: 0 })}
                  className="input"
                  placeholder="Ex: 5"
                />
                <p className="text-xs text-gray-500 mt-1">{t('quantityHelp')}</p>
                {errors.quantity && (
                  <p className="text-sm text-danger mt-1">{errors.quantity.message}</p>
                )}
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  {t('alertThreshold')}
                </label>
                <input
                  type="number"
                  {...register('min_stock_alert')}
                  className="input"
                  placeholder="10"
                />
              </div>
            </div>

            {/* Expiry Date */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('expirationDate')}
              </label>
              <input
                type="date"
                {...register('expiry_date')}
                className="input"
              />
            </div>

            {/* Expiry Alert Threshold */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                {t('expiryAlertThreshold') || 'Alerte Expiration (Jours)'}
              </label>
              <input
                type="number"
                {...register('expiry_alert_threshold')}
                className="input"
                placeholder="30"
                defaultValue={30}
              />
              <p className="text-xs text-gray-500 mt-1">Nombre de jours avant expiration pour déclencher l'alerte.</p>
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
              {isSubmitting ? t('saving') : medicine ? t('update') : t('create')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
