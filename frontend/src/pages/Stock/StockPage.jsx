import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useLanguage } from '../../context/LanguageContext';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Plus, Pencil, Trash2, AlertCircle } from 'lucide-react';
import stockService from '../../services/stockService';
import { Badge } from '../../components/common/Badge';
import { Pagination } from '../../components/common/Pagination';
import { MedicineModal } from '../../components/stock/MedicineModal';

export const StockPage = () => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  
  const queryClient = useQueryClient();

  // Fetch medicines
  const { data, isLoading, error } = useQuery({
    queryKey: ['medicines', page, search],
    queryFn: () => stockService.getMedicines({ page, search }),
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: stockService.deleteMedicine,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['medicines'] });
    },
  });

  const handleEdit = (medicine) => {
    setSelectedMedicine(medicine);
    setIsModalOpen(true);
  };

  const handleDelete = async (medicine) => {
    if (window.confirm(`${t('confirmDelete')} ${medicine.name}?`)) {
      try {
        await deleteMutation.mutateAsync(medicine.id);
      } catch (error) {
        alert(t('deleteError'));
      }
    }
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedMedicine(null);
  };


  const formatStock = (medicine) => {
    const qty = parseInt(medicine.quantity);
    const total_units_per_box = medicine.units_per_packaging || 1;
    const boxes_per_carton = medicine.boxes_per_carton || 1;
    
    // Total units per carton = units_per_box * boxes_per_carton
    const units_per_carton = total_units_per_box * boxes_per_carton;

    if (units_per_carton <= 1) return `${qty}`;

    // Calculate Cartons
    let cartons = 0;
    let remainder_from_carton = qty;
    
    if (boxes_per_carton > 1) {
        cartons = Math.floor(qty / units_per_carton);
        remainder_from_carton = qty % units_per_carton;
    }

    // Calculate Boxes
    const boxes = Math.floor(remainder_from_carton / total_units_per_box);
    const remainder_from_box = remainder_from_carton % total_units_per_box;
    
    // Calculate Blisters & Units
    const units_per_blister = medicine.units_per_blister || 1;
    let blisters = 0;
    let units = remainder_from_box;

    if (medicine.blisters_per_box > 1) {
       blisters = Math.floor(remainder_from_box / units_per_blister);
       units = remainder_from_box % units_per_blister;
    }

    let parts = [];
    if (cartons > 0) parts.push(`${cartons} ${medicine.carton_type || 'Crt'}`);
    if (boxes > 0) parts.push(`${boxes} ${medicine.packaging || 'Bt'}`);
    if (blisters > 0) parts.push(`${blisters} Pliq`);
    if (units > 0) parts.push(`${units} Un`);
    
    if (parts.length === 0) return "0";
    return parts.join(' + ');
  };

  return (
    <div className="space-y-6">
      {/* ... header ... */}

      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{t('stockManagement')}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">{t('stockSubtitle')}</p>
        </div>
        {user?.role?.toLowerCase() === 'admin' && (
        <button
          onClick={() => setIsModalOpen(true)}
          className="btn btn-primary flex items-center gap-2"
        >
          <Plus className="w-5 h-5" />
          <span>{t('addMedicine')}</span>
        </button>
        )}
      </div>

      {/* Search and Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder={t('search')}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input pl-10"
            />
          </div>
        </div>
      </div>

      {/* Medicines Table */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-gray-600 dark:text-gray-400">{t('loading')}</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <AlertCircle className="w-16 h-16 text-danger mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">{t('loadingError')}</h3>
              <p className="text-gray-600 dark:text-gray-400">{t('errorLoadingMedicines')}</p>
            </div>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-border">
                  <tr>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('name')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('form')} & {t('packaging')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('details')}</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('price')}</th>
                    <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('quantity')}</th>
                    <th className="text-left py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('status')}</th>
                    {user?.role?.toLowerCase() === 'admin' && (
                        <th className="text-right py-3 px-4 text-sm font-medium text-gray-600 dark:text-gray-400">{t('actions')}</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {data?.items && data.items.length > 0 ? (
                    data.items.map((medicine) => (
                      <tr key={medicine.id} className="border-b border-border hover:bg-gray-50 dark:hover:bg-gray-700/50">
                        <td className="py-3 px-4 text-sm text-gray-900 dark:text-white font-medium">{medicine.name}</td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                          {medicine.dosage_form || '-'} / {medicine.packaging || '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-gray-600 dark:text-gray-400">
                           {medicine.packaging ? `1 ${medicine.packaging} = ${medicine.units_per_packaging} un.` : '-'}
                        </td>
                        <td className="py-3 px-4 text-sm text-right font-medium text-gray-900 dark:text-white">
                          F{medicine.price_sell?.toFixed(2) || '0.00'}
                        </td>
                        <td className="py-3 px-4 text-sm text-right text-gray-900 dark:text-white">
                          <div className="flex flex-col items-end">
                            <span className="font-medium">{formatStock(medicine)}</span>
                            <span className="text-[10px] text-gray-400">({medicine.quantity} total)</span>
                          </div>
                        </td>
                        <td className="py-3 px-4 text-sm">
                          <div className="flex gap-2">
                            {medicine.is_low_stock && (
                              <Badge variant="danger">{t('lowStock')}</Badge>
                            )}
                            {medicine.is_expired && (
                              <Badge variant="warning">{t('expired')}</Badge>
                            )}
                            {!medicine.is_low_stock && !medicine.is_expired && (
                              <Badge variant="success">{t('ok')}</Badge>
                            )}
                          </div>
                        </td>
                        {user?.role?.toLowerCase() === 'admin' && (
                        <td className="py-3 px-4 text-sm text-right">
                          <div className="flex items-center justify-end gap-2">
                            <button
                              onClick={() => handleEdit(medicine)}
                              className="p-1.5 hover:bg-primary-50 rounded text-primary transition-colors"
                            >
                              <Pencil className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleDelete(medicine)}
                              className="p-1.5 hover:bg-danger-50 rounded text-danger transition-colors"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                        )}
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={user?.role?.toLowerCase() === 'admin' ? 7 : 6} className="py-12 text-center text-gray-500">
                        {t('noMedicinesFound')}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {data?.total > 0 && (
              <div className="px-4 pb-4">
                <Pagination
                  currentPage={page}
                  totalPages={data.total_pages}
                  totalItems={data.total}
                  onPageChange={setPage}
                />
              </div>
            )}
          </>
        )}
      </div>

      {/* Medicine Modal */}
      {isModalOpen && (
        <MedicineModal
          medicine={selectedMedicine}
          onClose={handleCloseModal}
          onSuccess={() => {
            queryClient.invalidateQueries({ queryKey: ['medicines'] });
            handleCloseModal();
          }}
        />
      )}
    </div>
  );
};
